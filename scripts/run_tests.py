"""Score the pre-registered tests T1-T5 (prereg/tests_v1.json, interpretation notes in prereg/addendum_v1.md).
Committed BEFORE scoring together with the frozen parser scripts/orient_parse.py.
  python scripts/run_tests.py              -> data/tests/results_v1.json + site/data/tests_v1.json
  python scripts/run_tests.py --synthetic  -> replaces every parsed bearing with a random one (pipeline check only, no real data scored)
Needs data/tests/horizons_all.npz from scripts/horizon_all.py and data/tests/orientations.json from scripts/orient_parse.py."""
import json, sys, math, subprocess, numpy as np
SEED, NDRAW = 20261009, 10000
NDRAW_T4 = int(__import__('os').environ.get('T4DRAWS', 1000))   # 1,000 as pre-registered; env override only for quick pipeline checks
SYN = '--synthetic' in sys.argv
D = math.pi / 180; I_MOON = 5.145; PAR = 0.95; SIG = 1.5
def obliquity(year):
    U = (year - 2000) / 10000; c = [84381.448, -4680.93, -1.55, 1999.25, -51.38, -249.67, -39.05, 7.12, 27.87, 5.79, 2.45]
    return sum(ci * U ** i for i, ci in enumerate(c)) / 3600
EPS = {'3200': obliquity(-3199), '2200': obliquity(-2199)}
def refr(h): h = np.maximum(h, -1.5); return 1 / np.tan((h + 7.31 / (h + 4.4)) * D) / 60
def dec(az, h_app, lat, body='sun'):
    ht = h_app - refr(h_app) + (PAR * np.cos(h_app * D) if body == 'moon' else 0)
    return np.arcsin(np.sin(lat * D) * np.sin(ht * D) + np.cos(lat * D) * np.cos(ht * D) * np.cos(az * D)) / D
def az_for(dc, lat, ht, rising):
    c = (math.sin(ht * D) - math.sin(lat * D) * math.sin(dc * D)) / (math.cos(lat * D) * math.cos(dc * D))
    if abs(c) > 1: return None
    H = math.acos(c); H = -H if rising else H
    return (math.atan2(math.sin(H), math.cos(H) * math.sin(lat * D) - math.tan(dc * D) * math.cos(lat * D)) / D + 180) % 360
def hor_at(prof, az):
    i = (np.asarray(az) % 360) / 0.5; i0 = np.floor(i).astype(int) % 720; f = i - np.floor(i)
    return prof[i0] * (1 - f) + prof[(i0 + 1) % 720] * f
def event_az(dc, lat, prof, rising):
    A = 90.0 if rising else 270.0
    for _ in range(8):
        h = float(hor_at(prof, A)) if prof is not None else 0.0
        A2 = az_for(dc, lat, h - float(refr(h)), rising)
        if A2 is None: return None
        A = A2
    return A
def mc_p(obs, null): return float((1 + np.sum(null >= obs - 1e-12)) / (len(null) + 1))
def holm(ps):
    k = sorted(ps, key=ps.get); m = len(k); out = {}; run = 0
    for j, t in enumerate(k): run = max(run, min(1, (m - j) * ps[t])); out[t] = run
    return out
def summ(null): return {'mean': float(np.mean(null)), 'sd': float(np.std(null)), 'q025': float(np.quantile(null, .025)), 'q975': float(np.quantile(null, .975))}

S = json.load(open('site/data/sites.json', encoding='utf-8')); META = S['meta']; SITES = {s[0]: s for s in S['sites']}
CO = {c: i for i, c in enumerate(META['counties'])}; CK = {CO['CORK'], CO['KERRY']}
Z = np.load('data/tests/horizons_all.npz'); _A, _I, _G = Z['alt'], [str(x) for x in Z['ids']], Z['ground']
HZ = {k: _A[i] for i, k in enumerate(_I)}; GROUND = {k: float(_G[i]) for i, k in enumerate(_I)}
O = json.load(open('data/tests/orientations.json', encoding='utf-8'))
if SYN:
    r0 = np.random.default_rng(1)
    for v in O.values(): v['bin'] = int(r0.integers(0, 16 if v['kind'] == 'facing' else 8))
