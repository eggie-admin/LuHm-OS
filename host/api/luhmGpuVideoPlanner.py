#!/usr/bin/env python3
"""Source-only LuHm GPU video minute-chunk planner and resource admission evaluator.

A user-provided GPU capacity report is NOT trusted telemetry. This module
does not load models, allocate VRAM, contact providers, encode media, pay for
GPU usage or run jobs. All stage and chunk IDs are deterministic and bounded.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
DOCTRINE = ROOT / "doctrine" / "remoteGpuVideoPipelineV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
ID = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
STATES = ("localhost", "privateHost", "remoteGpu", "enterprise")
VRAM_MODES = ("conservative", "balanced", "maxApproved")


def _read(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise RuntimeError("RED_VIDEO_CONTRACT_SHAPE")
    return result


def _contract() -> dict[str, Any]:
    policy = _read(DOCTRINE)
    if policy.get("schema") != "luhmOs.remoteGpuVideoPipeline.v1":
        raise RuntimeError("RED_VIDEO_CONTRACT_SCHEMA")
    if [p["id"] for p in policy.get("fourSecurityProfiles", [])] != list(STATES):
        raise RuntimeError("RED_VIDEO_SECURITY_PROFILES")
    if [x["id"] for x in policy.get("fourLanes", [])] != [
        "security", "compute", "media", "evidence"
    ]:
        raise RuntimeError("RED_VIDEO_FOUR_LANES")
    for ref in policy.get("anchorRefs", []):
        if (not isinstance(ref, str) or ref.startswith("/") or
                ".." in Path(ref).parts or not (ROOT / ref).is_file()):
            raise RuntimeError("RED_VIDEO_CANON_ANCHOR")
    return policy


def _identifier(value: str, name: str) -> str:
    if type(value) is not str or ID.fullmatch(value) is None:
        raise ValueError(f"{name} must be a bounded camelHump identifier")
    return value


def _int(value: Any, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"invalid {label}")
    return value


def assess_vram(report: Mapping[str, Any] | None, *, mode: str,
                model_estimate_mib: int) -> dict[str, Any]:
    """Compute an *untrusted* upper bound; never grants access to a GPU."""
    if mode not in VRAM_MODES:
        raise ValueError("unrecognized VRAM mode")
    _int(model_estimate_mib, 1, 1048576, "model VRAM estimate")
    if report is None:
        return {
            "state": "UNKNOWN_NO_TRUSTED_GPU_RECEIPT", "reported": False,
            "candidateUsableMiB": 0, "modelEstimateMiB": model_estimate_mib,
            "telemetryTrusted": False, "allocationAuthorized": False,
        }
    if not isinstance(report, Mapping) or set(report) != {
        "totalMiB", "freeMiB", "reservedMiB"
    }:
        raise ValueError("bounded GPU report requires exactly three numeric fields")
    total = _int(report["totalMiB"], 1024, 1048576, "total VRAM")
    free = _int(report["freeMiB"], 0, total, "free VRAM")
    reserved = _int(report["reservedMiB"], 0, total, "reserved VRAM")
    if free + reserved > total:
        raise ValueError("inconsistent reported GPU memory counters")
    # Do not treat entire physical VRAM or current free bytes as available.
    # Preserve at least 1 GiB of currently free VRAM, and additional policy
    # cap relative to total. Real host scheduler must remeasure at admission.
    cap = {"conservative": 0.60, "balanced": 0.75, "maxApproved": 0.90}[mode]
    upper = max(0, min(math.floor(total * cap), free - 1024))
    return {
        "state": "CAPACITY_FIT_SUGGESTED_UNVERIFIED" if upper >= model_estimate_mib
                 else "CAPACITY_INSUFFICIENT_OR_UNVERIFIED",
        "reported": True, "totalMiB": total, "freeMiB": free,
        "reservedMiB": reserved, "candidateUsableMiB": upper,
        "modelEstimateMiB": model_estimate_mib,
        "safetyReserveMiB": total - upper,
        "telemetryTrusted": False, "allocationAuthorized": False,
    }


def status() -> dict[str, Any]:
    p = _contract()
    q = _read(QUARANTINE)
    return {
        "schema": "luhmOs.remoteGpuVideoStatus.v1",
        "state": p["status"], "securityProfiles": [x["id"] for x in p["fourSecurityProfiles"]],
        "lanes": [x["id"] for x in p["fourLanes"]],
        "deliverySeconds": p["video"]["deliverySeconds"],
        "modelShotSecondsDefault": p["video"]["modelShotSecondsDefault"],
        "activeGpuDrivers": p["gpu"]["activeDrivers"],
        "companyQuarantine": q.get("state"),
        "actualGpuTelemetryAvailable": False,
        "gpuWorkerConnected": False,
        "costApproved": False,
        "videoRendered": False,
        "greenAuthority": False, "crownAuthority": False,
    }


def plan(*, task_id: str, source_ref: str, scope_id: str, seconds: int,
         prompt: str, width: int = 1280, height: int = 720, fps: int = 24,
         model_shot_seconds: int = 6, vram_mode: str = "balanced",
         model_vram_estimate_mib: int = 8192,
         reported_gpu: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a private safe plan for shots grouped into <=60-sec deliverables."""
    p = _contract()
    q = _read(QUARANTINE)
    _identifier(task_id, "taskId")
    _identifier(scope_id, "scopeId")
    if not isinstance(source_ref, str) or SHA.fullmatch(source_ref) is None:
        raise ValueError("sourceRef must be exact lowercase 40-character SHA")
    if type(prompt) is not str or not 1 <= len(prompt.strip()) <= 1024:
        raise ValueError("prompt must be nonempty and at most 1024 characters")
    _int(seconds, 1, p["video"]["maxProjectSeconds"], "total seconds")
    _int(model_shot_seconds, 1, 12, "model shot seconds")
    _int(width, 256, 3840, "width")
    _int(height, 256, 2160, "height")
    if width % 2 or height % 2:
        raise ValueError("width and height must be even for H264 encoding")
    if type(fps) is not int or fps not in p["video"]["fpsAllowed"]:
        raise ValueError("fps not allowlisted")
    memory = assess_vram(reported_gpu, mode=vram_mode,
                         model_estimate_mib=model_vram_estimate_mib)
    prompt_sha = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
    minute_rows: list[dict[str, Any]] = []
    shot_count = 0
    for minute_start in range(0, seconds, p["video"]["deliverySeconds"]):
        minute_index = minute_start // 60
        delivered_seconds = min(60, seconds - minute_start)
        shots = []
        for shot_start in range(0, delivered_seconds, model_shot_seconds):
            shot_count += 1
            duration = min(model_shot_seconds, delivered_seconds - shot_start)
            shot_id = "shot" + hashlib.sha256(
                f"{task_id}:{source_ref}:{scope_id}:{minute_index}:{shot_start}".encode("ascii")
            ).hexdigest()[:20]
            shots.append({
                "shotId": shot_id, "startSecond": minute_start + shot_start,
                "durationSeconds": duration, "status": "PLANNED_NOT_SUBMITTED",
                "operationId": None, "artifactSha256": None,
                "resumeRequiresVerifiedResult": True,
            })
        minute_rows.append({
            "minuteIndex": minute_index,
            "startSecond": minute_start,
            "durationSeconds": delivered_seconds,
            "status": "PLANNED_ONLY",
            "shots": shots,
            "artifactPointer": None,
            "videoSha256": None,
            "ffprobeVerified": False,
            "continuityVerified": False,
        })
    if shot_count > p["video"]["maxSubshotsPerPlan"]:
        raise ValueError("total shot count exceeds bounded plan")
    blockers = ["GPU_WORKER_NOT_CONNECTED", "GPU_TELEMETRY_UNATTESTED",
                "PROVIDER_MODEL_SHOT_LIMIT_UNVERIFIED", "MISSING_PER_JOB_COST_APPROVAL",
                "VIDEO_RIGHTS_NOT_VERIFIED", "EXACT_SOURCE_RUNTIME_UNPROVEN"]
    if q.get("state") != "RELEASED" or q.get("activeTaskWorkersAllowed") is not True:
        blockers.append("COMPANY_WORKER_QUARANTINE")
    if memory["state"] != "CAPACITY_FIT_SUGGESTED_UNVERIFIED":
        blockers.append("GPU_MEMORY_ADMISSION_UNPROVEN")
    return {
        "schema": "luhmOs.remoteGpuMinutePlan.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "promptSha256": prompt_sha, "rawPromptReturned": False,
        "seconds": seconds, "frameRate": fps, "width": width, "height": height,
        "vramMode": vram_mode, "vram": memory,
        "minuteCount": len(minute_rows), "modelShotCount": shot_count,
        "minuteDeliveries": minute_rows, "status": "HOLD_NOT_ADMITTED",
        "blockingConditions": blockers,
        "reviewCadence": "afterEachVerified60SecondOrFinalShorterChunk",
        "renderSchedulingStarted": False, "gpuMemoryAllocated": False,
        "networkCalls": 0, "paidProviderCalls": 0, "estimatedCostUsd": None,
        "snapshotActuallyStored": False, "publicationAllowed": False,
        "greenAuthority": False, "crownAuthority": False,
    }


