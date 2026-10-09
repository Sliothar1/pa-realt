#!/usr/bin/env bash
# Fetch the raw open data into data/raw (not committed). Licences: see RESEARCH.md section 2.
set -euo pipefail
cd "$(dirname "$0")/.."; mkdir -p data/raw data/dem
# NMS SMR open data (CC BY 4.0)
curl -L -o data/raw/SMROpenData_20251201.csv "https://heritagedata.maps.arcgis.com/sharing/rest/content/items/63841b2807504a24942e44955119c339/data"
# Northern Ireland SMR (OGL v3), via data.gov.uk / OpenDataNI
curl -L -A "Mozilla/5.0" -o data/raw/scope_notes.pdf "https://www.archaeology.ie/app/uploads/2025/03/monument-class-and-scope-notes-v1-1.pdf" && pdftotext -raw data/raw/scope_notes.pdf data/raw/scope_raw.txt
mkdir -p data/raw/msc; for c in carlow cavan clare cork donegal dublin galway kerry kildare kilkenny laois leitrim limerick longford louth mayo meath monaghan offaly roscommon sligo tipperary-north tipperary-south waterford westmeath wexford wicklow; do curl -sfL -A "Mozilla/5.0" -o data/raw/msc/$c.pdf "https://www.archaeology.ie/app/uploads/2025/03/monuments-in-state-care-$c.pdf" && pdftotext -layout data/raw/msc/$c.pdf; done
curl -L -A "Mozilla/5.0" -o data/raw/nismr.geojson "https://admin.opendatani.gov.uk/dataset/46240fa5-db15-469e-b1c8-0460504b951c/resource/a2af36e6-d3f0-4abc-9314-b1b72d5a9e06/download/nismr_10092026.geojson"
# d3-celestial star/constellation data (BSD-3)
for f in stars.6.json constellations.lines.json constellations.json starnames.json; do
  curl -L -o "data/raw/d3c_$f" "https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/$f"; done
# Tailte Éireann townland names (CC BY 4.0), attributes only, paged
python3 - <<'PY'
import json, urllib.request, urllib.parse
U = 'https://gsi.geodata.gov.ie/server/rest/services/Third_Party/IE_GSI_Tailte_Eireann_Townlands_IE26_ITM/FeatureServer/0/query'
out, off = [], 0
while True:
    q = urllib.parse.urlencode({'where': '1=1', 'outFields': 'ENGLISH,GAEILGE,COUNTY,CONTAE,GAELTACHT', 'returnGeometry': 'false',
                                'resultOffset': off, 'resultRecordCount': 2000, 'f': 'json'})
    f = json.load(urllib.request.urlopen(U + '?' + q))['features']
    if not f: break
    out += [x['attributes'] for x in f]; off += len(f)
json.dump(out, open('data/raw/townlands_ga_en.json', 'w', encoding='utf-8'), ensure_ascii=False); print(len(out), 'townlands')
PY
# Copernicus GLO-30 DSM tiles covering Ireland (some sea tiles do not exist; 404s are fine)
for lat in 51 52 53 54 55; do for lon in 006 007 008 009 010 011; do
  t="Copernicus_DSM_COG_10_N${lat}_00_W${lon}_00_DEM"
  [ -f "data/dem/$t.tif" ] || curl -sfL -o "data/dem/$t.tif" "https://copernicus-dem-30m.s3.amazonaws.com/$t/$t.tif" || echo "missing $t"
done; done
# Then: python scripts/townland_pip.py (point matches, slow), build_data.py, horizon.py, build_stars.py, d4m_triples.py
