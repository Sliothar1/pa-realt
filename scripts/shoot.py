"""Headless Chromium screenshots (desktop + mobile) and console-error check."""
import sys, asyncio
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8913/'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
        for name, vp, mob in (('desktop', {'width': 1440, 'height': 900}, False), ('mobile', {'width': 390, 'height': 844}, True)):
            ctx = await b.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            pg = await ctx.new_page(); errs = []
            pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            await pg.goto(URL + ('#site=ME019-045----&z=7' if not mob else ''), wait_until='networkidle', timeout=60000)
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{OUT}/shot-{name}.png', full_page=False)
            await pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))"); await pg.wait_for_timeout(600)
            await pg.screenshot(path=f'/tmp/full-{name}.png', full_page=True)
            print(name, 'errors:', errs[:10])
            await ctx.close()
        await b.close()
asyncio.run(run())
