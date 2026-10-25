#!/usr/bin/env python3
"""CAST-scoped Godot Web browser smoke; Chromium is a browser, not ChatGPT host proof."""
from __future__ import annotations
import argparse
import functools
import hashlib
import http.server
import json
import re
import socketserver
import threading
from pathlib import Path

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm", ".pck": "application/octet-stream"}
    def log_message(self,*args):
        pass


def inspect_export(root):
    html=root/"index.html"
    if not html.is_file() or not html.stat().st_size:
        raise ValueError("missing nonempty HTML")
    wasm=sorted(root.glob("*.wasm"))
    pck=sorted(root.glob("*.pck"))
    if not wasm or not pck or any(not p.stat().st_size for p in wasm+pck):
        raise ValueError("missing nonempty wasm or pck")
    record=root/"SHA256SUMS.txt"
    if not record.is_file():
        raise ValueError("missing exported file integrity list")
    entries={}
    for line in record.read_text(encoding="utf-8").splitlines():
        match=re.fullmatch(r"([0-9a-f]{64})\s+\*?(.+)",line)
        if not match:raise ValueError("invalid SHA256SUMS syntax")
        rel=match.group(2).removeprefix("./")
        if Path(rel).name!=rel or rel in entries:raise ValueError("invalid export path")
        item=root/rel
        if not item.is_file() or hashlib.sha256(item.read_bytes()).hexdigest()!=match.group(1):
            raise ValueError("export hash mismatch:"+rel)
        entries[rel]=match.group(1)
    if not all(p.name in entries for p in wasm+pck+[html]):
        raise ValueError("export not fully included in hash manifest")
    return {"html":html.name,"wasm":[p.name for p in wasm],"pck":[p.name for p in pck],"checkedFiles":len(entries)}


def self_test():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as folder:
        root=Path(folder)
        try:inspect_export(root)
        except ValueError:pass
        else:raise AssertionError("empty export accepted")
        for name in ("index.html","index.wasm","index.pck"):
            (root/name).write_bytes(b"x")
        content="".join(hashlib.sha256((root/n).read_bytes()).hexdigest()+"  "+n+"\n" for n in ("index.html","index.wasm","index.pck"))
        (root/"SHA256SUMS.txt").write_text(content,encoding="utf-8")
        assert inspect_export(root)["checkedFiles"]==3
        (root/"index.pck").write_bytes(b"spoof")
        try:inspect_export(root)
        except ValueError:pass
        else:raise AssertionError("corrupted Godot pack accepted")
    print("GREEN_GODOT_WEB_ASSET_NEGATIVE_TESTS")


def run_browser(root,output):
    # Playwright runs only in the explicit CAST Godot Web build lane.
    from playwright.sync_api import sync_playwright
    Handler=functools.partial(QuietHandler,directory=str(root))
    with socketserver.TCPServer(("127.0.0.1",0),Handler) as server:
        port=server.server_address[1]
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        failures=[]
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--enable-webgl","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
            page=browser.new_page(viewport={"width":1280,"height":800},device_scale_factor=1)
            page.on("pageerror",lambda error:failures.append(str(error)[:240]))
            page.goto(f"http://127.0.0.1:{port}/index.html",wait_until="domcontentloaded",timeout=60000)
            page.wait_for_function("() => {const c=document.querySelector('canvas');return !!c && c.width >= 300 && c.height >= 180 && c.offsetWidth > 0}",timeout=120000)
            canvas=page.locator("canvas").first
            output.parent.mkdir(parents=True,exist_ok=True)
            # Previous smoke only photographed the Cathedral menu. Preserve
            # it, then explicitly attempt to enter the rehearsal scene.
            menuProof=output.parent/"cathedralMenu.png"
            rehearsalProof=output.parent/"rehearsalStage.png"
            interactionProof=output.parent/"rehearsalInteractions.png"
            page.screenshot(path=str(menuProof),full_page=True)
            box=canvas.bounding_box()
            if box is None or box["width"] < 300 or box["height"] < 180:
                raise RuntimeError("Godot canvas position not observable")
            page.mouse.click(box["x"]+box["width"]*0.5,box["y"]+box["height"]*0.555)
            page.wait_for_timeout(1400)
            page.screenshot(path=str(rehearsalProof),full_page=True)
            page.keyboard.press("t")
            page.wait_for_timeout(220)
            page.keyboard.press("d")
            page.wait_for_timeout(220)
            page.keyboard.press("ArrowRight")
            page.keyboard.press("t")
            page.wait_for_timeout(450)
            page.screenshot(path=str(interactionProof),full_page=True)
            report={"schema":"luhmOs.godotBrowserSmoke.v1","status":"BROWSER_CANVAS_AND_INPUT_DISPATCH_OBSERVED" if not failures else "RED_BROWSER_SCRIPT_ERROR",
                    "browser":"Chromium headless","canvasVisible":True,
                    "keyboardEventsDispatched":True,"rehearsalClickDispatched":True,
                    "rehearsalSceneVerified":False,"playableQuestProgressProven":False,
                    "touchOnSamsungProven":False,"chatGptHostProven":False,
                    "errors":failures,"screenshot":interactionProof.name,
                    "additionalScreenshots":[menuProof.name,rehearsalProof.name],
                    "proofLimit":"screenshots are reviewable evidence, not a DOM-scene-state assertion",
                    "crownStatus":"STOP"}
            output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
            browser.close()
        server.shutdown()
        if failures:raise RuntimeError("Godot browser page error: "+"; ".join(failures))
        return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--run",action="store_true")
    ap.add_argument("--export-dir",default="host/harness/godot-export")
    ap.add_argument("--output",default="build/godot-browser/proof.json")
    args=ap.parse_args()
    if args.self_test:self_test()
    if not args.run:return
    root=Path(args.export_dir).resolve()
    files=inspect_export(root)
    output=Path(args.output).resolve()
    result=run_browser(root,output)
    print(json.dumps({"assets":files,"browser":result},indent=2))


if __name__=="__main__":
    main()
