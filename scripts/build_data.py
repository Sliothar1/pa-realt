"""Build compact site data for PA Réalt from the NMS SMR open-data CSV (CC BY 4.0)
and Tailte Éireann townland names (ENGLISH/GAEILGE). Real data only: no records invented.
Usage: python scripts/build_data.py  (run from repo root)"""
import json, re, collections, os
import pandas as pd

SMR = 'data/raw/SMROpenData_20251201.csv'
TL = 'data/raw/townlands_ga_en.json'
OUT = 'site/data'

# group code -> (English label, Irish label or None, source key for the Irish label, SMR classes)
GROUPS = collections.OrderedDict([
 ('pt', ('Passage tombs', 'Tuamaí pasáiste', 'fingal', ['Megalithic tomb - passage tomb'])),
 ('ct', ('Court tombs', 'Tuamaí cúirte', 'fingal', ['Megalithic tomb - court tomb'])),
 ('po', ('Portal tombs', 'Tuamaí ursanacha', 'fingal', ['Megalithic tomb - portal tomb'])),
 ('wt', ('Wedge tombs', 'Tuamaí dinge', 'fingal', ['Megalithic tomb - wedge tomb'])),
 ('mu', ('Megalithic tombs (unclassified)', 'Tuamaí meigiliteacha', 'nms_scope', ['Megalithic tomb - unclassified'])),
 ('sc', ('Stone circles', 'Liagchiorcail', 'nms_scope', ['Stone circle', 'Stone circle - multiple-stone', 'Stone circle - five-stone', 'Stone circle - embanked'])),
 ('sr', ('Stone rows', 'Sraitheanna gallán', 'nms_scope', ['Stone row'])),
 ('sp', ('Standing stones (pair)', 'Péirí cloch', 'fingal', ['Standing stone - pair'])),
 ('he', ('Henges', 'Heinsí', 'nms_scope', ['Henge'])),
 ('cu', ('Cursus monuments', None, None, ['Cursus'])),
 ('bb', ('Boulder-burials', None, None, ['Boulder-burial'])),
 ('ss', ('Standing stones', 'Galláin', 'nms_scope', ['Standing stone'])),
])
CLS2G = {c: g for g, v in GROUPS.items() for c in v[3]}

def norm(t):
    t = re.sub(r'\(.*?(\)|$)', ' ', str(t).upper()).split(',')[0]
    return re.sub(r'\s+', ' ', t).strip()

df = pd.read_csv(SMR, low_memory=False)
n_all = len(df)
cls_counts = df.MONUMENT_CLASS.value_counts()
sel = df[df.MONUMENT_CLASS.isin(CLS2G)].copy()
# quality filters: island of Ireland bounding box (catches e.g. one Dowth record geocoded at 46.5N 15.8W)
bad = ~(sel.LATITUDE.between(51.3, 55.5) & sel.LONGITUDE.between(-10.8, -5.3))
dropped_bbox = sel[bad][['SMRS', 'MONUMENT_CLASS', 'LATITUDE', 'LONGITUDE']].to_dict('records')
sel = sel[~bad]

tl = json.load(open(TL, encoding='utf-8'))
idx = collections.defaultdict(set)
county_ga = {}
for r in tl:
    if r['ENGLISH'] and r['GAEILGE'] and r['COUNTY']:
        idx[(r['ENGLISH'].upper().strip(), r['COUNTY'].upper())].add(r['GAEILGE'].strip())
        county_ga[r['COUNTY'].upper()] = r['CONTAE']

counties = sorted(sel.COUNTY.unique())
cidx = {c: i for i, c in enumerate(counties)}
import os
pip = json.load(open('data/townland_pip_ga.json', encoding='utf-8')) if os.path.exists('data/townland_pip_ga.json') else {}
rows, ga_hit, ga_amb, ga_pip = [], 0, 0, 0
for r in sel.itertuples():
    g = CLS2G[r.MONUMENT_CLASS]
    tn = norm(r.TOWNLAND)
    cands = idx.get((tn, str(r.COUNTY).upper()), set())
    ga = ''
    if len(cands) == 1:
        ga = next(iter(cands)); ga_hit += 1
    elif len(cands) > 1:
        ga_amb += 1
    if not ga and r.SMRS.strip() in pip:  # point-in-polygon match, name-checked (scripts/townland_pip.py)
        ga = pip[r.SMRS.strip()]; ga_pip += 1
    rows.append([r.SMRS.strip(), g, round(r.LATITUDE, 5), round(r.LONGITUDE, 5),
                 str(r.TOWNLAND).title() if isinstance(r.TOWNLAND, str) else '', ga, cidx[r.COUNTY], int(r.ITM_E), int(r.ITM_N)])

# ---- Northern Ireland SMR (OpenDataNI, UK Open Government Licence), EPSG:29902 Irish Grid ----
NI = 'data/raw/nismr.geojson'
NI_MAP = {'PASSAGE TOMB': 'pt', 'COURT TOMB': 'ct', 'DUAL COURT TOMB': 'ct', 'PORTAL TOMB': 'po', 'WEDGE TOMB': 'wt',
          'MEGALITHIC TOMB': 'mu', 'STONE CIRCLE': 'sc', 'STONE CIRCLE & ALIGNMENT': 'sc', 'STONE ALIGNMENT': 'sr', 'STONE ROW': 'sr',
          'TWO STANDING STONES': 'sp', 'STANDING STONES (2)': 'sp', 'HENGE': 'he', 'CURSUS': 'cu', 'STANDING STONE': 'ss'}
