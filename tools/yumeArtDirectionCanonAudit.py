#!/usr/bin/env python3
"""Fail-closed audit for the explicitly scoped Yume art-direction source canon."""
from __future__ import annotations
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

canon = load("doctrine/yumeArtDirectionCanonV1.json")
control = load("doctrine/luhmAiControlPlaneV1.json")
mesh = load("doctrine/agentSystemDeploymentV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
pipeline = load("doctrine/yumeCreativePipelineV1.json")
community = load("doctrine/yumeCommunityArtResourcesV1.json")
working = load("doctrine/proposedWorkingLaneV1.json")
skill = (ROOT / "agents/yumeArtOni/SKILL.md").read_text(encoding="utf-8")

def errors_for(canon: dict, control: dict, mesh: dict, truth: dict) -> list[str]:
    errors = []
    def require(ok: bool, name: str) -> None:
        if not ok:
            errors.append(name)

    role = control.get("agents", {}).get("yume", {})
    binding = canon.get("meshBinding", {})
    privacy = canon.get("rightsAndPrivacy", {})
    proof = canon.get("proofBoundary", {})
    borders = canon.get("productionBoundaries", {})
    governance = canon.get("governance", {})
    claim = truth.get("yumeArtDirectionCanon", {})
    pointer = truth.get("agentLayer", {}).get("yumeRoleCanon", {})

    require(canon.get("schema") == "luhmOs.yumeArtDirectionCanon.v1", "schema")
    require(canon.get("status") == "CANONICAL_ART_DIRECTION_SOURCE", "roleCanonStatus")
    require(canon.get("authority") == "Professor" and canon.get("professorApproved") is True, "humanAuthority")
    require(canon.get("promotionScope") == "yumeArtDirectionBehaviorAndSafety", "scope")
    require(canon.get("crownStatus") == "CROWNED_SOURCE_ROLE_ONLY", "scopedCrown")
    require(canon.get("canonicalRolePromotion") is True, "sourcePromotion")
    require(binding.get("canonicalAgentId") == "yume", "agentId")
    require(binding.get("skillIdentity") == "yumeArtOni", "skillIdentity")
    require(binding.get("skillPath") == role.get("skillPath") == "agents/yumeArtOni/SKILL.md", "roleSkill")
    require(role.get("speaksTo") == "lum" and role.get("mayRecruit") is False and role.get("maySelfApprove") is False, "roleAuthority")
    require(binding.get("boss") == "lum" and binding.get("mayRecruit") is False and binding.get("maySelfApprove") is False, "meshBoss")
    require(binding.get("residentReviewCabinet") == ["urdDoctorGoddess","belldandySecretary","skuldResearch"], "cabinet")
    require(binding.get("maxParallelSupportWorkers") == 3, "parallelLimit")
    require(binding.get("independentProviderWorkerProven") is False and binding.get("hiddenAsyncExecution") is False, "noHiddenAgents")
    require("yume" in mesh.get("globallyAvailableLazyAgents", []), "yumeLazy")
    require(mesh.get("requiredAgentCount") == 15 and len(set(mesh.get("requiredAgents", []))) == 15, "meshCount")
    require(mesh.get("status") == "PROPOSED_SYSTEM_WIDE_AGENT_DEPLOYMENT", "wholeMeshUnpromoted")
    require(mesh.get("promotion") is False and mesh.get("crownStatus") == "STOP", "meshCrown")
    require(mesh.get("activationLaw", {}).get("maxParallelSupportWorkers") == 3, "meshParallelLimit")
    require(truth.get("agentLayer", {}).get("workingLane") == "PROPOSED_ONLY" and truth.get("agentLayer", {}).get("crownStatus") == "STOP", "truthMeshBoundary")
    require(truth.get("crownStatus") == "STOP", "overallCrownBoundary")
    require(pointer.get("contract") == "doctrine/yumeArtDirectionCanonV1.json", "truthAgentPointer")
    require(pointer.get("canonicalRosterId") == "yume" and pointer.get("skillIdentity") == "yumeArtOni", "truthIdentity")
    require(pointer.get("wholeMeshDeploymentPromotion") is False and pointer.get("liveProviderWorkerProven") is False, "truthAgentAuthority")
    require(truth.get("creativeLayer", {}).get("yumeArtDirectionCanon") == "doctrine/yumeArtDirectionCanonV1.json", "truthCreativePointer")
    require(claim.get("contract") == "doctrine/yumeArtDirectionCanonV1.json" and claim.get("professorApproved") is True, "truthScope")
    require(claim.get("source3dRuntimePromoted") is False and claim.get("referenceGalleryRuntimePromoted") is False, "truthRuntime")
    require(claim.get("releaseAuthority") is False and claim.get("publicationAuthority") is False, "truthPublication")
    require(pipeline.get("workingLane") == "PROPOSED_ONLY" and pipeline.get("promotion") is False, "proposedPipeline")
    require(pipeline.get("crownStatus") == "STOP", "pipelineCrown")
    require(working.get("futureDoctrineMutationsDefault") == "PROPOSED_ONLY", "futureProposedLaw")
    require(community.get("storageLaw", {}).get("publicDoctrineStoresNoPrivateDriveIds") is True, "storageLaw")
    for name in ("publicDriveFileOrFolderIdentifiers","publicAuthenticatedAssetUrls","publicCredentials",
                 "communityAssetApprovalFromSourceLink","franchiseFanModelNotAutomaticallyRedistributable",
                 "publicGenerativeAiArtDefaultAllowed","automaticHistoryRewrite"):
        require(privacy.get(name) is False, "privacy:"+name)
    for name in ("sourceExistsNotRuntime","browserGalleryNot3dAnimation","thumbnailNotRuntimeCapture",
                 "CIStaticPassNotGodotRuntime","unknownRemainsUnknown","staleBodyOnCharacterSwapRequiresRepairAndTest"):
        require(proof.get(name) is True, "evidence:"+name)
    for name in ("creativePipelinePromotion","goddess3dProductionPromotion",
                 "referenceGalleryRuntimePromotion","providerSideDeploymentPromotion",
                 "androidPhysicalProof","releaseAuthority","publicationAuthority",
                 "productionSigningAuthority","autonomousCanonExpansion","wholeMeshPromotion"):
        require(borders.get(name) is False, "boundary:"+name)
    require(governance.get("newSourceChangesDefaultProposed") is True and governance.get("noAutomaticFuturePromotion") is True, "futureApproval")
    require(canon.get("characterIdentity", {}).get("characters") == ["lum","urd","belldandy","skuld"], "goddessSet")
    require(canon.get("characterIdentity", {}).get("noCrossCharacterFaceCopy") is True, "identityFirewall")
    require("## Yume final art-direction canon (scoped)" in skill, "yumeSkillBinding")
    require("not two agents" in skill, "duplicateAgentGuard")
    require("never private Google Drive IDs" in skill, "privateIdGuard")
    require("an HTML gallery is not Godot proof" in skill, "runtimeGuard")
    require("no automatic Crown" not in skill or binding.get("maySelfApprove") is False, "authorityGuard")
    # Current canonical text must not reintroduce private folder/file ID keys or their sensitive values.
    forbidden_keys = ("driveSourceId","driveApprovedArtFolder","driveCandidateReviewFolder","driveFileId","driveFolderId")
    canon_text = json.dumps(canon)
    require(not any(key in canon_text for key in forbidden_keys), "privateLocatorLeak")
    return errors

errors = errors_for(canon, control, mesh, truth)
if errors:
    for error in errors:
        print("RED:", error)
    raise SystemExit("YUME_ART_DIRECTION_CANON_AUDIT=FAIL")

# Negative controls must independently flip to RED, never optimistic success.
negative = []
case = copy.deepcopy(canon)
case["meshBinding"]["maySelfApprove"] = True
negative.append(("selfApproval", errors_for(case, control, mesh, truth)))
case = copy.deepcopy(canon)
case["productionBoundaries"]["publicationAuthority"] = True
negative.append(("publication", errors_for(case, control, mesh, truth)))
case = copy.deepcopy(truth)
case["agentLayer"]["crownStatus"] = "GREEN"
negative.append(("meshCrown", errors_for(canon, control, mesh, case)))
case = copy.deepcopy(canon)
case["rightsAndPrivacy"]["publicDriveFileOrFolderIdentifiers"] = True
negative.append(("privateId", errors_for(case, control, mesh, truth)))
for name, findings in negative:
    if not findings:
        raise SystemExit("YUME_ART_DIRECTION_CANON_NEGATIVE_CONTROL=FAIL:" + name)
print("YUME_ART_DIRECTION_CANON_SOURCE_GREEN")
print("negativeControls=4_PASS")
print("scope=yumeArtDirectionBehaviorAndSafety")
print("meshDeployment=PROPOSED_ONLY")
print("runtimeProof=NOT_CLAIMED")
print("releaseAndPublication=STOP")
