"""Headless test of the midwinter egg: mobile (390x844, triple-tap logo) and desktop (G key)."""
import sys, asyncio
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8913/'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        for name, vp, mob in (('mobile', {'width': 390, 'height': 844}, True), ('desktop', {'width': 1440, 'height': 900}, False)):
            ctx = await b.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            pg = await ctx.new_page(); errs = []
            pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            await pg.goto(URL, wait_until='networkidle', timeout=60000); await pg.wait_for_timeout(1800)
            info = await pg.evaluate("""()=>{const m=document.getElementById('map'),r=m.getBoundingClientRect();
              const L=window.L;return {note:getComputedStyle(document.querySelector('.skyline-note')).display}}""")
            # map view on load: scroll map into view, screenshot
            await pg.evaluate("document.getElementById('explore').scrollIntoView({block:'start'})"); await pg.wait_for_timeout(700)
            await pg.screenshot(path=f'/tmp/egg-{name}-load.png')
            await pg.evaluate("scrollTo(0,0)"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/tmp/egg-{name}-hero.png')
            if mob:
                for _ in range(3):
                    await pg.tap('.brandlink'); await pg.wait_for_timeout(120)
            else:
                await pg.mouse.move(5, 5); await pg.keyboard.press('g')
            for ms, tag in ((3300, 'a'), (2900, 'b'), (1300, 'c'), (1300, 'd')):
                await pg.wait_for_timeout(ms); await pg.screenshot(path=f'/tmp/egg-{name}-{tag}.png')
            if mob: import shutil; shutil.copy('/tmp/egg-mobile-c.png', f'{OUT}/egg-mobile.png')
            await pg.wait_for_timeout(2400)
            left = await pg.evaluate("document.querySelectorAll('.egg-canvas').length")
            print(name, info, 'canvas left after 11s:', left, 'errors:', errs[:8])
            await ctx.close()
        await b.close()
asyncio.run(run())
