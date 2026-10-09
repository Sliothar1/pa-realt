# PA Réalt · Stone and Sky

**Live site:** https://sliothar1.github.io/pa-realt/

*Réalt* is Irish for star. The site is an interactive map of Ireland's Neolithic and Bronze Age monuments (6,878 sites from the open Sites and Monuments Records, North and South), with:
- solstice, equinox and lunar-standstill rays;
- a Newgrange sunrise simulator built on the National Monuments Service's measured in-chamber sun positions;
- a live night-sky dome over Brú na Bóinne;
- an honest "claims vs evidence" section.

It is a project by **Garry Lohan** (mechanical engineer and lecturer, ATU Galway), and a sister site of [PA Marine](https://sliothar1.github.io/PA-Marine-Demo/) (see `BRAND.md`).

| | |
|---|---|
| `site/` | the static site (published to the `gh-pages` branch with `git subtree push --prefix site origin gh-pages`). No build step; Leaflet and Astronomy Engine are vendored |
| `site/js/config.js` | **the single place for the name**, subtitle, credit and PA family links |
| `RESEARCH.md` | sites and claims with sources, open data and licences, SMR class counts, methods, D4M design, pre-registered tests |
| `prereg/tests_v1.json` | frozen pre-registration of tests T1–T5 (nothing scored yet) |
| `BRAND.md` | the shared PA family brand and the PA Réalt palette |
| `NOTICE.md` | data and code attributions |
| `scripts/` | data pipeline: `fetch_data.sh` → `townland_pip.py` → `build_data.py` → `horizon.py` → `build_stars.py` → `d4m_triples.py`; `stamp.py` (name into the static HTML), `shoot.py` (screenshots) |
| `data/` | derived summaries (`smr_class_summary.json`, D4M triples); the raw data is not committed |

**Rename the project.** Edit `site/js/config.js`, then run `python scripts/stamp.py`.

**Run locally.** Run `python -m http.server -d site 8000` and open http://localhost:8000.

Data licences: NMS SMR (CC BY 4.0), NI SMR (OGL v3), Tailte Éireann (CC BY 4.0), Copernicus DSM (Copernicus licence), and © OpenStreetMap contributors. This is a research prototype and not an official National Monuments Service product.