ni_n = collections.Counter()
if os.path.exists(NI):
    from pyproj import Transformer
    tr = Transformer.from_crs(29902, 4326, always_xy=True)
    if 'NORTHERN IRELAND' not in counties: counties.append('NORTHERN IRELAND'); county_ga['NORTHERN IRELAND'] = 'Tuaisceart Éireann'
    ci = counties.index('NORTHERN IRELAND')
    for f in json.load(open(NI))['features']:
        p = f['properties']; t = str(p.get('Edited_Typ', '')).split(':')[0].strip().upper()
        if t not in NI_MAP or p.get('Located') != 'Located': continue
        x, y = f['geometry']['coordinates']; lon, lat = tr.transform(x, y)
        g = NI_MAP[t]; ni_n[g] += 1
        rows.append(['NI:' + p['SMRNo'], g, round(lat, 5), round(lon, 5), str(p.get('Townland_s', '')).title(), '', ci, 0, 0])

core = [x for x in rows if x[1] != 'ss']
ss = [x for x in rows if x[1] == 'ss']
meta = {
  'source': 'National Monuments Service, Archaeological Survey of Ireland: Sites and Monuments Record (SMR) open data, SMROpenData_20251201.csv, via data.gov.ie (CC BY 4.0)',
  'source_url': 'https://data.gov.ie/dataset/national-monuments-service-archaeological-survey-of-ireland',
  'irish_townlands': 'Tailte Éireann Townlands (National Statutory Boundaries 2019) ENGLISH/GAEILGE fields, via GSI geodata.gov.ie open data service',
  'hev_link_prefix': 'https://heritagedata.maps.arcgis.com/apps/webappviewer/index.html?id=0c9eb9575b544081b0d296436d8f60f8&query=18a4b61b268-layer-9%2CSMRS%2C',
  'fields': ['smrs', 'group', 'lat', 'lon', 'townland', 'townland_ga', 'county_idx', 'itm_e', 'itm_n'],
  'counties': counties, 'counties_ga': [county_ga.get(c, '') for c in counties],
  'groups': {g: {'en': v[0], 'ga': v[1], 'ga_src': v[2], 'classes': v[3], 'n': None} for g, v in GROUPS.items()},
  'ni_source': 'Northern Ireland Sites and Monuments Record, Department for Communities Historic Environment Division, via OpenDataNI (UK Open Government Licence v3.0), nismr_10092026.geojson', 'ni_url': 'https://www.data.gov.uk/dataset/46240fa5-db15-469e-b1c8-0460504b951c/northern-ireland-sites-and-monuments-record', 'ni_counts': dict(ni_n),
  'n_core': len(core), 'n_standing': len(ss), 'irish_name_matched': ga_hit, 'irish_name_ambiguous': ga_amb, 'irish_name_point_matched': ga_pip,
  'dropped_outside_ireland_bbox': dropped_bbox,
}
for g in GROUPS: meta['groups'][g]['n'] = sum(1 for x in rows if x[1] == g)
meta['counties_ga'] = [county_ga.get(c, '') for c in counties]; meta['counties'] = counties
json.dump({'meta': meta, 'sites': core}, open(f'{OUT}/sites.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump({'sites': ss}, open(f'{OUT}/standing.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# class summary for RESEARCH.md
pre = cls_counts[[bool(re.search(r'megalith|passage|stone circle|stone row|standing stone|wedge|portal|court tomb|henge|boulder|cursus|rock art|cupmark|cairn|barrow', k, re.I)) for k in cls_counts.index]]
summary = {'ni_counts': dict(ni_n), 'n_records': n_all, 'n_classes': int(cls_counts.size), 'top20': cls_counts.head(20).to_dict(),
           'prehistoric_ritual_funerary_classes': pre.to_dict(), 'site_groups': {g: meta['groups'][g]['n'] for g in GROUPS},
           'by_county_core': collections.Counter(counties[x[6]] for x in core).most_common(),
           'irish_name_matched': ga_hit, 'irish_name_ambiguous': ga_amb, 'irish_name_point_matched': ga_pip, 'n_mapped': len(rows), 'dropped_bbox': dropped_bbox}
json.dump(summary, open('data/smr_class_summary.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: summary[k] for k in ['n_records', 'n_classes', 'site_groups', 'irish_name_matched', 'irish_name_ambiguous', 'irish_name_point_matched', 'n_mapped']}, ensure_ascii=False))
print('dropped', len(dropped_bbox), 'records with ITM 0,0 / outside Ireland')
summary_zero = int(((df.ITM_E == 0) | (df.ITM_N == 0)).sum()); print('national records with ITM 0,0:', summary_zero)
summary['national_itm_zero'] = summary_zero; json.dump(summary, open('data/smr_class_summary.json', 'w'), ensure_ascii=False, indent=1)
