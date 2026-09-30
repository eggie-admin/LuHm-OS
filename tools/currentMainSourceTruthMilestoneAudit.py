#!/usr/bin/env python3
"""Fail-closed audit for the scoped current-main source-truth GREEN milestone."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "doctrine/SOURCE_OF_TRUTH.json"
SNAPSHOT_PATH = ROOT / "doctrine/PRE_GREEN_SNAPSHOT_20260930.json"
MILESTONE_PATH = ROOT / "doctrine/CURRENT_MAIN_SOURCE_TRUTH_GREEN_20260930.json"
BOUNDARY_PATH = ROOT / "doctrine/RELEASE_BOUNDARY.json"

BASE_MAIN = "013e056ad7fdf37ba92c298768d57806667a509c"
EXPECTED_GITHUB_ROOTS = {
    "eggie-admin/LuHm-OS": BASE_MAIN,
    "eggie-admin/hydra-shell-android": "08644e2dbb032b1804e260c8ece1060597a22ae0",
    "eggie-admin/vue-headless-cms": "1d51c5b90266f7beb8236cf07acfb17a085a4134",
}
EXPECTED_DRIVE_ID = "1dYYQgmWO6-zh-0G72dUDxswcWWuXsGeC"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(source: dict, snapshot: dict, milestone: dict, boundary: dict) -> list[str]:
    errors: list[str] = []

    if source.get("canonical_repository") != "eggie-admin/LuHm-OS":
        errors.append("canonical repository drift")
    if source.get("authority") != "Professor":
        errors.append("Professor authority drift")
    if source.get("source_law") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        errors.append("source law drift")
    if source.get("promotion") is not False:
        errors.append("promotion must remain false")
    if source.get("enterpriseReady") is not False:
        errors.append("enterprise readiness must remain false")
    if source.get("android", {}).get("production_signer") is not False:
        errors.append("production signer must remain false")
    if source.get("android", {}).get("publication_authority") is not False:
        errors.append("Android publication authority must remain false")
    if source.get("status", "").startswith("GREEN_FULL_SOURCE"):
        errors.append("full-source GREEN is forbidden for this scoped milestone")

    reconciliation = source.get("reconciliation", {})
    if reconciliation.get("observedMain") != BASE_MAIN:
        errors.append("reconciliation observedMain is not the audited canonical baseline")
    if reconciliation.get("status") != "GREEN_CURRENT_MAIN_SOURCE_TRUTH_RECONCILED":
        errors.append("reconciliation status is not scoped GREEN")
    if reconciliation.get("scope") != "doctrine-and-static-ci-only":
        errors.append("reconciliation scope drift")

    if snapshot.get("status") != "GREEN_REPO_DRIVE_SNAPSHOT_GATE":
        errors.append("snapshot gate is not GREEN")
    if snapshot.get("authority") != "Professor":
        errors.append("snapshot authority drift")
    if snapshot.get("destructiveMutationAuthorized") is not False:
        errors.append("snapshot unexpectedly authorizes destructive mutation")

    github_roots = {
        root.get("repository"): root.get("commit")
        for root in snapshot.get("roots", [])
        if root.get("type") == "github"
    }
    if github_roots != EXPECTED_GITHUB_ROOTS:
        errors.append("GitHub snapshot roots do not match the frozen refs")

    drive_roots = [root for root in snapshot.get("roots", []) if root.get("type") == "google_drive"]
    if len(drive_roots) != 1:
        errors.append("exactly one Drive compatibility root is required")
    else:
        drive = drive_roots[0]
        if drive.get("folderId") != EXPECTED_DRIVE_ID:
            errors.append("Drive compatibility root id drift")
        if drive.get("observedState") != "EMPTY_FOLDER_AT_INSPECTION":
            errors.append("Drive compatibility root state is not the observed empty state")

    if milestone.get("status") != "GREEN_CURRENT_MAIN_SOURCE_TRUTH_RECONCILIATION":
        errors.append("milestone status drift")
    if milestone.get("baseCanonicalMain") != BASE_MAIN:
        errors.append("milestone baseline drift")
    if milestone.get("scope") != "doctrine-and-static-ci-only":
        errors.append("milestone scope drift")
    if milestone.get("crownStatus") != "STOP":
        errors.append("Crown must remain STOP")
    if milestone.get("fullProductReadiness") != "AMBER":
        errors.append("full product readiness must remain AMBER")

    for field in (
        "runtimeAuthority",
        "releaseAuthority",
        "publicationAuthority",
        "productionSigningAuthority",
        "deviceProofAuthority",
        "crownAuthority",
    ):
        if milestone.get(field) is not False:
            errors.append(f"milestone authority creep: {field}")

    deny = set(boundary.get("deny", []))
    for required in (
        "production signing",
        "publishing",
        "stable promotion",
        "remote shell execution",
        "embedded provider secrets",
    ):
        if required not in deny:
            errors.append(f"release boundary lost deny rule: {required}")

    return errors


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    source = load(SOURCE_PATH)
    snapshot = load(SNAPSHOT_PATH)
    milestone = load(MILESTONE_PATH)
    boundary = load(BOUNDARY_PATH)
    errors = validate(source, snapshot, milestone, boundary)

    report = {
        "schema": "luhm-os.current-main-source-truth-audit-report.v1",
        "status": "GREEN_CURRENT_MAIN_SOURCE_TRUTH_RECONCILIATION" if not errors else "RED_CURRENT_MAIN_SOURCE_TRUTH_RECONCILIATION",
        "sourceCommit": git_head(),
        "baseCanonicalMain": BASE_MAIN,
        "scope": "doctrine-and-static-ci-only",
        "contractErrors": errors,
        "fullProductReadiness": "AMBER",
        "runtimeAuthority": False,
        "releaseAuthority": False,
        "publicationAuthority": False,
        "productionSigningAuthority": False,
        "crownStatus": "STOP",
    }

    out = ROOT / "build/current-main-source-truth/milestone.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if errors:
        raise SystemExit("current-main source-truth milestone audit failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
