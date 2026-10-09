# PA Réalt · Stone and Sky: research notes

*Garry Lohan, ATU Galway. First pass written 9 October 2026 (Europe/Dublin).*

This file collects what is published about astronomical alignments at Irish Neolithic and Bronze Age monuments, which open data can test those claims, and a set of **pre-registered tests** in the PA Marine style. No test has been scored yet; the protocol is frozen in [`prereg/tests_v1.json`](prereg/tests_v1.json).

---

## 1. Sites and claims

Verdict key, as used on the site: **strong** (measured and repeatable), **observed** (the light effect is real; intent unproven), **debated**, **proposed** (claim only), **not supported** (tested and failed).

| Site (SMR) | Claim | Evidence | Verdict |
|---|---|---|---|
| **Newgrange**, Brú na Bóinne (ME019-045----) | The roof-box admits the winter-solstice sunrise down the passage to the chamber | NMS 2024 measured 53 sun positions in the chamber, 12 Dec 2020 to 8 Jan 2021: light enters ~18–20 days either side of the solstice, for under 20 min each morning. Patrick (1974) measured the horizon at +0°51′. Ray (1989): the effect was very probably designed; obliquity c. 24.1° then. O'Kelly first saw it on 21 Dec 1967 ([NMS 2024](https://www.worldheritageireland.ie/publication/winter-solstice-phenomenon-at-newgrange-research-report-2024/); [Patrick 1974](https://doi.org/10.1038/249517a0); [Ray 1989](https://doi.org/10.1038/337343a0)) | strong |
| **Knowth** 1 (ME019-030001-) | The two passages face the equinox sunrise and sunset (Brennan 1983) | Prendergast & Ray (2015) surveyed both passages: the western passage is lit ~17 days after the autumn equinox, its inner part points 8° north of equinox sunset, and the eastern passage is ~6 days off ([ARROW](https://arrow.tudublin.ie/cgi/viewcontent.cgi?article=1002&context=arastbk)) | not supported (as an equinox design) |
| **Dowth** (ME020-017----) | The southern chamber catches the low winter sunset | Moroney (1999) photographed sunlight entering from October to February ([knowth.com](https://www.knowth.com/dowth-sunsets.htm)) | observed |
| **Loughcrew Cairn T** (ME015-012004-) | The equinox sunrise lights the backstone | The spectacle is real and attracts crowds. Prendergast gives a passage declination c. −1°, but the roof and entrance were altered by OPW restoration ([Prendergast 2011](https://arrow.tudublin.ie/cgi/viewcontent.cgi?article=1002&context=dsisbk); [Cochrane](https://knowth.com/loughcrew-cochrane4.htm)) | debated |
| **Carrowmore 51**, Listoghil (SL014-209) | Sunrise near Samhain and Imbolc, framed by the hills | Meehan (2012) observed sunrise ~31 Oct and 10 Feb ([Internet Archaeology 32](https://intarch.ac.uk/journal/issue32/3/3.html)) | proposed |
| **Carrowkeel Cairn G** (SL040-089----) | The summer-solstice sunset (and the Moon) shine through the roof-box | Observed and photographed by Martin Byrne ([carrowkeel.com](http://www.carrowkeel.com/sites/carrowkeel/cairng2.html); [BBC 1999](http://newsimg.bbc.co.uk/1/hi/sci/tech/313720.stm)) | observed |
| **Drombeg** (CO143-051002-) | The axis faces the winter-solstice sunset | Fahy (1959) saw the sunset slightly south of the axis. Ruggles (1994) found no solar pattern across 31 axial-stone circles, so Drombeg is possibly chance ([Fahy 1959](https://corkhist.ie/wp-content/uploads/jfiles/1959/b1959-001.pdf); [Ruggles 1994](https://web.cliveruggles.com/images/cliveruggles.com/documents/seac94-irish-ascs.pdf)) | debated |
| **Beltany**, Tops (DG070-026001-) | Bealtaine sunrise over Tullyrap, with a decorated stone | Photographed by Ken Williams ([2012](https://blog.shadowsandstone.com/2012/05/01/bealtaine-at-beltany-stone-circle-co-donegal/)); no statistical study | proposed |

**Across groups:**
- **National passage-tomb survey.** Prendergast (NMS 2024): of ~220 passage tombs, 136 can be measured. 23 are aligned on some solar/lunar target, but only 4 face the winter-solstice sunrise; the Silva test gives global **p = 0.896** (no clustering). Prendergast (2016, [J. Phys. Conf. Ser. 685](https://iopscience.iop.org/article/10.1088/1742-6596/685/1/012004)) finds a stronger pattern in *siting*: 52 of 132 tombs point at other tombs, 49 of them at higher ones.
- **Cork–Kerry stone rows.** Ruggles (1994, 1996) found a significant preference for the southern major and minor lunar standstills, often tied to prominent hills.
- **Axial-stone circles.** Ruggles (1994): 31 sites, with no clustering on solstices or equinoxes; there is only a weak peak near −29° (6 of 31).

**People.**
- **Clive Ruggles** (Leicester): statistically careful, and sceptical of single-site claims.
- **Frank Prendergast** (TU Dublin): has done the national surveys.
- **Tom Ray** (DIAS): showed Newgrange was designed.
- **Ken Williams** (Shadows and Stone): photographic documentation, and co-author of *Facing the Sun* (Archaeology Ireland 2017).
- **Martin Brennan**: *The Stars and the Stones* (1983) proposed many solar, lunar and art-as-calendar alignments in the Boyne and Loughcrew. They were influential and widely popular, but most have not survived survey; Knowth is the clearest example.

**Controversies.**
- **Newgrange reconstruction.** O'Kelly's quartz façade and parts of the roof-box were rebuilt, so the question is how much of today's effect is original. Ray (1989) and NMS 2024 argue the roof-box geometry is original. Heggie was sceptical in general.
- **Loughcrew Cairn T.** Restoration may have changed the light.
- **Carrowmore.** The early dates are disputed.
- **The "triple spiral."** The famous Newgrange stone C10 has three spirals but is not one continuous "triple spiral" (NMS 2024). Our motifs are original line art inspired by the style, not copies.
- **Selection effects.** Famous single sites are chosen *because* light enters them. Only group tests with a null model can address intent, which is what §6 is for.

## 2. Open data and licences

| Dataset | What we use | Licence / terms |
|---|---|---|
| NMS **Sites and Monuments Record** (SMR) open data, `SMROpenData_20251201.csv` ([data.gov.ie](https://data.gov.ie/dataset/national-monuments-service-archaeological-survey-of-ireland)) | 151,308 records, 470 classes; ITM (EPSG:2157) and WGS84 coordinates, townland, county, description. Each record links to the Historic Environment Viewer (HEV) | **CC BY 4.0**; attribute the National Monuments Service. Republic of Ireland only |
| **Northern Ireland SMR**, DfC Historic Environment Division, `nismr_10092026.geojson` ([data.gov.uk](https://www.data.gov.uk/dataset/46240fa5-db15-469e-b1c8-0460504b951c/northern-ireland-sites-and-monuments-record)) | 18,509 records, Irish Grid (EPSG:29902). We use 869 located records whose type maps exactly to one of our classes | **UK Open Government Licence v3.0** |
| **Tailte Éireann townlands** (2019 statutory, [GSI FeatureServer](https://gsi.geodata.gov.ie/server/rest/services/Third_Party/IE_GSI_Tailte_Eireann_Townlands_IE26_ITM/FeatureServer/0)) | Irish townland names (GAEILGE field) for the site cards: 4,694 matched by name and county, plus 1,172 by point-in-polygon | **CC BY 4.0**, Tailte Éireann. The Irish forms are the statutory names (logainm.ie lineage) |
| **Copernicus GLO-30 DSM** (AWS `copernicus-dem-30m`) | Horizon profiles for 8 featured sites | Free use with attribution: "produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA" |
| GSI **Open Topographic LiDAR** DTM, 1 m | Planned for T4/T5 at selected sites | CC BY 4.0 |
| **Heritage Maps** (heritagemaps.ie) | Reference viewer only | Heritage Council datasets are CC BY 4.0; layers from other providers need their permission; the OSi/Tailte basemap is for reference only |
| **OpenStreetMap** tiles | Basemap, recoloured with CSS | © OpenStreetMap contributors, ODbL; tile usage policy |
| d3-celestial (star and constellation data, from Hipparcos/Yale BSC), Astronomy Engine 2.1.19, Leaflet 1.9.4 | Sky dome, live Sun/Moon/planets, map | BSD-3, MIT, BSD-2 |
| NMS 2024 Newgrange report | 53 measured in-chamber sun positions (`site/data/newgrange_obs.json`) | Quoted with citation |

**Gaps.**
- 10,879 SMR records nationally have ITM 0,0 (coordinates withheld or missing). Of the monument classes we map, 589 are dropped for this reason; Cork, Kilkenny and Galway are the most affected.
- NI records have no Irish townland names in our sources.
- téarma.ie could not be queried (it shows a bot challenge, which we did not bypass). Irish class names come from focloir.ie and Fingal County Council's bilingual heritage leaflet; where no sourced term exists (cursus, boulder-burial) we leave it blank rather than invent one.

### SMR class counts (Republic, `SMROpenData_20251201.csv`)

| Class | Records | ITM 0,0 |
|---|---:|---:|
| Passage tomb | 204 | 3 |
| Court tomb | 305 | 1 |
| Portal tomb | 150 | 0 |
| Wedge tomb | 525 | 3 |
| Megalithic tomb – unclassified | 432 | 93 |
| Stone circle | 133 | 33 |
| Stone circle – multiple-stone | 57 | 0 |
| Stone circle – five-stone | 56 | 0 |
| Stone circle – embanked | 9 | 0 |
| Stone row | 202 | 14 |
| Standing stone – pair | 248 | 11 |
| Standing stone | 4,100 | 428 |
| Henge | 22 | 0 |
| Cursus | 14 | 0 |
| Boulder-burial | 141 | 3 |
| Passage tomb art | 13 | 1 |
| Rock art | 791 | 54 |
| Cupmarked stone | 92 | 1 |
| Cairn – unclassified | 1,291 | 122 |
| Barrow – ring-barrow | 1,554 | 14 |
| Megalithic structure | 443 | 112 |

**Context.** The largest classes are ringfort–rath (26,000), enclosure (16,621) and fulacht fia (6,637).

**By county.**
- Passage tombs: Sligo 77, Meath 57, Dublin 18, Donegal 12.
- Stone circles and rows (457): Cork 183, Kerry 68, Mayo 40.

The full summary is in `data/smr_class_summary.json`.

**Mapped on the site (Republic + NI):** 6,878 monuments.

| Class | Count |
|---|---:|
| Passage tombs | 216 |
| Court tombs | 406 |
| Portal tombs | 191 |
| Wedge tombs | 573 |
| Unclassified megalithic tombs | 468 |
| Stone circles | 255 |
| Stone rows | 197 |
| Stone pairs | 271 |
| Henges | 29 |
| Cursus monuments | 14 |
| Boulder-burials | 138 |
| Standing stones (lazy-loaded) | 4,120 |

## 3. Methods already built

- **Horizon** (`scripts/horizon.py`).
  - The Copernicus DSM is ray-marched every 0.5° of azimuth, from 400 m to 60 km.
  - It applies Earth curvature with refraction k = 0.13 and an eye height of 1.6 m.
  - **Validation:** at Newgrange, az 135°, the model gives 0.83°; Patrick (1974) measured +0°51′ (0.85°).
- **Rise and set azimuths** (`site/js/astro.js` and the mirror `scripts/astro.py`).
  - Each azimuth is solved iteratively against the horizon profile, with Bennett refraction, the Sun's semi-diameter and lunar parallax.
  - Obliquity uses the Laskar series (24.04° at 3200 BC, 23.44° today).
- **Recomputation for Newgrange.**
  - Winter-solstice first gleam: 134.3° at 3200 BC, 133.1° today.
  - The NMS-measured light window (133.7°–138.4°) corresponds to declinations −23.8° to −25.9°.
- **Simulator.** The beam is "on" when the Sun lies inside the convex hull of the 53 NMS-measured in-chamber positions. With the default settings it gives "beam in the chamber" at 08:58 GMT on 21 Dec, consistent with O'Kelly's account.

## 4. Data layer: D4M associative arrays

The tests use **D4M** (MIT Lincoln Laboratory's Dynamic Distributed Dimensional Data Model; Kepner et al.).
- Every relation is a sparse associative array A(row, col) = val, with string keys.
- Arrays support row and column selection, element-wise operations and matrix products.
- This suits the problem: monuments have very different and sparse properties, and the tests are mostly joins.

| Array | Rows | Columns | Values |
|---|---|---|---|
| `A_prop` | monument id (`ME019-045----`, `NI:ANT004:015`) | `field\|value`: `class\|pt`, `county\|SLIGO`, `townland_ga\|An Ghráinseach Nua`, `orient\|SW` (parsed, after prereg), `era\|neolithic` | 1 |
| `A_sky` | monument id | `event\|epoch`: `WS_rise\|3200BC`, `SS_set\|2026`, `MjN_set\|3200BC`, … | azimuth (deg) for the event |
| `A_hor` | monument id | `az\|134.5` | horizon altitude (deg) |
| `A_dec` | monument id | `axis\|facing`, `axis\|back` | declination of the axis |
| `A_vis` | monument id | monument id | 1 if intervisible (DSM line of sight), or Δheight (m) |

**Example queries** (D4M.py syntax):
```python
pt   = A_prop[:, 'class|pt,']                    # all passage tombs (column vector)
sligo_pt = (A_prop[:, 'county|SLIGO,'] & pt)     # passage tombs in Sligo
ws   = A_sky[pt.row, 'WS_rise|3200BC,']          # their midwinter sunrise azimuths
hit  = abs(A_dec[:, 'axis|facing,'] - (-24.04)) < 1.5   # facing within 1.5° of the solstice declination
A_vis[pt.row, pt.row]                            # passage-tomb intervisibility graph
(A_vis * A_vis)                                  # tombs linked through one intermediate tomb (2-hop)
A_prop.T * A_vis * A_prop                        # class × class intervisibility counts (e.g. pt→ct)
```
- **Current state.** The first pass exports `A_prop` and `A_sky` as D4M triples (`data/d4m/A_prop.tsv`, `A_sky.tsv`; 6,878 monuments, 129k triples) via `scripts/d4m_triples.py`.
- **Not yet done.**
  - The `D4M` package (0.3.3 on PyPI) failed to install on the build box because the `libarchive` wheel would not build. Loading the triples with `Assoc(rows, cols, vals)` is the next step.
  - `A_hor`, `A_dec` and `A_vis` come after the orientation parser is frozen.

## 5. Feasibility (no scoring)

We counted SMR descriptions containing an explicit compass-orientation phrase, **without tabulating which directions they give**:

| Class | Descriptions with a phrase |
|---|---:|
| Wedge tomb | 309 |
| Court tomb | 90 |
| Portal tomb | 81 |
| Passage tomb | 43 |
| Stone row | 136 |
| Standing-stone pair | 153 |
| Five-stone circle | 47 |
| Multiple-stone circle | 37 |

These counts set the sample sizes in the pre-registration.

## 6. Pre-registered tests (PA Marine style)

The full protocol, null models and adoption rules are in [`prereg/tests_v1.json`](prereg/tests_v1.json). It was committed before any orientation was tabulated; commit hashes will go in `TEST_LOG.md`.

**Shared rules for all tests.**
- Monte Carlo: 10,000 draws, seed 20261009.
- The null is quantised to the same 16-point compass bins as the data.
- Holm-Bonferroni correction across T1–T5 at α = 0.05.
- Every test must survive its stated robustness check.
- All results are reported, pass or fail.

**The tests.**
- **T1. Wedge tombs face the setting sun.** Facing azimuths are compared with the winter-solstice sunset at 2200 BC, using a random-rotation Monte Carlo and a V-test against 236°. Robustness: the result must hold with Cork and Kerry excluded.
- **T2. Passage-tomb declinations.** We test for density peaks at ±ε, 0 and ±(ε ± i), using DSM horizons. NMS 2024 (p = 0.896) is the benchmark. Robustness: the result must hold with Brú na Bóinne excluded.
- **T3. Stone rows and lunar standstills.** This is a replication of Ruggles on SMR data. It uses two nulls (random azimuth, and horizon peaks only) and runs Cork/Kerry and the rest of Ireland separately.
- **T4. Intervisibility.** Passage tombs are tested against random siting on matched terrain within 20 km of each cemetery.
- **T5. Horizon targets.** Stone pairs and rows are tested for aiming at horizon maxima of prominence ≥ 0.5°, checked at 0.3° and 1.0°.

**Outside the tests.** Single famous sites stay descriptive. Brennan's art-and-star readings have no testable protocol, so they are not scored.

## 7. Reproduce

See `README.md`. In short:
```
scripts/fetch_data.sh
python scripts/build_data.py
python scripts/horizon.py
python scripts/build_stars.py
python scripts/d4m_triples.py
```
Raw data (170 MB CSV, 367 MB DSM) is not in the repo.
