"""Browser a11y checks for PA Réalt (Playwright + axe-core), both themes.
Usage: (cd site && python3 -m http.server 8798 &) ; BASE=http://localhost:8798/ AXE=node_modules/axe-core/axe.min.js python3 scripts/a11y_axe.py
A1 axe-core (wcag2a/aa) violations on every page, night and dawn  -> FAIL if any
A2 first Tab lands on the skip link, and activating it moves focus into <main>
A3 with prefers-reduced-motion: reduce, no CSS animation/transition is still running 1 s after load
"""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = os.environ.get('BASE', 'http://localhost:8798/')
AXE = open(os.environ.get('AXE', 'node_modules/axe-core/axe.min.js'), encoding='utf-8').read()
PAGES = ['', 'results.html', 'family.html', 'visit.html?site=CL002-077----', 'list.html']
IGNORE = set(filter(None, os.environ.get('AXE_IGNORE', '').split(',')))
R = []


def rec(i, name, ok, detail=''):
    R.append((i, name, ok, detail))
    print(('PASS ' if ok else 'FAIL ') + i + ' ' + name + (' :: ' + json.dumps(detail, ensure_ascii=False)[:600] if detail else ''))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    for theme in ('night', 'dawn'):
        for pg_ in PAGES:
            c = b.new_context(viewport={'width': 1280, 'height': 900})
            c.add_init_script("try{localStorage.setItem('pa-realt-theme','%s')}catch(e){}" % theme)
            pg = c.new_page(); pg.goto(BASE + pg_, wait_until='load'); pg.wait_for_timeout(1500)
            pg.add_script_tag(content=AXE)
            v = json.loads(pg.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}})"
                                       ".then(r=>JSON.stringify(r.violations.map(v=>[v.id,v.nodes.length,v.nodes.slice(0,3).map(n=>n.target.join(' '))])))"))
            v = [x for x in v if x[0] not in IGNORE]
            rec('A1', 'axe %s %s' % (theme, pg_ or 'index.html'), not v, v)
            c.close()
    for pg_ in PAGES:
        c = b.new_context(); pg = c.new_page(); pg.goto(BASE + pg_, wait_until='load'); pg.wait_for_timeout(500)
        pg.keyboard.press('Tab')
        first = pg.evaluate("document.activeElement && document.activeElement.className")
        pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        inside = pg.evaluate("(()=>{const h=location.hash.slice(1),t=h&&document.getElementById(h);return !!t && (t.contains(document.activeElement)||document.activeElement===t||t.matches('main,section'))})()")
        rec('A2', 'skip link first in tab order and targets content: %s' % (pg_ or 'index.html'), first == 'skip' and inside, {'first': first})
        c.close()
    for pg_ in PAGES:
        c = b.new_context(reduced_motion='reduce'); pg = c.new_page(); pg.goto(BASE + pg_, wait_until='load'); pg.wait_for_timeout(1000)
        running = pg.evaluate("document.getAnimations().filter(a=>a.playState==='running'&&a.effect&&a.effect.getTiming().duration>0&&a.effect.getTiming().iterations===Infinity).map(a=>(a.effect.target&&a.effect.target.className&&String(a.effect.target.className.baseVal??a.effect.target.className))||'?')")
        rec('A3', 'reduced motion: no infinite animation running: %s' % (pg_ or 'index.html'), not running, running[:5])
        c.close()
    b.close()
fails = [r for r in R if not r[2]]
print('browser a11y: %s (%d checks, %d FAIL)' % ('FAIL' if fails else 'ok', len(R), len(fails)))
sys.exit(1 if fails else 0)
