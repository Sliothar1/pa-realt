"""Build the 'Ask PA Réalt' knowledge files (all from open/official sources):
 - site/data/notes/c<county_idx>.json : SMR description (WEB_NOTES, NMS, CC BY 4.0) per mapped monument, + State-care flag
 - site/data/ask_kb.json            : NMS Monument Class and Scope Notes (bilingual) for our classes
State-care flags: NMS 'National Monuments in State Care: Ownership & Guardianship' county lists (2009 edition, archaeology.ie)."""
import json, re, glob, os, collections
import pandas as pd
d = json.load(open('site/data/sites.json', encoding='utf-8')); st = json.load(open('site/data/standing.json', encoding='utf-8'))
allsites = d['sites'] + st['sites']; cidx = {s[0]: s[6] for s in allsites}
care = {}
for f in glob.glob('data/raw/msc/*.txt'):
    for line in open(f, encoding='utf-8', errors='ignore'):
        codes = re.findall(r'\b([A-Z]{2}\d{3}-\d{3}[\d-]*)', line)
        if not codes: continue
        kind = 'Ownership' if 'Ownership' in line else 'Guardianship' if 'Guardianship' in line else ''
        for c in codes:
            c = (c + '-------------')[:13]
            if c not in care or (kind and not care[c]): care[c] = kind
df = pd.read_csv('data/raw/SMROpenData_20251201.csv', usecols=['SMRS', 'WEB_NOTES'], dtype=str)
df = df[df.SMRS.isin(cidx)]
shards = collections.defaultdict(dict)
def clip(t, n=3200):
    t = re.sub(r'\s+\n', '\n', str(t or '')).strip()
    if len(t) <= n: return t
    k = t.rfind('. ', 0, n); return t[:k + 1 if k > 0 else n] + ' …'
for smrs, notes in zip(df.SMRS, df.WEB_NOTES):
    shards[cidx[smrs]][smrs] = [clip(notes), care.get(smrs)]
for s in allsites:
    if s[0] in care and s[0] not in shards[s[6]]: shards[s[6]][s[0]] = ['', care[s[0]]]
os.makedirs('site/data/notes', exist_ok=True)
for f in glob.glob('site/data/notes/*.json'): os.remove(f)
tot = 0
for c, v in shards.items():
    p = f'site/data/notes/c{c}.json'; json.dump(v, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); tot += os.path.getsize(p)
sc = json.load(open('data/scope_notes.json', encoding='utf-8'))
json.dump({'scope_source': sc['source'], 'care_source': 'National Monuments Service (2009). National Monuments in State Care: Ownership & Guardianship (county lists). https://www.archaeology.ie/',
           'scope': sc['notes']}, open('site/data/ask_kb.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('shards', len(shards), 'bytes', tot, 'care codes', len(care), 'mapped in care', sum(1 for s in allsites if s[0] in care))

# small State-care index for the visit sheet (site/data/care.json)
json.dump(sorted(k for k, v in care.items() if v), open('site/data/care.json', 'w'), separators=(',', ':'))
