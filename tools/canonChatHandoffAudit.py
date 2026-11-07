#!/usr/bin/env python3
"""Fail-closed audit of a sanitized, non-authoritative chat Canon checkpoint."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "doctrine/canonChatHandoff20261106.json"
M = ROOT / "manual/canonNewChatHandoff20261106.md"
SOURCE = ROOT / "doctrine/currentSourceTruthV3.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"

def main():
    checkpoint = json.loads(H.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    quarantine = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    assert checkpoint["schema"] == "luhmOs.chatCanonHandoff.v1"
    assert checkpoint["kind"] == "READ_ONLY_CONTINUITY_INDEX"
    assert checkpoint["canonicalSource"]["sourceRef"].isalnum()
    assert len(checkpoint["canonicalSource"]["sourceRef"]) == 40
    assert source["status"] == "AMBER_PROPOSED_SEAL_OF_TRUTH"
    assert checkpoint["canonicalSource"]["status"] == source["status"]
    assert checkpoint["canonicalSource"]["crown"] == "STOP"
    assert quarantine["state"] == "QUARANTINED"
    assert checkpoint["storagePipelineCandidate"]["timer"] == "NOT_ARMED"
    assert checkpoint["installedPrivateSitePlugin"]["directLibraryModify"] == "NOT_EXPOSED"
    assert checkpoint["taskCheckpoint"]["executionAuthorized"] is False
    assert "finalCanonCrown" in checkpoint["notProofOf"]
    assert "new ChatGPT chat" in M.read_text(encoding="utf-8")
    content = H.read_text(encoding="utf-8")
    for forbidden in ("sk-proj-", "-----BEGIN PRIVATE KEY", "refresh_token", "Authorization: Bearer"):
        assert forbidden not in content
    print("CANON_CHAT_HANDOFF_AUDIT=GREEN source-only, not Crown")

if __name__ == "__main__":
    main()
