"""shots.py - full-page screenshots of the local build (desktop + phone) for design review."""
import sys
from playwright.sync_api import sync_playwright
BASE = "http://localhost:8765/"
PAGES = sys.argv[1:] or ["index.html", "picks/index.html", "picks/feeding.html", "links/index.html"]
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in [("desk", {"width": 1440, "height": 900}), ("phone", {"width": 390, "height": 844})]:
        pg = b.new_page(viewport=vp, device_scale_factor=1)
        for path in PAGES:
            pg.goto(BASE + path, wait_until="networkidle")
            for y in range(0, 20000, 700):
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60)
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(1200)
            out = f"_shots/{name}_{path.replace('/', '_').replace('.html', '')}.png"
            pg.screenshot(path=out, full_page=True)
            print(out)
    b.close()