def verify_minute_metadata(packet: Mapping[str, Any], minute_index: int,
                           received_shots: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Only compares signed-looking *metadata*, not actual file contents.

    A future trusted worker must independently hash/read bytes and ffprobe.
    """
    if not isinstance(packet, Mapping) or packet.get("schema") != "luhmOs.remoteGpuMinutePlan.v1":
        raise ValueError("invalid parent plan")
    _int(minute_index, 0, 59, "minute index")
    if type(received_shots) is not list:
        raise ValueError("shot receipt collection required")
    minutes = packet.get("minuteDeliveries")
    if not isinstance(minutes, list) or minute_index >= len(minutes):
        raise ValueError("minute is not in bounded plan")
    expected = minutes[minute_index]["shots"]
    if len(received_shots) != len(expected):
        return {"state": "STOP_COUNT_MISMATCH", "bytesProven": False,
                "greenAuthority": False}
    for a, b in zip(expected, received_shots):
        if (not isinstance(b, Mapping) or set(b.keys()) !=
                {"shotId", "artifactSha256", "durationSeconds"} or
                b.get("shotId") != a["shotId"] or
                b.get("durationSeconds") != a["durationSeconds"] or
                not isinstance(b.get("artifactSha256"), str) or
                DIGEST.fullmatch(b["artifactSha256"]) is None):
            return {"state": "STOP_METADATA_MISMATCH", "bytesProven": False,
                    "greenAuthority": False}
    return {
        "state": "METADATA_CONSISTENT_UNVERIFIED",
        "minuteIndex": minute_index, "shotsDescribed": len(expected),
        "bytesProven": False, "ffprobeVerified": False,
        "publisherSignatureVerified": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
