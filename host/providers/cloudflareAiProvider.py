#!/usr/bin/env python3
"""Enterprise Cloudflare AI adapter boundary.

AI invocation is separate from DNS, TLS, tunnel, and public-exposure authority.
Those capabilities remain Crown-gated and cannot be reached through this file.
"""
from __future__ import annotations

import os
from typing import Any

def isConfigured() -> bool:
    return bool(
        os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
        and os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    )

def invoke(*, capabilityId: str, taskPacket: dict[str, Any]) -> dict[str, Any]:
    if not isConfigured():
        raise RuntimeError("cloudflare AI credential is not configured on the trusted host")
    raise RuntimeError(
        f"cloudflare AI adapter is enterprise-wired but runtime capability is not proven: {capabilityId}"
    )
