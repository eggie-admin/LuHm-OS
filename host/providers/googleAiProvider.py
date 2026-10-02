#!/usr/bin/env python3
"""Enterprise Google AI adapter boundary.

This module is intentionally fail-closed until a trusted runtime credential and
an observed entitlement are available. Vendor request details stay isolated
behind invoke(); no browser, Godot, Android, or agent calls Google directly.
"""
from __future__ import annotations

import os
from typing import Any

def isConfigured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())

def invoke(*, capabilityId: str, taskPacket: dict[str, Any]) -> dict[str, Any]:
    if not isConfigured():
        raise RuntimeError("googleAi credential is not configured on the trusted host")
    raise RuntimeError(
        f"googleAi adapter is enterprise-wired but capability is not entitlement-proven: {capabilityId}"
    )
