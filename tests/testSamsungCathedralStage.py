#!/usr/bin/env python3
"""Audit Samsung Canon icon rendering and the offline-to-Blender cockpit switch.

This test never signs or installs an APK and never grants release approval.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ICON_SCRIPT = ROOT / "tools/samsungCathedralIcons.py"
WORKFLOW = ROOT / ".github/workflows/samsung-lite-signed-beta.yml"
PRESET = ROOT / "export_presets.cfg"
SIZES = {
    "launcher192.png":192,
    "adaptiveForeground432.png":432,
    "adaptiveBackground432.png":432,
    "adaptiveMonochrome432.png":432,
}

def require(ok: bool, reason: str):
    if not ok:
        raise AssertionError("RED_SAMSUNG_CATHEDRAL_STAGE:" + reason)

def inspect_output(icon_dir: Path, preset: Path):
    receipt = json.loads((icon_dir / "iconReceipt.json").read_text(encoding="utf-8"))
    require(receipt["brand"] == "LuHm-OS" and receipt["crownStatus"] == "STOP", "brand and Crown")
    require(receipt["sourceLogoSha256"] == hashlib.sha256((ROOT/"publicationSite/logo.svg").read_bytes()).hexdigest(), "parent logo")
    require(receipt["androidPackageSigned"] is False and receipt["samsungDeviceProof"] is False, "fake release receipt")
    require({x["name"] for x in receipt["icons"]} == set(SIZES), "four icon families")
    for record in receipt["icons"]:
        path = icon_dir / record["name"]
        data = path.read_bytes()
        require(data.startswith(b"\x89PNG\r\n\x1a\n"), "PNG signature:" + record["name"])
        require(data[12:16] == b"IHDR", "PNG IHDR:" + record["name"])
        require(struct.unpack(">II", data[16:24]) == (SIZES[record["name"]],)*2, "PNG dimensions:" + record["name"])
        require(hashlib.sha256(data).hexdigest() == record["sha256"], "icon hash:" + record["name"])
    settings = preset.read_text()
    for key, name in (
        ("main_192x192","launcher192.png"),
        ("adaptive_foreground_432x432","adaptiveForeground432.png"),
        ("adaptive_background_432x432","adaptiveBackground432.png"),
        ("adaptive_monochrome_432x432","adaptiveMonochrome432.png"),
    ):
        iconpath = icon_dir.relative_to(ROOT).as_posix()
        require(f'launcher_icons/{key}="res://{iconpath}/{name}"' in settings, "Android preset icon hook:" + key)
    print("GREEN_SAMSUNG_FOUR_ICONS_PNG_AND_PRESET")

def inspect_source():
    workflow = WORKFLOW.read_text()
    source = ICON_SCRIPT.read_text()
    html = (ROOT/"frontEnd/index.html").read_text()
    js = (ROOT/"frontEnd/samsungStudioSwitch.js").read_text()
    css = (ROOT/"frontEnd/samsungStudioSwitch.css").read_text()
    require("Stage Canon launcher and adaptive icons into isolated beta preset" in workflow, "workﬂow stage marker")
    require("python3 tools/samsungCathedralIcons.py" in workflow, "stage execution")
    require("--export-release 'Android Proposed'" in workflow, "preserve real export")
    require("LUHM_BETA_SIGNING_P12_B64" in workflow, "owner signing not removed")
    require('package/name="LuHm-OS Tablet Beta"' in workflow, "canonical Android beta launcher label")
    require("VERIFIED_FIRST_BETA" in (ROOT/"tools/provisionOwnerBetaSigner.sh").read_text(), "historic signer guard")
    require("SOURCE_OF_TRUTH" not in source or "sourceLogo" in source, "no synthesized secret")
    require("plugins/luhm-os/assets/logo.svg" in source, "mirrored artwork audit")
    require("data-luhm-studio-bridge" in html and 'data-luhm-studio-mode="samsungCore"' in html, "Samsung mode present")
    require('data-luhm-studio-mode="blenderGarage"' in html, "Blender mode present")
    require("samsungStudioSwitch.css" in html and "samsungStudioSwitch.js" in html, "UI assets loaded")
    require("LuHm-OS | Samsung Studio" in html, "identity case")
    require("Crown: STOP" in html or "Crown: STOP".lower() in html.lower(), "Crown status visible")
    require("window.LuHmNative" not in js and "fetch(" not in js and "XMLHttpRequest" not in js, "no privileged web runner")
    require("data-luhm-studio-mode" in js and 'aria-pressed' in js and 'event.key==="Escape"' in js, "accessible role switch")
    require("min-height:44px" in css and "prefers-reduced-motion" in css, "touch / reduced motion")
    require("https://" not in html[html.find('data-luhm-studio-bridge'):html.find('data-luhm-system-layer')], "no active external studio link")
    for path in (ICON_SCRIPT, ROOT/"frontEnd/samsungStudioSwitch.js", ROOT/"frontEnd/samsungStudioSwitch.css"):
        require(path.is_file() and path.stat().st_size>100, "new source exists:"+path.name)
    require(json.loads((ROOT/"doctrine/androidBetaReleaseBaselineV1.json").read_text())["status"] == "UNVERIFIED", "no fabricated signer baseline")
    print("GREEN_SAMSUNG_STUDIO_OFFLINE_BRIDGE_AND_SOURCE_SCOPE")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inspect-icon-output", action="store_true")
    args = p.parse_args()
    inspect_source()
    if args.inspect_icon_output:
        inspect_output(ROOT/"build/signed-beta/icons", PRESET)
        return
    # Use a temporary copy of the Android preset: real default package and keys are untouched.
    (ROOT/"build").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="samsung-cathedral-icons-test-",dir=ROOT/"build") as tmp:
        d = Path(tmp)
        pth = d/"export_presets.cfg"
        shutil.copyfile(PRESET,pth)
        subprocess.run([sys.executable,str(ICON_SCRIPT),"--output",str(d/"icons"),"--preset",str(pth)],check=True,timeout=75)
        inspect_output(d/"icons",pth)
        spec = importlib.util.spec_from_file_location("samsung_icons_test", ICON_SCRIPT)
        require(spec is not None and spec.loader is not None, "icon module loader")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            module.stage_preset(pth,d/"icons")
        except ValueError:
            pass
        else:
            raise AssertionError("RED_DUPLICATE_ICON_STAGE_ACCEPTED")
    print("GREEN_SAMSUNG_CATHEDRAL_SOURCE_AND_ICON_SELFTEST_NO_APK_PROOF")

if __name__ == "__main__":
    main()
