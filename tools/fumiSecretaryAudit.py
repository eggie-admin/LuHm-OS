#!/usr/bin/env python3
"""Deterministic structural audit for Fumi Oni records doctrine.

This tool does not call an LLM, move files, rename paths, delete records, or mutate
external systems. It only validates that the secretary contract remains bounded.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "FUMI_SECRETARY_ONI_V1.json"
SKILL = ROOT / "agents" / "fumiSecretaryOni" / "SKILL.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def audit() -> dict:
    require(DOCTRINE.is_file(), "missing Fumi doctrine")
    require(SKILL.is_file(), "missing Fumi skill")

    doctrine = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    skill = SKILL.read_text(encoding="utf-8")

    require(doctrine["schema"] == "luhm-os.fumi-secretary-oni.v1", "unexpected schema")
    require(doctrine["boss"] == "Lum", "Fumi must report to Lum")
    require(doctrine["defaultAuthority"] == "READ_ONLY_PROPOSAL", "Fumi must default read-only")

    for denied in (
        "directMutationAuthority",
        "promotionAuthority",
        "deleteAuthority",
        "mergeAuthority",
        "publishAuthority",
    ):
        require(doctrine.get(denied) is False, f"authority unexpectedly enabled: {denied}")

    surfaces = doctrine.get("surfaces", [])
    keys = [entry.get("key") for entry in surfaces]
    require(len(keys) == len(set(keys)), "duplicate surface key")
    require(set(keys) == {"github", "googleDrive", "chatgptLibrary", "ciArtifacts", "local"}, "surface contract drift")

    classes = doctrine.get("classification", [])
    require(len(classes) == len(set(classes)), "duplicate classification")
    require({"MATCH", "DRIFT", "DUPLICATE", "UNKNOWN", "CONFLICT"}.issubset(classes), "missing core classifications")

    learning = doctrine.get("backgroundLearning", {})
    require(learning.get("mode") == "RECEIPT_BACKED_LEDGER_ONLY", "learning mode drift")
    require(learning.get("hiddenRetraining") is False, "hidden retraining must remain disabled")
    require(learning.get("silentMutation") is False, "silent mutation must remain disabled")

    serialized = DOCTRINE.read_text(encoding="utf-8")
    forbidden_public_locator_tokens = (
        "drive.google.com/file/d/",
        "drive.usercontent.google.com/download?id=",
        "library_file_id",
        "sk-proj-",
        "OPENAI_API_KEY",
    )
    for token in forbidden_public_locator_tokens:
        require(token not in serialized, f"private locator/secret leaked into doctrine: {token}")

    required_skill_phrases = (
        "Fumi speaks to Lum",
        "OpenAI may help Fumi classify records",
        "deterministic helper validates exact paths",
        "Learning\" means a receipt-backed lessons ledger".replace('\\"', '"'),
    )
    for phrase in required_skill_phrases:
        require(phrase in skill, f"missing bounded-skill rule: {phrase}")

    result = {
        "status": "GREEN",
        "agent": doctrine["name"],
        "authority": doctrine["defaultAuthority"],
        "surfaceCount": len(surfaces),
        "classificationCount": len(classes),
        "backgroundLearning": learning["mode"],
        "directMutationAuthority": doctrine["directMutationAuthority"],
    }
    print("FUMI_SECRETARY_AUDIT=GREEN", json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    audit()
