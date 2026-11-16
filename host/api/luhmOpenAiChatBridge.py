#!/usr/bin/env python3
"""LuHm OpenAI Responses adapter. Dry-run by default; never stores API keys or prompts."""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
API_SPINE = ROOT / "doctrine" / "apiSpineV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
SOURCE_TRUTH = ROOT / "doctrine" / "currentSourceTruthV3.json"
ENDPOINT = "https://api.openai.com/v1/responses"
MAX_INPUT_CHARS = 6000
MAX_OUTPUT_TOKENS = 512


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("RED_BRIDGE_CONTRACT_NOT_OBJECT")
    return value


def _contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    spine, hold, truth = _json(API_SPINE), _json(QUARANTINE), _json(SOURCE_TRUTH)
    if spine.get("schema") != "luhmOs.apiSpine.v1":
        raise RuntimeError("RED_API_SPINE_SCHEMA")
    if hold.get("schema") != "luhmOs.companyWideOperationalQuarantine.v1":
        raise RuntimeError("RED_QUARANTINE_SCHEMA")
    if truth.get("schema") != "luhmOs.currentSourceTruth.v3":
        raise RuntimeError("RED_SOURCE_TRUTH_SCHEMA")
    return spine, hold, truth


def _require_scope(task_id: str, source_ref: str, scope_id: str) -> None:
    if not task_id or not scope_id or len(task_id) > 160 or len(scope_id) > 160:
        raise ValueError("explicit bounded taskId and scopeId required")
    if not re.fullmatch(r"[0-9a-f]{40}", source_ref or ""):
        raise ValueError("sourceRef must be an exact 40-character Git SHA")


def _blockers(spine: dict[str, Any], hold: dict[str, Any],
              truth: dict[str, Any], env: dict[str, str]) -> list[str]:
    blocked = []
    if hold.get("state") != "RELEASED" or hold.get("activeTaskWorkersAllowed") is not True:
        blocked.append("COMPANY_QUARANTINE")
    if truth.get("publicationAuthority") is not True:
        # Publication is a separate gate, not a prerequisite for local execution.
        pass
    provider = spine.get("providers", {}).get("openAi", {})
    if provider.get("adapterId") != "openAiResponses":
        blocked.append("ADAPTER_CONTRACT")
    if env.get("LUHM_OPENAI_ENABLE_LIVE") != "1":
        blocked.append("LIVE_DISABLED")
    if env.get("LUHM_OPENAI_BILLING_APPROVED") != "1":
        blocked.append("BILLING_NOT_APPROVED")
    if not env.get("OPENAI_API_KEY"):
        blocked.append("MISSING_HOST_SECRET")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", env.get("LUHM_OPENAI_MODEL", "")):
        blocked.append("MODEL_NOT_SELECTED")
    return blocked


def bridge_status(env: dict[str, str] | None = None) -> dict[str, Any]:
    spine, hold, truth = _contracts()
    env = os.environ if env is None else env
    blockers = _blockers(spine, hold, truth, env)
    return {
        "schema": "luhmOs.openAiChatBridgeStatus.v1",
        "adapterId": "openAiResponses",
        "apiSurface": "ResponsesApi",
        "transport": "hostOnly",
        "state": "READY_FOR_REVIEW" if not blockers else "BLOCKED",
        "liveExecutionEnabled": not blockers,
        "blockingConditions": blockers,
        "keyPresentOnHost": bool(env.get("OPENAI_API_KEY")),
        "companyQuarantined": hold.get("state") != "RELEASED",
        "modelSelected": bool(env.get("LUHM_OPENAI_MODEL")),
        "automaticPublishing": False,
        "mutationAuthority": False,
        "providerExecutionProven": False,
        "crownAuthority": False,
    }


