"""Web shards of the real-horizon profiles (from data/tests/horizons_all.npz, made by scripts/horizon_all.py).
site/data/hz/index.json        {county: number of buckets}
site/data/hz/c<county>-<b>.json {SMRS: [ground_m, base64 uint8 x 360]}  bucket b = (sum of char codes of SMRS) % n
site/data/hz/pt.json           every passage tomb (for the midwinter egg rays)
1 deg azimuth steps (the whole-degree samples of the 0.5 deg profile); alt = v/20 - 1 deg."""
import json, glob, os, math, base64, numpy as np
Z = np.load('data/tests/horizons_all.npz'); A, I, G = Z['alt'], [str(x) for x in Z['ids']], Z['ground']
d = json.load(open('site/data/sites.json', encoding='utf-8')); st = json.load(open('site/data/standing.json', encoding='utf-8'))
S = {s[0]: s for s in d['sites'] + st['sites']}
def enc(a):
    a1 = a[::2]                                           # the whole-degree samples
    return base64.b64encode(np.clip(np.round((a1 + 1) * 20), 0, 255).astype(np.uint8).tobytes()).decode()
for f in glob.glob('site/data/hz/*.json'): os.remove(f)
os.makedirs('site/data/hz', exist_ok=True)
by = {}
for i, k in enumerate(I): by.setdefault(S[k][6], []).append((k, [round(float(G[i])), enc(A[i])]))
idx = {}; tot = 0; mx = 0
for c, items in by.items():
    n = max(1, math.ceil(len(items) * 500 / 110000)); idx[c] = n; sh = [dict() for _ in range(n)]
    for k, v in items: sh[sum(map(ord, k)) % n][k] = v
    for b, v in enumerate(sh):
        fn = f'site/data/hz/c{c}-{b}.json'; json.dump(v, open(fn, 'w'), separators=(',', ':')); sz = os.path.getsize(fn); tot += sz; mx = max(mx, sz)
json.dump(idx, open('site/data/hz/index.json', 'w'))
pt = {k: [S[k][2], S[k][3], enc(A[i])] for i, k in enumerate(I) if S[k][1] == 'pt'}
json.dump(pt, open('site/data/hz/pt.json', 'w'), separators=(',', ':'))
print('files', sum(idx.values()), 'total', tot, 'largest', mx, 'pt.json', os.path.getsize('site/data/hz/pt.json'))
