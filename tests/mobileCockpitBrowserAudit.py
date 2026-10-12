#!/usr/bin/env python3
"""Browser-level mobile cockpit layout regression against actual repository assets.

No network requests or live origin, no downloaded assets, no publication.
"""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "host/harness/index.html").read_text(encoding="utf-8")
CSS = (ROOT / "host/harness/cockpit.css").read_text(encoding="utf-8")

assert '<meta name="viewport" content="width=device-width,initial-scale=1">' in HTML
assert "text-size-adjust:100%" in CSS
assert "grid-template-columns:58px minmax(0,1fr)" in CSS
assert "grid-row:2" in CSS and "#edgeBadge" in CSS
assert "overflow-wrap:break-word" in CSS

# Inject the real CSS into the real header HTML, with no remote HTTP or JS.
html = HTML.replace('<link rel="stylesheet" href="/harness/assets/cockpit.css">', "<style>" + CSS + "</style>")
html = html.replace('<script src="/harness/assets/cockpit.js" defer></script>', "")
# Prevent any external iframe from being loaded.
html = html.replace('<iframe id="godotFrame"', '<iframe src="about:blank" id="godotFrame"')

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
    for width in (320, 390, 412, 640, 960):
        page = browser.new_page(viewport={"width": width, "height": 840}, device_scale_factor=1)
        page.set_content(html)
        geometry = page.evaluate("""() => {
          const rect = sel => {
            const {x,y,width,height,bottom,right} = document.querySelector(sel).getBoundingClientRect();
            return {x,y,width,height,bottom,right};
          };
          return {scroll: document.documentElement.scrollWidth,
                  header:rect('.topbar'),
                  title:rect('.titleBlock'),
                  subtitle:rect('.subtitle'),
                  badge:rect('#edgeBadge'),
                  h1Font:parseFloat(getComputedStyle(document.querySelector('.topbar h1')).fontSize),
                  subtitleFont:parseFloat(getComputedStyle(document.querySelector('.topbar .subtitle')).fontSize),
                  display:getComputedStyle(document.querySelector('.topbar')).display};
        }""")
        assert geometry["scroll"] <= width + 1, ("horizontal overflow", width, geometry)
        if width <= 640:
            assert geometry["display"] == "grid", ("mobile header not grid", width, geometry)
            assert geometry["title"]["width"] >= 165, ("title squeezed", width, geometry)
            assert geometry["header"]["height"] <= 175, ("header waterfall", width, geometry)
            assert geometry["badge"]["y"] >= geometry["title"]["bottom"] - 1, ("badge collision", width, geometry)
            assert geometry["h1Font"] <= 21, ("title font drift", width, geometry)
            assert geometry["subtitleFont"] <= 13, ("subtitle font drift", width, geometry)
        else:
            assert geometry["display"] == "flex", ("desktop header regressed", width, geometry)
        print(f"GREEN_MOBILE_COCKPIT width={width} headerPx={round(geometry['header']['height'])} titlePx={round(geometry['title']['width'])}")
        page.close()
    browser.close()
