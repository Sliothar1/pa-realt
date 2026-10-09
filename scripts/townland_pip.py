"""For mapped records whose townland Irish name was missing/ambiguous by name+county,
query Tailte Éireann townland polygons at the record's ITM point; accept the Irish name only
if the polygon's ENGLISH name equals the SMR townland name (normalised)."""
import json, urllib.request, urllib.parse, re, concurrent.futures as cf
B = "https://gsi.geodata.gov.ie/server/rest/services/Third_Party/IE_GSI_Tailte_Eireann_Townlands_IE26_ITM/FeatureServer/0/query"
def norm(t):
    t = re.sub(r'\(.*?(\)|$)', ' ', str(t).upper()).split(',')[0]; return re.sub(r'\s+', ' ', t).strip()
def q(rec):
    smrs, e, n, tn = rec
    p = urllib.parse.urlencode(dict(geometry=f'{e},{n}', geometryType='esriGeometryPoint', inSR=2157, spatialRel='esriSpatialRelIntersects', outFields='ENGLISH,GAEILGE', returnGeometry='false', f='json'))
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(B + '?' + p, timeout=30)); f = d.get('features', [])
            if f and norm(f[0]['attributes']['ENGLISH']) == norm(tn): return smrs, f[0]['attributes']['GAEILGE']
            return smrs, None
        except Exception: pass
    return smrs, None
import os
out = json.load(open('data/townland_pip_ga.json', encoding='utf-8')) if os.path.exists('data/townland_pip_ga.json') else {}
for fn in ('site/data/sites.json', 'site/data/standing.json'):
    d = json.load(open(fn, encoding='utf-8'))
    todo = [(s[0], s[7], s[8], s[4]) for s in d['sites'] if not s[5] and s[0] not in out]
    with cf.ThreadPoolExecutor(8) as ex:
        for smrs, ga in ex.map(q, todo):
            if ga: out[smrs] = ga
    print(fn, len(todo), 'resolved so far', len(out))
json.dump(out, open('data/townland_pip_ga.json', 'w', encoding='utf-8'), ensure_ascii=False)
