#!/usr/bin/env python3
"""Tiny, non-executing same-source continuity gate for accepted jQuery code.

An accepted source hash can be reused without repeating previous approvals.
This check does not promote incoming plugins, execute JS, mount the cockpit,
or grant permissions to its agents or publication lane.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "doctrine/jqueryPluginContinuityV1.json"
HASH = re.compile(r"^[0-9a-f]{40}$")


def verify_entry(root: Path, entry: dict) -> tuple[bool, str]:
    if not isinstance(entry, dict):
        return False, "invalidRecord"
    text = entry.get("path")
    fingerprint = entry.get("gitBlobSha")
    if not isinstance(text, str) or not text or "\\" in text:
        return False, "invalidPath"
    rel = PurePosixPath(text)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix != ".js":
        return False, "invalidPath"
    if not isinstance(fingerprint, str) or not HASH.fullmatch(fingerprint):
        return False, "invalidHash"
    root = root.resolve()
    path = root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root) or not path.is_file():
        return False, "missingOrOutsideRoot"
    if path.is_symlink():
        return False, "symlinkNotAllowed"
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\\0" + data).hexdigest()
    if actual != fingerprint:
        return False, "changedSourceNeedsDeltaReview"
    return True, "sameSourceAccepted"


def audit(root: Path = ROOT) -> bool:
    ledger = json.loads((root / "doctrine/jqueryPluginContinuityV1.json").read_text(encoding="utf-8"))
    entries = ledger["acceptedObservedSources"]
    if (ledger.get("baseline") != "PROFESSOR_ACCEPTED_SOURCE_REUSE"
            or ledger.get("fastPath", {}).get("noAutomaticExecutionFromIncoming") is not True
            or ledger.get("fastPath", {}).get("noAutonomousAgentRelease") is not True
            or ledger.get("fastPath", {}).get("skipRepeatedFullReaudits") is not True
            or len(entries) != 3 or len({x["path"] for x in entries}) != len(entries)):
        print("RED_JQUERY_CONTINUITY_CONTRACT")
        return False
    if ledger.get("jqueryVersion") != "3.7.1":
        print("RED_JQUERY_PIN_MISMATCH")
        return False
    all_green = True
    for entry in entries:
        path = entry["path"]
        good, reason = verify_entry(root, entry)
        if good and entry.get("professorAcceptance") != "GREEN_SOURCE_REUSE":
            good, reason = False, "acceptanceNotRecorded"
        if good:
            # node --check parses source only. It never evaluates the plugin.
            try:
                result = subprocess.run(["node", "--check", str(root / path)],
                                        capture_output=True, text=True, timeout=15, check=False)
                if result.returncode:
                    good, reason = False, "javascriptSyntaxChanged"
            except (OSError, subprocess.TimeoutExpired):
                good, reason = False, "nodeCheckUnavailable"
        print(f'{"GREEN" if good else "RED"} {entry["id"]}: {reason}')
        all_green &= good
    if all_green:
        print("GREEN_JQUERY_REUSE_3_OBSERVED_SOURCES_NO_REAUDIT")
        print("NOT_PROVEN: unlocated uploads, installed plugins, Android, chat host, publication")
    else:
        print("RED_JQUERY_REUSE_NEEDS_TARGETED_DELTA_REVIEW")
    return all_green


if __name__ == "__main__":
    raise SystemExit(0 if audit() else 1)
