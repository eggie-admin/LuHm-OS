#!/usr/bin/env python3
"""Offline, zero-dependency four-quarter source reconciler.

This does not start agents, cameras, network services, or migrations.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
QUARTERS = ("local", "remote", "studio", "company")
LAYERS = ("coreLibrary", "pluginExtension", "classWidgetOrganization", "stubAdapterBoundary")
BEATS = ("hear", "resolve", "act", "verify")


def document(path: str, root: Path = ROOT) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def sql_smoke(root: Path = ROOT) -> dict:
    """Prove SQL schema and negative constraints in an isolated :memory: DB."""
    database = sqlite3.connect(":memory:")
    database.execute("PRAGMA foreign_keys = ON")
    try:
        database.executescript((root / "host/api/typedLanesV1.sql").read_text(encoding="utf-8"))
        source_ref = "a" * 40
        database.execute(
            "INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt,evidenceRef) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            ("test-event", "test-task", source_ref, "audit", "syntheticTest", 1, 1, "2026-10-30T12:00:00Z", "synthetic"),
        )
        database.execute(
            "INSERT INTO aiManifestStream(eventId,manifestJson,manifestSchema,providerId,capabilityId) "
            "VALUES (?,?,?,?,?)",
            ("test-event", json.dumps({"taskId": "test-task", "authority": "NONE"}), "test", "none", "dryRun"),
        )
        refused = 0
        bad_queries = [
            ("INSERT INTO aiManifestStream(eventId,manifestJson,manifestSchema,providerId,capabilityId,mutationAuthority) VALUES(?,?,?,?,?,?)",
             ("test-event", "{}", "test", "none", "dryRun", 1)),
            ("INSERT INTO booleanStream(eventId,fieldName,booleanValue) VALUES(?,?,?)",
             ("test-event", "unauthorized", 2)),
            ("INSERT INTO textStream(eventId,fieldName,textValue) VALUES(?,?,?)",
             ("orphan-event", "text", "synthetic")),
            ("INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt) VALUES(?,?,?,?,?,?,?,?)",
             ("bad-event", "task", "bad", "audit", "none", 2, 1, "2026-10-30T12:00:00Z")),
        ]
        for statement, params in bad_queries:
            try:
                database.execute(statement, params)
            except sqlite3.IntegrityError:
                refused += 1
        count = database.execute("SELECT count(*) FROM streamEvent").fetchone()[0]
        if count != 1 or refused != len(bad_queries):
            raise AssertionError("SQL_ISOLATION_OR_CONSTRAINT_FAILURE")
        return {"status": "IN_MEMORY_SQL_GREEN", "negativeCasesRejected": refused, "productionDatabaseTouched": False}
    finally:
        database.close()


def inspect(policy_override: dict | None = None, root: Path = ROOT) -> dict:
    p = policy_override if policy_override is not None else document("doctrine/unifiedGoddessOrchestraV1.json", root)
    four = document("doctrine/luHmOSFourLayerArchitectureV1.json", root)
    rhythm = document("doctrine/fourBeatInteractionRhythmV1.json", root)
    typed = document("doctrine/typedFourLaneSqlV1.json", root)
    quarantine = document("doctrine/companyWideOperationalQuarantineV1.json", root)
    vendor = document("doctrine/vendorReductionV1.json", root)
    prior = document("doctrine/universalFourLaneV1.json", root)
    security = document("doctrine/dataProtectionLadderV1.json", root)
    npm = document("packages/unified-ops/package.json", root)
    checks: dict[str, bool] = {}
    def check(name: str, valid: bool) -> None:
        checks[name] = bool(valid)

    check("schema", p.get("schema") == "luhmOs.unifiedGoddessOrchestra.v1")
    check("candidate", p.get("status") == "SOURCE_ONLY_CANDIDATE_NO_RUNTIME_ACTIVATION")
    check("fourComposition", p.get("composition") == list(LAYERS)
          and [x["id"] for x in four["layers"]] == list(LAYERS))
    check("fourBeats", p.get("fourBeats") == list(BEATS)
          and [x["id"] for x in rhythm["measure"]] == list(BEATS))
    check("fourQuarters", p.get("quarters") == list(QUARTERS)
          and set(p["profileRoles"]) == set(QUARTERS))
    check("canonicalContracts", all((root / v).is_file() for v in p["existingContracts"].values()))
    check("classPluginPaths", len(p["moduleRegistry"]) == len({x["id"] for x in p["moduleRegistry"]})
          and all(x["layer"] in LAYERS and (root / x["ref"]).is_file() for x in p["moduleRegistry"]))
    check("typedSql", [x["id"] for x in typed["lanes"]] ==
          ["numericStream", "textStream", "booleanStream", "aiManifestStream"]
          and p["toolchain"]["sql"]["schema"] == "host/api/typedLanesV1.sql"
          and p["toolchain"]["sql"]["liveMigration"] is False)
    check("roleRoster", p["agentSong"]["existingSixRoleViews"] == prior["agents"]["proposalSix"]
          and all(x in quarantine["registeredAgents"] for x in p["agentSong"]["ownerByBeat"].values()))
    check("urdReview", p["agentSong"]["reviewer"] in quarantine["registeredAgents"])
    check("quarantine", quarantine["registeredCount"] == 15
          and quarantine["activeTaskWorkersAllowed"] is False
          and p["agentSong"]["all15WorkersQuarantined"] is True)
    check("agentNoAuthority", p["agentSong"]["actAuthority"] == "PROPOSED_ONLY_QUARANTINED"
          and p["tasks"]["noAutomaticWorkerSpawning"] is True)
    check("taskEnvelope", p["tasks"]["manifestFields"] == security["agentAI"]["manifestRequirements"]
          and p["tasks"]["noRemoteExecution"] is True)
    check("packagePrivate", npm.get("private") is True and npm.get("dependencies", {}) == {}
          and npm.get("devDependencies", {}) == {}
          and p["toolchain"]["npm"]["dependencies"] == {})
    check("npmNotProduction", all((p["toolchain"]["npm"][k] is False
          for k in ("runtimeOnAndroid","runtimeOnProductionVm","lifecycleInstallScripts"))))
    check("npmCli", all(k in npm.get("scripts", {}) for k in ("audit", "matrix", "sql-smoke", "test")))
    check("existingFrontendPins", vendor["npm"]["exactDirectDependencies"] ==
          {"@babylonjs/core": "9.32.0", "jquery": "3.7.1", "vue": "3.5.44"})
    vendors = p["toolchain"]["vendorSelection"]
    check("vendorDedup", len(vendors["core"]) == len(set(vendors["core"]))
          and not (set(vendors["core"]) & set(vendors["optional"]))
          and vendors["noDuplicateRendererInstall"] is True
          and vendors["noDuplicateReverseProxyByDefault"] is True)
    check("noRuntimeNodeOnAndroid", vendors["noRuntimeNodeOnAndroid"] is True)
    check("noVendorFetch", vendors["neverAutoPullThirdPartyCode"] is True)
    check("networkByQuarter", p["profileRoles"]["remote"]["remoteNetworkRequired"] is True
          and all(p["profileRoles"][q]["remoteNetworkRequired"] is False for q in ("local","studio","company")))
    check("noPublicDb", p["toolchain"]["sql"]["publicPort"] is False
          and "PublicSqlAdmin" in p["profileRoles"]["remote"]["forbidden"])
    check("safety", all(v is True for v in p["safety"].values()))
    check("releaseStop", p.get("crownStatus") == "STOP"
          and p["readyForPublicBrandingPublish"] is False)
    check("yamlExists", (root / p["toolchain"]["yaml"]["source"]).is_file()
          and p["toolchain"]["yaml"]["apply"] is False)

    problems = sorted(k for k, good in checks.items() if not good)
    return {"schema": "luhmOs.unifiedGoddessOrchestraAudit.v1", "checks": len(checks),
            "passed": len(checks) - len(problems), "failures": problems,
            "state": "SOURCE_PROFILE_GREEN_RUNTIME_UNVERIFIED" if not problems else "FAIL_CLOSED",
            "activeAgents": 0, "remoteDeployed": False, "crown": "STOP"}


def matrix() -> dict:
    cells = [{"quarter": q, "layer": layer, "beat": beat, "authority": "NONE",
              "liveCapabilityVerified": False}
             for q in QUARTERS for layer in LAYERS for beat in BEATS]
    return {"schema": "luhmOs.unifiedGoddessOrchestraMatrix.v1",
            "cells": cells, "count": len(cells), "crown": "STOP"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("audit", "matrix", "sql-smoke"), default="audit")
    args = parser.parse_args()
    try:
        result = {"audit": inspect, "matrix": matrix, "sql-smoke": sql_smoke}[args.mode]()
        passed = args.mode != "audit" or not result["failures"]
    except (OSError, ValueError, KeyError, sqlite3.DatabaseError, AssertionError) as err:
        result = {"state": "FAIL_CLOSED", "errorType": type(err).__name__, "crown": "STOP"}
        passed = False
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
