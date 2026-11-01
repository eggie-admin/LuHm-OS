#!/usr/bin/env python3
"""CAST machine closeout: source-only reconciler. Never authorizes builds or deployment."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine/castMachineCloseoutV1.json"
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
STAGES = ("concept", "prototype", "proposed", "beta", "final")
CHAIN = (477, 478, 479, 480)
ROLES = ("debianUserland", "nodePythonSql", "deviceRegistry", "piOsKiosk")
EXPECTED_HEADS = (
    "f44e0747944177c9c24a9a6c9b7edcad168318d8",
    "40c0ce5f35a32127acc2e176ad41bcf9f11066dc",
    "722730eadb7362a93f6a4660a026a60f598d4b06",
    "d5b2947360a0c8b9ec184162b7fa4f405d8b3616",
)
EXPECTED_RUNS = (41275191198, 41275728802, 41276356242, 41276769982)
LAYERS = ("piBootKernel", "headlessUserspace", "studioServices", "browserKiosk")
COLS = ("inventory", "authority", "safeProof", "propose")
PROVEN = ("canonSourceBound", "platformArchitectureChosen",
          "fourByFourSourceChecks", "debianContainerCi",
          "loopbackKioskCi", "typedNpmPythonSqlCi", "parentPrShaChain")
UNCERTAIN = ("exactHeadCiRecheck", "currentMainRecheck",
             "professorReviewsSourceScope", "physicalPiBoot",
             "physicalKernelFirmwareAndDrivers", "nonrootStudioSmoke",
             "securePhoneTransport", "rollbackRecovery", "explicitOneUseCast",
             "betaDeviceAcceptance", "rightsAndLicenses",
             "signedDistribution", "ownerReleaseApproval",
             "productionRollbackPlan")
DECISIONS = ("sourceCandidateFrozenUntilEvidence", "doNotAddAnotherKernelFork",
             "doNotAddSecondWebServer", "doNotAddGdmToHeadless",
             "doNotAutoMergeStackedBranches", "noAutomaticCastDispatch",
             "castDoesNotAuthorizeDeploy", "noImplicitModelInference",
             "noPhysicalHardwareProofFromCI", "blockedHardwareIsEscalationNotWorkToInvent",
             "remoteUnrealOutsideMachineBaseline", "noPaidComputeOrPublicAccess")
SOURCE_FILES = (
    "doctrine/machineDebianFourLayerV1.json",
    "doctrine/machineLocalAgentAuditV1.json",
    "doctrine/deviceCapabilityRegistryV1.json",
    "doctrine/piOsLiteMachineKioskV1.json",
    "doctrine/forgeTwinsV3.json",
    "tools/machineDebianSnapshot.py",
    "tools/luhm-machine-agent/src/index.mjs",
    "tools/pi-kiosk/preview.py",
    "infra/machine-debian/Dockerfile",
)

class MachineCastError(ValueError):
    pass

def need(condition: bool, msg: str):
    if not condition:
        raise MachineCastError("RED_CAST_MACHINE_" + msg)

def safe_file(name: str, root: Path = ROOT) -> Path:
    need(type(name) is str and name in SOURCE_FILES, "FILE_ALLOWLIST")
    p = root / name
    need(p.is_file() and not p.is_symlink() and
         p.resolve().is_relative_to(root.resolve()), "FILE_BOUNDARY")
    return p

def validate(m: dict, root: Path = ROOT):
    need(type(m) is dict and m.get("schema") == "luhmOs.castMachineCloseout.v1" and
         m.get("authority") == "Professor" and
         m.get("crownStatus") == "STOP" and
         m.get("status") == "PROPOSED_MACHINE_SOURCE_RECONCILIATION",
         "CONTRACT")
    need(m.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.",
         "LAW")
    need(SHA40.fullmatch(m.get("mainBaseline", "")) is not None, "MAIN_SHA")
    milestone=m.get("milestone", {})
    need(milestone.get("id") == "piOsLiteMachineToOsProposed20261101" and
         milestone.get("scopeId") == "piOsMachine4x4" and
         milestone.get("nextLayer") == "osAndStudioRuntime" and
         milestone.get("buildNotRequested") is True, "MILESTONE")
    chain=m.get("chain", [])
    need(type(chain) is list and len(chain) == 4 and
         tuple(row.get("pr") for row in chain) == CHAIN and
         tuple(row.get("role") for row in chain) == ROLES,
         "PR_CHAIN")
    for i,item in enumerate(chain):
        need(SHA40.fullmatch(item.get("sha", "")) is not None and
             item["sha"] == EXPECTED_HEADS[i] and
             item.get("sourceRun") == EXPECTED_RUNS[i] and
             type(item.get("branch")) is str and
             item["branch"].startswith("candidate/"), "PR_SOURCE_SHA")
        expected_base = "main" if i == 0 else chain[i-1]["branch"]
        need(item.get("base") == expected_base, "PR_PARENT_STACK")
    need(m.get("mainBaseline") == "f0cb6ee54066b490c0e80efc2c96200fec76ee2d",
         "BASELINE_DRIFT")
    lanes=m.get("lanes", [])
    need(type(lanes) is list and tuple(x.get("id") for x in lanes) == STAGES,
         "LANE_ORDER")
    expected_auth=("sourceReadOnly", "readOnlyCI", "humanReviewRequired",
                   "separateSingleUseCastOnly", "releaseApprovalSeparateFromCast")
    need(tuple(x.get("authorization") for x in lanes) == expected_auth and
         all(type(x.get("criteria")) is list and x["criteria"] for x in lanes),
         "LANE_AUTHORITY")
    matrix=m.get("machineFourByFour", {})
    need(matrix.get("namespace") == "piOsMachine" and
         matrix.get("layers") == list(LAYERS) and
         matrix.get("columns") == list(COLS) and
         matrix.get("indices") == [f"0x{i:02X}" for i in range(16)],
         "HEX_MATRIX")
    observations=m.get("observations", {})
    need(set(observations) == set(PROVEN+UNCERTAIN) and
         all(observations.get(k) is True for k in PROVEN) and
         all(observations.get(k) is False for k in UNCERTAIN),
         "EVIDENCE_CANNOT_SELF_PROMOTE")
    need(set(lanes[0]["criteria"]).issubset(PROVEN) and
         set(lanes[1]["criteria"]).issubset(PROVEN) and
         "physicalPiBoot" in lanes[3]["criteria"] and
         "explicitOneUseCast" in lanes[3]["criteria"] and
         "ownerReleaseApproval" in lanes[4]["criteria"],
         "PROMOTION_SCOPE")
    need(m.get("readyToPlanNextOsLayer") is True and
         m.get("readyForPhysicalBackend") is False, "MACHINE_TRUTH")
    decisions=m.get("contractDecisions", {})
    need(set(decisions) == set(DECISIONS) and
         all(decisions.get(key) is True for key in DECISIONS),
         "NO_VENDOR_OR_PRIVILEGE_ESCALATION")
    promotion=m.get("promotionLaw", {})
    need(promotion.get("automaticDestination") == "PROPOSED_SOURCE_REVIEW_ONLY" and
         promotion.get("maximumWithoutPhysicalProof") == "PROPOSED_SOURCE_REVIEW_ONLY" and
         all(promotion.get(k) is True for k in
         ("castSourceRequired", "castSingleUse", "buildRequiresDistinctAuthorization",
          "releaseRequiresSeparateApproval")) and
         set(promotion.get("prohibitedActions", [])) ==
         {"productionMerge", "physicalPiProvision", "firmwareFlash",
          "ownerSignedApp", "googlePlayUpload", "galaxyStoreUpload",
          "remoteTunnelEnable", "publicCdNDeploy", "agentPromotion"},
         "PROMOTION_LAW")
    gaps=m.get("requiredNextEvidence", [])
    need([g.get("id") for g in gaps]==
         ["HARDWARE-001", "STUDIO-002", "NETWORK-003", "CAST-004", "RELEASE-005"] and
         all(g.get("status", "").startswith("BLOCKED_") for g in gaps),
         "HONEST_BLOCKERS")
    sources=m.get("sourceReceipts", [])
    need(tuple(x.get("path") for x in sources)==SOURCE_FILES and
         all(type(x.get("role")) is str and x["role"] for x in sources),
         "SOURCE_INVENTORY")
    cast=json.loads(safe_file("doctrine/forgeTwinsV3.json",root).read_text(encoding="utf-8"))
    envelope=cast.get("castEnvelope", {})
    need(cast.get("crownStatus")=="STOP" and
         "singleUse" in envelope.get("requiredFields", []) and
         envelope.get("persistentAuthorizationAllowed") is False and
         envelope.get("consumedOnAttempt") is True and
         "deployment" in envelope.get("doesNotAuthorize", []) and
         "publication" in envelope.get("doesNotAuthorize", []) and
         cast.get("operationBoundaries", {}).get("CAST", {}).get("sourceWrite") is False,
         "EXISTING_CAST_AUTHORITY")
    pi=json.loads(safe_file("doctrine/piOsLiteMachineKioskV1.json",root).read_text(encoding="utf-8"))
    need(pi.get("crownStatus")=="STOP" and
         pi.get("baseline",{}).get("physicalBoardVerified") is False and
         pi.get("guards", {}).get("noProtectedMainMerge") is True and
         pi.get("preview",{}).get("loopbackAddress")=="127.0.0.1",
         "PI_SOURCE_TRUTH")
    digests=[]
    for item in sources:
        path=safe_file(item["path"],root)
        data=path.read_bytes()
        need(0<len(data)<=131072, "SOURCE_SIZE")
        digests.append({"path":item["path"],"sha256":sha256(data).hexdigest()})
    return digests

def receipt(m: dict, root: Path=ROOT):
    digests=validate(m,root)
    return {
        "schema":"luhmOs.castMachineCloseoutReceipt.v1",
        "status":"AMBER_MACHINE_SOURCE_READY_FOR_PROPOSED_REVIEW",
        "machineSourcePrototyped":True,
        "nextOsPlanningAllowed":True,
        "currentHeadReverified":False,
        "actualPiBooted":False,
        "kioskAccessibleFromPhone":False,
        "physicalBackendComplete":False,
        "betaReleaseReady":False,
        "finalReleaseReady":False,
        "castAuthorized":False,
        "castDispatched":False,
        "publicDeployment":False,
        "liveData":False,
        "historicalPrChain":[{"pr":x["pr"],"sha":x["sha"],"sourceRun":x["sourceRun"]}
                             for x in m["chain"]],
        "sourceDigests":digests,
        "nextBlockers":[{"id":x["id"],"status":x["status"]}
                        for x in m["requiredNextEvidence"]],
        "nextMachineAction":"READ_ONLY_ACTUAL_PI_BOARD_INVENTORY",
        "sourceChangesUntilHardwareEvidence":"SECURITY_FIXES_ONLY",
        "crownStatus":"STOP",
    }

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",type=Path,default=MANIFEST)
    args=parser.parse_args()
    model=json.loads(args.contract.read_text(encoding="utf-8"))
    print(json.dumps(receipt(model),sort_keys=True,indent=2))
