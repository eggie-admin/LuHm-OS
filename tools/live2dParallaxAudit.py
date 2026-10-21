#!/usr/bin/env python3
"""LuHm original layered 2D, Vue candidate and parallax negative controls."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = {}
    def handle_starttag(self, tag, attributes):
        ident = dict(attributes).get("id")
        if ident:
            assert ident not in self.ids, "RED_DUPLICATE_ID:" + ident
            self.ids[ident] = tag

def verify(html, css, js, jquery, vue, frontend):
    bad = []
    def need(ok, msg):
        if not ok:
            bad.append(msg)
    scan = Elements()
    scan.feed(html)
    required = {
        "lum2dPanel": "section", "lum2dStage": "div", "lum2dTitle": "h2",
        "lum2dMouth": "path", "lum2dBlink": "button", "lum2dSmile": "button",
        "lum2dWave": "button", "lum2dPause": "button", "lum2dMessage": "p"
    }
    for key, kind in required.items():
        need(scan.ids.get(key) == kind, "missing_html_" + key)
    need('aria-live="polite"' in html and 'aria-pressed="true"' in html, "accessible_ui")
    need("Live2D-style puppet" in html, "honest_provenance")
    need("lum2dStage.is-blinking" in css and "lum2dStage.is-waving" in css, "sprite_states")
    need("var(--l2x)" in css and "var(--l2bx)" in css, "parallax_depth")
    need("@media(prefers-reduced-motion:reduce)" in css and ".is-motion-paused" in css, "reduced_css")
    need("function initLumLive2d()" in js and "initLumLive2d();" in js, "boot_hook")
    need("function resetParallax()" in js and "reducedHeaderMotion.matches" in js, "header_accessibility")
    for item in ['"pointermove"', '"pointerleave"', 'requestAnimationFrame(draw)', 'cancelAnimationFrame(raf)',
                 '"visibilitychange"', '"pagehide"', 'Number.isFinite(event.clientX)',
                 'Math.max(-1, Math.min(1, n))', 'clearTimeout(blinkTimer)',
                 'stage.removeEventListener("pointermove", pointerMove)']:
        need(item in js, "puppet_lifecycle_" + item)
    start, end = js.find("function initLumLive2d()"), js.find("async function boot()")
    need(start >= 0 and end > start, "puppet_scope")
    source = js[start:end] if 0 <= start < end else ""
    for unsafe in ("fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "Function(", "innerHTML", "localStorage"):
        need(unsafe not in source, "unexpected_remote_or_injection_" + unsafe)
    need('$.fn.luhmParallax = function' in jquery and 'command === "destroy"' in jquery, "jquery_plugin")
    need('$.removeData(el, KEY)' in jquery and 'removeEventListener("pointermove", onMove)' in jquery, "jquery_cleanup")
    need("requestAnimationFrame(draw)" in jquery and "cancelAnimationFrame(raf)" in jquery, "jquery_raf_cleanup")
    need("prefers-reduced-motion: reduce" in jquery and "Number.isFinite(event.clientX)" in jquery, "jquery_bounded_pointer")
    need(all(unsafe not in jquery for unsafe in ("fetch(", "eval(", "innerHTML", "https://")), "jquery_no_remote")
    need('<script setup>' in vue and 'from "vue"' in vue and "onBeforeUnmount" in vue, "vue3_component")
    need('prefers-reduced-motion: reduce' in vue and '@pointermove="move"' in vue, "vue_motion")
    need(all(unsafe not in vue for unsafe in ("https://", "fetch(", "innerHTML", "CubismSdk", "window.Live2D")), "vue_no_donor_sdk")
    need('src="./jquery/luhm.parallax.js"' in frontend and
         'src="./vendor/jquery-3.7.1.min.js"' in frontend, "local_plugin_script")
    return bad

def main():
    read = lambda filename: (ROOT / filename).read_text(encoding="utf8")
    values = (
        read("host/harness/index.html"), read("host/harness/cockpit.css"),
        read("host/harness/cockpit.js"), read("frontEnd/jquery/luhm.parallax.js"),
        read("frontEnd/vue/LumLayeredPuppet.vue"), read("frontEnd/index.html")
    )
    failures = verify(*values)
    assert not failures, "RED_LIVE2D:" + ", ".join(failures)
    html, css, js, jquery, vue, frontend = values
    mutations = [
        ("html", (html.replace('id="lum2dStage"', 'id="broken"'), css, js, jquery, vue, frontend)),
        ("motion", (html, css.replaceAll("@media(prefers-reduced-motion:reduce)", "@media(min-width:1px)"), js, jquery, vue, frontend)),
        ("pointer", (html, css, js.replaceAll("Number.isFinite(event.clientX)", "true"), jquery, vue, frontend)),
        ("remote", (html, css, js.replace("const root = byId", "fetch('https://unexpected.invalid'); const root = byId"), jquery, vue, frontend)),
        ("vue_vendor", (html, css, js, jquery, vue + "<script src='https://invalid.example'></script>", frontend)),
        ("jquery_cleanup", (html, css, js, jquery.replace("$.removeData(el, KEY)", "void 0"), vue, frontend))
    ]
    for title, mutant in mutations:
        assert verify(*mutant), "RED_LIVE2D_NEGATIVE_MISSED:" + title
    print("GREEN_LUHM_LIVE2D_PARALLAX_SOURCE_AND_SIX_NEGATIVE_CONTROLS")
    print("VUE3=UNBUNDLED_OPT_IN_COMPONENT_NOT_PUBLIC_CUBISM_RUNTIME")

if __name__ == "__main__":
    main()
