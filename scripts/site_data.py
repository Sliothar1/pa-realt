"""Write site/data/sites.json and standing.json from the pa-core export (build/d4m-export/), which is
default-deny (data/d4m/export.allow.json). Same shape and bytes as build_data.py wrote before pa-core."""
import json
E = 'build/d4m-export/'
mon = json.load(open(E + 'mon.json', encoding='utf-8'))
meta = json.load(open(E + 'dataset.json', encoding='utf-8'))['dataset:smr']['meta']
F = meta['fields']
rows = [[r.split(':', 1)[1] if h == 'smrs' else c[h] for h in F] for r, c in sorted(mon.items(), key=lambda kv: kv[1]['meta|order'])]
core = [x for x in rows if x[1] != 'ss']; ss = [x for x in rows if x[1] == 'ss']
json.dump({'meta': meta, 'sites': core}, open('site/data/sites.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump({'sites': ss}, open('site/data/standing.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(core), 'core +', len(ss), 'standing -> site/data')
