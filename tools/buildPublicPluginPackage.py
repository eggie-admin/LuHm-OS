#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "luhm-os"
MEMBERS = [
    "plugin.json",
    "mcp.json",
    "skills/luhm-agent-workflow/SKILL.md",
    "assets/logo.svg",
]
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-ref", required=True)
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()

    actual = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != args.source_ref:
        raise SystemExit(f"SOURCE_DRIFT expected={args.source_ref} actual={actual}")

    if len(args.source_ref) != 40 or any(c not in "0123456789abcdef" for c in args.source_ref):
        raise SystemExit("source-ref must be a lowercase 40-character git SHA")

    manifest = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    short = args.source_ref[:8]

    for member in MEMBERS:
        path = PLUGIN / member
        if not path.is_file():
            raise SystemExit(f"missing package member: {member}")

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / f"LuHm-OS-plugin-{version}-{short}.zip"

    with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for member in sorted(MEMBERS):
            data = (PLUGIN / member).read_bytes()
            info = zipfile.ZipInfo(member, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)

    receipt = {
        "schema": "luhmOs.publicPluginPackageBuildReceipt.v1",
        "status": "BUILT_BY_CAST_SCOPE",
        "sourceRef": args.source_ref,
        "buildScope": "publicPluginPackage",
        "artifact": {
            "filename": artifact.name,
            "sha256": sha256(artifact),
            "bytes": artifact.stat().st_size,
        },
        "members": sorted(MEMBERS),
        "publicationAuthority": False,
        "releaseAuthority": False,
        "crownAuthority": False,
    }
    receipt_path = out_dir / "publicPluginPackageBuildReceipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print("PUBLIC_PLUGIN_PACKAGE=BUILT")
    print(f"sourceRef={args.source_ref}")
    print(f"artifact={artifact}")
    print(f"sha256={receipt['artifact']['sha256']}")
    print("publicationAuthority=false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
