#!/usr/bin/env python3
"""Execute desktop-safe-file and header functions with negative controls.

No FastAPI import, DB access, signing, media upload, external domains or daemon.
"""
from __future__ import annotations

import ast
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "host/mcp/luhmHarness.py"
UI = ROOT / "host/harness/index.html"
JS = ROOT / "host/harness/cockpit.js"
CSS = ROOT / "host/harness/cockpit.css"

def extract(name):
    program = ast.parse(SOURCE.read_text(encoding="utf8"))
    funcs = [x for x in program.body if isinstance(x,ast.FunctionDef) and x.name == name]
    assert len(funcs) == 1, "MISSING_PYTHON3_GATE:"+name
    namespace = {"Path": Path}
    exec(compile(ast.Module(body=funcs,type_ignores=[]),str(SOURCE),"exec"),namespace)
    return namespace[name]

def audit():
    path_gate = extract("_safe_file")
    headers = extract("_headers")
    with TemporaryDirectory() as folder:
        root = Path(folder)
        (root/"approved.txt").write_text("OWNER_SAFE")
        (root/"nested").mkdir()
        (root/"nested"/"image.png").write_bytes(b"PIXELS")
        (root/"nested"/"internalAlias.png").symlink_to(root/"nested"/"image.png")
        (root/"pathAlias").symlink_to(root/"nested",target_is_directory=True)
        outside = root.parent / "desktopHardeningOutsideSecret.test"
        outside.write_text("PRIVATE")
        try:
            accepted = ["approved.txt","nested/image.png"]
            for name in accepted:
                assert path_gate(root,name) is not None, "REJECTED_SAFE:"+name
            blocked = [
                "", ".", "../desktopHardeningOutsideSecret.test", "/etc/passwd",
                "nested/../approved.txt", "./approved.txt","nested//image.png",
                "nested/internalAlias.png", "pathAlias/image.png", "nested\\image.png",
                "approved.txt\x00more", "missing.jpg"
            ]
            for name in blocked:
                assert path_gate(root,name) is None, "RED_PATH_BYPASS:"+repr(name)
        finally:
            outside.unlink(missing_ok=True)
    assert headers(dynamic=True)["Cache-Control"]=="no-store"
    assert headers(html=True)["Cache-Control"]=="no-store"
    assert headers()["Cache-Control"]=="public, max-age=300"
    csp=headers(html=True)["Content-Security-Policy"]
    assert "frame-src 'self' blob: https://www.youtube-nocookie.com;" in csp
    assert "script-src 'self';" in csp
    assert "unsafe-inline" not in csp.split("script-src",1)[1].split(";",1)[0]
    assert "base-uri 'none'" in csp and "object-src 'none'" in csp
    assert "frame-ancestors 'self'" in csp
    assert "Content-Security-Policy" in headers(html=True,godot_embed=True)
    assert "Strict-Transport-Security" in headers(production=True)

    html=UI.read_text(encoding="utf8")
    js=JS.read_text(encoding="utf8")
    css=CSS.read_text(encoding="utf8")
    for token in ('id="deskStatus"','aria-live="polite"',
                  'accept=".png,.jpg,.jpeg,.gif,.webp,.mp4,.webm,.pdf"',
                  'sandbox="allow-scripts allow-same-origin allow-pointer-lock"'):
        assert token in html, "MISSING_DESKTOP_UI:"+token
    for token in ('MAX_DESK_FILES = 24','MAX_ASSET_BYTES = 32 * 1024 * 1024',
                  'MAX_DESK_BYTES = 128 * 1024 * 1024','AbortSignal.timeout(BOOT_TIMEOUT_MS)',
                  'setDeskStatus(','.finally(() => {','byId("agentLoadingScreen").hidden = true'):
        assert token in js, "MISSING_JS_BOUNDS:"+token
    assert "prefers-reduced-motion:reduce" in css
    assert "prefers-contrast:more" in css
    assert "focus-visible" in css
    assert "max-width:min(96vw,1760px)" in css
    print("GREEN_DESKTOP_PYTHON3_SECURITY_PATHS_12_NEGATIVE_CONTROLS")
    print("GREEN_DESKTOP_CSS_ACCESSIBILITY_AND_JS_SOURCE_CONTRACT")
    print("SOURCE_ONLY: no host-side browser interactions or Samsung device tested")

if __name__=="__main__":
    audit()
