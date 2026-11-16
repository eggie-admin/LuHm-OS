"""LuHm machine cockpit. Explicitly local-only, no SQL writes or provider tools."""
from __future__ import annotations
import os
import re
from flask import Flask, jsonify, make_response

app = Flask(__name__)
SHA = re.compile(r"[0-9a-f]{40}\Z")


def status():
    sha = os.environ.get("LUHM_SOURCE_REF", "")
    return {"schema":"luhmOs.machineHarnessStatus.v1",
            "name":"LuHm-OS Project Premonition · Machine Harness",
            "sourceRef":sha if SHA.fullmatch(sha) else "UNVERIFIED",
            "state":"SOURCE_CANDIDATE_ONLY",
            "sql":"NOT_EXPOSED",
            "androidFirmware":"UNTOUCHED",
            "bluetoothUsb":"OWNER_DEVICE_PROOF_REQUIRED",
            "agents":"QUARANTINED",
            "crown":"STOP"}


@app.get("/api/status")
def api_status():
    response = jsonify(status())
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/")
def root():
    s = status()
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
<title>LuHm-OS Machine Harness</title>
<style>body{font:1rem system-ui;background:#11101a;color:#e8e5ff;max-width:48rem;margin:6vh auto;padding:1rem}
h1{color:#c6a2ff}section{border:1px solid #685777;border-radius:1rem;padding:1.3rem}
small{color:#b2accb}.pill{display:inline-block;background:#33213a;padding:.35rem .6rem;border-radius:1rem}
code{overflow-wrap:anywhere}</style>
<h1>LuHm-OS ⬡ Machine Harness</h1><section><p><strong>Project Premonition</strong> · Project Hydra continuity</p>
<p class="pill">SOURCE CANDIDATE · CROWN STOP</p><p>Local Linux / Samsung / Pixel capability inventory</p>
<p>Exact source: <code>""" + s["sourceRef"] + """</code></p>
<small>No remote SQL, public network, firmware flashing, signing, or autonomous AI execution.</small></section></html>"""
    res = make_response(page)
    res.headers["Content-Type"] = "text/html; charset=utf-8"
    res.headers["Cache-Control"] = "no-store"
    res.headers["X-Content-Type-Options"] = "nosniff"
    return res


if __name__ == "__main__":
    app.run(host=os.environ.get("LUHM_BIND", "127.0.0.1"), port=8765, debug=False, use_reloader=False)
