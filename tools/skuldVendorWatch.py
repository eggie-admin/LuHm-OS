#!/usr/bin/env python3
"""Skuld's bounded read-only upstream release watch for the LuHm cabinet.

Only official GitHub release metadata from two explicitly allowlisted repos.
Upstream version != safe update. Unknown/unreachable != GREEN.
Does not change dependencies, import vendor code, run AI models or promote Canon.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VENDORS = {
    "mcpPythonSdk": {
        "repository": "modelcontextprotocol/python-sdk",
        "pinFile": "host/mcp/requirements.txt",
        "pinPattern": r"(?m)^mcp==([0-9]+\.[0-9]+\.[0-9]+)$",
    },
    "godotEngine": {
        "repository": "godotengine/godot",
        "pinFile": "README.md",
        "pinPattern": r"Godot ([0-9]+\.[0-9]+\.[0-9]+)",
    },
}
TAG = re.compile(r"^[vV]?([0-9]+\.[0-9]+\.[0-9]+)(?:[-.][A-Za-z0-9.]+)?$")


def pin(root: Path, vendor: dict) -> str:
    location = root / vendor["pinFile"]
    if not location.is_file() or location.is_symlink():
        raise ValueError("missing pinned version source")
    raw = location.read_text(encoding="utf-8")
    hits = re.findall(vendor["pinPattern"], raw)
    if not hits:
        raise ValueError("pinned version not found")
    return hits[0]


def latest_release(repository: str, timeout=9) -> dict:
    # URL is assembled only from hardcoded, allowlisted repository names.
    if repository not in {v["repository"] for v in VENDORS.values()}:
        raise ValueError("vendor endpoint not allowlisted")
    request = Request(
        "https://api.github.com/repos/" + repository + "/releases/latest",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "LuHm-SkuldVendorWatch/1",
                 "Cache-Control": "no-cache"},
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError("vendor upstream returned non-200")
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError("upstream release must be object")
    return data


def evaluate(name: str, vendor: dict, pinned: str, upstream: dict | None) -> dict:
    row = {"vendor": name, "repository": vendor["repository"],
           "pinnedVersion": pinned, "observedLatestVersion": None,
           "upstreamStatus": "UNVERIFIED", "reviewRequired": False,
           "safeToUpgrade": False, "dependencyChanged": False}
    if not isinstance(upstream, dict) or upstream.get("draft") is not False:
        return row
    if upstream.get("prerelease") is True or not isinstance(upstream.get("tag_name"), str):
        return row
    match = TAG.fullmatch(upstream["tag_name"])
    if not match:
        return row
    observed = match.group(1)
    row["observedLatestVersion"] = observed
    row["upstreamStatus"] = "OFFICIAL_RELEASE_METADATA_OBSERVED"
    try:
        pinnedParts = tuple(map(int, pinned.split(".")))
        observedParts = tuple(map(int, observed.split(".")))
        row["reviewRequired"] = observedParts > pinnedParts
    except (ValueError, TypeError):
        row["upstreamStatus"] = "UNVERIFIED"
        row["observedLatestVersion"] = None
    return row


def audit(root: Path, releases: dict) -> dict:
    rows = []
    for name, vendor in VENDORS.items():
        pinned = pin(root, vendor)
        rows.append(evaluate(name, vendor, pinned, releases.get(name)))
    return {
        "schema": "luhmOs.skuldVendorWatch.v1",
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "source": "publicOfficialReleaseMetadataOnly",
        "observations": rows,
        "vendorObservationComplete": all(
            r["upstreamStatus"] == "OFFICIAL_RELEASE_METADATA_OBSERVED" for r in rows),
        "mutationPerformed": False,
        "agentInferencePerformed": False,
        "dependencyUpdatesApproved": False,
        "crownStatus": "STOP",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="Opt in to public GitHub API GETs on scheduled/manual audit runs")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    releases = {}
    if args.live:
        for name, vendor in VENDORS.items():
            try:
                releases[name] = latest_release(vendor["repository"])
            except (HTTPError, URLError, ValueError, TimeoutError, OSError):
                # Fail closed as UNVERIFIED, not a fake no-update result.
                releases[name] = None
    report = audit(ROOT, releases)
    report["networkAttempted"] = args.live
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0  # UNVERIFIED is informational and never grants upgrade permission.


if __name__ == "__main__":
    raise SystemExit(main())