def pop(g): return [(k, v['bin']) for k, v in O.items() if v['g'] == g and k in SITES]
res = {'seed': SEED, 'draws': NDRAW, 'synthetic': SYN, 'eps': EPS, 'tests': {}}

# ---------------- T1 wedge tombs vs winter-solstice sunset ----------------
def T1():
    P = pop('wt'); n = len(P); rng = np.random.default_rng(SEED)
    lat = np.array([SITES[k][2] for k, _ in P]); b = np.array([x for _, x in P]); ck = np.array([SITES[k][6] in CK for k, _ in P])
    e = EPS['2200']
    az_flat = np.array([event_az(-e, la, None, False) for la in lat]); tb_flat = np.round(az_flat / 22.5).astype(int) % 16
    az_dsm = np.array([event_az(-e, SITES[k][2], HZ[k], False) for k, _ in P]); tb_dsm = np.round(az_dsm / 22.5).astype(int) % 16
    draws = rng.integers(0, 16, size=(NDRAW, n))
    def stat(bins, tb, m=None): m = np.ones(n, bool) if m is None else m; return (bins[..., m] == tb[m]).mean(axis=-1)
    obs = float(stat(b, tb_flat)); null = stat(draws, tb_flat); p = mc_p(obs, null)
    obs2 = float(stat(b, tb_dsm)); null2 = stat(draws, tb_dsm); p2 = mc_p(obs2, null2)
    m = ~ck; obs3 = float(stat(b, tb_flat, m)); null3 = stat(draws, tb_flat, m); p3 = mc_p(obs3, null3)
    def V(bins):
        a = bins * 22.5 * D; C, S_ = np.cos(a).mean(-1), np.sin(a).mean(-1); Rb = np.hypot(C, S_); th = np.arctan2(S_, C)
        return Rb * np.cos(th - 236 * D), Rb, (th / D) % 360
    v, Rb, th = V(b); vn, _, _ = V(draws)
    return {'name': 'Wedge tombs face the winter-solstice sunset bin', 'n': n, 'n_cork_kerry': int(ck.sum()),
            'target_bin_flat': sorted({int(x) for x in tb_flat}), 'target_bin_dsm': sorted({int(x) for x in tb_dsm}),
            'primary': {'stat': obs, 'null': summ(null), 'p': p, 'direction_ok': obs > float(np.mean(null))},
            'secondary_dsm': {'stat': obs2, 'null': summ(null2), 'p': p2},
            'v_test_236': {'V_mean_resultant_cos': float(v), 'Rbar': float(Rb), 'mean_dir_deg': float(th), 'null': summ(vn), 'p': mc_p(float(v), vn)},
            'robustness': {'what': 'Cork and Kerry excluded', 'n': int(m.sum()), 'stat': obs3, 'null': summ(null3), 'p': p3,
                           'holds': bool(obs3 > np.mean(null3) and p3 < 0.05)},
            'bin_counts': np.bincount(b, minlength=16).tolist()}

