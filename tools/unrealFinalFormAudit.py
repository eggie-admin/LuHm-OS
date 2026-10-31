#!/usr/bin/env python3
"""Fail-closed source-only Unreal migration audit. No network, GPU, mods or engine execution."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/unrealFinalFormBridgeV1.json"
def evaluate(p):
    errors=[]
    def ck(valid,code):
        if not valid: errors.append(code)
    ck(p.get("schema")=="luhmOs.unrealFinalFormBridge.v1" and p.get("status")=="PROPOSED_SOURCE_ONLY","WRONG_SCHEMA_OR_STAGE")
    ck(p.get("canonicalRepository")=="eggie-admin/LuHm-OS","SOURCE_OF_TRUTH_DRIFT")
    e=p.get("engineDirection",{})
    ck(e.get("finalForm")=="Unreal Engine 5" and e.get("migration")=="parallelRightsClearedVerticalSlice","ENGINE_MIGRATION_DRIFT")
    for k in ("godotDeletionAllowed","unrealInstalledOrBuilt","unrealRuntimeVerified"):
        ck(e.get(k) is False,"FALSE_ENGINE_PROOF_"+k)
    ck(e.get("licenseReviewRequired") is True and e.get("noEngineSourceVendoring") is True,"UNREAL_LICENSE_BOUNDARY")
    s=p.get("studioPipeline",{})
    for k in ("assetsRequireKnownRights","contentSha256Required","conversionRequiresSandbox","retainGodotAssetsUntilParity"):
        ck(s.get(k) is True,"ASSET_GATE_"+k)
    for k in ("executeUntrustedAssetScripts","autoUploadPrivateMasters"):
        ck(s.get(k) is False,"ASSET_EXPOSURE_"+k)
    ck(s.get("exportTargets")=={"staticAndSimpleScene":"glb","skinnedMeshes":"fbx","complexScenesOptional":"usd"},"INTERCHANGE_CONTRACT_DRIFT")
    b=p.get("integrationBoundaries",{})
    ck(b.get("unrealOwnsFinalRuntime") is True,"ENGINE_OWNERSHIP_DRIFT")
    for k in ("standaloneSecondRendererRequired","nodeRuntimeInsideAndroid","unrealEngineInsideSamsungTabletRequired"):
        ck(b.get(k) is False,"UNNECESSARY_RUNTIME_"+k)
    a=p.get("adapters",[])
    ck(len(a)==7 and {x.get("id") for x in a}=={"nvidiaAce","nvidiaDlss","amdFsr","amdRocm","oracleOciAi","nexusModsV3","vortexExtension"},"ADAPTER_INVENTORY_DRIFT")
    for x in a:
        k=str(x.get("id","missing"))
        ck(x.get("status")=="EVALUATE","UNPROVED_VENDOR_"+k)
        ck(x.get("enabledByDefault") is False and x.get("networkAllowedByDefault") is False,"AUTO_VENDOR_EXECUTION_"+k)
        ck(x.get("licenseReviewRequired") is True,"VENDOR_LICENSE_"+k)
    m=p.get("moddingLaw",{})
    for k in ("autoDownloadMods","autoRedistributeThirdPartyMods","allowUnknownScripts","publicAppRegistrationVerified","defaultUserKeysStoredOnServer"):
        ck(m.get(k) is False,"NEXUS_POLICY_"+k)
    r=p.get("repositoryInventory",{}); public=r.get("publicCandidates",[])
    ck(r.get("primary")==p.get("canonicalRepository") and len(public)==17 and len(set(public))==17 and all(x.startswith("eggie-admin/") for x in public),"REPOSITORY_INVENTORY_DRIFT")
    for k in ("bulkMerge","rewriteOtherRepositories","deleteDonors","hiddenPrivateRepoNamesInPublicRegistry"):
        ck(r.get(k) is False,"GIT_HISTORY_SAFETY_"+k)
    d=p.get("reduction",{})
    ck(d.get("mainWorkflowCountObserved")==129 and d.get("oneExistingCIWorkflow")==".github/workflows/free-first-workspace-daily.yml","CI_SOURCE_DRIFT")
    for k in ("noNewWorkflow","noNewRuntimePackageManager","noBundledThirdPartyEngineBinaries"):
        ck(d.get(k) is True,"WORKFLOW_SPRAWL_"+k)
    z=p.get("safety",{})
    for k in ("autoMerge","autoDeploy","autoPublish","autoUnquarantineAgents","autoSign","autoChangeCloudResources","acceptUnverifiedRuntime","unknownAssetRightsAccepted"):
        ck(z.get(k) is False,"UNAUTHORIZED_ACTION_"+k)
    ck(type(z.get("autoSpendUsd")) is int and z["autoSpendUsd"]==0,"UNAUTHORIZED_SPENDING")
    ck(z.get("crown")=="STOP","FALSE_CROWN")
    return sorted(set(errors))
def main():
    a=argparse.ArgumentParser();a.add_argument("--source-ref",required=True);a.add_argument("--output",required=True)
    args=a.parse_args()
    if not re.fullmatch("[a-f0-9]{40}",args.source_ref):raise SystemExit("EXACT_SHA_REQUIRED")
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if r.returncode or r.stdout.strip()!=args.source_ref:raise SystemExit("EXACT_CHECKOUT_MISMATCH")
    p=json.loads(POLICY.read_text(encoding="utf-8")); errors=evaluate(p)
    receipt={"schema":"luhmOs.unrealFinalFormReceipt.v1","sourceRef":args.source_ref,"status":"PASS_SOURCE_ONLY_CROWN_STOP" if not errors else "FAIL_POLICY","errors":errors,"candidateRepositories":len(p["repositoryInventory"]["publicCandidates"]),"optionalAdapters":len(p["adapters"]),"unrealRuntimeProven":False,"hardwareProven":False,"externalApiProven":False,"crown":"STOP","manifestSha256":hashlib.sha256(POLICY.read_bytes()).hexdigest()}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("sourceRef","status","errors","candidateRepositories","optionalAdapters","crown")},indent=2))
    if errors:raise SystemExit(2)
if __name__=="__main__":main()
