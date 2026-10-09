"""Headless checks for real horizons, Light this week, test results, visit sheet, family hub (390x844 and desktop)."""
import sys, asyncio
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8913/'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp'
WT = 'CL002-077----'
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        for name, vp, mob in (('mobile', {'width': 390, 'height': 844}, True), ('desktop', {'width': 1440, 'height': 900}, False)):
            ctx = await b.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            pg = await ctx.new_page(); errs = []; reqs = []
            pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            pg.on('requestfinished', lambda r: reqs.append(r.url))
            await pg.goto(URL + '#site=' + WT, wait_until='networkidle', timeout=60000); await pg.wait_for_timeout(2500)
            card = await pg.inner_text('#card'); hzc = await pg.locator('#hzc').count()
            print(name, 'card real-horizon:', 'Real horizon' in card, 'canvas', hzc, 'hz files:', [u.split('/')[-1] for u in reqs if '/hz/' in u])
            await pg.click('#card .ask-q[data-q="face"]'); await pg.wait_for_timeout(1200)
            ans = await pg.inner_text('#card .ask-a'); print(name, 'ask face mentions real horizon:', 'real horizon' in ans)
            await pg.click('#card .ask-q[data-q="real"]'); await pg.wait_for_timeout(1200)
            ans = await pg.inner_text('#card .ask-a'); print(name, 'ask real:', ans[ans.find('Our test'):][:220].replace('\n', ' '))
            await pg.evaluate("document.querySelector('#card').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'{OUT}/card-{name}.png')
            lw = await pg.inner_text('#lwList'); print(name, 'light this week:', lw[:400].replace('\n', ' | '))
            await pg.evaluate("document.getElementById('lightweek').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'{OUT}/lightweek-{name}.png')
            print(name, 'tres', await pg.locator('.tres').count())
            await pg.evaluate("document.getElementById('tests').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'{OUT}/tests-{name}.png')
            await pg.evaluate("document.getElementById('paFamily').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'{OUT}/family-strip-{name}.png')
            # egg with real horizons
            await pg.evaluate("window.scrollTo(0,0)"); await pg.keyboard.press('g'); await pg.wait_for_timeout(5000)
            print(name, 'egg canvas', await pg.locator('.egg-canvas').count()); await pg.screenshot(path=f'{OUT}/egg-{name}.png')
            for page, extra in (('results.html', ''), ('family.html', ''), ('visit.html?site=' + WT, ''), ('visit.html?site=ME019-045----', ''), ('visit.html?site=SL014-209', '')):
                await pg.goto(URL + page, wait_until='networkidle', timeout=60000); await pg.wait_for_timeout(1800)
                tag = page.split('.')[0] + ('-' + page.split('=')[1][:6] if '=' in page else '')
                if 'visit' in page:
                    t = await pg.inner_text('#sheet'); print(name, tag, 'qr', await pg.locator('.qr svg').count(), 'rows', await pg.locator('.sheet tbody tr').count(), '|', t[:160].replace('\n', ' | '))
                await pg.screenshot(path=f'{OUT}/{tag}-{name}.png', full_page=True)
            if not mob:
                await pg.goto(URL + 'visit.html?site=ME019-045----', wait_until='networkidle'); await pg.wait_for_timeout(1500)
                await pg.emulate_media(media='print'); await pg.pdf(path=f'{OUT}/visit-newgrange.pdf', format='A4', print_background=True)
            print(name, 'ERRORS:', errs)
            await ctx.close()
        await b.close()
asyncio.run(run())
