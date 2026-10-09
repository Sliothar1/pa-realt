"""Compact star + constellation-line data from d3-celestial (BSD-3, Olaf Frohn; Hipparcos/HYG-derived)."""
import json
S = json.load(open('data/raw/d3c_stars.6.json')); N = json.load(open('data/raw/d3c_starnames.json'))
L = json.load(open('data/raw/d3c_constellations.lines.json')); C = json.load(open('data/raw/d3c_constellations.json'))
stars = []
for f in S['features']:
    m = f['properties']['mag']
    if m > 5.3: continue
    ra, de = f['geometry']['coordinates']; ra = (ra + 360) % 360
    try: bv = round(float(f['properties']['bv']), 2)
    except Exception: bv = 0.6
    nm = N.get(str(f['id']), {}).get('name', '') if m < 1.6 else ''
    stars.append([round(ra, 3), round(de, 3), m, bv, nm])
lines = []
for f in L['features']:
    for seg in f['geometry']['coordinates']:
        lines.append([[round((p[0] + 360) % 360, 2), round(p[1], 2)] for p in seg])
names = [[f['properties']['en'], round((f['geometry']['coordinates'][0] + 360) % 360, 1), round(f['geometry']['coordinates'][1], 1)] for f in C['features'] if int(f['properties']['rank']) == 1]
json.dump({'src': 'd3-celestial (c) 2015 Olaf Frohn, BSD-3-Clause; star data derived from the Hipparcos/HYG catalogues', 'stars': stars, 'lines': lines, 'names': names}, open('site/data/sky.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(stars), len(lines), len(names), [s for s in stars if s[4]][:5])
