#!/usr/bin/env python3
"""Offline World Headquarters contract audit; no cloud calls, builds, or agent execution."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/worldHeadquartersOrchestrationV1.json"

def load(relative, root=ROOT):
    target = root / relative
    if not target.is_file() or target.is_symlink():
        raise ValueError("missing or symlink contract: " + relative)
    result = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("invalid contract: " + relative)
    return result

def assess(policy, contracts=None):
    errors = []
    def need(ok, code):
        if not ok:
            errors.append(code)
    def get_doc(name):
        return contracts.get(name, {}) if contracts is not None else load(name)
    layers = policy.get("compatibilityLayers", [])
    ids = [x.get("id") for x in layers]
    need(policy.get("schema") == "luhmOs.worldHeadquartersOrchestration.v1", "schema")
    need(policy.get("status") == "SOURCE_CANDIDATE_NOT_RUNTIME_DEPLOYED", "candidateStatus")
    need(policy.get("authority") == "Professor", "professorAuthority")
    need(policy.get("canonicalRepository") == "eggie-admin/LuHm-OS" and policy.get("canonicalBranch") == "main", "sourceIdentity")
    need(ids == ["chatGptOpenAi", "github"] and [x.get("priority") for x in layers] == [1, 2], "compatibilityPriority")
    if len(layers) == 2:
        one, two = layers
        need(one.get("canOwnCanonicalSource") is False and one.get("paidApiCallsWithoutSeparateApproval") is False, "openAiBoundary")
        need(one.get("requiresCodex") is False and one.get("accountWorkModeSwitchBySchema") is False, "openAiWorkEntitlement")
        need(two.get("sourceAuthority") is True and two.get("mirrorIsSecondSourceAuthority") is False and two.get("automaticallyMerge") is False, "gitHubBoundary")
    hq = policy.get("headquarters", {})
    roles = policy.get("roles", {})
    need(hq.get("president") == roles.get("singleBoss") == "lum", "singleLum")
    need(hq.get("notEnterpriseInfrastructure") is True, "privateStudio")
    need(set(roles.get("goddessCabinet", {})) == {"urdDoctorGoddess", "belldandySecretary", "skuldResearch"}, "cabinetIdentity")
    need(roles.get("creativeLead") == "yume", "artDirection")
    need(roles.get("forgeTwins", {}).get("tetsu", "").startswith("sourceForge") and roles.get("forgeTwins", {}).get("kaji", "").startswith("compileForge"), "forgeTwins")
    need(set(roles.get("oniSpecialists", [])) == {"kiri","momo","shiori","kugi","fumi","sumi","koe","mediaAssetFactory"}, "oniIdentity")
    need(roles.get("registeredRosterCount") == 15 and roles.get("liveAgentExecutionEnabled") is False, "rosterQuarantine")
    need(roles.get("maxParallelSupportWorkers") == 3 and roles.get("oneMutableSourceLane") is True, "resourceGuard")
    need(roles.get("hiddenAsyncExecution") is False and roles.get("recursiveRecruitment") is False, "noHiddenAgents")
    need(roles.get("noRoleMayGrantCrown") is True, "noCrownFromRole")
    atc = policy.get("airTraffic", {})
    need(atc.get("controller") == "cloudflare" and atc.get("mayBeAiBoss") is False and atc.get("mayBeSourceAuthority") is False, "trafficBoundary")
    need(atc.get("mayExposeLan") is False and atc.get("privatePortalActivationRequiresSeparateProof") is True, "privateNetworkBoundary")
    dev = policy.get("researchAndDevelopment", {})
    mirror = dev.get("secondSourceOfTruthInterpretation", {})
    need(dev.get("canonicalWorkspace") == "GitHub Codespaces" and dev.get("sourceOfTruth") == "githubMain", "workspaceIdentity")
    need(mirror.get("sourceAuthority") is False and mirror.get("conflictingSourceRef") == "STOP", "noSecondAuthority")
    garage = dev.get("basementWorkshop", {})
    need(garage.get("devcontainer") == ".devcontainer/devcontainer.json", "garageSource")
    need({"headlessBlender","gimp3BatchUnderXvfb","ffmpeg","nginx","python3"}.issubset(set(garage.get("tools", []))), "garageTools")
    need(garage.get("hardwareAndRuntimeStatus") == "NOT_VERIFIED_IN_THIS_CHANGE", "garageUnverified")
    forge = dev.get("forge", {})
    need(forge.get("castSingleUse") and forge.get("genericPhraseIsNotAValidCastEnvelope") and forge.get("sourceChangeLocation") == "candidateBranchOnly", "castScope")
    sc = policy.get("sidecars", {})
    render = sc.get("render", {})
    need(render.get("noAutomaticDeployment") and render.get("noPaidResources") and render.get("sameShaReceipt"), "renderBoundary")
    drive = sc.get("googleDrive", {})
    need(drive.get("privateDriveIdsInPublicRepo") is False and drive.get("extractedFilesRequireRightsAndHashCheck") is True, "privateDriveBoundary")
    pipe = policy.get("pipeline", {})
    need(pipe.get("orderedStates") == ["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"], "stageOrder")
    need(all(pipe.get(k) is True for k in ("noAutomaticMerge","noAutomaticBuild","noAutomaticCast","noAutomaticDeployment","noAutomaticPublicRelease","noAutomaticSigning","noAutomaticQuarantineRelease")), "noAutomaticPromotion")
    need(policy.get("crownStatus") == "STOP" and policy.get("promotion") is False and policy.get("deploymentStatus") == "SOURCE_ONLY", "crownStop")

    truth = get_doc("doctrine/currentSourceTruthV3.json")
    fast = get_doc("doctrine/studioCompatibilityFastMeshV1.json")
    cabinet = get_doc("doctrine/lumGoddessCabinetV1.json")
    quarantine = get_doc("doctrine/companyWideOperationalQuarantineV1.json")
    control = get_doc("doctrine/luhmAiControlPlaneV1.json")
    roster = get_doc("doctrine/agentSystemDeploymentV1.json")
    traffic = get_doc("doctrine/cloudflareAirTrafficControllerV1.json")
    storage = get_doc("doctrine/storageTopologyV1.json")
    twins = get_doc("doctrine/forgeTwinsV3.json")
    sidecar = get_doc("doctrine/githubRenderSidecarV1.json")
    tiers = get_doc("doctrine/fourTierOperatingModelV1.json")

    order = truth.get("activeCompatibilityOrder", {})
    need(order.get("first") == "chatGptOpenAi" and order.get("second") == "github" and order.get("sourceAuthority") == "github", "sourceCompatibilityDrift")
    need(fast.get("compatibilityPriority") and [x.get("id") for x in fast["compatibilityPriority"]] == ids, "studioCompatibilityDrift")
    need(fast.get("releaseBoundary", {}).get("merge") is False and fast.get("releaseBoundary", {}).get("deploy") is False, "studioReleaseBoundary")
    need(set(x.get("id") for x in cabinet.get("members", [])) == {"lum","urdDoctorGoddess","belldandySecretary","skuldResearch"}, "cabinetDrift")
    need(control.get("boss") == "lum" and control.get("invariants", {}).get("oneMutableSourceLane") is True, "controlPlaneDrift")
    need(roster.get("requiredAgentCount") == len(roster.get("requiredAgents", [])) == 15, "rosterCountDrift")
    need(quarantine.get("state") == "QUARANTINED" and quarantine.get("activeTaskWorkersAllowed") is False, "companyQuarantineDrift")
    need(traffic.get("authorityBoundary", {}).get("sourceTruthOwner") is False and traffic.get("authorityBoundary", {}).get("aiProvider") is False, "trafficAuthorityDrift")
    need(storage.get("roles", {}).get("github", {}).get("canonicalSourceAuthority") is True and storage.get("roles", {}).get("googleDrive", {}).get("canonicalBinaryStorage") is True, "storageAuthorityDrift")
    need(twins.get("twins", {}).get("Tetsu", {}).get("role") == "SOURCE_FORGE" and twins.get("twins", {}).get("Kaji", {}).get("role") == "COMPILE_FORGE", "forgeTwinsDrift")
    need(twins.get("castEnvelope", {}).get("singleUse") is True, "singleUseCastDrift")
    need(sidecar.get("githubPrimary", {}).get("canonicalBranch") == "main" and sidecar.get("renderSidecar", {}).get("autoDeployCanonical") is False, "githubRenderDrift")
    need(len(tiers.get("tiers", [])) == 4 and tiers.get("primeLaw") == "oneAuthorityChainManyPresentationAndWorkLayers", "fourTierDrift")
    return sorted(set(errors))

def negative_controls(policy, contracts):
    probes = [
        ("fakeSecondSource", ("researchAndDevelopment","secondSourceOfTruthInterpretation","sourceAuthority"), True),
        ("swapLayers", ("compatibilityLayers",0,"id"), "github"),
        ("forceCodex", ("compatibilityLayers",0,"requiresCodex"), True),
        ("autoMerge", ("pipeline","noAutomaticMerge"), False),
        ("autoDeploy", ("pipeline","noAutomaticDeployment"), False),
        ("quarantineRelease", ("roles","liveAgentExecutionEnabled"), True),
        ("crownEscalation", ("crownStatus",), "GREEN"),
        ("forgeCastBypass", ("researchAndDevelopment","forge","genericPhraseIsNotAValidCastEnvelope"), False),
    ]
    for title, path, bad_value in probes:
        changed = copy.deepcopy(policy)
        item = changed
        for key in path[:-1]:
            item = item[key]
        item[path[-1]] = bad_value
        if not assess(changed, contracts):
            raise AssertionError("negative control escaped: " + title)
    return len(probes)

def main():
    policy = load(CONTRACT)
    refs = {p: load(p) for p in (
        "doctrine/currentSourceTruthV3.json",
        "doctrine/studioCompatibilityFastMeshV1.json",
        "doctrine/lumGoddessCabinetV1.json",
        "doctrine/companyWideOperationalQuarantineV1.json",
        "doctrine/luhmAiControlPlaneV1.json",
        "doctrine/agentSystemDeploymentV1.json",
        "doctrine/cloudflareAirTrafficControllerV1.json",
        "doctrine/storageTopologyV1.json",
        "doctrine/forgeTwinsV3.json",
        "doctrine/githubRenderSidecarV1.json",
        "doctrine/fourTierOperatingModelV1.json",
    )}
    errors = assess(policy, refs)
    if errors:
        print(json.dumps({"status":"RED_SOURCE","issues":errors}, indent=2))
        return 1
    count = negative_controls(policy, refs)
    print(json.dumps({"status":"WORLD_HEADQUARTERS_SOURCE_ONLY_GREEN","negativeControls":count,
         "compatibilityLayers":["chatGptOpenAi","github"],"backendAgents":"QUARANTINED",
         "runtime":"NOT_PROVEN","merge":"NOT_AUTHORIZED","deploy":"NOT_AUTHORIZED","crown":"STOP"}, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        print(json.dumps({"status":"RED_FAIL_CLOSED","error":str(exc)}))
        raise SystemExit(1)
