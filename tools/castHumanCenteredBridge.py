#!/usr/bin/env python3
"""Read-only human-centered CAST presentation over the existing task-array planner.

This module never calls the GitHub CAST bridge, launches agent workers, accesses
private art bytes, tunes SQL, or changes a release/install state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from castTaskArray import compilePreview, readJson, repoRoot


def loadHumanBridge(root: Path = repoRoot) -> dict:
    # The canonical file is the YAML 1.2 JSON-compatible subset intentionally
    # used throughout the LuHmOS fnCast contract. No implicit YAML tags.
    bridge = readJson(root / "doctrine/castHumanCenteredBridgeV1.yaml")
    tech = readJson(root / "doctrine/operationTitan7ChatTriggerV2.json")
    arch = readJson(root / "doctrine/luHmOSFourLayerArchitectureV1.json")
    artist = readJson(root / "doctrine/artistFirstArtToolCanonV1.json")
    fnCast = readJson(root / "doctrine/fnCastV1.yaml")
    if bridge["schema"] != "luhmOs.castHumanCenteredBridge.v1":
        raise ValueError("Unknown human-centered bridge contract")
    if bridge["package"] != "LuHmOS" or bridge["entryPoint"] != fnCast["entryPoint"]:
        raise ValueError("CAST package or function identity drift")
    if [x["id"] for x in arch["layers"]] != [
        "coreLibrary", "pluginExtension", "classWidgetOrganization", "stubAdapterBoundary"
    ]:
        raise ValueError("Composition layer identity drift")
    tierMap = tech["escalationTierMap"]
    expectedTiers = [tierMap["technologyFastPath"], tierMap["forFuckSake"],
                     tierMap["scorchedEarth"], tierMap["finalForm"]]
    if expectedTiers != [0, 1, 2, 3]:
        raise ValueError("Technology escalation drift")
    if bridge["technologyEscalation"] != [
        "technologyFastPath", "forFuckSake", "scorchedEarth", "finalForm"
    ]:
        raise ValueError("Human CAST technology routing drift")
    if [x["id"] for x in bridge["humanRegisters"]] != [
        "friend", "underclassman", "assistant", "colleague"
    ]:
        raise ValueError("Human collaboration register drift")
    if [x["id"] for x in bridge["workflowPhases"]] != [
        "conceptDevelopment", "developmentWorkspace", "castBridge", "finalCastEvidence"
    ]:
        raise ValueError("CAST workflow phase drift")
    if any(mode["authorityChanged"] for mode in bridge["humanRegisters"]):
        raise ValueError("Relationship cannot change authority")
    if bridge["artFirstPrecondition"]["originalArtReadOnlyByDefault"] is not True:
        raise ValueError("Original artwork protection required")
    if artist["preservedArtLaw"]["humanDirectorDecidesCompositionActingStoryAndFinish"] is not True:
        raise ValueError("Human artist must direct")
    if any(bridge[key] is not True for key in ["presentationOnly", "zeroAutomaticDispatch", "finalBossIsOutcomeNotTier"]):
        raise ValueError("Human bridge cannot authorize consequence")
    if any(bridge["security"][k] is not True for k in [
        "noRawSql", "noHostOverlay", "noPrivateOriginalArtTransfer", "noUnscopedWorkers",
        "noSourceWrites", "noInstall", "noMerge", "noBuild", "noPublish"
    ]):
        raise ValueError("Human bridge forbidden effect missing")
    if bridge["crownStatus"] != "STOP" or bridge["promotion"] is not False:
        raise ValueError("Crown must stay STOP")
    return bridge


def present(
    taskIds: list[str], *, sourceRef: str, scopeId: str,
    humanRegister: str = "assistant",
    workflowPhase: str = "developmentWorkspace",
    technologyTier: int = 0,
    root: Path = repoRoot,
) -> dict:
    bridge = loadHumanBridge(root)
    registerNames = [x["id"] for x in bridge["humanRegisters"]]
    phaseNames = [x["id"] for x in bridge["workflowPhases"]]
    if humanRegister not in registerNames:
        raise ValueError("Unknown human collaboration register")
    if workflowPhase not in phaseNames:
        raise ValueError("Unknown CAST presentation phase")
    preview = compilePreview(
        taskIds, sourceRef=sourceRef, scopeId=scopeId,
        escalationTier=technologyTier, root=root
    )
    mode = next(x for x in bridge["humanRegisters"] if x["id"] == humanRegister)
    phase = next(x for x in bridge["workflowPhases"] if x["id"] == workflowPhase)
    return {
        "schema": "luhmOs.humanCenteredCastPreview.v1",
        "status": "READ_ONLY_SOURCE_CANDIDATE_NOT_HOST_MOUNTED",
        "package": bridge["package"],
        "entryPoint": bridge["entryPoint"],
        "humanRegister": mode["id"],
        "humanRegisterDescription": mode["description"],
        "workflowPhase": phase["id"],
        "workflowPhaseDescription": phase["description"],
        "technologyTier": bridge["technologyEscalation"][technologyTier],
        "sourceRef": sourceRef,
        "scopeId": scopeId,
        "artSafety": "PROTECTED_ORIGINALS_READ_ONLY_NO_ART_BYTES_ACCESSED",
        "tasks": preview["tasks"],
        "taskCount": preview["taskCount"],
        "castEnvelopesGranted": 0,
        "buildDispatched": False,
        "hostMountVerified": False,
        "originalArtworkAccessed": False,
        "agentWorkersStarted": 0,
        "releaseAuthorized": False,
        "crownGranted": False,
        "crownStatus": "STOP"
    }


def selfTest() -> None:
    loadHumanBridge()
    validRef = "a" * 40
    for register in ("friend", "underclassman", "assistant", "colleague"):
        for tier in range(4):
            packet = present(
                ["chatGptInlineMount"], sourceRef=validRef,
                scopeId="professor/cast-bridge", humanRegister=register,
                technologyTier=tier
            )
            assert packet["humanRegister"] == register
            assert packet["technologyTier"] == [
                "technologyFastPath", "forFuckSake", "scorchedEarth", "finalForm"
            ][tier]
            assert packet["buildDispatched"] is False
            assert packet["castEnvelopesGranted"] == 0
            assert packet["originalArtworkAccessed"] is False
            assert packet["crownGranted"] is False
    for bad in (
        {"humanRegister":"superuser"},
        {"workflowPhase":"release"},
        {"technologyTier":9},
        {"sourceRef":"main"},
        {"scopeId":"; DROP TABLE art;"},
    ):
        try:
            present(
                ["chatGptInlineMount"],
                **{"sourceRef":validRef, "scopeId":"professor/cast-bridge", **bad}
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe human CAST intent accepted")
    print("HUMAN_CENTERED_CAST_READ_ONLY_SELF_TEST_GREEN")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only human-centered LuHmOS CAST view")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--tasks", help="Comma-separated existing canonical queue task IDs")
    parser.add_argument("--source-ref", dest="sourceRef")
    parser.add_argument("--scope-id", dest="scopeId")
    parser.add_argument("--register", dest="humanRegister", default="assistant")
    parser.add_argument("--phase", dest="workflowPhase", default="developmentWorkspace")
    parser.add_argument("--tier", dest="technologyTier", type=int, default=0)
    args = parser.parse_args()
    if args.self_test:
        selfTest()
    if args.tasks:
        if not args.sourceRef or not args.scopeId:
            parser.error("Exact --source-ref and --scope-id required")
        packet = present(
            [name.strip() for name in args.tasks.split(",")],
            sourceRef=args.sourceRef, scopeId=args.scopeId,
            humanRegister=args.humanRegister,
            workflowPhase=args.workflowPhase, technologyTier=args.technologyTier
        )
        print(json.dumps(packet, indent=2))
    elif not args.self_test:
        parser.error("Choose --self-test or --tasks")


if __name__ == "__main__":
    main()
