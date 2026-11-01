#!/usr/bin/env python3
"""Read-only cross-toolchain machine-base planner: no installs, ports or privileges."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/unifiedMachineBaseV1.json"
KINDS = {"core", "client", "build", "studio", "optionalHost", "legacyInterop", "operatorOnly"}
EXPECTED_LANES = ("inventory", "sanityCheck", "test", "propose", "liveChange", "signDeployCast")
RESERVED = {"certbot", "gparted"}
CLIENT_EXCLUDE = {"python3", "sqlite3", "mariaDb", "nginx", "apache", "certbot", "gparted", "ffmpeg", "blender"}


def review(doc: dict, root: Path = ROOT) -> list[str]:
    errors = []
    def need(condition: bool, reason: str) -> None:
        if not condition:
            errors.append(reason)

    need(doc.get("schema") == "luhmOs.unifiedMachineBase.v1", "schema")
    need(doc.get("status") == "PROPOSED_SOURCE_ONLY", "source-only status")
    need(doc.get("canonicalRepository") == "eggie-admin/LuHm-OS", "canonical repository")
    need(doc.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "source law")
    grid = doc.get("logicalCells", {})
    need(grid.get("axes") == ["machine", "service", "studio", "interface"], "machine axes")
    need(grid.get("actions") == ["inventory", "scope", "verify", "propose"], "four actions")
    need(grid.get("count") == 16 and grid.get("physicalRegisters") is False, "logical hexadecimal only")

    components = doc.get("components", {})
    need(isinstance(components, dict) and len(components) >= 12, "component registry")
    for name, row in components.items():
        if not isinstance(row, dict):
            errors.append("component invalid: " + name)
            continue
        kind = row.get("kind")
        need(kind in KINDS, "component kind: " + name)
        need(row.get("privileged") is (kind == "operatorOnly"), "component privilege: " + name)
        source = row.get("source", "")
        # Canonical-repo file paths only; reject user-controlled absolute/parent hops.
        if not isinstance(source, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", source) or ".." in source.split("/"):
            errors.append("invalid source: " + name)
            continue
        target = root / source
        need(target.is_file() and not target.is_symlink(), "missing source: " + name)

    profiles = doc.get("profiles", {})
    need(set(profiles) == {"linuxHeadless", "linuxStudio", "raspberryPiDesktop", "androidClient"}, "profile set")
    for name, profile in profiles.items():
        if not isinstance(profile, dict):
            errors.append("invalid profile: " + name)
            continue
        required = profile.get("required", [])
        optional = profile.get("optional", [])
        forbidden = profile.get("forbidden", [])
        build_only = profile.get("buildOnly", [])
        values = (required, optional, forbidden, build_only)
        need(all(isinstance(v, list) and all(isinstance(x, str) for x in v) for v in values),
             "invalid component lists: " + name)
        if not all(isinstance(v, list) for v in values):
            continue
        selected = required + optional + build_only
        need(len(selected) == len(set(selected)) and len(forbidden) == len(set(forbidden)), "duplicates: " + name)
        need(set(selected + forbidden) <= set(components), "unknown component: " + name)
        need(not set(selected) & set(forbidden), "forbidden selected: " + name)
        need(not set(selected) & RESERVED, "operator tool selected: " + name)
        need(all(components.get(x, {}).get("kind") not in {"operatorOnly", "legacyInterop"} for x in required),
             "non-core service required: " + name)
        need(isinstance(profile.get("network"), str) and bool(profile["network"]), "network policy missing: " + name)
    android = profiles.get("androidClient", {})
    linux = profiles.get("linuxHeadless", {})
    need(set(android.get("forbidden", [])) >= CLIENT_EXCLUDE, "Android isolation")
    need(set(android.get("required", [])) == {"staticHtml"}, "Android thin client")
    need(set(android.get("buildOnly", [])) == {"javaGradle", "javascriptNpm"}, "Java/Gradle build boundary")
    need(set(linux.get("required", [])) == {"python3", "sqlite3"}, "minimal Linux base")

    for key in ("apacheToNginx", "mysqlToMariaDb"):
        migration = doc.get("migrationGates", {}).get(key, {})
        need(migration.get("automaticRewrite") is False and migration.get("state") == "NOT_EXECUTED"
             and isinstance(migration.get("requires"), list) and len(migration.get("requires", [])) >= 5,
             "migration gate: " + key)
    service = doc.get("serviceDecisions", {})
    need(set(service) == {"web", "sql", "certificates", "disks", "automation"}, "service decisions")
    for key in service:
        need(isinstance(service[key], str) and bool(service[key].strip()), "service description: " + key)

    lanes = doc.get("automationLanes", [])
    need(isinstance(lanes, list) and [x.get("id") for x in lanes if isinstance(x, dict)]
         == list(EXPECTED_LANES) and len(lanes) == 6, "automation sequence")
    if isinstance(lanes, list) and len(lanes) == 6 and all(isinstance(x, dict) for x in lanes):
        need(all(row.get("automatic") is (i < 4) for i, row in enumerate(lanes)), "privileged automation boundary")
        need(all(isinstance(row.get("scope"), str) and row.get("scope") for row in lanes), "scope missing")

    authority = doc.get("authority", {})
    need(authority.get("agentQuarantine") is True and authority.get("autonomousLiveBots") is False,
         "agent quarantine")
    for key in ("exposedSqlPort", "productionCertbot", "diskWrites", "firmwareWrites", "productionMerge", "publicPublish"):
        need(authority.get(key) is False, "authority boundary: " + key)
    need(authority.get("crownStatus") == "STOP", "crown held")

    # Verify existing shared source constraints, without starting any daemon.
    docker = root / ".devcontainer/Dockerfile"
    if docker.is_file():
        source = docker.read_text(encoding="utf-8")
        need("skip-networking=1" in source, "MariaDB private socket")
        need("USER codespace" in source, "non-root studio")
    else:
        errors.append("missing devcontainer")
    for path in ("frontEnd/package-lock.json", "androidWeb3Plugin/build.gradle.kts"):
        need((root / path).is_file(), "missing toolchain source: " + path)

    return sorted(set(errors))


def in_memory_sqlite_check() -> dict:
    # Temporary, private receipt table. Never touches user's real data.
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE receipt (key TEXT PRIMARY KEY, sha TEXT NOT NULL CHECK(length(sha)=64))")
        value = hashlib.sha256(b"luhm-machine-source-fixture").hexdigest()
        db.execute("INSERT INTO receipt VALUES (?,?)", ("fixture", value))
        matched = db.execute("SELECT sha FROM receipt WHERE key=?", ("fixture",)).fetchone()
    return {"inMemory": True, "sha256Matched": bool(matched and matched[0] == value),
            "databaseFilesCreated": False, "mysqlMariaDbMigrationExecuted": False}


def exact_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                             capture_output=True, timeout=5, check=False)
        sha = out.stdout.strip()
        return sha if out.returncode == 0 and re.fullmatch("[0-9a-f]{40}", sha) else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def run(profile: str, expected: str = "", root: Path = ROOT) -> dict:
    doc = json.loads((root / CONTRACT).read_text(encoding="utf-8"))
    errors = review(doc, root)
    if profile not in doc.get("profiles", {}):
        errors.append("unknown profile")
    sql = in_memory_sqlite_check()
    if not sql["sha256Matched"]:
        errors.append("in-memory SQLite fixture")
    observed = exact_head() if root == ROOT else None
    if expected and (not re.fullmatch(r"[0-9a-f]{40}", expected) or observed != expected):
        errors.append("exact source mismatch")
    selected = doc.get("profiles", {}).get(profile, {})
    return {
        "schema": "luhmOs.unifiedMachineBaseReceipt.v1",
        "sourceRef": observed,
        "profile": profile,
        "verdict": "RED_SOURCE" if errors else "AMBER_SOURCE_VERIFIED_RUNTIME_PENDING",
        "failures": sorted(set(errors)),
        "selectedRequired": selected.get("required", []),
        "selectedOptional": selected.get("optional", []),
        "buildOnly": selected.get("buildOnly", []),
        "sqlite": sql,
        "automationLanes": [x["id"] for x in doc["automationLanes"]],
        "privilegedExecution": False,
        "servicesStarted": False,
        "packagesInstalled": False,
        "physicalDeviceProven": False,
        "realMigrationPerformed": False,
        "actualBuildProven": False,
        "castAuthorized": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="linuxHeadless",
                        choices=("linuxHeadless", "linuxStudio", "raspberryPiDesktop", "androidClient"))
    parser.add_argument("--source-ref", default="", help="exact 40-character checkout SHA")
    parser.add_argument("--output", type=Path, help="local receipt JSON path")
    args = parser.parse_args()
    receipt = run(args.profile, args.source_ref)
    data = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    return 0 if not receipt["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
