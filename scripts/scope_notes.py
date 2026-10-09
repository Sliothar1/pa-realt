"""Extract English definitions (verbatim) + official Irish class names from the NMS Monument Class and Scope Notes
(pdftotext -raw output data/raw/scope_raw.txt) for our classes -> data/scope_notes.json"""
import json, re
R = open('data/raw/scope_raw.txt', encoding='utf-8').read()
spec = {'pt': ('Megalithic tomb - passage\ntomb', 'Tuama meigiliteach -\ntuama pasáiste', 'Tuama meigiliteach - tuama pasáiste'),
 'ct': ('Megalithic tomb - court tomb', 'Tuama meigiliteach -\ntuama cúirte', 'Tuama meigiliteach - tuama cúirte'),
 'po': ('Megalithic tomb - portal tomb', 'Tuama meigiliteach -\ntuama ursanach', 'Tuama meigiliteach - tuama ursanach'),
 'mu': ('Megalithic tomb - unclassified', 'Tuama meigiliteach -\nneamhaicmithe', 'Tuama meigiliteach - neamhaicmithe'),
 'wt': ('Megalithic tomb - wedge tomb', 'Tuama meigiliteach -', 'Tuama meigiliteach - tuama dingeach'),
 'sc': ('Stone circle', 'Liagchiorcal', 'Liagchiorcal'), 'sr': ('Stone row', 'Sraith gallán', 'Sraith gallán'),
 'sp': ('Standing stone - pair', 'Gallán - péire', 'Gallán - péire'), 'he': ('Henge', 'Heinse', 'Heinse'), 'cu': ('Cursus', 'Cursas', 'Cursas'),
 'bb': ('Boulder-burial', 'Adhlacadh bolláin', 'Adhlacadh bolláin'), 'ss': ('Standing stone', 'Gallán', 'Gallán'),
 'sc5': ('Stone circle - five-stone', 'Ciorcal cúig liag', 'Ciorcal cúig liag'), 'scm': ('Stone circle - multiple-stone', 'Ciorcal il-liagach', 'Ciorcal il-liagach')}
out = {}
for k, (a, endm, ga) in spec.items():
    i = R.index('\n' + a + '\n', 20000) + len(a) + 2; j = R.index(endm, i); t = R[i:j]
    t = re.sub(r'National Monuments Service - Scope Notes[^\n]*\n[^\n]*\nPage \d+ of 51\n', '', t)
    t = re.sub(r'\s+', ' ', t).strip(); t = re.sub(r'(\w)- (\w)', r'\1-\2', t)
    out[k] = {'en': t, 'ga_name': ga}
json.dump({'source': 'National Monuments Service (2023). Monument Class and Scope Notes, v1.1. https://www.archaeology.ie/collections-and-publications/publications/monument-class-and-scope-notes/', 'notes': out},
          open('data/scope_notes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'classes')
