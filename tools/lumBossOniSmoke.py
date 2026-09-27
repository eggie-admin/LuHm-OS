#!/usr/bin/env python3
"""Deterministic smoke test for the LuHm boss -> mini Oni tool chain.

No network calls, no provider credentials, no source mutation, and no GREEN authority.
This proves routing/authority/fail-closed contracts against the checked-out source tree.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."
EXPECTED_BRANCH = "feature/oni-pet-activity-dock-v2-20260927"
ROUTER = ROOT / "tools" / "lumTaskRouter.py"
RUNTIME = ROOT / "scripts" / "agentMeshRuntime.py"
OPENAI_HOST = ROOT / "host" / "openai" / "lumHost.py"

EXPECTED_ROUTES: dict[str, list[str]] = {
    "direct": ["Lum"],
    "read": ["Lum", "Kiri"],
    "records": ["Lum", "Fumi"],
    "proof": ["Lum", "Sumi", "DrNao"],
    "patch": ["Lum", "Kugi"],
    "build": ["Lum", "Kugi", "Tetsu", "Kaji", "DrNao"],
    "external": ["Lum", "Momo"],
    "monitor": ["Lum", "DrNao"],
    "release": ["Lum", "DrNao", "ProfessorCrown"],
    "art": ["Lum", "Yume"],
    "media": ["Lum", "Yume", "Sumi"],
    "dictation": ["Lum", "Koe"],
    "asset": ["Lum", "Sumi"],
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must be an object")
    return value


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_router(kind: str, *flags: str, expect_success: bool = True) -> dict[str, Any] | str:
    completed = subprocess.run(
        [sys.executable, str(ROUTER), kind, *flags],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        env={"PATH": os.environ.get("PATH", "")},
    )
    if expect_success:
        require(completed.returncode == 0, f"router {kind} failed: {completed.stderr.strip()}")
        value = json.loads(completed.stdout)
        require(isinstance(value, dict), f"router {kind} output must be object")
        return value
    require(completed.returncode != 0, f"router {kind} negative control unexpectedly passed")
    return (completed.stdout + completed.stderr).strip()


def smoke_source_truth() -> None:
    truth = load_json(ROOT / "doctrine" / "SOURCE_OF_TRUTH.json")
    control = load_json(ROOT / "doctrine" / "ONI_MESH_CONTROL_PLANE_V2.json")

    require(truth.get("source_law") == LAW, "source law drift")
    require(truth.get("authority") == "Professor", "human authority drift")
    require(truth.get("unknown_is_not_green") is True, "UNKNOWN must remain non-GREEN")
    require(truth.get("publication_authority") is False, "source truth gained publication authority")
    require(truth.get("promotion") is False, "source truth gained promotion authority")

    agent = truth.get("agentWorkflowCandidate", {})
    require(agent.get("branch") == EXPECTED_BRANCH, "agent candidate branch drift")
    for key in ("publicationAuthority", "promotionAuthority", "mcpMutationAuthority", "proofImportGreenAuthority"):
        require(agent.get(key) is False, f"agent workflow authority drift: {key}")

    topology = control.get("topology", {})
    require(control.get("boss") == "Lum", "Lum is not the single boss")
    require(control.get("humanAuthority") == "Professor", "Professor authority drift")
    require(topology.get("helperRecruitment") is False, "recursive helper recruitment enabled")
    require(topology.get("directQuestionBypassesMesh") is True, "direct fast-path disabled")
    require(topology.get("maxParallelSupportWorkers") == 3, "support-worker cap drift")
    require(topology.get("maxMutableSourceLanesPerCandidate") == 1, "mutable source-lane cap drift")
    require(topology.get("evidenceTransport") == "REFERENCE_FIRST", "reference-first evidence drift")

    roles = control.get("roles", {})
    require(set(roles) == {"Lum", "Kiri", "Tetsu", "Kaji", "Momo", "Shiori", "DrNao", "Kugi", "Fumi", "Sumi", "Koe", "Yume"}, "Oni roster drift")
    require(roles["Lum"].get("kind") == "boss-router-integrator", "Lum boss role drift")
    for name, role in roles.items():
        if name == "Lum":
            continue
        require(role.get("kind") != "boss-router-integrator", f"{name} became a second boss")
        require(role.get("defaultAuthority", "READ_ONLY") in {"READ_ONLY", "PLAN_ONLY"}, f"{name} gained unsafe default authority")


def smoke_router() -> None:
    for kind, expected_workers in EXPECTED_ROUTES.items():
        report = run_router(kind)
        assert isinstance(report, dict)
        require(report.get("schema") == "luhm-os.task-route.v2", f"{kind} schema drift")
        require(report.get("workers") == expected_workers, f"{kind} route drift: {report.get('workers')}")
        require(report.get("greenAuthority") is False, f"{kind} gained GREEN authority")
        require(report.get("dictationExecutesDirectly") is False, f"{kind} direct dictation execution enabled")
        require(len(report.get("supportWorkers", [])) <= 3, f"{kind} exceeded support cap")

    build = run_router("build")
    assert isinstance(build, dict)
    require(build.get("sourceMutationLanes") == 1, "build mutation lane drift")
    require(build.get("parallelBuilds") == 2, "dual-build lane drift")
    require(build.get("requiresDoctorVerdict") is True, "build lost DrNao adjudication")

    release = run_router("release")
    assert isinstance(release, dict)
    require(release.get("requiresProfessorCrown") is True, "release route bypasses Crown")

    max_legal = run_router("external", "--contested", "--asset-review", "--truth-sensitive")
    assert isinstance(max_legal, dict)
    require(max_legal.get("supportWorkers") == ["Momo", "Shiori", "Sumi"], "max legal support batch drift")
    require(max_legal.get("requiresDoctorVerdict") is True, "truth-sensitive contested route lost DrNao")

    overflow = run_router("art", "--contested", "--external-fact", "--asset-review", expect_success=False)
    assert isinstance(overflow, str)
    require("RED_ROUTER_SUPPORT_PARALLELISM_EXCEEDED" in overflow, "router overflow did not fail closed")


def smoke_authority_runtime() -> None:
    runtime = load_module(RUNTIME, "luhm_agent_mesh_runtime_smoke")

    require(runtime.authorize("ordinary_read") == runtime.Verdict.ALLOW, "ordinary action not allowed")
    require(runtime.authorize("publish") == runtime.Verdict.CROWN_REQUIRED, "publish bypassed Crown")
    require(runtime.authorize("publish", crown_approved=True) == runtime.Verdict.ALLOW, "Crown-approved publish not allowed")
    require(runtime.authorize("self_approve", crown_approved=True) == runtime.Verdict.DENY, "self approval became legal")
    require(runtime.authorize("embed_provider_secret") == runtime.Verdict.DENY, "provider-secret embedding became legal")

    runtime.validate_dispatch((runtime.KIRI, runtime.MOMO, runtime.SHIORI))
    try:
        runtime.validate_dispatch((runtime.KIRI, runtime.MOMO, runtime.SHIORI, runtime.FUMI))
    except ValueError:
        pass
    else:
        raise AssertionError("runtime accepted >3 support workers")

    runtime.validate_builders((runtime.TETSU, runtime.KAJI))
    try:
        runtime.validate_builders((runtime.TETSU, runtime.TETSU))
    except ValueError:
        pass
    else:
        raise AssertionError("runtime accepted duplicate builders")

    runtime.validate_truth_guard(runtime.DR_NAO)
    try:
        runtime.validate_truth_guard(runtime.KUGI)
    except ValueError:
        pass
    else:
        raise AssertionError("runtime accepted non-DrNao truth guard")

    progression = [
        runtime.deployment_state(exact_head_ci=False, provider_receipt=False, apk_receipt=False, device_receipt=False, human_promoted=False),
        runtime.deployment_state(exact_head_ci=True, provider_receipt=False, apk_receipt=False, device_receipt=False, human_promoted=False),
        runtime.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=False, device_receipt=False, human_promoted=False),
        runtime.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=False, human_promoted=False),
        runtime.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=True, human_promoted=False),
        runtime.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=True, human_promoted=True),
    ]
    require(
        progression == [
            "AMBER_EXACT_HEAD_CI_REQUIRED",
            "RED_OPENAI_LIVE_RECEIPT_MISSING",
            "RED_APK_RECEIPT_MISSING",
            "RED_PHYSICAL_SAMSUNG_RECEIPT_MISSING",
            "AMBER_HUMAN_PROMOTION_REQUIRED",
            "GREEN_DEPLOYED",
        ],
        f"deployment gate progression drift: {progression}",
    )


def smoke_openai_host_fail_closed() -> None:
    host = load_module(OPENAI_HOST, "luhm_openai_host_smoke")
    require(host.status({}) == "RED_OPENAI_LIVE_RECEIPT_MISSING", "OpenAI host did not fail closed without secret")
    require(host.status({"OPENAI_API_KEY": "present-for-status-only"}) == "AMBER_OPENAI_MODEL_NOT_CONFIGURED", "OpenAI model gate drift")
    require(
        host.status({"OPENAI_API_KEY": "present-for-status-only", "LUHM_OPENAI_MODEL": "configured-for-status-only"})
        == "AMBER_OPENAI_CONFIG_PRESENT_LIVE_PROBE_REQUIRED",
        "OpenAI live-probe gate drift",
    )


def smoke_exact_source() -> None:
    expected = os.environ.get("EXPECTED_SOURCE_SHA", "").strip()
    if not expected:
        return
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10).strip()
    require(actual == expected, f"exact source drift: expected {expected}, got {actual}")


def main() -> int:
    smoke_exact_source()
    smoke_source_truth()
    smoke_router()
    smoke_authority_runtime()
    smoke_openai_host_fail_closed()
    print("LUHM_BOSS_ONI_SMOKE_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
