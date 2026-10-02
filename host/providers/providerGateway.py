#!/usr/bin/env python3
"""Enterprise provider gateway for LuHm OS.

GitHub is compatibility layer #2. This module resolves provider adapters and
credential presence at runtime without exposing secret values. It does not
grant GREEN, Crown, publication, DNS, tunnel, or deployment authority.
"""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class ProviderSpec:
    providerId: str
    adapterModule: str
    requiredSecretRefs: tuple[str, ...]
    entitlementRequired: bool
    networkMutationAuthority: bool = False

providerSpecs = {
    "openAi": ProviderSpec(
        providerId="openAi",
        adapterModule="host.providers.openAiProvider",
        requiredSecretRefs=("OPENAI_API_KEY",),
        entitlementRequired=True,
    ),
    "googleAi": ProviderSpec(
        providerId="googleAi",
        adapterModule="host.providers.googleAiProvider",
        requiredSecretRefs=("GEMINI_API_KEY",),
        entitlementRequired=True,
    ),
    "cloudflare": ProviderSpec(
        providerId="cloudflare",
        adapterModule="host.providers.cloudflareAiProvider",
        requiredSecretRefs=("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"),
        entitlementRequired=True,
    ),
}

def hasSecretRef(secretRefId: str) -> bool:
    return bool(os.environ.get(secretRefId, "").strip())

def loadAdapter(providerId: str) -> Any:
    spec = providerSpecs.get(providerId)
    if spec is None:
        raise KeyError(f"unknown providerId: {providerId}")
    return importlib.import_module(spec.adapterModule)

def getCredentialState(providerId: str) -> str:
    spec = providerSpecs.get(providerId)
    if spec is None:
        return "unknown"
    return "present" if all(hasSecretRef(name) for name in spec.requiredSecretRefs) else "missing"

def getAdapterState(providerId: str) -> str:
    try:
        adapter = loadAdapter(providerId)
    except Exception:
        return "unknown"

    checkFn: Callable[[], bool] | None = getattr(adapter, "isConfigured", None)
    if checkFn is None:
        return "configured"
    try:
        return "configured" if bool(checkFn()) else "unknown"
    except Exception:
        return "unknown"

def healthPacket(providerId: str) -> dict[str, Any]:
    spec = providerSpecs.get(providerId)
    if spec is None:
        return {
            "schema": "luhmOs.providerHealth.v1",
            "providerId": providerId,
            "adapterState": "unknown",
            "credentialState": "unknown",
            "entitlementState": "unknown",
            "runtimeState": "unknown",
            "greenAuthority": False,
            "crownStatus": "stop",
        }

    return {
        "schema": "luhmOs.providerHealth.v1",
        "providerId": providerId,
        "adapterState": getAdapterState(providerId),
        "credentialState": getCredentialState(providerId),
        "entitlementState": "unknown",
        "runtimeState": "parked",
        "networkMutationAuthority": spec.networkMutationAuthority,
        "secretRefIds": list(spec.requiredSecretRefs),
        "greenAuthority": False,
        "crownStatus": "stop",
    }

def invoke(providerId: str, capabilityId: str, taskPacket: dict[str, Any]) -> dict[str, Any]:
    adapter = loadAdapter(providerId)
    invokeFn = getattr(adapter, "invoke", None)
    if invokeFn is None:
        raise RuntimeError(f"provider adapter lacks invoke(): {providerId}")

    requiredFields = ("taskId", "sourceRef", "scopeId", "authorityClass")
    for fieldName in requiredFields:
        if not taskPacket.get(fieldName):
            raise RuntimeError(f"missing task identity field: {fieldName}")

    result = invokeFn(capabilityId=capabilityId, taskPacket=taskPacket)
    if not isinstance(result, dict):
        raise RuntimeError("provider adapter returned non-object result")

    result["providerId"] = providerId
    result["providerSuccessMeans"] = "observed"
    result["greenAuthority"] = False
    result["crownStatus"] = "stop"
    return result
