#!/usr/bin/env python3
"""LuHm art VM cabinet four-by-four, exact-source and historical-warning review. No host writes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/artVmCabinetFourByFourV1.json"
SURFACES = ("googleVm", "androidSamsung", "appleIos", "openLinux")
LAYERS = ("firmware", "vmExecution", "artStudio", "appHandoff")
ROLES = ("lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "yume")
THREADS = ("python3", "json", "sqliteStrict", "htmlCssJs", "sha256", "ai", "godotBlenderFfmpeg")
HISTORICAL = ("runtimeDirectives", "sourceDigestShapes", "goddessKey", "commitBudget")
SKILLS = ("agents/shared/ONI_PROTOCOL_V2.md", "agents/goddessSharedSystemsPractice/SKILL.md",
          "agents/yumeArtOni/SKILL.md")
REF = "agents/shared/artVmCabinetFourByFour.md"
FORBIDDEN = ("productionMerge", "firmwareFlash", "grubInstall", "gpartedWrite",
             "kernelUpgrade", "hostDriverLoad", "androidAvbUnlock", "appleIosGuestVm",
             "newPaidGpuVm", "publicPublish", "agentUnquarantine", "overwriteArtMasters",
             "sqlServerStart")
APPROVED_SITES = {"docs.cloud.google.com", "source.android.com",
                  "developer.apple.com", "docs.kernel.org", "docs.github.com"}

class CabinetAuditError(ValueError):
    pass

def require(condition: bool, code: str) -> None:
    if not condition:
        raise CabinetAuditError(code)

def verified_file(root: Path, rel: object) -> Path:
    require(type(rel) is str and bool(rel) and len(rel) < 180, "SOURCE_PATH_SHAPE")
    require(not Path(rel).is_absolute() and "\\" not in rel and ".." not in Path(rel).parts,
            "SOURCE_PATH_TRAVERSAL")
    p = root / rel
    require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root.resolve()),
            "SOURCE_FILE_NOT_CANONICAL")
    return p

def audit(m: dict, root: Path = ROOT) -> dict:
    require(type(m) is dict and m.get("schema") == "luhmOs.artVmCabinetFourByFour.v1",
            "CONTRACT_SCHEMA")
    require(m.get("authority") == "Professor" and m.get("status") ==
            "PROPOSED_ART_VM_CABINET_SOURCE_ONLY" and m.get("crownStatus") == "STOP",
            "PROPOSED_ONLY")
    require(m.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.",
            "AUTHORITY_LAW")
    surfaces = m.get("surfaces", [])
    require(type(surfaces) is list and [r.get("id") for r in surfaces] == list(SURFACES)
            and m.get("dimensions") == list(LAYERS), "SURFACE_LAYER_ORDER")
    cells = m.get("matrix", [])
    require(type(cells) is list and len(cells) == 16, "EXACT_4X4")
    for index, row in enumerate(cells):
        require(type(row) is dict and row == {
            "index": index, "hex": f"0x{index:02X}",
            "surface": SURFACES[index // 4], "layer": LAYERS[index % 4],
            "sourceProof": "DOCS_AND_REPO_SOURCE_ONLY", "deviceProof": False
        }, "4X4_LOGICAL_HEX_OR_PROOF")
    for surface in surfaces:
        require(surface.get("runtimeProof") is None, "UNEXPECTED_SURFACE_RUNTIME_PROOF")
        require(surface.get("role") in ROLES and all(type(surface.get(k)) is str and surface[k]
                for k in ("firmware", "execution", "art", "adapter")), "SURFACE_BOUNDARY")
    require("iOSAppSandboxNoGeneralPurposeGuestVM" == surfaces[2]["execution"],
            "IOS_VM_FALSE_CLAIM")
    require("OEM_AVB_KNOX_AND_GKI_KMI_PRESERVED" == surfaces[1]["firmware"],
            "ANDROID_BOOT_FALSE_CLAIM")
    require("providerManagedNotGuestEditable" == surfaces[0]["firmware"],
            "CLOUD_HOST_AUTHORITY")
    require("hostDistroKernelAndPcGrubOnlyWhenPresent" == surfaces[3]["firmware"],
            "LINUX_GRUB_AUTHORITY")
    threads = m.get("commonThreads", [])
    require(type(threads) is list and [r.get("id") for r in threads] == list(THREADS),
            "COMMON_TYPED_THREADS")
    require(all(item.get("authority") in ("sourceOnly", "dataNotPermission", "notPublicSql",
                "uiNotFirmware", "notAuthority", "neverSelfPromotes", "runtimeProofRequired")
                for item in threads), "COMMON_THREADS_AUTHORITY")
    require(m.get("pipeline") == ["resolveExactSource", "classifyRightsAndDevice",
            "selectMinimumSurface", "boundTypedInput", "renderOrSourcePlan",
            "testAdversarialCases", "collectShaAndLogEvidence", "humanReviewOrStop"],
            "PIPELINE_ORDER")
    roles = m.get("roles", [])
    require(type(roles) is list and [r.get("id") for r in roles] == list(ROLES)
            and all(r.get("mutates") is False for r in roles), "CABINET_ROLE_AUTHORITY")
    warn = m.get("historicalWarnings", [])
    require(type(warn) is list and [r.get("id") for r in warn] == list(HISTORICAL),
            "HISTORICAL_LOG_ORDER")
    for row in warn:
        require(type(row.get("runId")) is int and row["runId"] > 0 and
                type(row.get("sourceSha")) is str and len(row["sourceSha"]) == 40
                and all(c in "0123456789abcdef" for c in row["sourceSha"]),
                "HISTORICAL_SOURCE_IDENTITY")
        require(type(row.get("symptom")) is str and type(row.get("safety")) is str
                and bool(row["symptom"]) and bool(row["safety"]), "HISTORICAL_LESSON")
    obs = m.get("sourceObservations", {})
    require(obs.get("candidateNotRuntime") is True and obs.get("unknownStaysUnknown") is True,
            "CANDIDATE_RUNTIME_CLAIM")
    require(all(obs.get(k) is False for k in (
            "physicalSamsungProven", "iosNativeBuildProven", "googleGpuVmStarted",
            "actualDockerComputeImageBuilt", "physicalGpuProven", "iosVmSupportedAsGeneralGuest",
            "agentWorkerReleased")), "FALSE_DEVICE_OR_AGENT_PROOF")
    require(m.get("allowedMutations") == ["draftSourceCandidate", "targetedTests",
            "existingWorkflowCIOnly"] and m.get("forbiddenMutations") == list(FORBIDDEN),
            "MUTATION_AUTHORITY_ESCALATION")
    for k in ("noAdditionalVendorServices", "noHiddenAsync", "noSecretsInPublicReceipts",
              "noSourceOnlyGreenRuntime", "noSelfApproval"):
        require(m.get(k) is True, "REQUIRED_SAFETY_GUARD")
    require(m.get("promotionGates") == ["sourceSHAAndScopeBound", "ownedArtProvenance",
            "exactHardwareAbiOrUnknown", "platformDriverCapabilityReceipt",
            "negativeTestsGreenAtExactHead", "artifactBuildAndRuntimeProof",
            "humanReleaseApproval"], "PROMOTION_GATES")
    sources = m.get("sourceRefs", [])
    require(type(sources) is list and len(sources) == len(set(sources))
            and len(sources) >= 11, "SOURCE_REFERENCE_INVENTORY")
    receipts = []
    for rel in sources:
        p = verified_file(root, rel)
        data = p.read_bytes()
        require(0 < len(data) <= 150000, "SOURCE_FILE_SIZE")
        receipts.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest()})
    require(m.get("agentSkillInstructionsPath") == REF, "SKILL_REFERENCE")
    instruction = verified_file(root, REF).read_text(encoding="utf-8")
    for text in ("Google VM", "Android/Samsung", "Apple iOS/iPadOS",
                 "Linux", "CROWN STOP", "Lum", "Urd", "Belldandy", "Skuld", "Yume"):
        require(text in instruction, "SKILL_RUBRIC_INCOMPLETE")
    for path in SKILLS:
        content = verified_file(root, path).read_text(encoding="utf-8")
        require(REF in content and "artVmCabinetFourByFourV1.json" in content,
                "SKILL_NOT_BOUND:" + path)
    docs = m.get("referenceDocs", [])
    require(type(docs) is list and len(docs) >= 6
            and {item.get("surface") for item in docs} == set(SURFACES),
            "OFFICIAL_DOC_COVERAGE")
    for item in docs:
        url = item.get("url")
        require(type(url) is str and url.startswith("https://")
                and urlparse(url).hostname in APPROVED_SITES
                and urlparse(url).username is None and urlparse(url).password is None,
                "UNTRUSTED_REFERENCE_URL")
    hold = json.loads(verified_file(root, "doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    require(hold.get("state") == "QUARANTINED" and hold.get("activeTaskWorkersAllowed") is False
            and hold.get("hiddenAsyncAgents") is False and hold.get("crownStatus") == "STOP",
            "AGENT_QUARANTINE_BREAK")
    cabinet = json.loads(verified_file(root, "doctrine/lumGoddessCabinetV1.json").read_text(encoding="utf-8"))
    require(cabinet.get("boss") == "lum" and {m.get("id") for m in cabinet.get("members", [])}
            == set(ROLES[:4]), "CANONICAL_CABINET_IDENTITY")
    return {"schema": "luhmOs.artVmCabinet4x4Receipt.v1",
            "status": "AMBER_SOURCE_REVIEW_ONLY", "cells": len(cells),
            "surfaces": list(SURFACES), "typedThreads": list(THREADS),
            "warningsHistorical": len(warn), "skillBindingsVerified": len(SKILLS),
            "sourceFileDigests": receipts, "actualArtVmStarted": False,
            "physicalDeviceProven": False, "workerActivated": False,
            "firmwareMutated": False, "sourceOnly": True, "crownStatus": "STOP",
            "contractSha256": hashlib.sha256(json.dumps(m, sort_keys=True,
                 separators=(",", ":")).encode("utf-8")).hexdigest()}

if __name__ == "__main__":
    print(json.dumps(audit(json.loads(CONTRACT.read_text(encoding="utf-8"))), sort_keys=True))
