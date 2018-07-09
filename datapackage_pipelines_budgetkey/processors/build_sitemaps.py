from datapackage_pipelines.wrapper import ingest, spew

import os
import itertools
from sqlalchemy import create_engine

def generate_sitemap(kind, db_table, doc_id):
    engine = create_engine(os.environ['DPP_DB_ENGINE'])
    rows = (dict(r) for r in engine.execute('select * from {}'.format(db_table)))
    doc_ids = ((doc_id.format(**r), r['__last_modified_at']) for r in rows)
    index = 0
    while True:
        filename = '/var/datapackages/sitemaps/{}.{:04d}.xml'.format(kind, index)
        with open(filename, 'w') as out:
            out.write('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
''')
            batch = list(itertools.islice(doc_ids, 10000))
            for doc_id, last_modified in batch:
                out.write('''   <url>
      <loc>https://next.obudget.org/i/{}</loc>
      <lastmod>{}</lastmod>
   </url>
'''.format(doc_id, last_modified.isoformat()))
            out.write('''</urlset>''')


if __name__ == '__main__':
    params, dp, res_iter = ingest()

    kind = params['kind']
    db_table = params['db-table']
    doc_id = params['doc-id']

    generate_sitemap(kind, db_table, doc_id)

    spew(dp, res_iter)