# ---------------- T2 passage-tomb declinations ----------------
FEAT = {'ME019-045----': ('Newgrange roof-box window, NMS 2024 / Patrick 1974', -24.85), 'ME015-012004-': ('Cairn T, Prendergast survey', -1.0)}
def T2():
    e = EPS['3200']; tg_sun = [e, 0, -e]; tg_moon = [e + I_MOON, -(e + I_MOON), e - I_MOON, -(e - I_MOON)]
    P = [x for x in pop('pt') if x[0] not in FEAT]; ids = [k for k, _ in P] + list(FEAT); n = len(ids)
    rng = np.random.default_rng(SEED)
    grid = np.arange(0, 360, 0.5)
    dsun = np.zeros((n, 720)); dmoon = np.zeros((n, 720))
    for i, k in enumerate(ids):
        la = SITES[k][2]; h = HZ[k]; dsun[i] = dec(grid, h, la, 'sun'); dmoon[i] = dec(grid, h, la, 'moon')
    obs_sun = np.array([dsun[i, int(b * 45)] for i, (_, b) in enumerate(P)] + [v[1] for v in FEAT.values()])
    obs_moon = np.array([dmoon[i, int(b * 45)] for i, (_, b) in enumerate(P)] + [v[1] for v in FEAT.values()])
    def score(ds, dm, m):
        k = lambda d, t: np.exp(-0.5 * ((d - t) / SIG) ** 2) / (SIG * math.sqrt(2 * math.pi))
        return sum(k(ds[..., m], t).mean(-1) for t in tg_sun) + sum(k(dm[..., m], t).mean(-1) for t in tg_moon)
    nP = len(P); idx = np.empty((NDRAW, n), int)
    idx[:, :nP] = rng.integers(0, 16, size=(NDRAW, nP)) * 45          # quantised compass bins (0.5 deg grid index)
    idx[:, nP:] = rng.integers(0, 720, size=(NDRAW, n - nP))          # surveyed axes: uniform azimuth
    rows = np.arange(n)
    ns, nm = dsun[rows, idx], dmoon[rows, idx]
    allm = np.ones(n, bool)
    brú = np.array([math.hypot((SITES[k][2] - 53.69473) * 111.2, (SITES[k][3] + 6.47554) * 111.2 * math.cos(53.69 * D)) <= 4.0 for k in ids])
    obs = float(score(obs_sun, obs_moon, allm)); null = score(ns, nm, allm); p = mc_p(obs, null)
    m = ~brú; obs3 = float(score(obs_sun, obs_moon, m)); null3 = score(ns, nm, m); p3 = mc_p(obs3, null3)
    near = lambda tg, d: int(sum((np.abs(d - t) <= SIG).sum() for t in tg))
    return {'name': 'Passage tombs at solstice/equinox/standstill declinations', 'n': n, 'n_parsed': nP, 'featured_axes': {k: v for k, v in FEAT.items()}, 'n_bru': int(brú.sum()),
            'targets': {'sun': tg_sun, 'moon': tg_moon},
            'primary': {'stat': obs, 'null': summ(null), 'p': p, 'direction_ok': obs > float(np.mean(null))},
            'descriptive': {'n_within_1.5_of_any_target': near(tg_sun, obs_sun) + near(tg_moon, obs_moon), 'declinations_sun': [round(float(x), 2) for x in obs_sun]},
            'robustness': {'what': 'Brú na Bóinne (within 4 km of Newgrange) excluded', 'n': int(m.sum()), 'stat': obs3, 'null': summ(null3), 'p': p3,
                           'holds': bool(obs3 > np.mean(null3) and p3 < 0.05)}}

# ---------------- horizon peaks ----------------
def peaks(prof):
    """local maxima of a circular 0.5-deg horizon profile with their topographic prominence (deg) -> list of (az, prom)"""
    a = np.asarray(prof, float); n = len(a); s = int(np.argmax(a)); r = np.roll(a, -s); r = np.append(r, r[0]); out = []
    for i in range(1, n):
        if r[i] > r[i - 1] and r[i] >= r[i + 1]:
            j = i - 1; mL = r[i]
            while j >= 0 and r[j] <= r[i]: mL = min(mL, r[j]); j -= 1
            j = i + 1; mR = r[i]
            while j <= n and r[j] <= r[i]: mR = min(mR, r[j]); j += 1
            out.append((((i + s) % n) * 0.5, r[i] - max(mL, mR)))
    out.append((s * 0.5, a.max() - a.min()))
    return out
def bin16(az): return int(np.round(az / 22.5)) % 16

