#!/usr/bin/env python3
"""LuHm-OS eight-domain × Canon 4×4×4 = 512 source-only SQL integrity checks.

No database connection strings, network traffic, real machine identifiers,
firmware reads, root privileges, phpMyAdmin install, migrations or Crown.
Uses disposable in-memory SQLite and generated SYNTHETIC fixtures only.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "host/api/machineRegistrySqliteV1.sql"
MARIA = ROOT / "host/api/machineRegistryMariaDbReviewV1.sql"
POLICY = ROOT / "doctrine/machineSqlHex512EscalationV1.json"
CAST = ROOT / "doctrine/fnCastV1.yaml"
KERNEL = ROOT / "doctrine/escalationKernelV1.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"
STORAGE = ROOT / "doctrine/storageTopologyV1.json"
PRIVACY = ROOT / "doctrine/machineToHumanWizardV1.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
HEX32 = re.compile(r"^[a-f0-9]{32}$")
TIMESTAMP = "2026-11-07T00:00:00Z"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def insist(ok, msg: str):
    if not ok:
        raise ValueError(msg)


def setup():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SQL.read_text(encoding="utf-8"))
    insist(db.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign key enforcement missing")
    return db


def seed(db, source_ref: str):
    # No real IMEI, serial, MAC, device address or device fingerprint.
    machine_key = "1" * 32
    device_key = "2" * 32
    digest = "b" * 64
    db.execute("INSERT INTO sourceRevision VALUES(?,?,?,?,?)",
               (source_ref, "a" * 64, "eggie-admin/LuHm-OS", "SOURCE_CANDIDATE", TIMESTAMP))
    db.execute("INSERT INTO machineIdentity VALUES(?,?,?,?,?,?)",
               (machine_key, "SYNTHETIC_DEVICE_ONLY", "synthetic", source_ref, None, 1))
    db.execute("INSERT INTO deviceRecord VALUES(?,?,?,?,?,?)",
               (device_key, machine_key, "emulator", "SYNTHETIC_MODEL", "UNKNOWN", source_ref))
    db.execute("INSERT INTO firmwareRecord VALUES(?,?,?,?,?,?,?)",
               ("testFirmware", device_key, "unknown", "UNREAD_SYNTHETIC", None, "UNKNOWN", source_ref))
    db.execute("INSERT INTO namespaceRegistry VALUES(?,?,?,?,?)",
               ("testRegistry", "plugin", "LuHm-OS", source_ref, "SOURCE_ONLY"))
    db.execute("INSERT INTO machineApi VALUES(?,?,?,?,?,?,?)",
               ("testApi", machine_key, "MCP_TOOL", "mcp", "synthetic/status", "READ_ONLY", source_ref))
    db.execute("INSERT INTO artifactPointer VALUES(?,?,?,?,?,?,?)",
               ("testArtifact", digest, 64, "localSynthetic", "synthetic/receipt", source_ref, "SOURCE_ONLY"))
    db.execute("INSERT INTO evidenceReceipt VALUES(?,?,?,?,?,?)",
               ("testReceipt", source_ref, "c" * 64, TIMESTAMP, "SOURCE_CI", "SOURCE_ONLY"))
    db.commit()


def negative_controls(db, source_ref: str) -> int:
    # Every attempted corruption should fail at the SQL constraint layer.
    attempts = [
        ("badSourceRef", "INSERT INTO sourceRevision VALUES(?,?,?,?,?)",
         ("x" * 40, "a" * 64, "eggie-admin/LuHm-OS", "UNKNOWN", TIMESTAMP)),
        ("nonHexDigest", "INSERT INTO sourceRevision VALUES(?,?,?,?,?)",
         ("a" * 40, "g" * 64, "eggie-admin/LuHm-OS", "UNKNOWN", TIMESTAMP)),
        ("badMachineKey", "INSERT INTO machineIdentity VALUES(?,?,?,?,?,?)",
         ("x" * 32, "SYNTHETIC", "synthetic", source_ref, None, 1)),
        ("rawHardwareType", "INSERT INTO machineIdentity VALUES(?,?,?,?,?,?)",
         ("3" * 32, "SYNTHETIC", "rawImei", source_ref, None, 1)),
        ("orphanDevice", "INSERT INTO deviceRecord VALUES(?,?,?,?,?,?)",
         ("4" * 32, "9" * 32, "phone", "SYNTHETIC", "UNKNOWN", source_ref)),
        ("invalidVerifiedBoot", "INSERT INTO deviceRecord VALUES(?,?,?,?,?,?)",
         ("4" * 32, "1" * 32, "phone", "SYNTHETIC", "GREEN", source_ref)),
        ("firmwareBadDigest", "INSERT INTO firmwareRecord VALUES(?,?,?,?,?,?,?)",
         ("badFirmware", "2" * 32, "kernel", "SYNTHETIC", "F" * 64, "UNKNOWN", source_ref)),
        ("apiIllegalPolicy", "INSERT INTO machineApi VALUES(?,?,?,?,?,?,?)",
         ("badApi", None, "POST", "mcp", "synthetic/admin", "ALLOW_WRITE", source_ref)),
        ("artifactBadDigest", "INSERT INTO artifactPointer VALUES(?,?,?,?,?,?,?)",
         ("badArtifact", "0" * 63, 1, "localSynthetic", "synthetic", source_ref, "UNKNOWN")),
        ("artifactForbiddenStorage", "INSERT INTO artifactPointer VALUES(?,?,?,?,?,?,?)",
         ("badArtifact", "0" * 64, 1, "publicPrivateDriveId", "private/id", source_ref, "UNKNOWN")),
        ("sourceCannotSelfProveExternal", "INSERT INTO evidenceReceipt VALUES(?,?,?,?,?,?)",
         ("badReceipt", source_ref, "0" * 64, TIMESTAMP, "SOURCE_CI", "EXTERNALLY_VERIFIED")),
        ("unbackedReceiptSource", "INSERT INTO evidenceReceipt VALUES(?,?,?,?,?,?)",
         ("badReceipt", "9" * 40, "0" * 64, TIMESTAMP, "SOURCE_CI", "SOURCE_ONLY")),
        ("badHexRange", "INSERT INTO auditCoordinate VALUES(?,?,?,?,?,?,?)",
         ("identity", "0x40", "cast", "verify", "finalForm", source_ref, "HOLD")),
        ("badHexCase", "INSERT INTO auditCoordinate VALUES(?,?,?,?,?,?,?)",
         ("identity", "0x0g", "cast", "verify", "finalForm", source_ref, "HOLD")),
        ("noEvidenceLevelUpgrade", "UPDATE evidenceReceipt SET proofLevel=? WHERE receiptKey=?",
         ("EXTERNALLY_VERIFIED", "testReceipt")),
        ("cannotDeleteBoundSource", "DELETE FROM sourceRevision WHERE sourceRef=?", (source_ref,)),
    ]
    passed = 0
    for name, query, args in attempts:
        try:
            db.execute("SAVEPOINT negativeCase")
            db.execute(query, args)
        except sqlite3.IntegrityError:
            passed += 1
        else:
            raise ValueError("negative control was accepted: " + name)
        finally:
            db.execute("ROLLBACK TO negativeCase")
            db.execute("RELEASE negativeCase")
    return passed


def main():
    policy, cast = load(POLICY), load(CAST)
    kernel, truth, storage, privacy, quarantine = (
        load(p) for p in (KERNEL, TRUTH, STORAGE, PRIVACY, QUARANTINE))
    c = cast["castMatrix"]
    dimensions = policy["count"]
    surfaces = policy["surfaces"]
    insist(policy["schema"] == "luhmOs.machineSqlHex512Escalation.v1"
           and policy["status"] == "REVIEW_ONLY_SQL_PROJECTION_NO_RUNTIME", "policy status drift")
    insist(dimensions == {"surfaces": 8, "castStages": 4, "interactionBeats": 4,
                          "auditTiers": 4, "total": 512, "perSurface": 64}, "512 matrix drift")
    insist(len(surfaces) == len(set(surfaces)) == 8, "eight domains required")
    insist(policy["coordinates"]["stages"] == c["stages"] and
           policy["coordinates"]["beats"] == c["beats"] and
           policy["coordinates"]["tiers"] == c["tiers"], "CAST Canon drift")
    insist([t["tier"] for t in kernel["tierSemantics"]] == [0,1,2,3], "escalation drift")
    insist(kernel["commonLaws"].count("tierIncreaseChangesFocusAndMaturityNotAuthority") == 1,
           "escalation authority misinterpreted")
    insist(truth["status"] == "AMBER_PROPOSED_SEAL_OF_TRUTH" and
           truth["crownStatus"] == "STOP", "source truth promotion drift")
    insist(storage["rules"]["databaseMayStoreCanonicalBinary"] is False and
           storage["roles"]["github"]["canonicalSourceAuthority"] is True,
           "database cannot replace Git or file store")
    insist(set(("hardwareId", "imeis", "macAddress", "diskSerial", "credentials")).issubset(
           set(privacy["privacy"]["doNotCollect"])), "machine privacy drift")
    insist(quarantine["state"] == "QUARANTINED" and
           quarantine["activeTaskWorkersAllowed"] is False, "agent quarantine drift")
    insist(policy["crownStatus"] == "STOP" and policy["productionMutation"] is False and
           policy["phpMyAdmin"]["installed"] is False and
           policy["tests"]["notLiveSql"] is True and
           policy["tests"]["sqliteOnlyInMemory"] is True, "deployment or Crown overclaim")
    maria_text = MARIA.read_text(encoding="utf-8")
    insist(maria_text.count("ENGINE=InnoDB") == 9
           and "CREATE VIEW machineStateOverview" in maria_text
           and "FOREIGN KEY" in maria_text
           and re.search(r"(?im)^\s*(CREATE DATABASE|GRANT|DROP DATABASE|ALTER USER)\b", maria_text) is None,
           "MariaDB schema drift or privileged statement found")
    source_ref = policy["sourceCanon"]["sourceRef"]
    insist(bool(HEX40.fullmatch(source_ref)), "exact source SHA format")
    db = setup()
    try:
        seed(db, source_ref)
        insist(db.execute("SELECT COUNT(*) FROM machineStateOverview WHERE verifiedBoot='UNKNOWN' AND firmwareKind='unknown' AND sourceRef=?", (source_ref,)).fetchone()[0] == 1,
               "operator-facing SQL view lost synthetic machine/device/firmware relationship")
        # Domain-specific FK and authority tests for each of 64 distinct
        # CAST coordinates. These are 512 materialized SQL scenarios, not
        # 512 live probes or 512 new agent processes.
        domain_queries = {
            "identity": "SELECT COUNT(*) FROM machineIdentity WHERE isSynthetic=1 AND identityProven IS NULL AND sourceRef=?",
            "source": "SELECT COUNT(*) FROM sourceRevision WHERE recordState='SOURCE_CANDIDATE' AND sourceRef=?",
            "device": "SELECT COUNT(*) FROM deviceRecord d JOIN machineIdentity m ON d.machineKey=m.machineKey WHERE d.verifiedBoot='UNKNOWN' AND m.isSynthetic=1 AND d.sourceRef=?",
            "firmware": "SELECT COUNT(*) FROM firmwareRecord f JOIN deviceRecord d ON f.deviceKey=d.deviceKey WHERE f.imageSha256 IS NULL AND f.verification='UNKNOWN' AND f.sourceRef=?",
            "registry": "SELECT COUNT(*) FROM namespaceRegistry WHERE namespaceKind='plugin' AND normalizedName='LuHm-OS' AND entryState='SOURCE_ONLY' AND sourceRef=?",
            "machineApi": "SELECT COUNT(*) FROM machineApi WHERE accessPolicy='READ_ONLY' AND surface='mcp' AND sourceRef=?",
            "artifact": "SELECT COUNT(*) FROM artifactPointer WHERE length(sha256)=64 AND storageLane='localSynthetic' AND sourceRef=?",
            "governance": "SELECT COUNT(*) FROM evidenceReceipt WHERE proofLevel='SOURCE_ONLY' AND evidenceKind='SOURCE_CI' AND sourceRef=?"
        }
        insist(set(domain_queries) == set(surfaces), "missing domain-specific check")
        checks, passed = 0, 0
        for domain in surfaces:
            for stage_index, stage in enumerate(c["stages"]):
                for beat_index, beat in enumerate(c["beats"]):
                    for tier_index, tier in enumerate(c["tiers"]):
                        number = 16*stage_index + 4*beat_index + tier_index
                        hex_cell = f"0x{number:02X}"
                        domain_ok = db.execute(domain_queries[domain], (source_ref,)).fetchone()[0] == 1
                        db.execute(
                            "INSERT INTO auditCoordinate VALUES(?,?,?,?,?,?,?)",
                            (domain,hex_cell,stage,beat,tier,source_ref,
                             "PASS_SOURCE_ONLY" if domain_ok else "FAIL"))
                        row = db.execute(
                            "SELECT * FROM auditCoordinate WHERE surface=? AND cellHex=?",
                            (domain,hex_cell)).fetchone()
                        passed += int(domain_ok and row is not None and
                                      row["castStage"] == stage and
                                      row["interactionBeat"] == beat and
                                      row["auditTier"] == tier and
                                      row["sourceRef"] == source_ref and
                                      row["evaluation"] == "PASS_SOURCE_ONLY")
                        checks += 1
        insist(checks == passed == 512, "a SQL coordinate or domain invariant failed")
        insist(db.execute("SELECT COUNT(*) FROM auditCoordinate").fetchone()[0] == 512,
               "SQL row coverage missing")
        negatives = negative_controls(db,source_ref)
        insist(negatives == 16,"negative SQL cases not rejected")
        db.rollback()  # synthetic rows never saved
    finally:
        db.close()
    result = {
        "schema":"luhmOs.machineSqlHex512AuditReceipt.v1",
        "status":"GREEN_SQLITE_SYNTHETIC_SOURCE_ONLY",
        "coordinates":"8×4×4×4",
        "checks":checks, "passed":passed, "negativeControls":negatives,
        "perDomain":{name:64 for name in surfaces},
        "sqliteSchemaSha256":hashlib.sha256(SQL.read_bytes()).hexdigest(),
        "mariaDbReviewSha256":hashlib.sha256(MARIA.read_bytes()).hexdigest(),
        "policySha256":hashlib.sha256(POLICY.read_bytes()).hexdigest(),
        "realDeviceInspected":False,
        "firmwareInspected":False,
        "mariaDbExecuted":False,
        "phpMyAdminInstalled":False,
        "dbPromotion":False,
        "sourceAuthorityChanged":False,
        "crownStatus":"STOP"
    }
    for digest in ("sqliteSchemaSha256","mariaDbReviewSha256","policySha256"):
        insist(bool(HEX64.fullmatch(result[digest])), "malformed schema digest")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
