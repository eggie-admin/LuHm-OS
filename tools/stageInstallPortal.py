#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def read_export_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    def grab(pattern: str, cast=str):
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            raise SystemExit(f"missing export metadata: {pattern}")
        return cast(match.group(1))

    return {
        "packageName": grab(r'^package/unique_name="([^"]+)"$'),
        "versionName": grab(r'^version/name="([^"]+)"$'),
        "versionCode": grab(r'^version/code=(\d+)$', int),
        "targetSdk": grab(r'^gradle_build/target_sdk="?(\d+)"?$', int),
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--export-preset", default="export_presets.cfg")
    args = parser.parse_args()

    apk = Path(args.apk)
    out = Path(args.out)
    if not apk.is_file() or apk.stat().st_size == 0:
        raise SystemExit(f"APK missing or empty: {apk}")

    meta = read_export_meta(Path(args.export_preset))
    package_name = meta["packageName"]
    if not package_name.startswith("art.eggiebagelface.luhmos."):
        raise SystemExit(f"unexpected package namespace: {package_name}")
    if meta["targetSdk"] != 36:
        raise SystemExit(f"unexpected target SDK: {meta['targetSdk']}")

    apk_hash = sha256(apk)
    out_apk = out / "apk" / "current.apk"
    out_apk.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(apk, out_apk)
    shutil.copy2("installPortal/index.html", out / "index.html")

    template = Path("installPortal/manifest.template.json").read_text(encoding="utf-8")
    rendered = (
        template
        .replace("__PACKAGE_NAME__", package_name)
        .replace("__VERSION_NAME__", meta["versionName"])
        .replace("__VERSION_CODE__", str(meta["versionCode"]))
        .replace("__APK_SHA256__", apk_hash)
        .replace("__BUILD_COMMIT__", args.commit)
    )
    if "__" in rendered:
        raise SystemExit("unresolved install manifest placeholder")
    manifest = json.loads(rendered)
    if manifest["packageName"] != package_name:
        raise SystemExit("rendered package identity mismatch")
    if manifest["targetSdk"] != meta["targetSdk"]:
        raise SystemExit("rendered target SDK mismatch")
    if manifest["apkSha256"] != sha256(out_apk):
        raise SystemExit("copied APK hash mismatch")

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out / "SHA256SUMS.txt").write_text(
        f"{manifest['apkSha256']}  apk/current.apk\n",
        encoding="utf-8",
    )
    (out / "README-FIRST.txt").write_text(
        "Serve this directory as the document root for get.lum.eggiebagelface.lan.\n"
        "DNS, TLS, Apache activation, F-Droid signing and release promotion are separate Professor gates.\n",
        encoding="utf-8",
    )

    print("LUHM INSTALL PORTAL BUNDLE GREEN")
    print(json.dumps({
        "fqdn": manifest["fqdn"],
        "package": manifest["packageName"],
        "version": manifest["versionName"],
        "apkSha256": manifest["apkSha256"],
        "fdroidReady": manifest["fdroidReady"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
