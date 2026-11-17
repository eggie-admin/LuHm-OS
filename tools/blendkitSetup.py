#!/usr/bin/env python3
"""Install a pinned official Blendkit (formerly BlenderKit) add-on in this user's Blender.

No account login, asset scraping, publishing, background worker, or live provider entitlement.
Installs into Blender's reported per-user add-ons directory, not the repository.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

VERSION = "v3.21.5.261103"
ZIP_NAME = "blenderkit-v3.21.5.261103.zip"
DOWNLOAD_URL = "https://github.com/BlenderKit/Blendkit/releases/download/" + VERSION + "/" + ZIP_NAME
SHA256 = "58c437d20fc079f111a7c71a6fdc4c055e4459e1a4fb770e3446d7263c6ebc58"
SIZE_BYTES = 32628967
RECEIPT_NAME = "luhmBlendkitInstallReceipt.json"
ENABLED_MARKER = "LUHM_BLENDKIT_REGISTERED_AND_ENABLED"


def run_blender(expression: str, timeout: int = 120) -> str:
    result = subprocess.run(
        ["blender", "--background", "--python-expr", expression],
        capture_output=True, text=True, timeout=timeout, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    if result.returncode:
        raise RuntimeError(f"Blender exited {result.returncode}: {output[-2600:]}")
    return output


def user_addons_dir() -> Path:
    output = run_blender(
        "import bpy; print('LUHM_ADDONS_DIR=' + bpy.utils.user_resource('SCRIPTS', path='addons', create=True))",
        timeout=60,
    )
    matches = [line.partition("LUHM_ADDONS_DIR=")[2].strip()
               for line in output.splitlines() if "LUHM_ADDONS_DIR=" in line]
    if len(matches) != 1 or not matches[0]:
        raise RuntimeError("Could not obtain Blender's actual user add-ons folder")
    path = Path(matches[0]).expanduser().resolve()
    if not path.is_relative_to(Path.home().resolve()):
        raise RuntimeError(f"Refusing to install outside user home: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def receipt_matches(target: Path, receipt: Path) -> bool:
    if not target.is_dir() or not (target / "__init__.py").is_file() or not receipt.is_file():
        return False
    try:
        data = json.loads(receipt.read_text())
        return data.get("version") == VERSION and data.get("sha256") == SHA256
    except (OSError, ValueError):
        return False


def download_verified(target_zip: Path) -> None:
    request = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "LuHmOS-BlenderKit-Installer/1.0"})
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=75) as response, target_zip.open("wb") as out:
        while True:
            data = response.read(1024 * 1024)
            if not data:
                break
            size += len(data)
            if size > 45_000_000:
                raise RuntimeError("Blendkit archive exceeded approved download size")
            digest.update(data)
            out.write(data)
    if size != SIZE_BYTES or digest.hexdigest() != SHA256:
        raise RuntimeError(f"Official archive size/hash mismatch: size={size} sha256={digest.hexdigest()}")
    print(f"GREEN_BLENDKIT_ARCHIVE_SHA256 {SHA256}")


def unpack_checked(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        if len(members) > 10000:
            raise RuntimeError("Unexpected number of archive entries")
        total = sum(i.file_size for i in members)
        if total > 450_000_000:
            raise RuntimeError("Archive uncompressed size exceeds limit")
        files = {}
        for item in members:
            raw = item.filename
            path = PurePosixPath(raw)
            if not raw or "\\" in raw or path.is_absolute() or ".." in path.parts:
                raise RuntimeError(f"Unsafe ZIP path: {raw!r}")
            if stat.S_IFMT(item.external_attr >> 16) == stat.S_IFLNK:
                raise RuntimeError("ZIP contains a symbolic link")
            if item.is_dir():
                continue
            files[path] = item
        prefixes = sorted(
            (path.parent for path in files if path.name == "__init__.py"
             and (path.parent.name == "blenderkit" or len(path.parts) == 1)),
            key=lambda p: len(p.parts),
        )
        if not prefixes:
            raise RuntimeError("No BlenderKit Python package root in official release archive")
        prefix = prefixes[0]
        destination.mkdir(parents=True, exist_ok=True)
        count = 0
        for path, info in files.items():
            if prefix != PurePosixPath("."):
                if path.parts[:len(prefix.parts)] != prefix.parts:
                    continue
                relative = PurePosixPath(*path.parts[len(prefix.parts):])
            else:
                relative = path
            if not relative.parts:
                continue
            out = destination.joinpath(*relative.parts)
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as reader, out.open("wb") as writer:
                shutil.copyfileobj(reader, writer)
            count += 1
        if count < 10 or not (destination / "__init__.py").is_file():
            raise RuntimeError("Extracted add-on lacks expected Python module layout")
        print(f"GREEN_BLENDKIT_PACKAGE_STRUCTURE {count}_files")


def enable_and_check() -> None:
    expression = (
        "import addon_utils, bpy; "
        "addon_utils.modules_refresh(); "
        "addon_utils.enable('blenderkit', default_set=True, persistent=True); "
        "assert addon_utils.check('blenderkit')[1], 'blenderkit not enabled'; "
        "bpy.ops.wm.save_userpref(); "
        f"print('{ENABLED_MARKER}', bpy.app.version_string)"
    )
    output = run_blender(expression, timeout=120)
    if ENABLED_MARKER not in output:
        raise RuntimeError("Blender did not confirm registered and enabled add-on")
    print(next(line.strip() for line in output.splitlines() if ENABLED_MARKER in line))


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"install", "verify"}:
        print("Usage: python3 tools/blendkitSetup.py [install|verify]", file=sys.stderr)
        return 2
    folder = user_addons_dir()
    target = folder / "blenderkit"
    receipt = folder / RECEIPT_NAME
    mode = sys.argv[1]
    if mode == "install" and not receipt_matches(target, receipt):
        if target.exists():
            raise RuntimeError("Existing unmanaged BlenderKit install; refusing to overwrite it")
        with tempfile.TemporaryDirectory(prefix="luhm-blendkit-") as temporary:
            work = Path(temporary)
            archive = work / ZIP_NAME
            staged = work / "blenderkit"
            download_verified(archive)
            unpack_checked(archive, staged)
            shutil.move(str(staged), str(target))
        receipt.write_text(json.dumps({
            "version": VERSION, "sha256": SHA256,
            "source": DOWNLOAD_URL, "kind": "perUserBlenderAddon",
            "rights": "GPL add-on; individual Blendkit marketplace assets have their own terms",
        }, indent=2) + "\n")
    if not receipt_matches(target, receipt):
        raise RuntimeError("No hash-pinned Blendkit installation receipt and module found")
    enable_and_check()
    print("GREEN_BLENDKIT_WORKSPACE_ADDON_PROOF; ASSET_SERVICE_AUTH_UNPROVEN")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        print(f"RED_BLENDKIT_SETUP: {exc}", file=sys.stderr)
        raise SystemExit(1)
