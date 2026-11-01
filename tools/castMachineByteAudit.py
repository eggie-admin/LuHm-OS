#!/usr/bin/env python3
"""CAST machine-layer byte/priority boundary audit; no device, network or kernel writes."""
from __future__ import annotations
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
MAX_PAYLOAD = 4096
MAX_QUEUE = 32
MAX_COUNTER = (1 << 63) - 1
AGING_NS = 2_000_000_000
REGISTRY = {
    "compute": "doctrine/computeFourCoreV1.json",
    "driverPolicy": "doctrine/hardwareVendorMinimumV1.json",
    "kernelBoundary": "doctrine/processorHexCeilingsV1.json",
    "sql": "doctrine/typedFourLaneSqlV1.json",
}
CORE_ORDER = ("gpu", "cpu", "memory", "firmware")
PHASES = ("identify", "bound", "probe", "verify")
SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z")

class MachineBoundaryError(ValueError):
    pass

def checked_int(value: object, maximum: int = MAX_COUNTER) -> int:
    if type(value) is not int or value < 0 or value > maximum:
        raise MachineBoundaryError("INVALID_NONNEGATIVE_INTEGER")
    return value

def utf8_payload(value: object) -> bytes:
    if type(value) is not str or not value or unicodedata.normalize("NFC", value) != value:
        raise MachineBoundaryError("TEXT_NOT_CANONICAL")
    try:
        raw = value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise MachineBoundaryError("INVALID_UTF8_TEXT") from exc
    if not 0 < len(raw) <= MAX_PAYLOAD:
        raise MachineBoundaryError("UTF8_BYTE_BUDGET")
    return raw

def frame_text(value: object) -> tuple[bytes, str]:
    """Four-byte big-endian APPLICATION length, not an IP packet or kernel allocation."""
    data = utf8_payload(value)
    return len(data).to_bytes(4, "big") + data, hashlib.sha256(data).hexdigest()

def unframe_text(frame: object, expected_sha256: object) -> str:
    if type(frame) is not bytes or len(frame) < 5 or len(frame) > MAX_PAYLOAD + 4:
        raise MachineBoundaryError("FRAME_SIZE")
    if type(expected_sha256) is not str or SHA256_HEX.fullmatch(expected_sha256) is None:
        raise MachineBoundaryError("DIGEST_SHAPE")
    n = int.from_bytes(frame[:4], "big")
    if n < 1 or n > MAX_PAYLOAD or n != len(frame) - 4:
        raise MachineBoundaryError("FRAME_LENGTH")
    data = frame[4:]
    if not hmac.compare_digest(hashlib.sha256(data).hexdigest(), expected_sha256):
        raise MachineBoundaryError("SHA256_MISMATCH")
    try:
        decoded = data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise MachineBoundaryError("FRAME_UTF8") from exc
    if utf8_payload(decoded) != data:
        raise MachineBoundaryError("FRAME_NOT_CANONICAL")
    return decoded