# ---------------- T3 stone rows and the lunar standstills ----------------
def T3():
    e = EPS['2200']; tg = [e + I_MOON, -(e + I_MOON), e - I_MOON, -(e - I_MOON)]
    P = pop('sr'); n = len(P); rng = np.random.default_rng(SEED)
    tab = np.zeros((n, 8), int); maxbins = []
    for i, (k, _) in enumerate(P):
        la, h = SITES[k][2], HZ[k]
        for b in range(8):
            a1, a2 = b * 22.5, b * 22.5 + 180; h1, h2 = float(hor_at(h, a1)), float(hor_at(h, a2))
            a, hh = (a1, h1) if h1 <= h2 else (a2, h2)
            d = float(dec(a, hh, la, 'moon')); tab[i, b] = int(any(abs(d - t) <= SIG for t in tg))
        mb = [bin16(az) % 8 for az, pr in peaks(h) if pr >= 0.1]; maxbins.append(mb if mb else list(range(8)))
    b = np.array([x for _, x in P]); ck = np.array([SITES[k][6] in CK for k, _ in P]); rows = np.arange(n)
    obs_v = tab[rows, b]; obs = int(obs_v.sum())
    d1 = rng.integers(0, 8, size=(NDRAW, n)); null1 = tab[rows, d1].sum(-1)
    d2 = np.stack([rng.choice(mb, size=NDRAW) for mb in maxbins], axis=1); null2 = tab[rows, d2].sum(-1)
    p1, p2 = mc_p(obs, null1), mc_p(obs, null2)
    sub = {}
    for nm, m in (('cork_kerry', ck), ('rest', ~ck)):
        o = int(obs_v[m].sum()); n1 = tab[rows, d1][:, m].sum(-1); n2 = tab[rows, d2][:, m].sum(-1)
        sub[nm] = {'n': int(m.sum()), 'stat': o, 'null1_mean': float(n1.mean()), 'null2_mean': float(n2.mean()), 'effect_vs_null1': float(o - n1.mean()), 'effect_vs_null2': float(o - n2.mean())}
    holds = all(sub[x]['effect_vs_null1'] > 0 and sub[x]['effect_vs_null2'] > 0 for x in sub)
    return {'name': 'Stone rows and the lunar standstills (Ruggles replication)', 'n': n, 'targets': tg,
            'primary': {'stat': obs, 'null_random': summ(null1), 'p_random': p1, 'null_peaks': summ(null2), 'p_peaks': p2, 'p': max(p1, p2),
                        'direction_ok': bool(obs > null1.mean() and obs > null2.mean())},
            'robustness': {'what': 'Cork/Kerry and the rest analysed separately; excess must be positive in both, against both nulls', 'subsets': sub, 'holds': bool(holds)}}

# ---------------- T5 axes aimed at horizon peaks ----------------
def T5():
    P = pop('sp') + pop('sr'); n = len(P); rng = np.random.default_rng(SEED); out = {}
    b = np.array([x for _, x in P]); rows = np.arange(n); d = rng.integers(0, 8, size=(NDRAW, n))
    for thr in (0.5, 0.3, 1.0):
        tab = np.zeros((n, 8), bool)
        for i, (k, _) in enumerate(P):
            pb = {bin16(az) for az, pr in peaks(HZ[k]) if pr >= thr}
            for x in range(8): tab[i, x] = x in pb or (x + 8) in pb
        obs = float(tab[rows, b].mean()); null = tab[rows, d].mean(-1)
        out[thr] = {'stat': obs, 'null': summ(null), 'p': mc_p(obs, null), 'direction_ok': obs > float(null.mean())}
    rob = all(out[t]['direction_ok'] and out[t]['p'] < 0.05 for t in (0.3, 1.0))
    return {'name': 'Stone pairs and rows aimed at horizon peaks', 'n': n, 'n_pairs': len(pop('sp')), 'n_rows': len(pop('sr')),
            'primary': dict(out[0.5]), 'robustness': {'what': 'prominence thresholds 0.3 and 1.0 deg', 'thr_0.3': out[0.3], 'thr_1.0': out[1.0], 'holds': bool(rob)}}

