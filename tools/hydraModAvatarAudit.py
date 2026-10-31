#!/usr/bin/env python3
"""Source-only adapter catalog and finite 500x500x500 coverage sampling; no media/engines/mod execution."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/hydraModAvatarMatrixV1.json"
SHA256=re.compile(r"^[a-f0-9]{64}$")
def sample_matrix(size=500):
    """500 evenly distributed *planned* triples, not 125 million executed tests."""
    if size!=500:raise ValueError("MATRIX_AXIS_SIZE")
    return tuple((i,(73*i+19)%size,(137*i+29)%size) for i in range(size))
def audit(p):
    errors=[]
    def gate(condition,name):
        if not condition:errors.append(name)
    gate(p.get("schema")=="luhmOs.hydraModAvatarMatrix.v1" and p.get("state")=="PROPOSED_SOURCE_ONLY","POLICY_SCHEMA")
    gate(p.get("canonicalRepo")=="eggie-admin/LuHm-OS" and p.get("authority")=="Professor" and p.get("crown")=="STOP","CANON_AUTHORITY")
    c=p.get("coverage",{}); axes=c.get("axes",[])
    gate(len(axes)==3 and [x.get("slots") for x in axes]==[500]*3,"MATRIX_AXES")
    samples=sample_matrix()
    gate(c.get("combinatorialSpace")==125000000 and c.get("deterministicSamples")==len(samples)==500 and
         all(len({v[j] for v in samples})==500 for j in range(3)),"MATRIX_UNIQUE_SAMPLE")
    gate(c.get("sampleExecutedAsHardwareTests") is False and c.get("sampleStatuses")=="PLANNED_NOT_EXECUTED","FAKE_TEST_PASS")
    s=p.get("stack",{})
    gate(s.get("unreal")=="FINAL_TARGET_UNVERIFIED_LICENSE_HOLD" and s.get("godot")=="CURRENT_PLAYABLE_SPINE" and
         s.get("unity")=="OPTIONAL_ADAPTER_NOT_INSTALLED" and s.get("web")=="EXISTING_BABYLON_GLASS_WORLD","ENGINE_DRIFT")
    pc=p.get("pythonCandidates",[])
    gate(len(pc)==8 and len({x.get("id") for x in pc})==8 and all(x.get("status")=="OPTIONAL_RESEARCH" for x in pc),"UNAPPROVED_PYTHON_INSTALL")
    nexus=p.get("nexus",{})
    gate(nexus.get("api")=="NEXUS_MODS_API_V3_METADATA_ONLY" and nexus.get("vortex")=="CURRENT_VORTEX_REPO_SCOPED_PACKAGE","OUTDATED_NEXUS_API")
    gate(nexus.get("adultContentCatalog")=="OPT_IN_ADULT_ONLY" and nexus.get("userVerifiedAdult") is False,"ADULT_AGE_GATE")
    for key in ("archivedVortexApiRepoUse","personalApiKeyInCi","autoBrowseAdult","autoDownloadMods","redistributeMods",
                "repurposeGameAssets","runThirdPartyInstallers","apiCredentialsConfigured"):
        gate(nexus.get(key) is False,"NEXUS_BOUNDARY_"+key)
    for key in ("requirePerModAuthorRights","creditIsNotPermission"):
        gate(nexus.get(key) is True,"MOD_AUTHOR_RIGHTS_"+key)
    ups=nexus.get("upstreams",[])
    gate(len(ups)==6 and len({v.get("id") for v in ups})==6 and
         all(str(v.get("url","")).startswith("https://") and v.get("licenseState") for v in ups),"MOD_UPSTREAM_REGISTRY")
    a=p.get("avatar",{})
    gate(a.get("id")=="originalAdultGothAvatar" and a.get("ageClassification")=="ADULT_ORIGINAL_CHARACTER_ONLY","AVATAR_IDENTITY")
    gate(len(a.get("topologyLoops",[]))>=10 and len(a.get("deformationTests",[]))>=10 and
         len(a.get("requiredMorphTargets",[]))>=6 and a.get("weightedBoneLimitPerVertex")==4,"AVATAR_DEFORMATION_CRITERIA")
    gate(a.get("desktopTriangleBudget")==120000 and a.get("mobileTriangleBudget")==20000,"AVATAR_LOD_BUDGET")
    for key in ("assetRightsApproved","modelSha256Verified","actualBlenderMeshInspected","automaticRetopologyPassIsFinal",
                "secondaryMotionReviewed","liveMocapProven","allowPrivateFaceDataToCloud"):
        gate(a.get(key) is False,"FALSE_AVATAR_PROOF_"+key)
    w=p.get("web",{})
    gate(w.get("renderer")=="existingBabylonGlassWorld" and w.get("skyboxFormat")=="localEnvOrHdr" and
         w.get("assetPathPrefix")=="assets/skyboxes/" and w.get("maxSkyboxBytes")==16777216,"SKYBOX_CONTRACT")
    for key in ("additionalRendererAllowed","hdrAssetReady","skyboxRightsApproved","allowRemoteUntrustedTextureUrls",
                "allowPublicCdnsByDefault","thirdPartyMeshImportAllowed"):
        gate(w.get(key) is False,"WEB_UNSAFE_"+key)
    for key in ("requireRelativeAssetPath","enablePbr","enableTonalMapping","explicitGammaColorSpace",
                "accessibilityReducedMotion","depthCorrectOcclusionRequired"):
        gate(w.get(key) is True,"WEB_REQUIRE_"+key)
    gate(w.get("sceneRuntimeEvidence")=="UNVERIFIED","FALSE_WEB_PROOF")
    sec=p.get("security",{})
    for key in ("autoInstallPackages","runUntrustedPython","evalRemoteJavaScript","autoPublish","autoMerge",
                "autoDeploy","cloudProviderCalls","sideLoadUnverifiedMods","quarantineResumed","licenseReviewComplete"):
        gate(sec.get(key) is False,"UNSAFE_PRIVILEGE_"+key)
    gate(type(sec.get("autoSpendUsd")) is int and sec.get("autoSpendUsd")==0,"SPEND_GATE")
    return sorted(set(errors))
def inspect_mod(record):
    """Independently check a user-supplied *metadata-only* mod reference; never fetch it."""
    if not isinstance(record,dict) or record.get("schema")!="luhmOs.externalModReference.v1":
        return "REJECT_INVALID_RECORD"
    if record.get("audience")=="adult" and record.get("adultVerified") is not True:return "HOLD_ADULT_AGE_GATE"
    if record.get("source") not in ("nexus","github"):return "REJECT_UNKNOWN_SOURCE"
    if record.get("downloadRequested") is True or record.get("execRequested") is True:return "REJECT_AUTOMATIC_EXECUTION"
    if record.get("game") not in ("residentEvil","fallout4","other"):return "REJECT_GAME_ID"
    if record.get("authorPermissionForHydraReuse") is not True or record.get("gamePublisherRightsCleared") is not True:
        return "HOLD_REUSE_RIGHTS"
    if not SHA256.fullmatch(str(record.get("sha256",""))):return "HOLD_UNVERIFIED_HASH"
    return "REVIEW_ORIGINAL_AND_LICENSES_MANUALLY"
def inspect_avatar(record):
    """Only pass supplied measured author-approved topology evidence, never certify from doctrine."""
    if not isinstance(record,dict) or record.get("schema")!="luhmOs.measuredAvatarReport.v1":
        return "NO_MEASURED_AVATAR_REPORT"
    if record.get("adultOriginalCharacter") is not True:return "HOLD_CHARACTER_RIGHTS"
    if record.get("assetRightsCleared") is not True:return "HOLD_CHARACTER_RIGHTS"
    if not SHA256.fullmatch(str(record.get("sha256",""))):return "HOLD_MESH_HASH"
    if record.get("measuredInBlender") is not True:return "HOLD_MESH_INSPECTION"
    if record.get("uvAndNormalsInspected") is not True or record.get("weightsNormalized") is not True:return "HOLD_TOPOLOGY"
    if type(record.get("triangles")) is not int or not 0<record["triangles"]<=120000:return "HOLD_TRIANGLE_BUDGET"
    if not isinstance(record.get("edgeLoopPasses"),dict) or not all(record["edgeLoopPasses"].get(k) is True for k in
       ("eyes","mouth","shoulder","elbow","hip","knee")):return "HOLD_DEFORMING_EDGE_LOOPS"
    if not isinstance(record.get("morphTargets"),list) or not set(
       ("blinkLeft","blinkRight","smile","jawOpen","visemeAa","visemeOh")).issubset(record["morphTargets"]):
        return "HOLD_FACE_MORPHS"
    if record.get("artistReviewed") is not True:return "HOLD_ARTIST_REVIEW"
    return "REVIEW_CANDIDATE_SOURCE_ONLY"
def inspect_skybox(record):
    if not isinstance(record,dict) or record.get("schema")!="luhmOs.localSkyboxReference.v1":return "NO_SKYBOX_REPORT"
    path=record.get("path")
    if not isinstance(path,str) or not re.fullmatch(r"assets/skyboxes/[a-zA-Z0-9][a-zA-Z0-9_.-]{0,90}\.(?:hdr|env)",path):return "HOLD_SKYBOX_LOCAL_PATH"
    if record.get("licenseClear") is not True or record.get("artistApproved") is not True:return "HOLD_SKYBOX_RIGHTS"
    if not SHA256.fullmatch(str(record.get("sha256",""))):return "HOLD_SKYBOX_HASH"
    if type(record.get("sizeBytes")) is not int or not 0<record["sizeBytes"]<=16777216:return "HOLD_SKYBOX_SIZE"
    return "REVIEW_CANDIDATE_NOT_RENDERED"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}",args.source_ref):raise SystemExit("EXACT_SHA_REQUIRED")
    state=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if state.returncode or state.stdout.strip()!=args.source_ref:raise SystemExit("EXACT_CHECKOUT_MISMATCH")
    policy=json.loads(POLICY.read_text(encoding="utf-8"));errors=audit(policy)
    receipt={"schema":"luhmOs.modAvatarMatrixReceipt.v1","sourceRef":args.source_ref,"status":"PASS_SOURCE_ONLY_CROWN_STOP" if not errors else "FAIL_SOURCE","errors":errors,
      "combinationsInDesign":125000000,"representativeCasesPlanned":500,"casesExecutedAgainstRuntime":0,
      "avatarRuntimeVerified":False,"nexusApiCalled":False,"remoteAssetsDownloaded":False,"skyboxRendered":False,"crown":"STOP",
      "manifestSha256":hashlib.sha256(POLICY.read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("sourceRef","status","errors","combinationsInDesign","representativeCasesPlanned","casesExecutedAgainstRuntime")},indent=2))
    if errors:raise SystemExit(2)
if __name__=="__main__":main()
