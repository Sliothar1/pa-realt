"""Horizon profiles for featured sites from Copernicus GLO-30 DSM (30 m surface model).
Ray-march 0.5 deg azimuth steps from START_M to MAX_M, Earth curvature + refraction k=0.13.
DSM includes trees/buildings; sampling starts at START_M to skip the monument itself and near clutter.
Output: site/data/horizons.json  (altitudes in degrees, apparent)."""
import json, math, os, numpy as np, tifffile, pandas as pd
DEM = 'data/dem'; R = 6371000.0; K = 0.13; EYE = 1.6
START_M, MAX_M, STEP_M, AZ_STEP = 400.0, 60000.0, 30.0, 0.5
_cache = {}
def tile(lat0, lon0):
    key = (lat0, lon0)
    if key not in _cache:
        f = f'{DEM}/Copernicus_DSM_COG_10_N{lat0:02d}_00_W{-lon0:03d}_00_DEM.tif'
        _cache[key] = tifffile.imread(f) if os.path.exists(f) else None
    return _cache[key]
def elev(lat, lon):
    lat0, lon0 = math.floor(lat), math.floor(lon)
    a = tile(lat0, lon0)
    if a is None: return 0.0  # sea / no tile
    ny, nx = a.shape
    y = (lat0 + 1 - lat) * ny; x = (lon - lon0) * nx
    i, j = min(int(y), ny - 1), min(int(x), nx - 1)
    v = float(a[i, j]); return max(v, 0.0)
def profile(lat, lon):
    h0 = elev(lat, lon) + EYE
    azs = np.arange(0, 360, AZ_STEP); out = []; far = []
    dists = np.arange(START_M, MAX_M, STEP_M)
    cl = math.cos(math.radians(lat))
    for az in azs:
        a = math.radians(az); best = -2.0; bd = 0
        for d in dists:
            la = lat + (d * math.cos(a)) / R * 180 / math.pi
            lo = lon + (d * math.sin(a)) / (R * cl) * 180 / math.pi
            h = elev(la, lo)
            drop = d * d / (2 * R) * (1 - K)
            alt = math.degrees(math.atan2(h - h0 - drop, d))
            if alt > best: best, bd = alt, d
        out.append(round(best, 3)); far.append(int(bd))
    return h0 - EYE, out, far

df = pd.read_csv('data/raw/SMROpenData_20251201.csv', low_memory=False)
def smr(s):
    r = df[df.SMRS == s].iloc[0]; return float(r.LATITUDE), float(r.LONGITUDE)
cm = df[(df.COUNTY == 'SLIGO') & df.TOWNLAND.str.contains('CARROWMORE', na=False) & (df.MONUMENT_CLASS == 'Megalithic tomb - passage tomb') & (df.ITM_E > 0)]
FEATURED = {
 'newgrange': smr('ME019-045----'), 'knowth': smr('ME019-030001-'), 'dowth': smr('ME020-017----'),
 'cairnT': smr('ME015-012004-'), 'carrowmore': (float(cm.LATITUDE.mean()), float(cm.LONGITUDE.mean())),
 'carrowkeelG': smr('SL040-089----'), 'drombeg': smr('CO143-051002-'), 'beltany': smr('DG070-026001-'),
}
res = {}
for k, (la, lo) in FEATURED.items():
    g, prof, far = profile(la, lo)
    res[k] = {'lat': round(la, 5), 'lon': round(lo, 5), 'ground_m': round(g, 1), 'step': AZ_STEP, 'alt': prof, 'dist_m': far}
    i = int(round(135 / AZ_STEP)); print(k, round(g, 1), 'alt@135', prof[i], 'max', max(prof), 'min', min(prof))
res['_meta'] = {'dem': 'Copernicus GLO-30 DSM (30 m), AWS open data copernicus-dem-30m', 'start_m': START_M, 'max_m': MAX_M, 'k': K, 'eye_m': EYE,
  'note': 'Digital SURFACE model: includes modern trees and buildings; nearest-neighbour sampling; first 400 m skipped. Indicative, not a field survey.'}
json.dump(res, open('site/data/horizons.json', 'w'), separators=(',', ':'))
