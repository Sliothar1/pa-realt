"""Export D4M-style (row, col, val) triples for the alignment tests, through pa-core (rows mon:<SMR>).
A_prop : monument x property   (col = 'field|value', val = 1)
A_sky  : monument x sky-event  (col = 'event|epoch', val = flat-horizon azimuth, deg, float)
Provenance and visibility for mon: rows live in A_prov / A_mon (pa-core tabular adapter).
Reads data/d4m/A_mon.tsv (run scripts/d4m_build.py)."""
import json, os, sys
sys.path.insert(0, 'scripts'); import astro
sys.path.insert(0, 'vendor/pa-core')
from pa_core.schema import Schema
from pa_core.dataset import Dataset, typed_load, write_dataset
SCH = Schema.load('data/d4m/schema.json')
A = typed_load('data/d4m', SCH, errors=[]).assocs['A_mon']  # A_prop/A_sky are rewritten below
m = A['dataset:smr']['meta']
sites = [[r.split(':', 1)[1]] + [c[h] for h in m['fields'][1:]] for r, c in sorted(A.items(), key=lambda kv: kv[1].get('meta|order', -1)) if r.startswith('mon:')]
EV = [('WS_rise', -1, True), ('WS_set', -1, False), ('SS_rise', 1, True), ('SS_set', 1, False), ('EQ_rise', 0, True), ('EQ_set', 0, False)]
P, S = {}, {}
for s in sites:
    r = 'mon:' + s[0]
    p = P.setdefault(r, {}); p['class|' + s[1]] = 1; p['county|' + m['counties'][s[6]]] = 1
    if s[5]: p['townland_ga|' + s[5]] = 1
    for ep, yr in (('3200BC', -3199), ('2026', 2026)):
        e = astro.obliquity(yr)
        for k, sg, rise in EV:
            az = astro.event_az(sg * e, s[2], None, rise)
            S.setdefault(r, {})[f'{k}|{ep}'] = float(f'{az:.2f}')
        for k, dec, rise in (('MjN_set', e + astro.I_MOON, False), ('MjS_rise', -(e + astro.I_MOON), True)):
            az = astro.event_az(dec, s[2], None, rise, 'moon'); S[r][f'{k}|{ep}'] = float(f'{az:.2f}')
write_dataset(Dataset({'A_prop': P, 'A_sky': S}), 'data/d4m', SCH)
print(len(sites), 'monuments exported')
