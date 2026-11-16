#!/usr/bin/env python3
"""Read-only MCP surface for the existing host-side LuHm OpenAI bridge."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_openai_chat_bridge(server: Any, *, root: Path, annotations: Any) -> None:
    adapter_path = root / "host" / "api" / "luhmOpenAiChatBridge.py"
    if not adapter_path.is_file():
        raise RuntimeError("RED_OPENAI_BRIDGE_ADAPTER_MISSING")
    spec = importlib.util.spec_from_file_location("luhmOpenAiChatBridge", adapter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_OPENAI_BRIDGE_IMPORT")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)

    @server.tool(
        name="luhm_openai_bridge_status",
        title="LuHm OpenAI bridge status",
        description=(
            "Inspect gated OpenAI Responses API configuration, quarantine and billing blocks. "
            "Read-only; does not contact OpenAI or disclose credentials."
        ),
        annotations=annotations,
    )
    def luhm_openai_bridge_status() -> dict[str, Any]:
        return adapter.bridge_status()

    @server.tool(
        name="luhm_openai_bridge_plan",
        title="LuHm OpenAI bridge dry-run plan",
        description=(
            "Plan one bounded OpenAI API request using taskId, exact 40-character sourceRef, "
            "scopeId and capabilityId. No provider call, model execution or billing occurs."
        ),
        annotations=annotations,
    )
    def luhm_openai_bridge_plan(
        taskId: str,
        sourceRef: str,
        scopeId: str,
        capabilityId: str = "interactiveReasoning",
        inputText: str = "",
        maxOutputTokens: int = 256,
    ) -> dict[str, Any]:
        return adapter.plan_request(
            taskId, sourceRef, scopeId, capabilityId, inputText, maxOutputTokens
        )
