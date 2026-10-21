#!/usr/bin/env python3
"""Exact-source 3D embed gate; execute real bundle verifier with negative files."""
from __future__ import annotations
import ast
import hashlib
import re
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
HARNESS=ROOT/"host/mcp/luhmHarness.py"
COCKPIT=ROOT/"host/harness/cockpit.js"
PAGE=ROOT/"host/harness/godotPlayerWidget.html"

def verifier():
    data=HARNESS.read_text(encoding="utf8")
    parsed=ast.parse(data)
    nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=="_inspect_godot_bundle"]
    assert len(nodes)==1
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(HARNESS),"exec"),
         globals(), namespace:={})
    return namespace["_inspect_godot_bundle"]

def make_manifest(root):
    files=["index.html","index.wasm","index.pck"]
    for file in files:
        (root/file).write_bytes(file.encode("utf8"))
    (root/"SHA256SUMS.txt").write_text(
        "".join(hashlib.sha256((root/file).read_bytes()).hexdigest()+"  "+file+"\n" for file in files),
        encoding="utf8")

def check():
    py=HARNESS.read_text(encoding="utf8")
    js=COCKPIT.read_text(encoding="utf8")
    html=PAGE.read_text(encoding="utf8")
    pocket=(ROOT/"publicationSite/pocketLab.html").read_text(encoding="utf8")
    assert 'godot_frame_origin = public_origin' in py
    assert 'EXTERNAL_GODOT_FRAME_CANDIDATE' not in py
    assert '"/harness/godot-readiness.json"' in py
    assert 'not _inspect_godot_bundle(godot_root)["ready"]' in py
    assert 'https://luhm-os-publication-site.onrender.com' in py
    assert 'https://*.web-sandbox.oaiusercontent.com' in py
    assert "privateDonorIncluded" in py
    assert 'fetch("/harness/godot-readiness.json"' in js
    assert 'proof?.integrity !== "SHA256_PASS"' in js
    assert "LUHM_GODOT_FRAME" in html
    assert 'id="live3dframe"' in pocket
    assert 'id="launch3d"' in pocket
    assert pocket.count('https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html') == 2
    assert 'https://luhm-os-harness-green.onrender.com/harness/godot-export/index.html' not in pocket
    assert 'sandbox="allow-scripts allow-same-origin allow-pointer-lock"' in pocket
    assert 'private Rebel models' in pocket
    verify=verifier()
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        assert not verify(root)["ready"],"missing bundle accepted"
        make_manifest(root)
        verify.cache_clear()
        result=verify(root)
        assert result["ready"] and result["integrity"]=="SHA256_PASS" and result["fileCount"]==3
        (root/"index.wasm").write_bytes(b"changed")
        verify.cache_clear()
        assert not verify(root)["ready"],"corrupted WASM accepted"
        make_manifest(root)
        (root/"index.pck").unlink()
        verify.cache_clear()
        assert not verify(root)["ready"],"missing PCK accepted"
        make_manifest(root)
        (root/"SHA256SUMS.txt").write_text("f"*64+"  ../private.glb\n",encoding="utf8")
        verify.cache_clear()
        assert not verify(root)["ready"],"path escape accepted"
        make_manifest(root)
        (root/"private.glb").write_bytes(b"PRIVATE")
        with (root/"SHA256SUMS.txt").open("a",encoding="utf8") as out:
            out.write(hashlib.sha256(b"PRIVATE").hexdigest()+"  private.glb\n")
        verify.cache_clear()
        assert not verify(root)["ready"],"private donor accepted"
        make_manifest(root)
        (root/"SHA256SUMS.txt").write_text("f"*64+"  index.wasm\n",encoding="utf8")
        verify.cache_clear()
        assert not verify(root)["ready"],"partial export accepted"
        make_manifest(root)
        (root/"SHA256SUMS.txt").write_text("",encoding="utf8")
        verify.cache_clear()
        assert not verify(root)["ready"],"empty manifest accepted"
    print("GREEN_GODOT_EMBED_SOURCE_7_NEGATIVE_CONTROLS")
    print("BROWSER_CHATGPT_AND_SAMSUNG_RUNTIME_NOT_PROVEN_BY_SOURCE")

if __name__=="__main__":
    check()
