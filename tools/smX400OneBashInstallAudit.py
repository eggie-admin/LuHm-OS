#!/usr/bin/env python3
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []

def need(ok, msg):
    if not ok:
        errors.append(msg)

wrapper_path = root / "tools/smX400OneBashInstall.sh"
seal_path = root / "doctrine/smX400OneBashInstallSealV1.json"
installer_path = root / "tools/termuxVirginInstall.sh"

for p in (wrapper_path, seal_path, installer_path):
    need(p.is_file(), f"missing {p.relative_to(root)}")

if not errors:
    wrapper = wrapper_path.read_text()
    installer = installer_path.read_text()
    seal = json.loads(seal_path.read_text())

    need(seal.get("status") == "GREEN_INSTALL_BUNDLE_READY_DEVICE_PROOF_PENDING", "seal status drift")
    need(seal.get("authority") == "Professor", "authority drift")
    need(seal.get("crownStatus") == "stop", "crown must remain stop")
    rel = seal.get("release", {})
    need(rel.get("tag") == "android-web3-b25cfad1-r37000025238", "tag drift")
    need(rel.get("apkSha256") == "2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8", "apk digest drift")
    need(rel.get("productionSigned") is False, "must remain testing signer")
    for token in (
        'SOURCE_REF="b25cfad18051ba2799b19e27f035487366b256c9"',
        'TAG="android-web3-b25cfad1-r37000025238"',
        'EXPECTED_APK_SHA256="2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8"',
        'RELEASE_SHA="$(awk',
        'pinned release checksum drift',
        'raw.githubusercontent.com/$REPO/$SOURCE_REF/tools/termuxVirginInstall.sh',
        'exec bash "$INSTALLER" "$TAG" "$APK_NAME" "$SHA_NAME"',
    ):
        need(token in wrapper, f"wrapper missing {token}")
    need(wrapper.index('RELEASE_SHA="$(awk') < wrapper.index('exec bash "$INSTALLER"'), "digest pin must precede installer execution")
    for token in (
        '[ "$MODEL" = "SM-X400" ]',
        '[ "$ANDROID" = "16" ]',
        '[ "$ABI" = "arm64-v8a" ]',
        'sha256sum -c "$SHA_NAME"',
        'su -c id',
        'pm install -t',
        'cmd package resolve-activity --brief',
        'LUHM_VIRGIN_INSTALL=GREEN',
    ):
        need(token in installer, f"virgin installer missing {token}")

print(json.dumps({
    "schema": "luhmOs.smX400OneBashInstallAudit.v1",
    "status": "GREEN_SM_X400_ONE_BASH_INSTALL" if not errors else "RED_SM_X400_ONE_BASH_INSTALL",
    "errors": errors,
    "deviceProof": False,
    "crownStatus": "stop"
}, indent=2))
raise SystemExit(1 if errors else 0)
