"""POST HOC sensitivity checks for T2 (not part of any verdict; written after T2 was scored).
(a) without the two surveyed featured axes; (b) one tomb per 2 km cluster (first in file order), to reduce non-independence."""
import sys, json, math, numpy as np
sys.argv = ['x']; src = open('scripts/run_tests.py').read().split("if __name__ == '__main__':")[0]; exec(src)
e = EPS['3200']; tg_sun = [e, 0, -e]; tg_moon = [e + I_MOON, -(e + I_MOON), e - I_MOON, -(e - I_MOON)]
def run(P, feat):
    ids = [k for k, _ in P] + list(feat); n = len(ids); nP = len(P); rng = np.random.default_rng(SEED); grid = np.arange(0, 360, 0.5)
    ds = np.array([dec(grid, HZ[k], SITES[k][2], 'sun') for k in ids]); dm = np.array([dec(grid, HZ[k], SITES[k][2], 'moon') for k in ids])
    os_ = np.array([ds[i, int(b * 45)] for i, (_, b) in enumerate(P)] + [FEAT[k][1] for k in feat]); om = np.array([dm[i, int(b * 45)] for i, (_, b) in enumerate(P)] + [FEAT[k][1] for k in feat])
    kf = lambda d, t: np.exp(-0.5 * ((d - t) / SIG) ** 2) / (SIG * math.sqrt(2 * math.pi))
    sc = lambda a, b: sum(kf(a, t).mean(-1) for t in tg_sun) + sum(kf(b, t).mean(-1) for t in tg_moon)
    idx = np.empty((NDRAW, n), int); idx[:, :nP] = rng.integers(0, 16, (NDRAW, nP)) * 45; idx[:, nP:] = rng.integers(0, 720, (NDRAW, n - nP))
    r = np.arange(n); obs = float(sc(os_, om)); null = sc(ds[r, idx], dm[r, idx]); return {'n': n, 'stat': obs, 'null_mean': float(null.mean()), 'p': mc_p(obs, null)}
P = [x for x in pop('pt') if x[0] not in FEAT]
out = {'note': 'POST HOC, descriptive; written after T2 was scored', 'without_featured_axes': run(P, [])}
keep, seen = [], []
for k, b in P + [(k, None) for k in FEAT]:
    la, lo = SITES[k][2], SITES[k][3]
    if any(math.hypot((la - a) * 111.2, (lo - c) * 111.2 * math.cos(la * D)) <= 2 for a, c in seen): continue
    seen.append((la, lo)); keep.append((k, b))
out['one_per_2km_cluster'] = run([x for x in keep if x[1] is not None], [k for k, b in keep if b is None])
print(json.dumps(out, indent=1)); json.dump(out, open('data/tests/posthoc_t2.json', 'w'), indent=1)
