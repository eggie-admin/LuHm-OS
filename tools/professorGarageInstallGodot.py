#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_VERSION = os.environ.get("PROFESSOR_GARAGE_GODOT_VERSION", "4.7.2-stable")
REPO = "godotengine/godot-builds"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def gh_release(tag):
    proc = subprocess.run(
        ["gh", "api", f"repos/{REPO}/releases/tags/{tag}"],
        check=True, capture_output=True, text=True
    )
    return json.loads(proc.stdout)

def select_linux_asset(release):
    assets = release.get("assets", [])
    candidates = []
    for asset in assets:
        name = asset.get("name", "")
        low = name.lower()
        if low.endswith("linux.x86_64.zip") and "mono" not in low:
            candidates.append(asset)
    if len(candidates) != 1:
        names = [a.get("name") for a in candidates]
        raise SystemExit(f"expected one non-Mono linux.x86_64 zip, found {len(candidates)}: {names}")
    return candidates[0]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", default=DEFAULT_VERSION)
    p.add_argument("--install-root", default=str(Path.home() / ".local" / "opt" / "godot"))
    args = p.parse_args()

    if not shutil.which("gh"):
        raise SystemExit("gh is required")
    if not shutil.which("unzip"):
        raise SystemExit("unzip is required")

    release = gh_release(args.version)
    asset = select_linux_asset(release)
    install_root = Path(args.install_root).expanduser().resolve()
    target_dir = install_root / args.version
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="professor-garage-godot-") as td:
        archive = Path(td) / asset["name"]
        urllib.request.urlretrieve(asset["browser_download_url"], archive)
        digest = sha256(archive)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target_dir)

    executables = [p for p in target_dir.iterdir() if p.is_file() and p.name.startswith("Godot") and "console" not in p.name.lower()]
    if len(executables) != 1:
        raise SystemExit(f"unable to identify exact Godot executable in {target_dir}")
    executable = executables[0]
    executable.chmod(executable.stat().st_mode | 0o111)

    link = bin_dir / "godot"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(executable)

    receipt = {
        "schema": "luhmOs.professorGarageGodotInstallReceipt.v1",
        "version": args.version,
        "releaseUrl": release.get("html_url"),
        "assetName": asset.get("name"),
        "assetSha256": digest,
        "installedExecutable": str(executable),
        "symlink": str(link),
        "crownAuthority": False,
        "providerEntitlementProof": False
    }
    receipt_path = target_dir / "install-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
