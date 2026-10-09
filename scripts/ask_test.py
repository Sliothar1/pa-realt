"""Headless checks: Ask panel (featured + generic), Features menu, Near me (simulated Galway location), egg timing."""
import sys, asyncio
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8913/'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        for name, vp, mob in (('mobile', {'width': 390, 'height': 844}, True), ('desktop', {'width': 1440, 'height': 900}, False)):
            ctx = await b.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob,
                                      geolocation={'latitude': 53.2707, 'longitude': -9.0568}, permissions=['geolocation'])
            pg = await ctx.new_page(); errs = []
            pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            await pg.goto(URL + '#site=ME019-045----', wait_until='networkidle', timeout=60000); await pg.wait_for_timeout(1500)
            # featured: Newgrange, "Is the alignment real?"
            await pg.locator('#card .ask').scroll_into_view_if_needed()
            await pg.click('#card .ask-q[data-q="real"]'); await pg.wait_for_timeout(500)
            await pg.locator('#card .ask').scroll_into_view_if_needed(); await pg.evaluate("document.querySelector('#card .ask').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/tmp/ask-{name}-ng.png')
            if mob: await pg.screenshot(path=f'{OUT}/ask-mobile.png')
            # generic: a wedge tomb, all 5 questions
            await pg.goto(URL + '#site=CL010-064006-', wait_until='networkidle'); await pg.reload(wait_until='networkidle'); await pg.wait_for_timeout(1500)
            txt = {}
            for q in ('face', 'when', 'real', 'name', 'visit'):
                await pg.click(f'#card .ask-q[data-q="{q}"]'); await pg.wait_for_timeout(700)
                txt[q] = (await pg.inner_text('#card .ask-a'))[:260].replace('\n', ' ')
                if q == 'face':
                    await pg.evaluate("document.querySelector('#card .ask').scrollIntoView({block:'start'})"); await pg.screenshot(path=f'/tmp/ask-{name}-wt.png')
            for k, v in txt.items(): print(name, k, '=>', v)
            # features menu
            await pg.evaluate('scrollTo(0,0)'); await pg.click('#featBtn'); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/tmp/menu-{name}.png')
            await pg.click('#featMenu [data-act="near"]'); await pg.wait_for_timeout(3500)
            await pg.evaluate("document.getElementById('explore').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'/tmp/near-{name}.png')
            print(name, 'near:', (await pg.inner_text('#nearList'))[:300].replace('\n', ' | '))
            await pg.click('#nearList [data-i="0"]'); await pg.wait_for_timeout(1500)
            print(name, 'card after near tap:', (await pg.inner_text('#card'))[:80].replace('\n', ' | '), '| ask panel:', await pg.locator('#card .ask').count())
            # egg via menu: check toast + canvas at 7s and gone by 17s
            await pg.evaluate('scrollTo(0,0)'); await pg.click('#featBtn'); await pg.wait_for_timeout(300); await pg.click('#featMenu [data-act="egg"]')
            await pg.wait_for_timeout(7000); c1 = await pg.evaluate("[document.querySelectorAll('.egg-canvas').length, document.getElementById('toast').innerText.slice(0,40)]")
            await pg.wait_for_timeout(10000); c2 = await pg.evaluate("document.querySelectorAll('.egg-canvas').length")
            # tap-to-clear
            await pg.keyboard.press('g'); await pg.wait_for_timeout(1500); await pg.mouse.click(30, 30); await pg.wait_for_timeout(1200)
            c3 = await pg.evaluate("document.querySelectorAll('.egg-canvas').length")
            print(name, 'egg at 7s', c1, 'after 17s', c2, 'after tap', c3, 'errors:', errs[:6])
            await ctx.close()
        await b.close()
asyncio.run(run())
