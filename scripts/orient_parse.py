"""FROZEN orientation parser for the pre-registered tests (prereg/tests_v1.json).
Committed before any test is scored; do not edit after the freeze commit (see TEST_LOG.md).

Reads WEB_NOTES (NMS SMR open data) and extracts ONLY explicit 16-point compass phrases.
  facing  : 'faces X', 'facing X', 'opens/opening to the X', 'entrance at/to/on the X'  (wedge and passage tombs)
  axis    : 'aligned/oriented/orientated X-Y', 'axis X-Y', 'alignment X-Y'                 (stone rows and pairs)
A bare axis is ambiguous by 180 deg and is never turned into a facing direction.
Excluded matches: a landscape/field feature as the subject or object, 'long axis' (one stone), or a single stone as the subject.
Output: data/tests/orientations.json  {SMRS: {g, kind, bin, text}}  bin = 0..15 (0 = N, 4 = E, ...); axis bins are 0..7.
"""
import json, re, pandas as pd
PTS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
IDX = {p: i for i, p in enumerate(PTS)}
C = r'(NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|NW|SE|SW|N|S|E|W)'
NOTF = r'(?!\s+(?:and|or|&)\s+(?:the\s+)?[NSEW])(?!\s+(?:of|corner|corners|passage|tomb|chamber|mound|half|quadrant)\b)'
ADV = r'(?:(?:roughly|approximately|approx\.?|broadly|generally|more or less|almost|due|slightly)\s+)?'
DASH = r'\s*[-–—/]\s*'
FACING = [re.compile(r'\b(?:faces|facing|faced)\s+' + ADV + r'(?:to\s+|towards\s+)?(?:the\s+)?' + C + r'\b(?!\s*[-–—/]\s*[NSEW])(?!-facing)' + NOTF),
          re.compile(r'\b(?:opens|opening|opened|open)\s+' + ADV + r'(?:to|towards|on|at|onto)\s+(?:the\s+)?' + C + r'\b(?!\s*[-–—/]\s*[NSEW])' + NOTF),
          re.compile(r'\bentrance\s+(?:is\s+|was\s+|lies\s+|lay\s+)?' + ADV + r'(?:at|to|on|towards|facing)\s+(?:the\s+)?' + C + r'\b(?!\s*[-–—/]\s*[NSEW])' + NOTF)]
AXIS = [re.compile(r'\b(?:aligned|oriented|orientated|alignment|axis)\s+' + ADV + r'(?:on\s+|along\s+|of\s+)?(?:an?\s+|the\s+)?' + C + DASH + C + r'\b')]
LAND = r'(?:slope|hill|ridge|valley|field|wall|road|fence|hedge|ditch|bank|track|river|stream|boundary|enclosure|trench|lane|terrace|outcrop|mountain|plateau|scarp|esker|townland|house|building|cliff|shore|coast|bog|lake|lough)'
LAND_BEFORE = re.compile(LAND + r'[a-z]*\b[^,;()]{0,30}$', re.I)          # landscape noun is the subject: 'the slope faces S'
LAND_AFTER = re.compile(r'^\s*(?:\w+\s+){0,1}' + LAND, re.I)             # 'aligned NE-SW ridges', 'oriented N-S field wall'
NOUNS = re.compile(r'\b(stones|uprights|slabs|orthostats|boulders|monoliths|row|rows|pair|alignment|monument|stone|upright|slab|orthostat|boulder|monolith)\b', re.I)
SINGULAR = {'stone', 'upright', 'slab', 'orthostat', 'boulder', 'monolith'}
def ok(se, m, kind):
    pre, post = se[:m.start()], se[m.end():m.end() + 30]
    if LAND_BEFORE.search(pre) or LAND_AFTER.search(post): return False
    if kind == 'axis':
        if re.search(r'long\s*$', pre, re.I) or re.match(r'axis', m.group(0), re.I) and re.search(r'long\s*$', pre, re.I): return False
        ns = NOUNS.findall(pre)
        if ns and ns[-1].lower() in SINGULAR: return False   # one stone's own orientation, not the row/pair axis
    return True
GROUPS = {'Megalithic tomb - wedge tomb': ('wt', 'facing'), 'Megalithic tomb - passage tomb': ('pt', 'facing'),
          'Stone row': ('sr', 'axis'), 'Standing stone - pair': ('sp', 'axis')}
def sentences(t): return re.split(r'(?<=[.;])\s+(?=[A-Z(])', re.sub(r'\s+', ' ', str(t)))
def parse(text, kind):
    for se in sentences(text):
        if kind == 'facing':
            for rx in FACING:
                for m in rx.finditer(se):
                    if ok(se, m, kind): return IDX[m.group(1)], se
        else:
            for rx in AXIS:
                for m in rx.finditer(se):
                    if not ok(se, m, kind): continue
                    a, b = IDX[m.group(1)], IDX[m.group(2)]
                    if (a - b) % 16 != 8: continue   # not a straight axis (e.g. 'N-SW'): skip
                    return a % 8, se
    return None, None
if __name__ == '__main__':
    df = pd.read_csv('data/raw/SMROpenData_20251201.csv', low_memory=False)
    sites = {s[0] for s in json.load(open('site/data/sites.json', encoding='utf-8'))['sites']}
    out = {}
    for smrs, cls, notes in zip(df.SMRS, df.MONUMENT_CLASS, df.WEB_NOTES):
        if cls not in GROUPS or not isinstance(notes, str) or smrs not in sites: continue
        g, kind = GROUPS[cls]; b, se = parse(notes, kind)
        if b is not None: out[smrs] = {'g': g, 'kind': kind, 'bin': b, 'text': se[:300]}
    json.dump(out, open('data/tests/orientations.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    import collections; print('parsed records per class (counts only):', dict(collections.Counter(v['g'] for v in out.values())))
