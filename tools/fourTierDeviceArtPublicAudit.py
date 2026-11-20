#!/usr/bin/env python3
"""Source-only four-tier device, art rights and public inventory guard.
No private-file reads, network calls, builds, registration filings or deployment.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = "doctrine/fourTierDeviceArtPublicCanonV1.json"
SURFACE = "doctrine/publicSurfaceInventory20261104.json"

def read(root: Path, path: str):
    obj = json.loads((root / path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("object expected: " + path)
    return obj

def audit(spec: dict, public: dict, root: Path):
    failures = []
    def need(ok, label):
        if not ok: failures.append(label)
    need(spec.get("schema") == "luhmOs.fourTierDeviceArtPublicCanon.v1", "schema")
    need(spec.get("status") == "SOURCE_CANDIDATE_NOT_BUILT_OR_PUBLISHED", "not-built-claim")
    need(spec.get("promotion") is False and spec.get("crownStatus") == "STOP"
         and spec.get("publicationAuthority") is False and spec.get("signingAuthority") is False, "promotion")
    need(spec.get("distinctFrom") == "doctrine/fourTierOperatingModelV1.json", "tier-model-conflation")
    need([t.get("id") for t in spec.get("stages",[])] == 
         ["designToTesting","propose","data","final"], "four-tiers")
    need(all(t.get("promotion") is False for t in spec.get("stages",[])[:3]), "early-tier-promotion")
    need(spec.get("stages",[])[3].get("promotion") == "HUMAN_ONLY", "final-human")
    need(set(spec.get("platforms",{})) ==
         {"samsungAndroid","iphoneIos","raspberryPiLinux","windowsWsl","basementPrivateStudio"}, "five-platforms")
    need(spec["platforms"]["samsungAndroid"].get("pluginPath") ==
         "plugins/luhm-android-beta/plugin.json", "samsung-plugin")
    need(spec["platforms"]["iphoneIos"].get("hostBuild") ==
         "MACOS_XCODE_REQUIRED_FOR_GODOT_IOS_EXPORT", "no-mac-ios-build-claim")
    need(spec["platforms"]["raspberryPiLinux"].get("x11","").startswith("OPTIONAL"), "headless-x11")
    need(spec["platforms"]["raspberryPiLinux"].get("netplan","").startswith("ONLY_ON_UBUNTU"),
         "universal-netplan-assumption")
    boundary = spec.get("crossDeviceArchitecture", {})
    need(boundary.get("publicRepoRunnerPolicy") ==
         "NEVER_ATTACH_PERSISTENT_SELF_HOSTED_RUNNER_TO_PUBLIC_PR_WORKFLOWS", "public-runner-exposure")
    need(boundary.get("noPortForwarding") is True
         and boundary.get("noAutomaticCloudDeployment") is True, "lan-ingress")
    need(boundary.get("sql") == "PRIVATE_AND_BACKEND_ONLY", "sql-exposure")
    godot = spec.get("godotWeb", {})
    need("WebGL executes in client browser" in godot.get("remoteExecutionTruth",""), "server-side-webgl-false-claim")
    need(godot.get("runtimeWebgl") == "UNVERIFIED_THIS_AUDIT", "fake-webgl-green")
    art = spec.get("artCanon", {})
    need(art.get("generatedDraftPublicAllowed") is False
         and art.get("defaultPublicAllowed") is False, "art-public-bypass")
    need(art.get("privateUrdPack") == "PRIVATE_ONLY_UNAPPROVED_NOT_PUBLIC_RELEASE", "urd-public-bypass")
    need(art.get("copyrightRegistrationStatus") == "NO_EVIDENCE_OF_FILING_OR_REGISTRATION"
         and art.get("trademarkRegistrationStatus") == "NO_EVIDENCE_OF_FILING_OR_REGISTRATION",
         "fake-registration")
    need(art.get("sourceControlLicenseNotAutomaticallyArtLicense") is True, "code-art-license")
    need(art.get("underlyingThirdPartyCharacterRights","").startswith("NEEDS_INDEPENDENT"),
         "third-party-character-lineage")
    brand = spec.get("brands",{})
    need([brand.get(x) for x in ("publisher","product","studio","world")] ==
         ["Eggie Bagelface","LuHm-OS","PIRATE DADDIES FILM","Project Premonition"],
         "brand-canon")
    need(brand.get("registeredMarkClaim") is False, "trademark-claim")
    need(public.get("schema") == "luhmOs.publicSurfaceInventory20261104.v1", "public-inventory-schema")
    need(public.get("status") == "CONNECTED_ACCOUNT_METADATA_NOT_PUBLIC_HTTP_CRAWL", "live-audit-overclaim")
    gh = public.get("github",{})
    repos = gh.get("repositories",[])
    need(len(repos) == gh.get("visiblePublicRepositoryCount") == 19, "repo-inventory")
    need(len({x.get("url") for x in repos}) == 19, "repo-duplicates")
    need(all(x.get("url","").startswith("https://github.com/eggie-admin/") for x in repos),
         "repo-origin")
    need(gh.get("notAllOriginalCreativeWork") is True, "fork-originality")
    render = public.get("render",{})
    services = render.get("services",[])
    need(len(services) == render.get("configuredServiceCount") == 9, "render-inventory")
    need(render.get("livePublicHttpAndContent") == "NOT_CHECKED", "render-live-overclaim")
    need(all(x.get("visibility") == "CONFIGURED_EXTERNAL_ORIGIN_NOT_HTTP_PROVEN"
             for x in services), "render-content-proof")
    need(public.get("chatGptSites",{}).get("status","").startswith("PRIVATE_VS_PUBLIC_PERMISSION_NOT_VERIFIED"),
         "private-site-leak")
    need(public.get("publicArt",{}).get("status") == "NO_BLANKET_APPROVAL", "blanket-art-claim")
    need(public.get("automaticPublishing") is False and public.get("crownStatus") == "STOP",
         "public-release-authority")
    require_files = [
        "plugins/luhm-android-beta/plugin.json",
        "androidWeb3Plugin/plugin/src/main/AndroidManifest.xml",
        "manual/professor-ubuntu2604-basement.md",
        "project.godot",
        "tools/buildGodotWebHarness.sh",
        "game/canon/CHARACTER_CANON_V1.json",
        "doctrine/brandCanonV1.json",
        "doctrine/characterCanonRegistryV1.json",
        "media/public-release-art-ledger.json",
        "doctrine/artistCreditLedgerV1.json",
        "doctrine/assetEligibilityMatrixV1.json",
        "doctrine/fourTierOperatingModelV1.json",
    ]
    need(all((root / f).is_file() for f in require_files), "existing-source-missing")
    original_ledger = read(root,"media/public-release-art-ledger.json")
    need(original_ledger.get("generatedDraftPublicAllowed") is False
         and original_ledger.get("publicationAuthority") is False, "actual-art-ledger-bypass")
    need(all(original_ledger.get("characters",{}).get(c) for c in
             ("lum","urd","belldandy","skuld")), "four-character-canon")
    return failures

def main():
    s=read(ROOT,SPEC)
    p=read(ROOT,SURFACE)
    failures=audit(s,p,ROOT)
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    result={
        "schema":"luhmOs.fourTierDeviceArtPublicAudit.v1",
        "sourceRef":sha,
        "status":"RED_SOURCE" if failures else "GREEN_SOURCE_ONLY_EXTERNAL_AMBER",
        "errors":failures,
        "platformLiveProof":False,
        "deviceAppsBuilt":False,
        "approvedArtPublished":False,
        "copyrightOrTrademarkFiled":False,
        "privateBasementRunnerConnected":False,
        "publicLiveLinksHttpValidated":False,
        "crownStatus":"STOP",
    }
    out=ROOT / "build/four-tier-device-art/evidence.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 1 if failures else 0
if __name__=="__main__":
    raise SystemExit(main())
