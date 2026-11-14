#!/usr/bin/env python3
"""LuHm-OS source-only compatibility roundtrip. NO network, secrets or provider calls.

Transport is the fixed Canon dialect: SQLite STRICT typed lanes -> manifest v2
JSON -> ZIP/Deflate -> RFC4648 Base64 -> decoded ZIP -> SHA-256 -> SQLite.
Google AI and 7z are explicitly non-executing gates, not simulated successes.
"""
from __future__ import annotations

import argparse
import base64
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import typedSqlStub as lanes
import archiveIntake as archive


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(b):
    return hashlib.sha256(b).hexdigest()


def expected_error(callable_, exception, message):
    try:
        callable_()
    except exception:
        return
    raise AssertionError(message)


def audit():
    source_ref = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip().lower()
    assert re.fullmatch(r"[0-9a-f]{40}", source_ref), "RED_SOURCE_REF"
    template = read("doctrine/aiTaskManifestV2.template.json")
    format_law = read("doctrine/aiManifestFormatV1.json")
    four_lanes = read("doctrine/typedFourLaneSqlV1.json")
    spine = read("doctrine/apiSpineV1.json")
    google = read("doctrine/googleAiProxyDeploymentV1.json")
    entitlements = read("doctrine/googleAiDeveloperEntitlementsV1.json")
    storage = read("doctrine/storageTopologyV1.json")
    front_pkg = read("frontEnd/package.json")
    front_lock = read("frontEnd/package-lock.json")

    assert template["schema"] == "luhmOs.aiTaskManifest.v2"
    assert template["schema"] in format_law["currentSchemas"]
    assert four_lanes["canonicalManifest"] == "doctrine/aiTaskManifestV2.template.json"
    assert [row["id"] for row in four_lanes["lanes"]] == [
        "numericStream", "textStream", "booleanStream", "aiManifestStream"
    ]
    assert four_lanes["runtimeDatabase"] is False
    assert four_lanes["crownStatus"] == "STOP"
    assert template["budget"] == {"maxRequests": 1, "maxParallel": 1, "maxPasses": 1}
    assert template["authority"] == {"mutation": False, "green": False, "crown": False}

    event_id, task_id, scope_id = "eventOne", "compatibilityTest", "testSourceOnly"
    manifest = deepcopy(template)
    manifest.update(
        status="SYNTHETIC_SOURCE_TEST_ONLY",
        providerId="googleAi",
        capabilityId="candidateReview",
        taskId=task_id,
        sourceRef=source_ref,
        scopeId=scope_id,
        requiredOutputSchema="luhmOs.providerExecutionReceipt.v1",
        inputRefs=["fixture:hello-world"],
    )
    canonical_json = json.dumps(
        manifest, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
    assert json.loads(canonical_json) == manifest
    assert len(canonical_json) < 16384
    with lanes.openStub() as db:
        lanes.addEvent(db, event_id, task_id, source_ref, scope_id,
                       "lumSupervised", 0, 1, "2026-11-14T12:00:00Z")
        lanes.putNumeric(db, event_id, "requestCount", "integer", 1)
        lanes.putNumeric(db, event_id, "fixedCost", "fixed", "0.000", scale=3)
        lanes.putText(db, event_id, "envelope", "synthetic-local-only")
        lanes.putBoolean(db, event_id, "providerVerified", None)
        no_scope = dict(manifest, scopeId="wrongScope")
        expected_error(
            lambda: lanes.putManifest(db, event_id, no_scope),
            ValueError, "RED_MISMATCH_ACCEPTED"
        )
        privileged = dict(manifest, authority={"mutation": False, "green": True, "crown": False})
        expected_error(
            lambda: lanes.putManifest(db, event_id, privileged),
            ValueError, "RED_SELF_APPROVAL_ACCEPTED"
        )
        lanes.putManifest(db, event_id, manifest)
        db.execute(
            "INSERT INTO artifactPointer "
            "(artifactId,eventId,fileName,sha256,storageLane,logicalFileRef,sizeBytes) "
            "VALUES (?,?,?,?,?,?,?)",
            ("fixtureOne", event_id, "manifest.json", digest(canonical_json),
             "githubSource", "synthetic-fixture-not-a-drive-file", len(canonical_json))
        )
        actual = lanes.orderedEvents(db, task_id, source_ref, scope_id)
        assert len(actual) == 1 and actual[0]["eventId"] == event_id
        stored = db.execute(
            "SELECT manifestJson, mutationAuthority, greenAuthority, crownAuthority "
            "FROM aiManifestStream WHERE eventId=?", (event_id,)
        ).fetchone()
        assert json.loads(stored[0]) == manifest
        assert list(stored)[1:] == [0, 0, 0]
        assert db.execute(
            "SELECT booleanValue FROM booleanStream WHERE eventId=?", (event_id,)
        ).fetchone()[0] is None
        assert db.execute(
            "SELECT scaledValue,decimalScale FROM numericStream "
            "WHERE eventId=? AND fieldName='fixedCost'", (event_id,)
        ).fetchone()[:] == (0, 3)
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []

    # Deterministic source package with only synthetic public-safe fixture.
    archive_stream = io.BytesIO()
    with ZipFile(archive_stream, "w") as zf:
        info = ZipInfo("manifest.json", date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        zf.writestr(info, canonical_json)
    sent = archive_stream.getvalue()
    encoded = base64.b64encode(sent).decode("ascii")
    received = base64.b64decode(encoded, validate=True)
    assert received == sent and received[:4] == b"PK\x03\x04"
    with ZipFile(io.BytesIO(received)) as zf:
        assert zf.namelist() == ["manifest.json"] and zf.testzip() is None
        assert archive.clean_name(zf.namelist()[0]) == "manifest.json"
        decoded = zf.read("manifest.json")
    assert decoded == canonical_json
    assert digest(decoded) == digest(canonical_json)
    assert json.loads(decoded)["sourceRef"] == source_ref
    expected_error(
        lambda: archive.clean_name("../escape.json"),
        archive.IntakeError, "RED_ARCHIVE_TRAVERSAL_ACCEPTED"
    )
    expected_error(
        lambda: archive.open_members(Path("untrusted.7z")),
        archive.IntakeError, "RED_UNREVIEWED_7Z_ACCEPTED"
    )
    tampered = bytearray(decoded)
    tampered[-1] ^= 1
    assert digest(tampered) != digest(canonical_json), "RED_HASH_MISMATCH_IGNORED"

    assert front_pkg["dependencies"]["jquery"] == "3.7.1"
    assert front_lock["packages"][""]["dependencies"]["jquery"] == "3.7.1"
    assert front_lock["packages"]["node_modules/jquery"]["version"] == "3.7.1"
    staged_js = (ROOT / "frontEnd/tools/stage-jquery.mjs").read_text(encoding="utf-8")
    assert "node_modules/jquery/dist/jquery.min.js" in staged_js
    assert "jquery-LICENSE.txt" in staged_js

    assert spine["providers"]["googleAi"]["adapterId"] == "bigBrother"
    assert spine["providers"]["googleAi"]["readiness"] == "RECEIPT_REQUIRED"
    assert google["runtimeMode"] == "READ_ONLY_STATUS_ONLY"
    assert google["networkEgress"] == "DISABLED"
    assert google["billingApproval"] == "NOT_GRANTED"
    assert google["automaticProviderCalls"] is False
    assert entitlements["executionLaw"]["defaultAction"] == "DENY"
    assert entitlements["entitlementAxes"]["developerApi"]["authorizedSmokeState"] == "UNKNOWN"
    assert storage["status"] == "candidateReview"

    return {
        "schema": "luhmOs.canonCompatibilityTransportAudit.v1",
        "verdict": "LOCAL_ROUNDTRIP_PASS_EXTERNAL_PROVIDER_BLOCKED",
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "fixture": "SYNTHETIC_NONPRIVATE",
        "proof": {
            "sqliteStrictFourLanes": True,
            "jsonManifestV2IdentityAndAuthority": True,
            "zipDeflateRoundtrip": True,
            "base64Rfc4648Roundtrip": True,
            "sha256Identity": True,
            "archiveTraversalNegativeControl": True,
            "sevenZip7zSupported": False,
            "jqueryPinnedStagingContract": True,
            "base44CanonicalContract": False,
            "githubCiWorkflowReceiptRequired": True,
            "googleAiAuthenticated": False,
            "googleAiCalled": False,
            "cloudTransferCompleted": False,
        },
        "manifestSha256": digest(canonical_json),
        "zipSha256": digest(sent),
        "manifestBytes": len(canonical_json),
        "zipBytes": len(sent),
        "base64Characters": len(encoded),
        "authority": {"mutation": False, "green": False, "crown": False},
        "crownStatus": "STOP",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