# ---------------- T4 passage-tomb intervisibility ----------------
sys.path.insert(0, 'scripts')
def T4():
    import horizon_all as H
    R, K, EYE = 6371000.0, 0.13, 1.6; SKIP = 100.0; RANGE = 10000.0; BANDS = [(0, 1000), (1000, 3000), (3000, 10000)]
    ids = [k for k, s in SITES.items() if s[1] == 'pt']; n = len(ids)
    lat = np.array([SITES[k][2] for k in ids]); lon = np.array([SITES[k][3] for k in ids])
    def xy(la, lo): return (lo + 8) * 111320 * math.cos(53.5 * D), la * 110574
    def slope(la, lo):
        dy = 110574 / 3600; dx = 111320 * np.cos(la * D) / 2400
        zx = (H.elev(la, lo + 1 / 2400) - H.elev(la, lo - 1 / 2400)) / (2 * dx); zy = (H.elev(la + 1 / 3600, lo) - H.elev(la - 1 / 3600, lo)) / (2 * dy)
        return np.degrees(np.arctan(np.hypot(zx, zy)))
    def vis(la, lo):
        x, y = xy(la, lo); dd = np.hypot(x[:, None] - x[None], y[:, None] - y[None]); I, J = np.where(np.triu(dd <= RANGE, 1))
        if len(I) == 0: vis.bands = [(0, 0)] * len(BANDS); return np.zeros(len(la), bool), np.zeros(len(la), bool), 0, 0
        g = H.elev(la, lo).astype(float); ok = np.ones(len(I), bool)
        for c0 in range(0, len(I), 400):
            ii, jj = I[c0:c0 + 400], J[c0:c0 + 400]; Dm = dd[ii, jj]
            t = np.arange(SKIP, RANGE, 30.0)[None] ; frac = t / np.maximum(Dm[:, None], 1)
            valid = (t < Dm[:, None] - SKIP)
            la_s = la[ii, None] + (la[jj] - la[ii])[:, None] * frac; lo_s = lo[ii, None] + (lo[jj] - lo[ii])[:, None] * frac
            z = H.elev(np.where(valid, la_s, la[ii, None]), np.where(valid, lo_s, lo[ii, None])).astype(float)
            line = (g[ii] + EYE)[:, None] + ((g[jj] + EYE) - (g[ii] + EYE))[:, None] * frac
            bulge = t * (Dm[:, None] - t) / (2 * R / (1 - K))
            ok[c0:c0 + 400] = ~np.any(valid & (z + bulge >= line), axis=1)
        V = np.zeros((len(la), len(la)), bool); V[I[ok], J[ok]] = True; V = V | V.T
        anyv = V.any(1); higher = np.array([np.any(V[i] & (g > g[i])) for i in range(len(la))])
        bands = [(int(((dd[I, J] > lo_) & (dd[I, J] <= hi_)).sum()), int((ok & (dd[I, J] > lo_) & (dd[I, J] <= hi_)).sum())) for lo_, hi_ in BANDS]
        vis.bands = bands
        return anyv, higher, int(ok.sum()), len(I)
    a, hgh, nv, npairs = vis(lat, lon); real_bands = vis.bands
    obs = float(a.mean()); obs_h = float(hgh[a].mean()) if a.any() else 0.0
    # cemeteries: single-linkage at 2 km
    x, y = xy(lat, lon); dd = np.hypot(x[:, None] - x[None], y[:, None] - y[None]); lab = -np.ones(n, int); c = 0
    for i in range(n):
        if lab[i] >= 0: continue
        st = [i]; lab[i] = c
        while st:
            j = st.pop()
            for k in np.where((dd[j] <= 2000) & (lab < 0))[0]: lab[k] = c; st.append(k)
        c += 1
    rng = np.random.default_rng(SEED); e0 = H.elev(lat, lon).astype(float); s0 = slope(lat, lon); pools = []
    for i in range(n):
        m = lab == lab[i]; cla, clo = lat[m].mean(), lon[m].mean()
        r = 20000 * np.sqrt(rng.random(6000)); th = rng.random(6000) * 2 * math.pi
        pla = cla + r * np.cos(th) / 110574; plo = clo + r * np.sin(th) / (111320 * math.cos(cla * D))
        pe = H.elev(pla, plo).astype(float); ps = slope(pla, plo); land = pe > 0
        tol_e, tol_s = max(15, 0.15 * e0[i]), 2.0
        for _ in range(6):
            sel = np.where(land & (np.abs(pe - e0[i]) <= tol_e) & (np.abs(ps - s0[i]) <= tol_s))[0]
            if len(sel) >= 20: break
            tol_e *= 2; tol_s *= 2
        pools.append((pla[sel], plo[sel]))
    nulls, nulls_h, prs, nb = [], [], [], np.zeros((len(BANDS), 2))
    for dr in range(NDRAW_T4):
        ch = [rng.integers(0, len(p[0])) for p in pools]
        la_r = np.array([p[0][j] for p, j in zip(pools, ch)]); lo_r = np.array([p[1][j] for p, j in zip(pools, ch)])
        a_r, h_r, nv_r, np_r = vis(la_r, lo_r); nulls.append(a_r.mean()); nulls_h.append(h_r[a_r].mean() if a_r.any() else 0); prs.append(nv_r / max(np_r, 1)); nb += np.array(vis.bands)
    nulls, nulls_h, prs = map(np.array, (nulls, nulls_h, prs))
    return {'name': 'Passage-tomb intervisibility', 'n': n, 'n_cemeteries': int(c), 'pairs_within_10km': npairs, 'pairs_intervisible': nv,
            'primary': {'stat': obs, 'null': summ(nulls), 'p': mc_p(obs, nulls), 'direction_ok': obs > float(nulls.mean())},
            'secondary_higher': {'stat': obs_h, 'null': summ(nulls_h), 'p': mc_p(obs_h, nulls_h)},
            'descriptive_pair_rate': {'stat': nv / max(npairs, 1), 'null': summ(prs), 'p': mc_p(nv / max(npairs, 1), prs),
                                      'note': 'share of tomb pairs within 10 km that are intervisible; removes the clustering effect'},
            'post_hoc_distance_bands': {'note': 'POST HOC, descriptive: added after the T4 primary was seen in the pipeline check. Intervisible share of pairs by separation, real vs pooled null pairs.',
                                        'bands_km': [[a_ / 1000, b_ / 1000] for a_, b_ in BANDS], 'real': [[n_, v_, v_ / max(n_, 1)] for n_, v_ in real_bands],
                                        'null': [[float(n_), float(v_), float(v_ / max(n_, 1))] for n_, v_ in nb]},
            'robustness': {'what': 'none named (Prendergast 2016: 52 of 132 tombs directed at other tombs, 49 of them higher, is a published comparison, not scored)', 'holds': True}}

if __name__ == '__main__':
    for t, f in (('T1', T1), ('T2', T2), ('T3', T3), ('T5', T5), ('T4', T4)):
        res['tests'][t] = f(); pr = res['tests'][t]['primary']; print(t, 'n', res['tests'][t]['n'], 'stat', pr['stat'], 'p', pr['p'], flush=True)
    H_ = holm({t: res['tests'][t]['primary']['p'] for t in res['tests']})
    for t, v in res['tests'].items():
        v['p_holm'] = H_[t]; v['supported'] = bool(H_[t] < 0.05 and v['primary']['direction_ok'] and v['robustness']['holds'])
        print(t, 'holm', round(H_[t], 4), 'SUPPORTED' if v['supported'] else 'not supported')
    res['code_commit'] = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    out = 'data/tests/synthetic_results.json' if SYN else 'data/tests/results_v1.json'
    json.dump(res, open(out, 'w'), indent=1, default=float)
    if not SYN: json.dump(res, open('site/data/tests_v1.json', 'w'), separators=(',', ':'), default=float)
