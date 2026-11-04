#!/usr/bin/env python3
"""Reproducible UNSIGNED Firefox Antenna package; Mozilla signs the XPI separately.

AMO JWT API credentials or TLS keys are never read by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REL = Path("plugins/luhm-firefox-antenna")
FILES = ("manifest.json", "popup.html", "popup.css", "popup.js")
MAX_BYTES = 100_000_000
ADDON_ID = "luhm-antenna@eggiebagelface.art"
SOURCE_RE = re.compile(r"^[a-f0-9]{40}$")


def fetch_head(root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True, timeout=5,
    )
    ref = proc.stdout.strip().lower()
    if not SOURCE_RE.fullmatch(ref):
        raise ValueError("SOURCE_SHA_UNVERIFIED")
    return ref


def inspect_package_source(root: Path) -> tuple[dict, dict[str, bytes]]:
    parent = root / "plugins"
    src = root / REL
    if parent.is_symlink() or src.is_symlink():
        raise ValueError("SOURCE_SYMLINK_FORBIDDEN")
    known = set(FILES)
    actual = {p.name for p in src.iterdir() if p.is_file() or p.is_symlink()}
    if actual != known:
        raise ValueError("UNREVIEWED_EXTENSION_FILE_SET")
    contents = {}
    for name in FILES:
        target = src / name
        if target.is_symlink() or not target.is_file():
            raise ValueError("SOURCE_FILE_UNSAFE")
        contents[name] = target.read_bytes()
        if not contents[name] or len(contents[name]) > 1_000_000:
            raise ValueError("SOURCE_FILE_TOO_LARGE")
    if sum(map(len, contents.values())) > MAX_BYTES:
        raise ValueError("SHELL_BUDGET_EXCEEDED")
    manifest = json.loads(contents["manifest.json"])
    gecko = manifest.get("browser_specific_settings", {}).get("gecko", {})
    if (manifest.get("manifest_version") != 3
            or manifest.get("version") != "0.1.0"
            or gecko.get("id") != ADDON_ID
            or gecko.get("data_collection_permissions") != {"required": ["none"]}
            or manifest.get("host_permissions") != ["http://127.0.0.1:8765/*"]
            or manifest.get("permissions") != []
            or manifest.get("action", {}).get("default_popup") != "popup.html"
            or "background" in manifest or "content_scripts" in manifest
            or "update_url" in gecko):
        raise ValueError("AMO_PACKAGE_POLICY_DRIFT")
    csp = manifest.get("content_security_policy", {}).get("extension_pages", "")
    if "script-src 'self'" not in csp or "object-src 'none'" not in csp:
        raise ValueError("UNSAFE_EXTENSION_CSP")
    js = contents["popup.js"].decode("utf-8")
    if any(token in js for token in ("eval(", "innerHTML", "new Function(", "document.write(")):
        raise ValueError("DYNAMIC_EXECUTION_FORBIDDEN")
    if 'http://127.0.0.1:8765/antenna/v1/status' not in js:
        raise ValueError("LOCAL_ANTENNA_ROUTE_DRIFT")
    return manifest, contents


def build_source_zip(root: Path, source_ref: str) -> tuple[bytes, dict]:
    if not SOURCE_RE.fullmatch(source_ref):
        raise ValueError("INVALID_SOURCE_SHA")
    manifest, files = inspect_package_source(root)
    out = io.BytesIO()
    with zipfile.ZipFile(out, mode="w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9, strict_timestamps=True) as z:
        for name in FILES:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name], compress_type=zipfile.ZIP_DEFLATED,
                       compresslevel=9)
    data = out.getvalue()
    receipt = {
        "schema": "luhmOs.firefoxAntennaSigningPreflight.v1",
        "sourceRef": source_ref,
        "extensionId": ADDON_ID,
        "version": manifest["version"],
        "packageFilename": "luhm-firefox-antenna-0.1.0-unsigned.zip",
        "packageSha256": hashlib.sha256(data).hexdigest(),
        "packageBytes": len(data),
        "uncompressedShellBytes": sum(map(len, files.values())),
        "includedFiles": list(FILES),
        "dataCollection": "none",
        "certificateType": "NOT_APPLICABLE_UNSIGNED_ARCHIVE",
        "mozillaSignaturePresent": False,
        "amoSubmissionPerformed": False,
        "browserRuntimeProven": False,
        "installerRan": False,
        "noPrivateKeyAccess": True,
        "distribution": "UNLISTED_RECOMMENDED_REQUIRES_MOZILLA_SIGNING",
        "verdict": "PACKAGE_SOURCE_READY_NOT_SIGNED",
        "crownStatus": "STOP",
    }
    return data, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/firefoxAntennaSigning")
    parser.add_argument("--expected-source-ref")
    args = parser.parse_args()
    head = fetch_head(ROOT)
    if args.expected_source_ref and head != args.expected_source_ref.lower():
        parser.error("exact-source mismatch; refusing to package")
    data, receipt = build_source_zip(ROOT, head)
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / receipt["packageFilename"]).write_bytes(data)
    (output / "signing-preflight.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