def plan_request(task_id: str, source_ref: str, scope_id: str,
                 capability_id: str = "interactiveReasoning",
                 input_text: str = "", max_output_tokens: int = 256,
                 env: dict[str, str] | None = None) -> dict[str, Any]:
    _require_scope(task_id, source_ref, scope_id)
    spine, hold, truth = _contracts()
    provider = spine["providers"]["openAi"]
    if capability_id not in provider.get("capabilityClasses", []):
        raise ValueError("capabilityId not allowed for OpenAI adapter")
    if not isinstance(input_text, str) or len(input_text) > MAX_INPUT_CHARS:
        raise ValueError("input exceeds bounded input size")
    if not isinstance(max_output_tokens, int) or not 16 <= max_output_tokens <= MAX_OUTPUT_TOKENS:
        raise ValueError("maxOutputTokens outside approved bounds")
    env = os.environ if env is None else env
    blockers = _blockers(spine, hold, truth, env)
    return {
        "schema": "luhmOs.openAiChatBridgePlan.v1",
        "taskId": task_id,
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "capabilityId": capability_id,
        "providerId": "openAi",
        "adapterId": "openAiResponses",
        "promptSha256": hashlib.sha256(input_text.encode("utf-8")).hexdigest(),
        "promptCharacters": len(input_text),
        "maxOutputTokens": max_output_tokens,
        "state": "BLOCKED" if blockers else "ELIGIBLE_NOT_EXECUTED",
        "blockingConditions": blockers,
        "networkCalls": 0,
        "estimatedCostUsd": None,
        "providerExecutionProven": False,
        "mutationAuthority": False,
        "crownAuthority": False,
    }


def _extract_output(body: dict[str, Any]) -> str:
    fragments: list[str] = []
    for item in body.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if isinstance(part, dict) and part.get("type") == "output_text":
                fragments.append(str(part.get("text", "")))
    return "\n".join(fragments)


def execute_request(task_id: str, source_ref: str, scope_id: str, input_text: str,
                    capability_id: str = "interactiveReasoning", max_output_tokens: int = 256,
                    *, transport: Callable[..., Any] | None = None,
                    env: dict[str, str] | None = None) -> dict[str, Any]:
    """Only an approved host may call this function; never exposed as an MCP tool."""
    env = os.environ if env is None else env
    plan = plan_request(task_id, source_ref, scope_id, capability_id,
                        input_text, max_output_tokens, env)
    if plan["blockingConditions"]:
        raise PermissionError("RED_OPENAI_GATE:" + ",".join(plan["blockingConditions"]))
    model = env["LUHM_OPENAI_MODEL"]
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({
            "model": model, "input": input_text,
            "max_output_tokens": max_output_tokens, "store": False,
        }).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + env["OPENAI_API_KEY"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    send = transport or urllib.request.urlopen
    started = datetime.now(timezone.utc).isoformat()
    try:
        with send(request, timeout=20) as response:
            payload = json.loads(response.read(262145))
        if not isinstance(payload, dict):
            raise ValueError("RED_PROVIDER_RESPONSE_SHAPE")
    except urllib.error.HTTPError as exc:
        # Never relay provider response bodies, request headers, or credentials.
        raise RuntimeError("OPENAI_HTTP_" + str(exc.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("OPENAI_NETWORK_UNAVAILABLE") from None

    return {
        "schema": "luhmOs.providerExecutionReceipt.v1",
        "taskId": task_id,
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "providerId": "openAi",
        "adapterId": "openAiResponses",
        "capabilityId": capability_id,
        "state": "OBSERVED_PROVIDER_RESPONSE",
        "startedAt": started,
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "evidenceRefs": [str(payload.get("id", "UNKNOWN"))],
        "outputText": _extract_output(payload),
        "model": str(payload.get("model", model)),
        "greenAuthority": False,
        "crownAuthority": False,
        "mutationAuthority": False,
        "requiresUrdAdjudication": True,
        "requiresLumReconciliation": True,
    }


if __name__ == "__main__":
    print(json.dumps(bridge_status(), indent=2))
