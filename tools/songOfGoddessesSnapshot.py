#!/usr/bin/env python3
"""Read-only Canon crosswalk / Song of Goddesses. No workers, firmware, providers or source edits."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/songOfGoddessesSnapshotV1.json"
SHA40 = re.compile(r"[0-9a-f]{40}\\Z")

class SnapshotError(ValueError):
    pass

def stable_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")

def path_exists(path: str, root: Path) -> bool:
    if type(path) is not str or not path or "\\\\" in path:
        return False
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or p.parts[0] == ".":
        return False
    full = root / p
    return full.is_file() and not full.is_symlink() and full.resolve().is_relative_to(root.resolve())

def validate(snapshot: dict, root: Path = ROOT) -> dict:
    if type(snapshot) is not dict:
        raise SnapshotError("CONTRACT_TYPE")
    if snapshot.get("schema") != "luhmOs.songOfGoddessesSnapshot.v1" or snapshot.get("identity") != "LuHm-OS: Project Premonition":
        raise SnapshotError("IDENTITY")
    if snapshot.get("status") != "PROPOSED_SOURCE_INDEX_ONLY" or snapshot.get("authority") != "Professor":
        raise SnapshotError("STATUS_AUTHORITY")
    boundary = snapshot.get("boundaries", {})
    if (boundary.get("sourceOnly") is not True or boundary.get("activeAgentWorkers") != 0
        or boundary.get("quarantineExpected") != "QUARANTINED" or boundary.get("crownStatus") != "STOP"
        or any(boundary.get(name) is not False for name in ("automaticAgentLaunch", "automaticProductionDeploy",
            "automaticMerge", "signingAuthorized", "paidApisAuthorized", "deviceFirmwareWrite",
            "claimedSamsungProof", "claimedBlenderRuntimeProof", "claimedReleaseProof"))):
        raise SnapshotError("AUTHORITY_DRIFT")
    canon = snapshot.get("canon", {})
    required = {"architecture":"doctrine/luHmOSFourLayerArchitectureV1.json",
                "rhythm":"doctrine/fourBeatInteractionRhythmV1.json",
                "escalation":"doctrine/escalationKernelV1.json",
                "typedData":"doctrine/typedFourLaneSqlV1.json",
                "orchestra":"doctrine/lumOrchestraHardeningV1.json",
                "quarantine":"doctrine/companyWideOperationalQuarantineV1.json",
                "naming":"doctrine/namingNamespaceCanonV1.json",
                "storage":"doctrine/storageTopologyV1.json"}
    if canon != required or any(not path_exists(p, root) for p in required.values()):
        raise SnapshotError("CANON_POINTERS")
    layer_ids = [x["id"] for x in json.loads((root / required["architecture"]).read_text())["layers"]]
    beats = [x["id"] for x in json.loads((root / required["rhythm"]).read_text())["measure"]]
    streams = [x["id"] for x in json.loads((root / required["typedData"]).read_text())["lanes"]]
    environments = ["vmHeadless", "deviceKiosk", "webUi", "githubBuild"]
    if ([snapshot.get("compositionRows"),snapshot.get("interactionBeats"),snapshot.get("typedSqlStreams"),snapshot.get("runtimeSurfaces")]
        != [layer_ids,beats,streams,environments] or len(layer_ids) != 4 or len(beats) != 4 or len(streams) != 4):
        raise SnapshotError("FOUR_AXES_DRIFT")
    q=json.loads((root / required["quarantine"]).read_text())
    roles=json.loads((root / "doctrine/lumGoddessCabinetV1.json").read_text())
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        raise SnapshotError("WORKER_QUARANTINE")
    if [x.get("id") for x in roles.get("members", [])] != [x.get("id") for x in snapshot.get("godddesses", [])]:
        raise SnapshotError("GODDESS_IDENTITY")
    if len(snapshot.get("matrix", [])) != 16 or len(snapshot.get("environmentSqlMatrix", [])) != 16:
        raise SnapshotError("4X4_DIMENSIONS")
    all_addresses = set()
    for row in range(4):
        for col in range(4):
            ix=row*4+col
            first=snapshot["matrix"][ix]
            second=snapshot["environmentSqlMatrix"][ix]
            if (first.get("address") != f"0x{ix:03X}" or first.get("layer") != layer_ids[row]
                or first.get("beat") != beats[col] or first.get("status") != "SOURCE_ROUTE_ONLY"
                or not path_exists(first.get("source"),root)):
                raise SnapshotError("ARCHITECTURE_ADDRESS_DRIFT")
            if (second.get("address") != f"0x{ix+16:03X}" or second.get("environment") != environments[row]
                or second.get("stream") != streams[col] or second.get("status") != "SCHEMA_ROUTE_ONLY"
                or second.get("sqlContract") != required["typedData"] or not path_exists(second.get("entry"),root)):
                raise SnapshotError("SQL_ENV_ADDRESS_DRIFT")
            all_addresses.update((first["address"], second["address"]))
    address=snapshot.get("addressing",{})
    if (len(all_addresses) != 32 or address.get("start") != 0 or address.get("maxValue") != 2047
        or address.get("capacity") != 2048 or address.get("exclusiveUpperBoundHex") != "0x800"
        or address.get("allocatedAliases") != 32 or address.get("unusedLogicalAliases") != 2016
        or address.get("byteOffset") is not False or address.get("firmwareAddress") is not False):
        raise SnapshotError("ADDRESS_CAPACITY")
    ladder=[0]+[2**i for i in range(1,12)]
    if snapshot.get("capacityLadder") != ladder or snapshot.get("capacitySemantics") != "logicalRoutingAddressesNotConcurrentAgentsOrVerifiedTestRuns":
        raise SnapshotError("CAPACITY_LADDER")
    enc=snapshot.get("transport", {})
    if (enc.get("canonical") != "UTF-8 JSON" or enc.get("base44IsEncoding") is not False
        or enc.get("base64IsCompression") is not False or enc.get("base64IsEncryption") is not False):
        raise SnapshotError("TRANSPORT_MEANING")
    sample=stable_json({"hexAddress":"0x01F","emote":"<EMOTE_ANGRY>","product":snapshot["identity"]})
    encoded=base64.b64encode(sample)
    if base64.b64decode(encoded,validate=True) != bytes.fromhex(sample.hex()):
        raise SnapshotError("ENCODING_ROUNDTRIP")
    if snapshot.get("governingLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise SnapshotError("GOVERNANCE")
    studio=snapshot.get("studio", {})
    for key in ("assetGate","godot","ffmpeg"):
        if not path_exists(studio.get(key),root):
            raise SnapshotError("STUDIO_POINTER")
    if any(x.get("status") not in ("PROPOSED_UNMERGED","RUNTIME_UNVERIFIED","BLOCKED_PROVIDER_EVIDENCE","BLOCKED_EXTERNAL_ACL","PHYSICAL_UNVERIFIED")
           or not path_exists(x.get("reference"),root) for x in snapshot.get("completionTargets", [])):
        raise SnapshotError("FALSE_COMPLETION")
    return {"schema":"luhmOs.songOfGoddessesReceipt.v1","status":"AMBER_SOURCE_ONLY",
            "architectureCells":16,"environmentSqlCells":16,"logicalCapacity":2048,
            "allocated":32,"unverifiedCapacity":2016,"activeWorkers":0,
            "encodingRoundtrip":True,"snapshotSha256":hashlib.sha256(stable_json(snapshot)).hexdigest(),
            "githubMutation":False,"signedRelease":False,"crownStatus":"STOP"}

def index_slot(slot: int) -> str:
    if type(slot) is not int or slot < 0 or slot >= 2048:
        raise SnapshotError("INDEX_OUTSIDE_0_TO_2047")
    return f"0x{slot:03X}"

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=None)
    args=parser.parse_args()
    snapshot=json.loads(CONTRACT.read_text(encoding="utf-8"))
    receipt=validate(snapshot)
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=False)
    receipt["sourceRef"]=head.stdout.strip() if head.returncode==0 and SHA40.fullmatch(head.stdout.strip()) else None
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
