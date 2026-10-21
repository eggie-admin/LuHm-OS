#!/usr/bin/env python3
"""Zero-dependency source security gate. No cloud, secret or live SQL access."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = {"cloudflare", "huggingFace", "render", "github", "copilot", "openAi", "sql"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError("RED_STUDIO_SECURITY: " + message)


def main() -> None:
    baseline = json.loads((ROOT / "doctrine/studioSecurityBaselineV1.json").read_text("utf-8"))
    spec = json.loads((ROOT / "doctrine/studioSecurityBaselineV1.schema.json").read_text("utf-8"))
    require(spec["$schema"].endswith("/2020-12/schema"), "JSON Schema dialect")
    for key in spec["required"]:
        require(key in baseline, "missing baseline field " + key)
    require(baseline["schema"] == spec["properties"]["schema"]["const"], "wrong contract")
    require(baseline["profile"] == spec["properties"]["profile"]["const"], "not solo-studio")
    require(baseline["status"] in spec["properties"]["status"]["enum"], "unknown status")
    require(baseline["promotion"] is False, "self-promotion forbidden")
    require(set(baseline["providerControls"]) == PROVIDERS, "provider inventory drift")
    require(set(baseline["evidence"]) == PROVIDERS, "missing provider evidence lanes")
    require(set(baseline["gates"]) == set(spec["properties"]["gates"]["required"]), "gate inventory drift")
    for name, control in baseline["providerControls"].items():
        require(isinstance(control["must"], list) and len(control["must"]) >= 3, name + " controls")
        require(isinstance(control["never"], str) and len(control["never"]) >= 12, name + " deny rule")
        require(isinstance(baseline["evidence"][name], str) and len(baseline["evidence"][name]) >= 10, name + " evidence")
    for gate, requirements in baseline["gates"].items():
        require(isinstance(requirements, list) and "humanAuthorization" in requirements, gate + " missing human stop")
        require(len(requirements) == len(set(requirements)), gate + " duplicate controls")

    sql = (ROOT / "host/api/typedLanesV1.sql").read_text("utf-8")
    for invariant in ("STRICT;", "PRAGMA foreign_keys = ON", "sourceRef NOT GLOB '*[^0-9a-f]*'",
                      "sha256 NOT GLOB '*[^0-9a-f]*'", "observedAt GLOB '????-??-??T??:??:??*Z'",
                      "CHECK(mutationAuthority=0)", "CHECK(greenAuthority=0)", "CHECK(crownAuthority=0)"):
        require(invariant in sql, "SQLite invariant missing: " + invariant)

    ignore = (ROOT / ".gitignore").read_text("utf-8").splitlines()
    for pattern in (".env", "*.key", "*.pem", "*.sqlite3", "*.db", "*.rar", ".secrets/"):
        require(pattern in ignore, "gitignore missing " + pattern)
    copilot = (ROOT / ".github/copilot-instructions.md").read_text("utf-8")
    for marker in ("doctrine/studioSecurityBaselineV1.json", "SQL uses parameter binding", "human authorization"):
        require(marker.lower() in copilot.lower(), "Copilot lacks " + marker)
    render = (ROOT / "render.yaml").read_text("utf-8")
    require("healthCheckPath: /healthz" in render, "Render desired health path")
    require("autoDeployTrigger: off" in render, "Render deployment policy")

    print(json.dumps({
        "status": "SOURCE_SECURITY_GATE_GREEN",
        "providers": sorted(PROVIDERS),
        "schemaContract": baseline["schema"],
        "sqlite": "SOURCE_ONLY_SQLITE_STRICT",
        "renderLiveHealth": "NOT_VERIFIED_BY_THIS_GATE",
        "cloudflareLive": "NOT_VERIFIED_BY_THIS_GATE",
        "remoteDatabase": "NOT_VERIFIED_BY_THIS_GATE",
        "approval": "REQUIRED_FOR_PROVIDER_MUTATION",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
