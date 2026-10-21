#!/usr/bin/env python3
"""Fast-path Samsung source-only APK gate.

Only checks the exact checked-out source. No provider, phone, signing key,
Google Drive, DNS, or F-Droid account access. Never claims a built APK.
"""
from __future__ import annotations
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "art.eggiebagelface.luhmos.beta"

def audit(workflow: str, preset: str, avatar: str, private_assets: list[str]) -> list[str]:
    bad = []
    def need(ok: bool, key: str) -> None:
        if not ok: bad.append(key)
    need("workflow_dispatch:" in workflow and "inputs.sourceRef" in workflow,
         "exactManualSource")
    need('== "cast"' in workflow, "ownerCast")
    need('GITHUB_ACTOR' in workflow and "branches/main" in workflow,
         "ownerAndExactMain")
    need("LUHM_BETA_SIGNING_P12_B64" in workflow and
         "LUHM_BETA_SIGNER_SHA256" in workflow, "persistentOwnerSigner")
    need('"$OBSERVED" == "$TRUSTED_SIGNER"' in workflow, "independentCertificatePin")
    need("--export-release 'Android Proposed'" in workflow and
         "RED_DEBUG_CERTIFICATE_MODE" in workflow, "nonDebugApk")
    need(EXPECTED in workflow, "isolatedBetaApplicationId")
    need('targetSdkVersion:\'36\'' in workflow and
         "arm64-v8a" in workflow, "tabletSdkAbi")
    need("python3 tools/fdroidTabletSourceAudit.py" in workflow,
         "beforeBuildLocalAudit")
    need("Stage rigged Lum from Google Drive" not in workflow and
         "drive.usercontent.google.com" not in workflow and
         "drive.google.com/uc" not in workflow and
         "DRIVE_ID" not in workflow, "noDonorDownload")
    need("privatePrototype" not in workflow and "assetMode" not in workflow,
         "noPrivateBuildMode")
    need("assets/lum/luhm.glb" in workflow and
         "assets/lum/luhmRunning.glb" in workflow and
         not private_assets, "noDonorBundled")
    need("ResourceLoader.exists(ASSET_PATH)" in avatar and
         "_build_procedural_lum()" in avatar, "noAssetBootCrash")
    need('permissions/internet=false' in preset,
         "offlineCoreOnly")
    need('package/unique_name="art.eggiebagelface.luhmos.testing"' in preset,
         "preserveTestingPackageInCanonicalPreset")
    need("gh release create" not in workflow and
         "gh release upload" not in workflow, "noAutoPublish")
    need("fdroid update" not in workflow and
         "fdroid publish" not in workflow, "noImplicitFdroidPublish")
    need('\"deviceProof\":False' in workflow and
         '\"betaUpgradeProof\":False' in workflow and
         '\"publicPublished\":False' in workflow, "honestReceipts")
    return bad

def main() -> None:
    workflow=(ROOT/".github/workflows/samsung-lite-signed-beta.yml").read_text()
    preset=(ROOT/"export_presets.cfg").read_text()
    avatar=(ROOT/"scripts/game/lumAvatar.gd").read_text()
    donor=[str(x.relative_to(ROOT)) for name in
           ("assets/lum/luhm.glb","assets/lum/luhmRunning.glb")
           if (x:=ROOT/name).is_file()]
    errors=audit(workflow,preset,avatar,donor)
    if errors: raise SystemExit("RED_FDROID_TABLET_FASTPATH_"+",".join(errors))
    controls=[
      ("donorDownload",workflow+"\nStage rigged Lum from Google Drive"),
      ("fakePublishing",workflow+"\ngh release create"),
      ("fakePackage",workflow.replace(EXPECTED,"art.eggiebagelface.luhmos.testing")),
      ("missingPin",workflow.replace('"$OBSERVED" == "$TRUSTED_SIGNER"',"true")),
      ("missingSource",workflow.replace("branches/main","branches/develop")),
    ]
    for name,changed in controls:
        assert audit(changed,preset,avatar,donor), "NEGATIVE_FALSE_GREEN:"+name
    assert audit(workflow,preset,avatar,["assets/lum/luhm.glb"]),"privateDonorNotRejected"
    assert audit(workflow,preset,avatar.replace("_build_procedural_lum()",""),donor),"fallbackNotEnforced"
    print("GREEN_FDROID_TABLET_SOURCE_7_NEGATIVE_CONTROLS")
    print("SOURCE_ONLY: signed APK, F-Droid index, HTTPS hosting and tablet install unproven")

if __name__ == "__main__":
    main()
