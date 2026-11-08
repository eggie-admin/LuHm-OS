#!/usr/bin/env python3
"""LuHm-OS 0xC1 CAST Bridge: strict AI JSON -> read-only candidate SQL receipt.
No remote connection, phpMyAdmin, shell, firmware, plugin install or CAST dispatch.
All tests execute against disposable in-memory SQLite synthetic fixtures.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/machineCastHexBridgeV1.json"
SCHEMA = ROOT / "doctrine/machineCastHexManifestV1.schema.json"
CAST = ROOT / "doctrine/fnCastV1.yaml"
TEMPLATE = ROOT / "doctrine/aiTaskManifestV2.template.json"
SQL = ROOT / "host/api/machineRegistrySqliteV1.sql"
MACHINE_POLICY = ROOT / "doctrine/machineSqlHex512EscalationV1.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IDENT = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
TIME = "2026-11-07T00:00:00Z"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def build_manifest(source_ref, task_id="machineCastReview", scope_id="machineSql", *,
                   beat="hear", tier="technologyFastPath"):
    policy = load(POLICY)
    template = load(TEMPLATE)
    manifest = {k: deepcopy(template[k]) for k in (
        "schema", "providerId", "capabilityId", "taskId", "sourceRef", "scopeId",
        "inputRefs", "requiredOutputSchema", "budget", "stopConditions",
        "authority", "responseRequired")}
    manifest.update({
        "status": "SOURCE_CANDIDATE",
        "providerId": policy["api"]["providerId"],
        "capabilityId": policy["api"]["capabilityId"],
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "requiredOutputSchema": "luhmOs.machineCastHexBridgeReceipt.v1",
        "machineBridge": {
            "schema": policy["api"]["bridgeSchema"],
            "displayName": policy["product"],
            "asciiHex": policy["encoding"]["asciiBytesHex"],
            "opcode": policy["encoding"]["opcode"],
            "mode": "inspectCandidate",
            "fromStage": "castProposed",
            "stage": "castBridge",
            "beat": beat, "tier": tier,
            "dispatchAuthorized": False,
            "machineSqlWritable": False
        }
    })
    return manifest


def validate_manifest(manifest, checked_out_source_ref):
    policy, contract, schema = load(POLICY), load(CAST), load(SCHEMA)
    check(policy["status"] == "REVIEW_ONLY_HEX_INTENT_NO_EXECUTION"
          and policy["boundary"]["hexOpcodeDispatchesBuild"] is False
          and policy["boundary"]["sqlExecutesManifest"] is False
          and policy["boundary"]["crown"] == "STOP", "unsafe policy")
    check(schema["$schema"] == "https://json-schema.org/draft/2020-12/schema",
          "unknown schema dialect")
    check(isinstance(manifest, dict) and type(checked_out_source_ref) is str
          and HEX40.fullmatch(checked_out_source_ref), "manifest or bound SHA malformed")
    props = schema["properties"]
    required = schema["required"]
    check(set(manifest) == set(required) == set(props), "extra or missing manifest key")
    for name in ("taskId", "scopeId"):
        check(type(manifest.get(name)) is str and IDENT.fullmatch(manifest[name]),
              "invalid task or scope")
    source_ref = manifest.get("sourceRef")
    check(type(source_ref) is str and HEX40.fullmatch(source_ref)
          and source_ref == checked_out_source_ref, "exact checked-out sourceRef required")
    for field in ("schema", "status", "providerId", "capabilityId", "requiredOutputSchema"):
        check(manifest.get(field) == props[field]["const"], "manifest identity drift: " + field)
    check(manifest.get("inputRefs") == [], "no external refs on bridge")
    check(manifest.get("budget") == {"maxRequests": 1, "maxParallel": 1, "maxPasses": 1},
          "unbounded budget")
    check(manifest.get("authority") == {"mutation": False, "green": False, "crown": False}
          and all(type(x) is bool for x in manifest["authority"].values()), "self approval")
    base = load(TEMPLATE)
    check(manifest.get("stopConditions") == base["stopConditions"]
          and manifest.get("responseRequired") == base["responseRequired"], "CANON fields modified")
    bridge = manifest.get("machineBridge")
    bridge_schema = props["machineBridge"]
    check(isinstance(bridge,dict) and set(bridge) == set(bridge_schema["required"]),
          "bridge missing/extra field")
    check(bridge.get("schema") == policy["api"]["bridgeSchema"] and
          bridge.get("displayName") == "LuHm-OS"
          and bridge.get("opcode") == "0xC1"
          and bridge.get("asciiHex") == "CAST".encode("ascii").hex().upper()
          and bridge.get("mode") == "inspectCandidate", "hex or brand drift")
    check(bridge.get("dispatchAuthorized") is False
          and bridge.get("machineSqlWritable") is False, "execution attempted")
    check(bridge.get("fromStage") == "castProposed"
          and bridge.get("stage") == "castBridge"
          and bridge.get("beat") in contract["castMatrix"]["beats"]
          and bridge.get("tier") in contract["castMatrix"]["tiers"], "CAST coordinate drift")
    # Validate via the existing CAST compiler; never set voiceAccepted true
    # based on a hexadecimal string or JSON packet.
    try:
        from tools.fnCastMatrix import compileMatrixIntent
    except ModuleNotFoundError:
        from fnCastMatrix import compileMatrixIntent
    cast = compileMatrixIntent(contract, stage=bridge["stage"],
                               beat=bridge["beat"], tier=bridge["tier"],
                               fromStage=bridge["fromStage"],
                               taskId=manifest["taskId"], scopeId=manifest["scopeId"],
                               requestedSourceRef=source_ref,
                               checkedOutSourceRef=checked_out_source_ref,
                               voiceAccepted=False)
    check(cast["stageTransitionValid"] is True and cast["sourceBound"] is True
          and cast["buildDispatched"] is False and cast["crownGranted"] is False
          and cast["status"] == "HOLD_UNARMED_OR_UNSCOPED", "CAST authority drift")
    packed = canonical_json(manifest)
    check(len(packed.encode("utf-8")) <= 16384, "manifest exceeds bounded size")
    return {"validated": True, "sha256": digest(packed), "packed": packed,
            "cast": cast, "status": "HOLD_SEPARATE_PROFESSOR_CAST"}


def open_memory_db():
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SQL.read_text(encoding="utf-8"))
    return db


def stage_in_memory(db, manifest, checked_out_source_ref):
    receipt = validate_manifest(manifest, checked_out_source_ref)
    source_ref = manifest["sourceRef"]
    bridge = manifest["machineBridge"]
    db.execute("INSERT INTO sourceRevision VALUES(?,?,?,?,?)",
               (source_ref, "a"*64, "eggie-admin/LuHm-OS", "SOURCE_CANDIDATE", TIME))
    db.execute("INSERT INTO castOpcodeRegistry VALUES(?,?,?,?,?,?)",
               ("0xC1", "43415354", "castIntent", "INTENT_ONLY", 0, source_ref))
    sha = receipt["sha256"]
    db.execute("INSERT INTO aiManifestReceipt VALUES(?,?,?,?,?,?,?,?,?,?)",
               (sha[:32], "0xC1", manifest["taskId"], manifest["scopeId"], source_ref,
                sha, receipt["packed"], "INTENT_CANDIDATE_HOLD", 0, 0))
    db.execute("INSERT INTO castIntentReceipt VALUES(?,?,?,?,?,?,?,?,?)",
               ("intentCandidate", sha[:32], source_ref, "castBridge",
                bridge["beat"], bridge["tier"], "HOLD_SEPARATE_PROFESSOR_CAST",
                0, "none"))
    row = db.execute("""SELECT m.manifestSha256,m.mutationGranted,m.crownGranted,
                              i.dispatched,i.authorityEffect
                        FROM aiManifestReceipt m
                        JOIN castIntentReceipt i ON m.manifestKey=i.manifestKey
                        WHERE m.manifestKey=?""", (sha[:32],)).fetchone()
    check(row is not None and row[0] == sha and row[1:] == (0,0,0,"none"),
          "SQL receipt lost authority boundary")
    return {"schema":"luhmOs.machineCastHexBridgeReceipt.v1",
            "opcode":"0xC1","asciiHex":"43415354","manifestSha256":sha,
            "sourceBound":True, "stageTransitionValid":True,
            "state":"HOLD_SEPARATE_PROFESSOR_CAST",
            "sql":"SYNTHETIC_SQLITE_IN_MEMORY", "dispatched":False,
            "crownGranted":False, "machineInspected":False}


def self_test():
    source_ref = load(MACHINE_POLICY)["sourceCanon"]["sourceRef"]
    check(HEX40.fullmatch(source_ref), "fixture source SHA")
    manifest = build_manifest(source_ref)
    check(validate_manifest(manifest,source_ref)["validated"], "positive manifest failed")
    with open_memory_db() as db:
        success = stage_in_memory(db, manifest, source_ref)
        # A replayed manifest digest cannot register as a new source event.
        try:
            stage_in_memory(db,manifest,source_ref)
        except sqlite3.IntegrityError:
            pass
        else:
            raise ValueError("replayed manifest accepted")
        classes = load(POLICY)["sql"]["componentClasses"]
        check(len(classes) == 29, "component classes changed")
        db.execute("INSERT INTO machineIdentity VALUES(?,?,?,?,?,?)",
                   ("1"*32,"SYNTHETIC", "synthetic",source_ref,None,1))
        for index, kind in enumerate(classes):
            key = f"{index+1:032x}"
            db.execute("INSERT INTO machineComponent VALUES(?,?,?,?,?,?,?,?)",
                       (key, "1"*32, kind, "SYNTHETIC_"+kind,None,None,"SYNTHETIC",source_ref))
        # Synthetic linked machine graph, not real hardware proof.
        db.execute("INSERT INTO machineComponentLink VALUES(?,?,?,?)",
                   (f"{1:032x}", f"{2:032x}", "dependsOn", source_ref))
        check(db.execute("SELECT count(*) FROM machineComponent").fetchone()[0] == 29,
              "component class inventory incomplete")
        db.rollback()
    negatives=[]
    def reject(label,mutate,checkout=None):
        x=deepcopy(manifest);mutate(x)
        try:
            validate_manifest(x,source_ref if checkout is None else checkout)
        except (ValueError,TypeError,KeyError):
            negatives.append(label)
        else:
            raise ValueError("negative control accepted: "+label)
    reject("wrongHexOpcode",lambda x:x["machineBridge"].update(opcode="0xC2"))
    reject("textCastAsciiAsOpcode",lambda x:x["machineBridge"].update(opcode="0x43415354"))
    reject("lowercaseOpcode",lambda x:x["machineBridge"].update(opcode="0xc1"))
    reject("incorrectAscii",lambda x:x["machineBridge"].update(asciiHex="43415355"))
    reject("wrongProductCase",lambda x:x["machineBridge"].update(displayName="LuHm-os"))
    reject("unscopedTask",lambda x:x.update(taskId="../shell"))
    reject("badScope",lambda x:x.update(scopeId=""))
    reject("sourceDrift",lambda x:x.update(sourceRef="b"*40))
    reject("unknownCheckout",lambda x:x,checkout="b"*40)
    reject("shortSource",lambda x:x.update(sourceRef="a"*7))
    reject("oversizedBudget",lambda x:x["budget"].update(maxPasses=512))
    reject("selfCrown",lambda x:x["authority"].update(crown=True))
    reject("selfMutation",lambda x:x["authority"].update(mutation=True))
    reject("selfGreen",lambda x:x["authority"].update(green=True))
    reject("secretInput",lambda x:x.update(inputRefs=["private://credential"]))
    reject("extraCommand",lambda x:x.update(command="rm -rf /"))
    reject("extraBridgeParameter",lambda x:x["machineBridge"].update(sql="DROP TABLE sourceRevision"))
    reject("prematureStage",lambda x:x["machineBridge"].update(stage="cast"))
    reject("wrongFromStage",lambda x:x["machineBridge"].update(fromStage="castTesting"))
    reject("invalidTier",lambda x:x["machineBridge"].update(tier="newAuthorityTier"))
    reject("networkAuthorization",lambda x:x["machineBridge"].update(dispatchAuthorized=True))
    reject("sqlAuthorization",lambda x:x["machineBridge"].update(machineSqlWritable=True))
    reject("otherProvider",lambda x:x.update(providerId="untrusted"))
    reject("otherSchema",lambda x:x.update(schema="luhmOs.aiTaskManifest.v3"))
    check(len(negatives)==24, "24 negative manifest controls required")
    return {"status":"GREEN_SQLITE_SOURCE_ONLY","passedManifestControls":24,
            "componentClasses":29,"hexOpcode":"0xC1",
            "asciiHex":"43415354",**success,"sourceAuthorityChanged":False,
            "agentQuarantineLifted":False,"crown":"STOP"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--source-ref",default="")
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2,sort_keys=True))
        return
    if not HEX40.fullmatch(args.source_ref):
        parser.error("full exact lowercase 40-hex sourceRef required")
    result=validate_manifest(build_manifest(args.source_ref), args.source_ref)
    print(json.dumps({"state":result["status"],"manifestSha256":result["sha256"],
                      "opcode":"0xC1", "dispatchAuthorized":False, "crown":"STOP"},indent=2))


if __name__ == "__main__":
    main()
