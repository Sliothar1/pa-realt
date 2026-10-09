"""Build site/results.html (static) from data/tests/results_v1.json + data/tests/posthoc_t2.json."""
import json, math, html
R = json.load(open('data/tests/results_v1.json')); T = R['tests']; PH = json.load(open('data/tests/posthoc_t2.json'))
CODE, RES = 'c244e8f', 'ab7fb46'; GH = 'https://github.com/Sliothar1/pa-realt'
def p(x): return '&lt; 0.0001' if x < 1e-4 + 1e-9 else ('%.4f' % x if x < 0.01 else '%.3f' % x)
def pc(x): return '%.1f%%' % (100 * x)
PTS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
def rose(counts, target):
    cx = cy = 110; mx = max(counts) or 1; out = [f'<svg viewBox="0 0 220 220" class="rose" role="img" aria-label="Wedge-tomb facing directions, 16 compass bins">']
    for r in (30, 60, 90): out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" class="rg"/>')
    for i, c in enumerate(counts):
        a0, a1 = math.radians(i * 22.5 - 11.25 - 90), math.radians(i * 22.5 + 11.25 - 90); r = 90 * math.sqrt(c / mx)
        if c: out.append(f'<path d="M{cx},{cy} L{cx + r * math.cos(a0):.1f},{cy + r * math.sin(a0):.1f} A{r:.1f},{r:.1f} 0 0 1 {cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f} Z" class="{"rt" if i == target else "rb"}"/>')
        if i % 2 == 0:
            a = math.radians(i * 22.5 - 90); out.append(f'<text x="{cx + 102 * math.cos(a):.1f}" y="{cy + 102 * math.sin(a) + 4:.1f}" text-anchor="middle">{PTS[i]}</text>')
    out.append('</svg>'); return ''.join(out)
def strip(decs, tg):
    W, X = 640, lambda d: 20 + (d + 40) / 80 * 600
    o = [f'<svg viewBox="0 0 {W} 90" class="strip" role="img" aria-label="Passage-tomb declinations against the targets">']
    for t in tg: o.append(f'<rect x="{X(t - 1.5):.1f}" y="10" width="{X(t + 1.5) - X(t - 1.5):.1f}" height="50" class="tw"/><line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="8" y2="62" class="tl"/>')
    for d in decs: o.append(f'<line x1="{X(d):.1f}" x2="{X(d):.1f}" y1="22" y2="48" class="dl"/>')
    for d in range(-40, 41, 10): o.append(f'<text x="{X(d):.1f}" y="80" text-anchor="middle">{d:+d}°</text>')
    o.append('</svg>'); return ''.join(o)
