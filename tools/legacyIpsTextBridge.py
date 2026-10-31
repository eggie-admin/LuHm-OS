#!/usr/bin/env python3
"""Synthetic IPS and text/emote bytes projected to existing typed SQLite streams.

No device, firmware, ROM file, external data, network access or binary disk writes.
"""
from __future__ import annotations
import hashlib
import json
import re

MAGIC = b"LTXT"
SLOTS = ((16, 8), (24, 8))
TOKENS = {**{i: chr(i) for i in range(65, 91)}, 0x20: " ",
          0xF0: "<EMOTE_HAPPY>", 0xF1: "<EMOTE_ANGRY>",
          0xFE: "<NEWLINE>", 0xFF: "<END>"}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fixture() -> bytes:
    data = bytearray(32)
    data[:6] = b"LTXT\x01\x02"
    data[8:12] = b"\x10\x00\x18\x00"  # Two little-endian 16-bit pointers.
    data[16:22] = bytes([0x41, 0x42, 0xF0, 0xFE, 0x43, 0xFF])
    data[24:28] = bytes([0x43, 0x20, 0xF1, 0xFF])
    return bytes(data)

def decode(data: bytes) -> list[dict]:
    if type(data) is not bytes or len(data) != 32 or data[:6] != b"LTXT\x01\x02":
        raise ValueError("SYNTHETIC_FIXTURE_ONLY")
    if data[6:8] != b"\x00\x00" or data[8:12] != b"\x10\x00\x18\x00" or data[12:16] != bytes(4):
        raise ValueError("HEADER_OR_POINTER_DRIFT")
    result = []
    for index, (offset, length) in enumerate(SLOTS):
        block = data[offset:offset+length]
        if 0xFF not in block: raise ValueError("MISSING_TERMINATOR")
        end = block.index(0xFF)
        if any(block[end+1:]): raise ValueError("NONZERO_AFTER_END")
        if any(byte not in TOKENS for byte in block[:end+1]): raise ValueError("UNMAPPED_TEXT_BYTE")
        result.append({"dialogueId": f"dialogue{index}", "offset": offset,
                       "tokens": [TOKENS[byte] for byte in block[:end+1]]})
    return result

def records(ips: bytes) -> list[tuple[int,bytes]]:
    if type(ips) is not bytes or not ips.startswith(b"PATCH") or len(ips) > 65536:
        raise ValueError("BAD_IPS")
    cursor, found = 5, []
    while True:
        if cursor + 3 > len(ips): raise ValueError("MISSING_EOF")
        if ips[cursor:cursor+3] == b"EOF":
            if cursor + 3 != len(ips) or not found: raise ValueError("TRAILING_OR_EMPTY_IPS")
            return found
        if cursor + 5 > len(ips): raise ValueError("TRUNCATED_RECORD")
        offset = int.from_bytes(ips[cursor:cursor+3], "big")
        length = int.from_bytes(ips[cursor+3:cursor+5], "big")
        cursor += 5
        if length == 0:
            if cursor+3 > len(ips): raise ValueError("TRUNCATED_RLE")
            length = int.from_bytes(ips[cursor:cursor+2], "big")
            if length == 0: raise ValueError("EMPTY_RLE")
            payload = ips[cursor+2:cursor+3] * length
            cursor += 3
        else:
            if cursor+length > len(ips): raise ValueError("TRUNCATED_PAYLOAD")
            payload = ips[cursor:cursor+length]
            cursor += length
        found.append((offset,payload))
        if len(found) > 64: raise ValueError("RECORD_LIMIT")

def demoIps() -> bytes:
    return b"PATCH" + (18).to_bytes(3,"big") + b"\x00\x01\xF1EOF"

def preview(base: bytes, ips: bytes, sourceSha256: str) -> dict:
    before = decode(base)
    if type(sourceSha256) is not str or not re.fullmatch("[0-9a-f]{64}", sourceSha256):
        raise ValueError("MISSING_SOURCE_SHA256")
    if digest(base) != sourceSha256: raise ValueError("WRONG_SOURCE_BYTES")
    changes, updated = set(), bytearray(base)
    parsed = records(ips)
    for offset, payload in parsed:
        end = offset + len(payload)
        if not any(offset >= a and end <= a+n for a,n in SLOTS):
            raise ValueError("HEADER_POINTER_OR_OUT_OF_BOUNDS_WRITE")
        if any(x in changes for x in range(offset,end)):
            raise ValueError("OVERLAPPING_PATCH")
        changes.update(range(offset,end))
        updated[offset:end] = payload
    after = decode(bytes(updated))
    changed = sum(x != y for x,y in zip(base,updated))
    if changed == 0: raise ValueError("NO_EFFECT")
    return {"schema":"luhmOs.legacyIpsTextBridge.v1",
            "status":"SYNTHETIC_SOURCE_ONLY", "sourceSha256":digest(base),
            "patchSha256":digest(ips), "targetSha256":digest(updated),
            "before":before,"after":after,"changedBytes":changed,
            "deviceFirmwareTouched":False,"publicRelease":False,"crownStatus":"STOP"}

def projectSql(receipt: dict, sourceRef: str) -> dict:
    """Reuse existing local-only four-stream schema; do not save raw binary."""
    from tools import typedSqlStub as sql
    with sql.openStub() as db:
        sql.addEvent(db,"ipsTextPreview","projectPremonition",sourceRef,
                     "syntheticBytes","lum",1,1,"2026-10-31T00:00:00Z")
        for field in ("sourceSha256","targetSha256","patchSha256"):
            sql.putText(db,"ipsTextPreview",field,receipt[field])
        sql.putText(db,"ipsTextPreview","beforeTokens",json.dumps(receipt["before"]))
        sql.putText(db,"ipsTextPreview","afterTokens",json.dumps(receipt["after"]))
        sql.putNumeric(db,"ipsTextPreview","changedBytes","integer",receipt["changedBytes"])
        count = db.execute("SELECT count(*) FROM textStream WHERE eventId=?",("ipsTextPreview",)).fetchone()[0]
    return {"textFields":count,"sqlitePersisted":False,"firmwareWritten":False}

if __name__ == "__main__":
    base = fixture()
    print(json.dumps(preview(base,demoIps(),digest(base)),indent=2))
