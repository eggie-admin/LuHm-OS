#!/usr/bin/env python3
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
errors = []

def need(ok, msg):
    if not ok:
        errors.append(msg)

wrapperPath = root / "tools/smX400OneBashInstall.sh"
sealPath = root / "doctrine/smX400OneBashInstallSealV1.json"
installerPath = root / "tools/termuxVirginInstall.sh"
contractPath = root / "doctrine/rootedTermuxGitHubReleaseInstallV1.json"

for path in (wrapperPath, sealPath, installerPath, contractPath):
    need(path.is_file(), f"missing {path.relative_to(root)}")

if not errors:
    wrapper = wrapperPath.read_text()
    installer = installerPath.read_text()
    seal = json.loads(sealPath.read_text())
    contract = json.loads(contractPath.read_text())

    need(seal.get("status") == "greenInstallBundleReadyDeviceProofPending", "seal status drift")
    need(seal.get("authority") == "Professor", "authority drift")
    need(seal.get("crownStatus") == "stop", "crown must remain stop")
    need(contract.get("status") == "greenReleaseArtifactReadyDeviceProofPending", "install contract status drift")
    release = seal.get("release", {})
    need(release.get("tag") == "android-web3-b25cfad1-r37000025238", "tag drift")
    need(release.get("apkSha256") == "2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8", "apk digest drift")
    need(release.get("productionSigned") is False, "must remain testing signer")
    for token in (
        'sourceRef="b25cfad18051ba2799b19e27f035487366b256c9"',
        'releaseTag="android-web3-b25cfad1-r37000025238"',
        'expectedApkSha256="2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8"',
        'releaseSha="$(awk',
        'pinned release checksum drift',
        'raw.githubusercontent.com/$repoName/$sourceRef/tools/termuxVirginInstall.sh',
        'exec bash "$installerPath" "$releaseTag" "$apkName" "$shaName"',
    ):
        need(token in wrapper, f"wrapper missing {token}")
    need(wrapper.index('releaseSha="$(awk') < wrapper.index('exec bash "$installerPath"'), "digest pin must precede installer execution")
    need(not re.search(r"(?m)^[A-Z][A-Z0-9_]*=", wrapper), "new wrapper contains non-camelHump internal variable")
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
        need(token in installer, f"legacy virgin installer missing compatibility token {token}")

print(json.dumps({
    "schema": "luhmOs.smX400OneBashInstallAudit.v1",
    "status": "greenSmX400OneBashInstall" if not errors else "redSmX400OneBashInstall",
    "errors": errors,
    "deviceProof": False,
    "crownStatus": "stop"
}, indent=2))
raise SystemExit(1 if errors else 0)
