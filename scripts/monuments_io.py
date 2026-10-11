"""Write the monument table that build_data.py derives from the raw SMR data, in the form pa-core ingests:
data/monuments.csv (one row per monument, columns = meta['fields'], core sites then standing stones)
and data/monuments_meta.json (the sites.json meta block, key order kept).
  python3 scripts/monuments_io.py --from-site-data   one-off bootstrap from the published site/data (no raw data needed)"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vendor', 'pa-core'))
from pa_core.adapters.tabular import write_table
from pa_core.schema import Schema, to_text

CSV, META = 'data/monuments.csv', 'data/monuments_meta.json'


def write_monuments(core, ss, meta):
    sch = Schema.load('data/d4m/schema.json'); f = meta['fields']
    cell = lambda h, v: v if h == 'smrs' else to_text(sch.col_type('A_mon', h), v)
    write_table(CSV, f, [[cell(h, v) for h, v in zip(f, r)] for r in core + ss])
    with open(META, 'w', encoding='utf-8', newline='') as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1); fh.write('\n')


if __name__ == '__main__' and '--from-site-data' in sys.argv:
    d = json.load(open('site/data/sites.json', encoding='utf-8')); st = json.load(open('site/data/standing.json', encoding='utf-8'))
    write_monuments(d['sites'], st['sites'], d['meta']); print(len(d['sites']) + len(st['sites']), 'monuments ->', CSV)
