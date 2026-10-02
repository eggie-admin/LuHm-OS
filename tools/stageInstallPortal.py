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
    parser.add_argument("--android-contract", default="doctrine/androidCandidate.json")
    args = parser.parse_args()

    apk = Path(args.apk)
    out = Path(args.out)
    if not apk.is_file() or apk.stat().st_size == 0:
        raise SystemExit("APK missing or empty")

    meta = read_export_meta(Path(args.export_preset))
    contract = json.loads(Path(args.android_contract).read_text(encoding="utf-8"))
    if meta["packageName"] != contract["package"]:
        raise SystemExit(f"package drift: export={meta['packageName']} contract={contract['package']}")
    if meta["versionName"] != contract["versionName"]:
        raise SystemExit("versionName drift between export preset and Android contract")
    if meta["versionCode"] != contract["versionCode"]:
        raise SystemExit("versionCode drift between export preset and Android contract")
    if meta["targetSdk"] != contract["targetSdk"]:
        raise SystemExit("targetSdk drift between export preset and Android contract")

    apk_hash = sha256(apk)
    out_apk = out / "apk" / "current.apk"
    out_apk.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(apk, out_apk)
    shutil.copy2("installPortal/index.html", out / "index.html")

    template = Path("installPortal/manifest.template.json").read_text(encoding="utf-8")
    rendered = (
        template
        .replace("__PACKAGE_NAME__", meta["packageName"])
        .replace("__VERSION_NAME__", meta["versionName"])
        .replace("__VERSION_CODE__", str(meta["versionCode"]))
        .replace("__APK_SHA256__", apk_hash)
        .replace("__BUILD_COMMIT__", args.commit)
    )
    if "__" in rendered:
        raise SystemExit("unresolved install manifest placeholder")
    manifest = json.loads(rendered)
    if manifest["packageName"] != contract["package"]:
        raise SystemExit("rendered portal package does not match Android contract")
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
