#!/usr/bin/env python3
"""Offline age-lane and vendor authority policy. No network, identity storage or publication."""
from dataclasses import dataclass

CORE = frozenset({"github", "openai", "google"})
ADAPTERS = frozenset({"samsung", "meta", "tiktok"})
LANES = frozenset({"family", "teen", "adult21"})
CATEGORIES = frozenset({"general", "teen", "adult"})

@dataclass(frozen=True)
class Request:
    provider: str
    lane: str
    category: str
    eligibility: str  # unknown, minor, adult_verified
    rights_reviewed: bool
    human_approved: bool


def evaluate(req: Request):
    if req.provider not in CORE | ADAPTERS or req.lane not in LANES or req.category not in CATEGORIES:
        return "DENY_UNKNOWN"
    if req.provider in ADAPTERS and not req.human_approved:
        return "DENY_ADAPTER_AUTHORITY"
    if not req.rights_reviewed:
        return "DENY_RIGHTS_UNREVIEWED"
    if req.category == "adult":
        if req.lane != "adult21" or req.eligibility != "adult_verified":
            return "DENY_ADULT_BOUNDARY"
    elif req.category == "teen" and req.lane == "family":
        return "DENY_FAMILY_BOUNDARY"
    if req.eligibility not in {"unknown", "minor", "adult_verified"}:
        return "DENY_ELIGIBILITY"
    return "ELIGIBLE_FOR_HUMAN_REVIEW"  # never publishes or grants access
