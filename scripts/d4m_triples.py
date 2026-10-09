"""Export D4M-style (row, col, val) triples for the alignment tests (first pass: TSV, no D4M dependency).
A_prop : monument x property   (col = 'field|value', val = 1)
A_sky  : monument x sky-event  (col = 'event|epoch', val = flat-horizon azimuth, deg)
Load later with D4M.py:  Assoc(rows, cols, vals) from these files."""
import json, sys
sys.path.insert(0, 'scripts'); import astro
d = json.load(open('site/data/sites.json', encoding='utf-8')); m = d['meta']
sites = d['sites'] + json.load(open('site/data/standing.json', encoding='utf-8'))['sites']
EV = [('WS_rise', -1, True), ('WS_set', -1, False), ('SS_rise', 1, True), ('SS_set', 1, False), ('EQ_rise', 0, True), ('EQ_set', 0, False)]
with open('data/d4m/A_prop.tsv', 'w', encoding='utf-8') as P, open('data/d4m/A_sky.tsv', 'w', encoding='utf-8') as S:
    for s in sites:
        r = s[0]
        P.write(f'{r}\tclass|{s[1]}\t1\n{r}\tcounty|{m["counties"][s[6]]}\t1\n')
        if s[5]: P.write(f'{r}\ttownland_ga|{s[5]}\t1\n')
        for ep, yr in (('3200BC', -3199), ('2026', 2026)):
            e = astro.obliquity(yr)
            for k, sg, rise in EV:
                az = astro.event_az(sg * e, s[2], None, rise)
                S.write(f'{r}\t{k}|{ep}\t{az:.2f}\n')
            for k, dec, rise in (('MjN_set', e + astro.I_MOON, False), ('MjS_rise', -(e + astro.I_MOON), True)):
                az = astro.event_az(dec, s[2], None, rise, 'moon'); S.write(f'{r}\t{k}|{ep}\t{az:.2f}\n')
print(len(sites), 'monuments exported')