def rank_work(items: object, now_ns: object) -> list[dict]:
    """Pure in-memory queue receipt. Priority 0..3; wait aging prevents silent starvation."""
    now = checked_int(now_ns)
    if type(items) is not list or len(items) > MAX_QUEUE:
        raise MachineBoundaryError("QUEUE_BUDGET")
    seen: set[int] = set()
    result = []
    for item in items:
        if type(item) is not dict:
            raise MachineBoundaryError("QUEUE_ITEM_SHAPE")
        seq = checked_int(item.get("sequence"))
        prio = checked_int(item.get("priority"), 3)
        stamp = checked_int(item.get("enqueuedNs"))
        if seq in seen or stamp > now:
            raise MachineBoundaryError("QUEUE_SEQUENCE_OR_FUTURE")
        seen.add(seq)
        wait = now - stamp
        result.append({"sequence": seq, "basePriority": prio,
                       "effectivePriority": min(3, prio + wait // AGING_NS),
                       "waitNs": wait})
    return sorted(result, key=lambda row: (-row["effectivePriority"], row["sequence"]))

def sqlite_receipt(rows: list[dict], digest: str, byte_count: int) -> dict:
    """Disposable STRICT SQLite table; never contacts or alters a SQL service."""
    checked_int(byte_count, MAX_PAYLOAD)
    if byte_count == 0 or SHA256_HEX.fullmatch(digest) is None:
        raise MachineBoundaryError("SQL_RECEIPT_INPUT")
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE machineReceipt(
          sequence INTEGER PRIMARY KEY CHECK(sequence >= 0),
          priority INTEGER NOT NULL CHECK(priority BETWEEN 0 AND 3),
          wait_ns INTEGER NOT NULL CHECK(wait_ns >= 0),
          payload_bytes INTEGER NOT NULL CHECK(payload_bytes BETWEEN 1 AND 4096),
          sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*')
        ) STRICT""")
        for row in rows:
            db.execute("INSERT INTO machineReceipt VALUES(?,?,?,?,?)",
                       (row["sequence"], row["effectivePriority"], row["waitNs"],
                        byte_count, digest))
        got = db.execute("SELECT sequence,priority,wait_ns,payload_bytes FROM machineReceipt ORDER BY priority DESC, sequence ASC").fetchall()
    return {"sqlite": "IN_MEMORY_STRICT", "records": len(got),
            "prioritySequence": [row[0] for row in got], "serviceOpened": False}

def source_registry(root: Path = ROOT) -> list[dict]:
    receipts = []
    for kind, relative in sorted(REGISTRY.items()):
        file = root / relative
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
            raise MachineBoundaryError("REGISTRY_PATH_NOT_CANONICAL:" + kind)
        # Read at most 1 MiB; do not silently hash truncated source.
        with file.open("rb") as handle:
            data = handle.read(1048577)
        if not data or len(data) > 1048576:
            raise MachineBoundaryError("REGISTRY_SOURCE_BUDGET:" + kind)
        try:
            obj = json.loads(data.decode("utf-8"))
        except (UnicodeError, ValueError) as exc:
            raise MachineBoundaryError("REGISTRY_JSON_INVALID:" + kind) from exc
        if type(obj) is not dict or type(obj.get("schema")) is not str:
            raise MachineBoundaryError("REGISTRY_SCHEMA_INVALID:" + kind)
        receipts.append({"kind": kind, "source": relative, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest(), "proof": "SOURCE_DIGEST_ONLY"})
    return receipts

def audit(root: Path = ROOT) -> dict:
    contract = json.loads((root / REGISTRY["compute"]).read_text(encoding="utf-8"))
    if contract.get("schema") != "luhmOs.computeFourCore.v1" or contract.get("crownStatus") != "STOP":
        raise MachineBoundaryError("COMPUTE_AUTHORITY")
    if [r.get("id") for r in contract.get("rows", [])] != list(CORE_ORDER) or contract.get("phases") != list(PHASES):
        raise MachineBoundaryError("COMPUTE_4X4_AXES")
    runtime = contract.get("runtime", {})
    for key in ("physicalSamsungVerified", "deviceDriverVerified", "hostGpuAccelerationVerified",
                "firmwareVersionVerified", "biosChange", "grubChange", "gpuDriverInstall",
                "dmaOrKernelModuleLoad", "networkListener", "agentActivated"):
        if runtime.get(key) is not False:
            raise MachineBoundaryError("RUNTIME_PROMOTION_OR_MUTATION:" + key)
    if any(contract.get(flag) is not True for flag in
           ("noHardwareMutation", "noPackageMutation", "noProductionDeploy", "noAutomaticMerge")):
        raise MachineBoundaryError("AUTHORITY_FLAGS")
    frame, sha = frame_text("Lum ✦ 優先: priority")
    if unframe_text(frame, sha) != "Lum ✦ 優先: priority":
        raise MachineBoundaryError("ROUNDTRIP")
    items = [{"sequence": 1, "priority": 0, "enqueuedNs": 0},
             {"sequence": 2, "priority": 3, "enqueuedNs": 9_000_000_000},
             {"sequence": 3, "priority": 1, "enqueuedNs": 8_000_000_000}]
    ranked = rank_work(items, 10_000_000_000)
    sql = sqlite_receipt(ranked, sha, len(frame) - 4)
    registry = source_registry(root)
    # Scores express blocked proof gates, not measured performance or kernel run-queue priorities.
    missing = [
        {"priority": 0, "area": "firmware/driver", "missing": "actual OEM/kernel binding and boot proof"},
        {"priority": 1, "area": "gpu", "missing": "real device acceleration and frame-time proof"},
        {"priority": 2, "area": "memory/packet", "missing": "device memory pressure and p95 transport proof"},
        {"priority": 3, "area": "cpu", "missing": "physical device thermal/quota performance baseline"},
    ]
    return {"schema": "luhmOs.castMachineBoundaryReceipt.v1", "status": "AMBER_SOURCE_ONLY",
            "matrix": {"core": list(CORE_ORDER), "phase": list(PHASES),
                       "logicalCells": [f"0x{i:02X}" for i in range(16)],
                       "cellsPhysicallyProven": 0},
            "utf8": {"characters": len("Lum ✦ 優先: priority"), "bytes": len(frame) - 4,
                     "headerBytes": 4, "sha256": sha, "packetType": "APPLICATION_FRAME_NOT_IP"},
            "priority": {"agingNs": AGING_NS, "ordered": ranked, "schedulerModified": False},
            "sql": sql, "registry": registry, "unverifiedGates": missing,
            "driverQueried": False, "kernelChanged": False, "physicalDeviceVerified": False,
            "publicNetworkOpened": False, "crownStatus": "STOP"}

if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
