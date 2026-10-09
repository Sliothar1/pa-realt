"""Real-horizon profiles for ALL mapped monuments, same method as scripts/horizon.py
(Copernicus GLO-30 DSM, 0.5 deg azimuth, 400 m to 60 km in 30 m steps, k = 0.13, eye 1.6 m, nearest-neighbour).
Vectorised on a DEM mosaic. Outputs:
  data/tests/horizons_all.npz      full 0.5 deg profiles (float32) for the tests (not committed: regenerate)
  site/data/hz/c<county>.json      1 deg profiles for the web, uint8 base64: alt = v/20 - 1 deg (-1 .. 11.75 deg)
"""
import json, os, glob, math, base64, numpy as np, tifffile
from multiprocessing import Pool
R = 6371000.0; K = 0.13; EYE = 1.6; START_M, MAX_M, STEP_M, AZ_STEP = 400.0, 60000.0, 30.0, 0.5
LAT_TOP, LON_W, NR, NC = 56, -11, 3600, 2400
MOS = np.zeros(((LAT_TOP - 51) * NR, 6 * NC), dtype=np.float32)
for f in glob.glob('data/dem/*.tif'):
    import re; m = re.search(r'_N(\d+)_00_W(\d+)_00_', os.path.basename(f)); lat0 = int(m.group(1)); lon0 = -int(m.group(2))
    if not (51 <= lat0 < LAT_TOP and LON_W <= lon0 < LON_W + 6): continue
    r0 = (LAT_TOP - 1 - lat0) * NR; c0 = (lon0 - LON_W) * NC
    MOS[r0:r0 + NR, c0:c0 + NC] = tifffile.imread(f)
np.maximum(MOS, 0, out=MOS)
def elev(lat, lon):
    r = np.clip(((LAT_TOP - lat) * NR).astype(np.int64), 0, MOS.shape[0] - 1)
    c = np.clip(((lon - LON_W) * NC).astype(np.int64), 0, MOS.shape[1] - 1)
    return MOS[r, c]
AZS = np.radians(np.arange(0, 360, AZ_STEP)); DISTS = np.arange(START_M, MAX_M, STEP_M)
DROP = DISTS ** 2 / (2 * R) * (1 - K)
def profile(latlon):
    lat, lon = latlon
    h0 = float(elev(np.array([lat]), np.array([lon]))[0]) + EYE
    cl = math.cos(math.radians(lat)); out = np.empty(len(AZS), np.float32)
    for k0 in range(0, len(AZS), 90):
        a = AZS[k0:k0 + 90, None]
        la = lat + (DISTS * np.cos(a)) / R * 180 / math.pi
        lo = lon + (DISTS * np.sin(a)) / (R * cl) * 180 / math.pi
        h = elev(la, lo)
        alt = np.degrees(np.arctan2(h - h0 - DROP, DISTS))
        out[k0:k0 + 90] = np.maximum(alt.max(axis=1), -2.0)
    return h0 - EYE, out
if __name__ == '__main__':
    d = json.load(open('site/data/sites.json', encoding='utf-8')); st = json.load(open('site/data/standing.json', encoding='utf-8'))
    sites = d['sites'] + st['sites']
    g, p = profile((53.69473, -6.47554))  # validation gate (Newgrange, Patrick 1974: +0 deg 51')
    print('Newgrange ground', round(g, 1), 'alt@135', round(float(p[270]), 3), 'Patrick 0.850')
    with Pool(7) as pool: res = pool.map(profile, [(s[2], s[3]) for s in sites], chunksize=20)
    os.makedirs('data/tests', exist_ok=True)
    np.savez_compressed('data/tests/horizons_all.npz', ids=np.array([s[0] for s in sites]), ground=np.array([r[0] for r in res], np.float32),
                        alt=np.stack([r[1] for r in res]).astype(np.float32))
    os.makedirs('site/data/hz', exist_ok=True)
    for f in glob.glob('site/data/hz/*.json'): os.remove(f)
    shards = {}
    for s, (g, a) in zip(sites, res):
        q = np.clip(np.round((a[::2] + 1) * 20), 0, 255).astype(np.uint8)
        shards.setdefault(s[6], {})[s[0]] = [round(float(g)), base64.b64encode(q.tobytes()).decode()]
    tot = 0
    for c, v in shards.items():
        fn = f'site/data/hz/c{c}.json'; json.dump(v, open(fn, 'w'), separators=(',', ':')); tot += os.path.getsize(fn)
    print('sites', len(sites), 'web bytes', tot)
