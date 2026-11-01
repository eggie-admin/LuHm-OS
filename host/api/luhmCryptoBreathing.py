#!/usr/bin/env python3
"""LuHm R1-R4 crypto breathing gates. Host-only and bounded, never a release decision.

R1/R2 verify unkeyed digests, R3 verifies a keyed MAC, R4 verifies AEAD
decryption if cryptography is installed and an authorized host supplies keys.
No keys/contents are logged, persisted, or returned. No network calls.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "doctrine" / "cryptoBreathingEscalationV1.json"
IDENT = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
SOURCE = re.compile(r"^[0-9a-f]{40}$")
HEX = re.compile(r"^[0-9a-f]+$")
MAX_BYTES = 1024 * 1024


def load_canon() -> dict[str, Any]:
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    if canon.get("schema") != "luhmOs.cryptoBreathingEscalation.v1":
        raise RuntimeError("RED_CRYPTO_CANON_SCHEMA")
    if [s["id"] for s in canon["stages"]] != ["R1", "R2", "R3", "R4"]:
        raise RuntimeError("RED_CRYPTO_LADDER_ORDER")
    return canon


def _hex(value: str | None, digits: int) -> bool:
    return isinstance(value, str) and len(value) == digits and HEX.fullmatch(value) is not None


def _bound(task_id: str, source_ref: str, scope_id: str, artifact_id: str,
           payload: bytes) -> None:
    if not all(isinstance(v, str) and IDENT.fullmatch(v)
               for v in (task_id, scope_id, artifact_id)):
        raise ValueError("task/scope/artifact identity invalid")
    if not isinstance(source_ref, str) or not SOURCE.fullmatch(source_ref):
        raise ValueError("exact 40-digit source SHA required")
    if not isinstance(payload, bytes) or len(payload) > MAX_BYTES:
        raise ValueError("bounded immutable bytes required")


def _auth_bytes(task_id: str, source_ref: str, scope_id: str, artifact_id: str,
                snapshot_ref: str, sha256_hex: str) -> bytes:
    # Domain-separated deterministic canonical form. The same bytes are GCM AAD.
    return b"LUHM-CRYPTO-BREATHING-V1\0" + json.dumps({
        "artifactId": artifact_id, "scopeId": scope_id,
        "snapshotRef": snapshot_ref, "sourceRef": source_ref,
        "sha256": sha256_hex, "taskId": task_id,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def seal_local_snapshot(*, task_id: str, source_ref: str, scope_id: str,
                        artifact_id: str, snapshot_ref: str,
                        payload: bytes, encryption_key: bytes) -> dict[str, bytes]:
    """Encrypt a bounded snapshot in memory with AES-256-GCM.

    Returned nonce/ciphertext must be stored through a separately authorized
    private binary-storage lane. A random 96-bit nonce is generated per call.
    This does not write a file, export a key or publish an artifact.
    """
    import secrets
    _bound(task_id, source_ref, scope_id, artifact_id, payload)
    if not isinstance(snapshot_ref, str) or IDENT.fullmatch(snapshot_ref) is None:
        raise ValueError("valid snapshotRef required")
    if not isinstance(encryption_key, bytes) or len(encryption_key) != 32:
        raise ValueError("AES-256 key must be 32 bytes")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = secrets.token_bytes(12)
    aad = _auth_bytes(task_id, source_ref, scope_id, artifact_id,
                      snapshot_ref, hashlib.sha256(payload).hexdigest())
    return {"nonce": nonce, "ciphertext": AESGCM(encryption_key).encrypt(nonce, payload, aad)}


def status() -> dict[str, Any]:
    canon = load_canon()
    return {
        "schema": "luhmOs.cryptoBreathingStatus.v1",
        "stages": [{"id": row["id"], "check": row["check"]} for row in canon["stages"]],
        "maxPasses": 4,
        "mariaDbConnected": False,
        "keyAvailability": "UNKNOWN_NOT_EXPOSED",
        "storedSnapshotsProven": False,
        "liveAgentThreads": 0,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def run_ladder(*, task_id: str, source_ref: str, scope_id: str,
               artifact_id: str, payload: bytes,
               expected_sha256: str | None = None,
               expected_sha512: str | None = None,
               expected_sha3_256: str | None = None,
               snapshot_ref: str | None = None,
               mac_key: bytes | None = None, expected_mac: str | None = None,
               encrypted_snapshot: bytes | None = None,
               nonce: bytes | None = None, encryption_key: bytes | None = None,
               ) -> dict[str, Any]:
    """A strictly bounded for-loop, stopping at first non-PASS. No I/O."""
    _bound(task_id, source_ref, scope_id, artifact_id, payload)
    canon = load_canon()
    sha256 = hashlib.sha256(payload).hexdigest()
    sha512 = hashlib.sha512(payload).hexdigest()
    sha3 = hashlib.sha3_256(payload).hexdigest()
    results: list[dict[str, Any]] = []
    auth_data: bytes | None = None
    for stage in canon["stages"]:
        name = stage["id"]
        check_state, reason = "HOLD", "EVIDENCE_MISSING"
        if name == "R1":
            if _hex(expected_sha256, 64):
                check_state, reason = (
                    ("PASS", "BYTE_DIGEST_MATCH") if
                    hmac.compare_digest(sha256, expected_sha256) else
                    ("STOP", "SHA256_MISMATCH"))
        elif name == "R2":
            if not isinstance(snapshot_ref, str) or IDENT.fullmatch(snapshot_ref) is None:
                reason = "SNAPSHOT_REF_MISSING"
            elif _hex(expected_sha512, 128) and _hex(expected_sha3_256, 64):
                if hmac.compare_digest(sha512, expected_sha512) and hmac.compare_digest(sha3, expected_sha3_256):
                    check_state, reason = "PASS", "SECONDARY_DIGESTS_MATCH"
                    auth_data = _auth_bytes(task_id, source_ref, scope_id, artifact_id, snapshot_ref, sha256)
                else:
                    check_state, reason = "STOP", "SECONDARY_DIGEST_MISMATCH"
        elif name == "R3":
            if isinstance(mac_key, bytes) and len(mac_key) >= 32 and _hex(expected_mac, 64) and auth_data is not None:
                actual_mac = hmac.new(mac_key, auth_data, hashlib.sha256).hexdigest()
                check_state, reason = (
                    ("PASS", "HOST_MAC_VERIFIED") if hmac.compare_digest(actual_mac, expected_mac)
                    else ("STOP", "HOST_MAC_MISMATCH"))
            else:
                reason = "HOST_MAC_PROOF_MISSING"
        elif name == "R4":
            if isinstance(encryption_key, bytes) and len(encryption_key) == 32 and (
                isinstance(nonce, bytes) and len(nonce) == 12) and (
                isinstance(encrypted_snapshot, bytes) and 16 <= len(encrypted_snapshot) <= MAX_BYTES + 16) and auth_data is not None:
                try:
                    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                except ImportError:
                    reason = "AESGCM_DEPENDENCY_UNAVAILABLE"
                else:
                    try:
                        plaintext = AESGCM(encryption_key).decrypt(nonce, encrypted_snapshot, auth_data)
                    except (ValueError, Exception):
                        # Never reveal keys, ciphertext, or attacker-controlled exception text.
                        check_state, reason = "STOP", "AESGCM_AUTHENTICATION_FAILED"
                    else:
                        check_state, reason = (
                            ("PASS", "AEAD_SNAPSHOT_BYTES_MATCH") if hmac.compare_digest(plaintext, payload)
                            else ("STOP", "ENCRYPTED_SNAPSHOT_CONTENT_MISMATCH"))
            else:
                reason = "AEAD_SNAPSHOT_PROOF_MISSING"
        results.append({"stage": name, "state": check_state, "reason": reason,
                        "localEvidenceOnly": True})
        if check_state != "PASS":
            break
    all_passed = len(results) == 4 and all(r["state"] == "PASS" for r in results)
    return {
        "schema": "luhmOs.cryptoBreathingReceipt.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "artifactId": artifact_id, "sha256": sha256, "sha512": sha512,
        "sha3_256": sha3, "bytesInspected": len(payload),
        "stages": results, "passes": len(results), "maxPasses": 4,
        "state": "HOLD_FOR_PROFESSOR" if all_passed else
                 ("STOP" if results[-1]["state"] == "STOP" else "HOLD"),
        "nextGate": "EXACT_SHA_CI_AND_PROFESSOR_APPROVAL" if all_passed else results[-1]["stage"],
        "networkCalls": 0, "mariaDbWrites": 0, "agentExecutions": 0,
        "encryptedSnapshotPersisted": False,
        "sourceVerifiedAgainstCurrentMain": False,
        "mutationAuthority": False, "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
