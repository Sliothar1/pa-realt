# Addendum to prereg/tests_v1.json: implementation choices fixed before scoring

Written 2026-10-09 (Europe/Dublin), committed together with the frozen parser (`scripts/orient_parse.py`) and the scorer (`scripts/run_tests.py`), **before** any orientation-based test (T1, T2, T3, T5) was scored. `tests_v1.json` left several details open. These are the choices, made without looking at any parsed direction.

## What was looked at before this commit
- Parser development used WEB_NOTES sentences with every compass token **masked** (`<C>`), so the extraction rules could be checked without seeing directions. Only per-class counts of parsed records were printed: wedge 51, passage 35, stone row 119, standing-stone pair 126.
- The scorer was run in `--synthetic` mode, where every parsed bearing is replaced by a random one. That checks the code, not the hypotheses.
- **Disclosure.** T4 (intervisibility) does not use parsed directions, so the synthetic run scored it on the **real** tomb locations. Its primary result was therefore seen before this commit. The T4 code was not changed after that, except to add a **post hoc, descriptive** table of intervisibility by pair separation (labelled as post hoc in the output). It is not part of any verdict.

## Shared
- Horizons: `scripts/horizon_all.py` runs the `scripts/horizon.py` method on every mapped monument (0.5° azimuth, 400 m to 60 km in 30 m steps, k = 0.13, eye 1.6 m, nearest neighbour). Validation gate: Newgrange at az 135° gives 0.833° against Patrick's 0.850°, a difference of 0.017°, so it passes.
- Declination: apparent horizon altitude h minus Bennett refraction, plus 0.95° cos h lunar parallax for Moon targets. Obliquity (Laskar 1986): 3200 BC = 24.0385°, 2200 BC = 23.9445°. 3200 BC is astronomical year −3199.
- Monte Carlo p = (1 + #null ≥ observed) / (N + 1). Each test uses its own generator, seeded 20261009. N = 10,000 (T4: 1,000).
- Quantisation: a 16-point bin centre is k × 22.5°. A null draw is a uniform random bin, which is the same as a quantised uniform azimuth.
- "Robustness holds" means that, in the named subset, the effect is in the pre-stated direction and its own Monte Carlo p < 0.05 (unadjusted). T3 uses the sign rule given in the prereg.
- Holm–Bonferroni over the five primary p values. T3's primary p is the larger of its two null p values, because the prereg requires an excess over both.

## T1
- Target bin: the 16-point bin containing the winter-solstice sunset azimuth (Sun's centre, 2200 BC). Primary uses a flat horizon (apparent altitude 0°). Secondary uses the DSM horizon.
- V-test against 236°: V = R̄·cos(θ̄ − 236°) on bin centres, with a Monte Carlo p from the same quantised null. Reported as secondary.
- Robustness: COUNTY CORK and KERRY excluded.

## T2
- Population: passage tombs with a parsed **facing** phrase ("opens to", "faces", "entrance at"). Bare axes are ambiguous and are not used.
- Surveyed featured axes, used only where a published declination exists: Newgrange δ = −24.85° (the middle of the NMS 2024 light window, −23.8° to −25.9°) and Cairn T δ = −1.0° (Prendergast). These replace any parsed entry for the same monument. In the null they get a uniform (unquantised) random azimuth through their own DSM horizon.
- Score: the sum, over the 7 targets, of the Gaussian KDE (σ 1.5°) of the declinations at that target. Solar targets use solar declinations and lunar targets use lunar ones (with parallax).
- Robustness: monuments within 4 km of Newgrange excluded (Brú na Bóinne).

## T3
- Axis bins 0–7. Of the two ends, the one with the lower DSM horizon is the target end. Statistic: the number of rows whose target-end lunar declination is within 1.5° of ±(ε+i) or ±(ε−i).
- Null 1: a uniform random axis bin. Null 2 (hill targets): a random local maximum of that site's horizon (prominence ≥ 0.1°), quantised to its 16-point bin, with the same lower-end rule. A site with no maximum falls back to uniform.
- Robustness: the excess (observed minus null mean) must be positive against both nulls, in both Cork+Kerry and the rest.

## T4
- Population: all mapped passage tombs (Republic + NI), n = 216.
- Line of sight: DSM ground + 1.6 m at both tombs. 30 m samples, ignoring the first and last 100 m (mound and site clutter). Curvature uses k = 0.13. Range 10 km.
- Cemeteries: single-linkage clusters at 2 km. Null: for each real tomb, a random land cell within 20 km of its cemetery's centroid, with elevation within ±max(15 m, 15%) and slope within ±2° of the tomb's. Tolerance doubles, up to 6 times, until at least 20 candidates exist.
- Primary: the fraction of tombs with at least one intervisible tomb within 10 km. Secondary: among those, the fraction where one of the visible tombs stands higher.
- Known weakness, stated before the T4 result was seen: this null does not keep the tight within-cemetery clustering, so an excess can come from clustering alone. A descriptive pair-level rate is reported alongside.

## T5
- Prominence: 1-D topographic prominence on the circular 0.5° profile. A peak counts in the 16-point bin containing its azimuth. An axis scores if either end's bin contains a peak at or above the threshold.
- Robustness: thresholds of 0.3° and 1.0°, both of which must hold.
