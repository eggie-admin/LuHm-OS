#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."
EXPECTED_AGENT_BRANCH = "feature/oni-pet-activity-dock-v2-20260927"


def load_json(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def route(kind: str, *flags: str) -> dict[str, Any]:
    cmd = [sys.executable, str(ROOT / "tools/lumTaskRouter.py"), kind, *flags]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    result = json.loads(completed.stdout)
    require(isinstance(result, dict), f"route {kind} did not return object")
    require(result.get("greenAuthority") is False, f"route {kind} gained GREEN authority")
    require(len(result.get("supportWorkers", [])) <= 3, f"route {kind} exceeded support cap")
    return result


def fake_openai_probe(lum_host) -> dict[str, Any]:
    captured: dict[str, Any] = {}
    payload = {
        "id": "resp_luhm_smoke",
        "model": "luhm-smoke-model",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "LUHM_OPENAI_OK"}],
            }
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(payload).encode("utf-8")

    def fake_opener(request, timeout=45.0):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    receipt = lum_host.probe(
        env={"OPENAI_API_KEY": "test-key-not-secret", "LUHM_OPENAI_MODEL": "luhm-smoke-model"},
        opener=fake_opener,
        receipt_path=None,
    )
    require(receipt.get("status") == "OPENAI_LIVE_GREEN", "mock host probe failed")
    require(receipt.get("credential_persisted") is False, "mock probe claims credential persistence")
    require(receipt.get("prompt_persisted") is False, "mock probe claims prompt persistence")
    require(receipt.get("output_persisted") is False, "mock probe claims output persistence")
    body = captured.get("body", {})
    require(body.get("store") is False, "Responses smoke must use store=false")
    require("Lum" in str(body.get("instructions", "")), "Lum boss instructions missing from host request")
    require(LAW in str(body.get("instructions", "")), "source law missing from host request")
    return {
        "status": receipt["status"],
        "network": "MOCKED_NO_EXTERNAL_CALL",
        "store": body.get("store"),
        "credentialPersisted": receipt.get("credential_persisted"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha", default="UNKNOWN")
    parser.add_argument("--output", type=Path, default=Path("build/boss-smoke/luhm-boss-chain-smoke.json"))
    args = parser.parse_args()

    truth = load_json("doctrine/SOURCE_OF_TRUTH.json")
    control = load_json("doctrine/ONI_MESH_CONTROL_PLANE_V2.json")
    mesh = load_module("luhm_agent_mesh_runtime_smoke", "scripts/agentMeshRuntime.py")
    lum_host = load_module("luhm_openai_host_smoke", "host/openai/lumHost.py")

    require(truth.get("source_law") == LAW, "source law drift")
    require(truth.get("authority") == "Professor", "Professor authority drift")
    require(truth.get("unknown_is_not_green") is True, "UNKNOWN became GREEN")
    require(truth.get("promotion") is False, "unproven promotion")
    require(truth.get("agentWorkflowCandidate", {}).get("branch") == EXPECTED_AGENT_BRANCH, "agent branch drift")
    require(control.get("boss") == "Lum", "Lum is not sole boss")
    require(control.get("humanAuthority") == "Professor", "human authority drift")
    require(control.get("topology", {}).get("helperRecruitment") is False, "helper recursion enabled")
    require(control.get("topology", {}).get("maxParallelSupportWorkers") == 3, "support worker cap drift")
    require(control.get("topology", {}).get("maxMutableSourceLanesPerCandidate") == 1, "mutable lane drift")

    # Required task-envelope fields are doctrine, not optional prose.
    required_fields = list(control.get("requiredTaskEnvelope", []))
    require(len(required_fields) >= 10, "task-envelope contract unexpectedly small")
    envelope = {
        "taskId": "smoke-001",
        "intent": "verify boss routing",
        "scope": "agent-control-plane",
        "repository": "eggie-admin/LuHm-OS",
        "sourceRef": args.source_sha,
        "authorityClass": "READ_ONLY",
        "allowedCapabilities": ["read", "route", "verify"],
        "forbiddenCapabilities": ["publish", "production_sign", "self_approve"],
        "evidenceRefs": ["doctrine/SOURCE_OF_TRUTH.json"],
        "requiredOutputs": ["smoke-receipt"],
        "stopConditions": ["authority-drift", "source-drift", "unknown-state"],
        "budget": {"supportWorkersMax": 3, "buildWorkersMax": 2},
    }
    require(all(field in envelope for field in required_fields), "task envelope missing required field")
    require(envelope["authorityClass"] in set(control.get("authorityClasses", [])), "invalid authority class")

    expected_routes = {
        "direct": (["Lum"], ()),
        "records": (["Lum", "Fumi"], ()),
        "proof": (["Lum", "Sumi", "DrNao"], ()),
        "patch": (["Lum", "Kugi", "DrNao"], ()),
        "build": (["Lum", "Kugi", "Tetsu", "Kaji", "DrNao"], ()),
        "dictation": (["Lum", "Koe"], ()),
        "release": (["Lum", "DrNao", "ProfessorCrown"], ()),
        "external-contested": (["Lum", "Momo", "Shiori", "DrNao"], ("--contested",)),
        "read-truth": (["Lum", "Kiri", "DrNao"], ("--truth-sensitive",)),
    }
    route_receipts: dict[str, Any] = {}
    for label, (workers, flags) in expected_routes.items():
        kind = label.split("-")[0]
        result = route(kind, *flags)
        require(result.get("workers") == workers, f"route drift for {label}: {result.get('workers')}")
        if kind == "patch":
            require(result.get("sourceMutationLanes") == 1, "patch did not reserve one mutable lane")
            require(result.get("requiresDoctorVerdict") is True, "patch bypassed DrNao")
        if kind == "build":
            require(result.get("parallelBuilds") == 2, "dual-build route drift")
            require(result.get("requiresDoctorVerdict") is True, "build bypassed DrNao")
        if kind == "dictation":
            require(result.get("dictationExecutesDirectly") is False, "dictation gained execution authority")
        if kind == "release":
            require(result.get("requiresProfessorCrown") is True, "release bypassed Crown")
        route_receipts[label] = {
            "workers": result.get("workers"),
            "supportWorkers": result.get("supportWorkers"),
            "sourceMutationLanes": result.get("sourceMutationLanes"),
            "parallelBuilds": result.get("parallelBuilds"),
            "doctor": result.get("requiresDoctorVerdict"),
            "crown": result.get("requiresProfessorCrown"),
        }

    # Runtime authority tests.
    require(mesh.authorize("recursive_recruit") == mesh.Verdict.DENY, "recursive recruitment not denied")
    require(mesh.authorize("self_approve") == mesh.Verdict.DENY, "self approval not denied")
    require(mesh.authorize("embed_provider_secret") == mesh.Verdict.DENY, "provider-secret embedding not denied")
    require(mesh.authorize("merge_main") == mesh.Verdict.CROWN_REQUIRED, "merge_main did not require Crown")
    require(mesh.authorize("merge_main", crown_approved=True) == mesh.Verdict.ALLOW, "approved merge_main not recognized")

    mesh.validate_dispatch([mesh.KIRI, mesh.MOMO, mesh.FUMI])
    try:
        mesh.validate_dispatch([mesh.KIRI, mesh.MOMO, mesh.FUMI, mesh.YUME])
    except ValueError:
        pass
    else:
        raise AssertionError("support-worker overflow was not rejected")

    mesh.validate_builders(mesh.BUILD_ONI)
    mesh.validate_truth_guard(mesh.DR_NAO)
    require(mesh.provider_ready({}) is False, "empty provider env incorrectly ready")
    require(mesh.provider_ready({"OPENAI_API_KEY": "test-key-not-secret"}) is True, "provider presence check broken")

    state_tests = {
        "no_ci": mesh.deployment_state(exact_head_ci=False, provider_receipt=False, apk_receipt=False, device_receipt=False, human_promoted=False),
        "no_provider": mesh.deployment_state(exact_head_ci=True, provider_receipt=False, apk_receipt=False, device_receipt=False, human_promoted=False),
        "no_apk": mesh.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=False, device_receipt=False, human_promoted=False),
        "no_device": mesh.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=False, human_promoted=False),
        "no_crown": mesh.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=True, human_promoted=False),
        "all_green": mesh.deployment_state(exact_head_ci=True, provider_receipt=True, apk_receipt=True, device_receipt=True, human_promoted=True),
    }
    require(state_tests["no_device"] == "RED_PHYSICAL_SAMSUNG_RECEIPT_MISSING", "device gate precedence drift")
    require(state_tests["all_green"] == "GREEN_DEPLOYED", "positive deployment-state contract drift")
    require(truth.get("status") == "RED_DEVICE_PRESENTATION_BLOCKS_CROWN", "source truth failed to preserve real device RED")

    host_receipt = fake_openai_probe(lum_host)
    require(lum_host.status({}) == "RED_OPENAI_LIVE_RECEIPT_MISSING", "empty host config status drift")
    require(lum_host.status({"OPENAI_API_KEY": "test-key-not-secret"}) == "AMBER_OPENAI_MODEL_NOT_CONFIGURED", "model-missing status drift")
    require(lum_host.status({"OPENAI_API_KEY": "test-key-not-secret", "LUHM_OPENAI_MODEL": "luhm-smoke-model"}) == "AMBER_OPENAI_CONFIG_PRESENT_LIVE_PROBE_REQUIRED", "configured host status drift")

    receipt = {
        "schema": "luhm-os.boss-chain-smoke.v1",
        "sourceSha": args.source_sha,
        "status": "BOSS_CHAIN_SMOKE_GREEN",
        "systemSourceTruthStatus": truth.get("status", "UNKNOWN"),
        "boss": "Lum",
        "humanAuthority": "Professor",
        "taskEnvelope": "GREEN",
        "routes": route_receipts,
        "runtimeAuthority": "GREEN",
        "mockOpenAiAdapter": host_receipt,
        "deploymentStateTests": state_tests,
        "liveProviderCalled": False,
        "repositoryMutatedBySmoke": False,
        "greenAuthority": False,
        "crownAuthorized": False,
        "note": "Smoke GREEN proves the boss/tool-chain contract, not product/device/release GREEN.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("LUHM_BOSS_CHAIN_SMOKE_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