t1, t2, t3, t4, t5 = (T[k] for k in ('T1', 'T2', 'T3', 'T4', 'T5'))
rows = [
 ('T1', 'Wedge tombs face the midwinter-sunset bin', t1['n'], f"{pc(t1['primary']['stat'])} in the SW bin", f"{pc(t1['primary']['null']['mean'])} ({pc(t1['primary']['null']['q025'])}–{pc(t1['primary']['null']['q975'])})", t1['primary']['p'], t1, 'Cork + Kerry excluded'),
 ('T2', 'Passage tombs at solar/lunar declinations', t2['n'], f"score {t2['primary']['stat']:.3f}", f"{t2['primary']['null']['mean']:.3f} ({t2['primary']['null']['q025']:.3f}–{t2['primary']['null']['q975']:.3f})", t2['primary']['p'], t2, 'Brú na Bóinne excluded'),
 ('T3', 'Stone rows at lunar standstills', t3['n'], f"{t3['primary']['stat']} rows", f"{t3['primary']['null_random']['mean']:.1f} random · {t3['primary']['null_peaks']['mean']:.1f} hill targets", t3['primary']['p'], t3, 'Cork/Kerry vs rest'),
 ('T4', 'Passage-tomb intervisibility', t4['n'], f"{pc(t4['primary']['stat'])} see another tomb", f"{pc(t4['primary']['null']['mean'])} ({pc(t4['primary']['null']['q025'])}–{pc(t4['primary']['null']['q975'])})", t4['primary']['p'], t4, 'none named'),
 ('T5', 'Pair/row axes at horizon peaks', t5['n'], f"{pc(t5['primary']['stat'])} hit a peak", f"{pc(t5['primary']['null']['mean'])} ({pc(t5['primary']['null']['q025'])}–{pc(t5['primary']['null']['q975'])})", t5['primary']['p'], t5, 'thresholds 0.3°, 1.0°'),
]
tab = ''.join(f'<tr class="{"yes" if t["supported"] else "no"}"><td><a href="#{k}">{k}</a></td><td>{nm}</td><td>{n}</td><td>{obs}</td><td>{null}</td><td>{p(pp)}</td><td>{p(t["p_holm"])}</td><td>{rb}: {"holds" if t["robustness"]["holds"] else "fails"}</td><td><b>{"Supported" if t["supported"] else "Not supported"}</b></td></tr>' for k, nm, n, obs, null, pp, t, rb in rows)
bands = t4['post_hoc_distance_bands']
bt = ''.join(f'<tr><td>{a:g}–{b:g} km</td><td>{r[1]} / {r[0]} ({pc(r[2])})</td><td>{pc(nl[2])}</td></tr>' for (a, b), r, nl in zip(bands['bands_km'], bands['real'], bands['null']))
page = f'''<!doctype html>
<html lang="en" data-theme="night"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Test results · Torthaí · PA Réalt · Garry Lohan</title>
<meta name="description" content="PA Réalt pre-registered archaeoastronomy tests T1–T5 on Irish monuments: what was tested, the numbers, and what they do and do not show.">
<meta name="theme-color" content="#1a080c"><link rel="icon" href="assets/icon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="pages.css">
<script>(function(){{try{{var t=localStorage.getItem('pa-realt-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}}})();</script>
</head><body class="subpage">
<header class="minihead"><div class="wrap"><a class="brandlink" href="./"><img src="assets/icon.svg" alt="" width="28" height="28"><span class="brand">PA Réalt</span></a><a class="toplink" href="./#tests">← Back to the map</a></div></header>
<main class="wrap page">
<p class="eyebrow"><i lang="ga">Torthaí na dtástálacha</i> · Pre-registered test results</p>
<h1>Five tests, scored once</h1>
<p class="lead">Each test was written down with its data, comparison (null) model and pass rule <b>before</b> scoring (<a href="{GH}/blob/main/prereg/tests_v1.json">prereg/tests_v1.json</a>). The code that reads compass directions from the monument records, and the scoring code, were frozen and published first (commit <a href="{GH}/commit/{CODE}"><code>{CODE}</code></a>, with an <a href="{GH}/blob/main/prereg/addendum_v1.md">addendum</a> fixing the details). Everything was then run once on 9 Oct 2026 (results commit <a href="{GH}/commit/{RES}"><code>{RES}</code></a>). Every result is shown here, including the nulls. Log: <a href="{GH}/blob/main/TEST_LOG.md">TEST_LOG.md</a>.</p>
<div class="verdicts"><span class="vchip yes">T1 supported</span><span class="vchip yes">T2 supported</span><span class="vchip no">T3 null</span><span class="vchip yes">T4 supported, with a caveat</span><span class="vchip no">T5 null</span></div>
<div class="credits-wrap"><table class="credits rtab"><thead><tr><th>Test</th><th>Question</th><th>n</th><th>Observed</th><th>Chance (mean, 95% range)</th><th>p</th><th>Holm p</th><th>Robustness</th><th>Verdict</th></tr></thead><tbody>{tab}</tbody></table></div>
<p class="note">p = one-sided Monte Carlo p value (10,000 random draws; T4: 1,000). The smallest possible values are 1/10,001 and 1/1,001. Holm p is adjusted for running five tests. “Supported” requires Holm p &lt; 0.05, an effect in the stated direction, and passing the named robustness check.</p>

<section id="T1" class="rsec"><h2><span class="ga" lang="ga">Tuamaí dingeacha</span>T1 · Wedge tombs and the setting Sun: <em class="yes">supported</em></h2>
<div class="rgrid"><div>{rose(t1['bin_counts'], 10)}<p class="note center">Facing directions of the {t1['n']} wedge tombs (area ∝ count). The SW bin (gold) holds the midwinter sunset at every site.</p></div><div>
<p><b>{t1['bin_counts'][10]} of {t1['n']}</b> wedge tombs ({pc(t1['primary']['stat'])}) face the south-west bin that holds the winter-solstice sunset. Random directions would put about {t1['primary']['null']['mean'] * t1['n']:.0f} there ({pc(t1['primary']['null']['mean'])}). p {p(t1['primary']['p']).replace('&lt;', '&lt;')}, Holm p = {p(t1['p_holm'])}. The real horizon gives the same bin. The mean direction is <b>{t1['v_test_236']['mean_dir_deg']:.0f}°</b> (WSW), with strong concentration (R̄ = {t1['v_test_236']['Rbar']:.2f}). With Cork and Kerry left out (n = {t1['robustness']['n']}), it is still {pc(t1['robustness']['stat'])} (p {p(t1['robustness']['p'])}).</p>
<p><b>What it shows:</b> wedge tombs that say which way they face overwhelmingly face SW to W, as the NMS scope note says (“invariably … westerly”). <b>What it does not show:</b> that the builders aimed at the midwinter sunset. A SW–W preference is also consistent with the afternoon or setting Sun in general, with slope, or with prevailing weather. Only 51 of the 309 records with a compass phrase say “faces”, “opens to” or “entrance at”, so this sample may not represent all wedge tombs.</p></div></div></section>

<section id="T2" class="rsec"><h2><span class="ga" lang="ga">Tuamaí pasáiste</span>T2 · Passage tombs at solstice, equinox and standstill declinations: <em class="yes">supported</em></h2>
{strip(t2['descriptive']['declinations_sun'], t2['targets']['sun'] + t2['targets']['moon'])}
<p class="note center">Each tick is one tomb’s declination through its own real horizon. The gold bands are the 7 targets ±1.5°: solstices, equinox, and the Moon’s major and minor standstills.</p>
<p><b>{t2['descriptive']['n_within_1.5_of_any_target']} of {t2['n']}</b> tombs fall within 1.5° of a target. The summed density score is {t2['primary']['stat']:.3f}, against {t2['primary']['null']['mean']:.3f} for random directions (95% range up to {t2['primary']['null']['q975']:.3f}). p = {p(t2['primary']['p'])}, Holm p = {p(t2['p_holm'])}. With Brú na Bóinne left out (n = {t2['robustness']['n']}): p = {p(t2['robustness']['p'])}. Two checks added <i>after</i> scoring point the same way: without the two surveyed axes, p = {PH['without_featured_axes']['p']:.3f}; keeping only one tomb per 2 km cluster (n = {PH['one_per_2km_cluster']['n']}), p = {PH['one_per_2km_cluster']['p']:.3f}.</p>
<p><b>Read this with care.</b> The national survey of passage tombs (NMS 2024, Prendergast: 136 surveyed tombs) found <b>no</b> overall clustering (global p = 0.896). Our sample is smaller (36), comes from compass phrases in text (each ±11°), and covers the tombs whose descriptions happen to say which way they open. The larger, measured survey should carry more weight. Our result is a reason to look again, not a reversal.</p></section>

<section id="T3" class="rsec"><h2><span class="ga" lang="ga">Sraitheanna gallán</span>T3 · Stone rows and the lunar standstills: <em class="no">not supported (a null result)</em></h2>
<p><b>{t3['primary']['stat']} of {t3['n']}</b> stone rows point (at their lower-horizon end) within 1.5° of a major or minor standstill declination. Random directions give {t3['primary']['null_random']['mean']:.1f} on average (p = {p(t3['primary']['p_random'])}), and directions aimed at horizon peaks give {t3['primary']['null_peaks']['mean']:.1f} (p = {p(t3['primary']['p_peaks'])}). There is no excess. Cork/Kerry is slightly above chance (+{t3['robustness']['subsets']['cork_kerry']['effect_vs_null1']:.2f}) and the rest is below (−{abs(t3['robustness']['subsets']['rest']['effect_vs_null1']):.2f}).</p>
<p><b>What it means:</b> on SMR compass data, this does not replicate Ruggles’s lunar preference for the Cork–Kerry rows. Compass phrases are much coarser than his theodolite surveys, so a weak real pattern could be hidden. This is a null result, not proof of absence.</p></section>

<section id="T4" class="rsec"><h2><span class="ga" lang="ga">Infheictheacht</span>T4 · Passage-tomb intervisibility: <em class="yes">supported, with a caveat</em></h2>
<p><b>{pc(t4['primary']['stat'])}</b> of the {t4['n']} passage tombs can see at least one other passage tomb within 10 km over the real terrain, against {pc(t4['primary']['null']['mean'])} for random points on similar ground near each cemetery. p = {p(t4['primary']['p'])} (the floor for 1,000 draws), Holm p = {p(t4['p_holm'])}. Of the tombs that see another, {pc(t4['secondary_higher']['stat'])} see a <b>higher</b> one (chance: {pc(t4['secondary_higher']['null']['mean'])}). For comparison, Prendergast (2016) found 52 of 132 tombs directed at other tombs, 49 of them higher.</p>
<div class="credits-wrap"><table class="credits"><thead><tr><th>Pair separation</th><th>Real pairs intervisible</th><th>Random pairs</th></tr></thead><tbody>{bt}</tbody></table></div>
<p><b>The caveat, stated before scoring:</b> passage tombs come in tight cemeteries, and the random points do not keep that clustering, so part of the gap is just that real tombs have more near neighbours. The distance table (added after the T4 result had been seen, so it is descriptive only) shows that even at 3–10 km, real pairs see each other far more often than random pairs (62% against 6%). Tombs sit on summits and ridges, and that siting makes them visible. <b>Disclosure:</b> T4 does not use compass data, and its headline number was seen during a code check before the freeze. The code was not changed afterwards.</p></section>

<section id="T5" class="rsec"><h2><span class="ga" lang="ga">Beanna na spéire</span>T5 · Stone pairs and rows aimed at horizon peaks: <em class="no">not supported (a null result)</em></h2>
<p><b>{pc(t5['primary']['stat'])}</b> of {t5['n']} axes ({t5['n_pairs']} pairs, {t5['n_rows']} rows) have a horizon peak of at least 0.5° prominence in one of their two bearing bins. Random directions on the same horizons give {pc(t5['primary']['null']['mean'])}, so p = {p(t5['primary']['p'])}. At 0.3° the figures are {pc(t5['robustness']['thr_0.3']['stat'])} against {pc(t5['robustness']['thr_0.3']['null']['mean'])} (p = {p(t5['robustness']['thr_0.3']['p'])}), and at 1.0° {pc(t5['robustness']['thr_1.0']['stat'])} against {pc(t5['robustness']['thr_1.0']['null']['mean'])} (p = {p(t5['robustness']['thr_1.0']['p'])}). No evidence that the axes target hills.</p></section>

<section class="rsec"><h2><span class="ga" lang="ga">Teorainneacha</span>Limits</h2><ul>
<li>Directions are 16-point compass phrases from SMR descriptions (±11.25°), not surveys. The parser reads only explicit phrases, and its output is published (<a href="{GH}/blob/main/data/tests/orientations.json">orientations.json</a>).</li>
<li>Horizons come from the Copernicus GLO-30 <i>surface</i> model, which includes modern trees and buildings. The validation gate at Newgrange: 0.833° against Patrick’s 0.850°.</li>
<li>Monuments in the same cemetery are not independent. The post hoc one-per-cluster check for T2 is reported above.</li>
<li>A supported test means the pattern is unlikely to be chance under that null model. It does not prove what the builders intended.</li></ul>
<p class="note">Data: NMS Sites and Monuments Record (CC BY 4.0), NI SMR (OGL v3), Copernicus GLO-30 DEM (© DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA). Code: <a href="{GH}/tree/main/scripts">scripts/</a>.</p></section>
</main>
<nav class="pa-family" aria-label="The PA family of sites"><a href="https://sliothar1.github.io/PA-Marine-Demo/">PA Marine</a><a href="./" aria-current="page">PA Réalt</a><a href="family.html" class="pa-hub">All PA sites →</a></nav>
<p class="pa-credit">Designed and built by Garry Lohan · <a href="https://scholar.google.com/citations?user=9aBECzQAAAAJ&amp;hl=en" target="_blank" rel="noopener">Google Scholar</a> · <a href="https://www.linkedin.com/in/garry-lohan-14923814" target="_blank" rel="noopener">LinkedIn</a></p>
</body></html>'''
open('site/results.html', 'w', encoding='utf-8').write(page); print('ok', len(page))
