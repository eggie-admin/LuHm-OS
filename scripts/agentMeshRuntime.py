#!/usr/bin/env python3
"""Fail-closed LuHm/Oni agent mesh contract.

This module is deterministic policy/runtime scaffolding. Network/provider adapters live
outside the APK and must present evidence receipts before a live deployment can be GREEN.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class Verdict(str, Enum):
    ALLOW = "ALLOW"
    CROWN_REQUIRED = "CROWN_REQUIRED"
    DENY = "DENY"

@dataclass(frozen=True)
class Agent:
    name: str
    blade: str
    may_execute: bool = False

LUM = Agent("Lum", "Orchestrator")
ONI = (
    Agent("Kiri", "Context"),
    Agent("Tetsu", "Build"),
    Agent("Momo", "Research"),
)
SHIORI = Agent("Shiori", "Critic")
KUGI = Agent("Kugi", "Tool Executor", may_execute=True)
MAX_PARALLEL = 3

CONSEQUENTIAL = frozenset({
    "merge_main", "stable_promote", "publish", "production_sign",
    "public_expose", "write_secret", "remote_shell"
})
DENIED = frozenset({
    "embed_provider_secret", "apk_remote_shell", "recursive_recruit",
    "self_approve", "bypass_crown"
})

def authorize(action: str, *, crown_approved: bool = False) -> Verdict:
    action = action.strip().lower()
    if action in DENIED:
        return Verdict.DENY
    if action in CONSEQUENTIAL:
        return Verdict.ALLOW if crown_approved else Verdict.CROWN_REQUIRED
    return Verdict.ALLOW

def validate_dispatch(workers: Iterable[Agent]) -> None:
    batch = tuple(workers)
    if len(batch) > MAX_PARALLEL:
        raise ValueError("parallelism exceeds Crown contract")
    if any(w.name == LUM.name for w in batch):
        raise ValueError("Lum cannot recruit herself")
    if len({w.name for w in batch}) != len(batch):
        raise ValueError("duplicate worker dispatch")

def provider_ready(env: dict[str, str]) -> bool:
    # Presence only. Never return, print, hash, persist, or inspect the secret.
    return bool(env.get("OPENAI_API_KEY", "").strip())

def deployment_state(*, exact_head_ci: bool, provider_receipt: bool,
                     apk_receipt: bool, device_receipt: bool,
                     human_promoted: bool) -> str:
    if not exact_head_ci:
        return "AMBER_EXACT_HEAD_CI_REQUIRED"
    if not provider_receipt:
        return "RED_OPENAI_LIVE_RECEIPT_MISSING"
    if not apk_receipt:
        return "RED_APK_RECEIPT_MISSING"
    if not device_receipt:
        return "RED_PHYSICAL_SAMSUNG_RECEIPT_MISSING"
    if not human_promoted:
        return "AMBER_HUMAN_PROMOTION_REQUIRED"
    return "GREEN_DEPLOYED"
