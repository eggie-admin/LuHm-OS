#!/usr/bin/env python3
"""Canon HEX evidence into existing typed SQLite lanes; never a remote DB or signer.

Audits use existing hydraHexReleaseAudit.assess. Every 64 assessed cells
produce a SHA256 chain checkpoint; assessed cells are NOT all passed tests.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile

from tools.hydraHexReleaseAudit import assess, exact_git_sha
from tools.typedSqlStub import addEvent, openStub, putBoolean, putManifest, putNumeric, putText

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
INDEX_FIELD = re.compile(r"(?:sha(?:1|256)?|commit(?:sha|ref|id)?|sourceRef|digest|fingerprint|checksum|treeSha|headSha|baseSha)\Z", re.I)
EXCLUDE_FIELD = re.compile(r"secret|private|token|password|credential|apiKey|session|auth|pem|keyMaterial", re.I)
SCALES = (256, 512, 1024)
MAX_HASH_REFS = 4096


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf8")).hexdigest()


def hex_ref(value, field):
    """Index *explicitly named* digest/revision metadata, never generic hex strings."""
    return (isinstance(value, str) and not EXCLUDE_FIELD.search(field)
            and INDEX_FIELD.search(field) is not None
            and (SHA40.fullmatch(value) is not None or HEX64.fullmatch(value) is not None))


def collected_refs(root: Path):
    output = set()
    canon_dir = root / "doctrine"
    for path in sorted(canon_dir.glob("*.json")):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 262144:
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf8"))
        except (ValueError, UnicodeError):
            continue
        def visit(value, pointer="", field=""):
            if hex_ref(value, field):
                output.add((path.relative_to(root).as_posix(), pointer, field, value))
            elif isinstance(value, dict):
                for key, child in value.items():
                    if isinstance(key, str) and not EXCLUDE_FIELD.search(key):
                        visit(child, pointer + "/" + key.replace("~", "~0").replace("/", "~1"), key)
            elif isinstance(value, list):
                for idx, child in enumerate(value):
                    visit(child, pointer + "/" + str(idx), field)
        visit(doc)
    result = sorted(output)
    if len(result) > MAX_HASH_REFS:
        raise RuntimeError("RED_HASH_INVENTORY_CAP_REQUIRES_EXPLICIT_REVIEW")
    return result


def history(root: Path, limit=64):
    cmd = ["git", "log", "--max-count=" + str(limit), "--pretty=format:%H%x09%G?"]
    raw = subprocess.check_output(cmd, cwd=root, text=True, timeout=15)
    rows = []
    for line in raw.splitlines():
        sha, sig = line.split("\t", 1)
        if not SHA40.fullmatch(sha) or sig not in "GBUXYREN":
            raise RuntimeError("RED_COMMIT_SIGNATURE_METADATA")
        rows.append((sha, sig))
    return rows


def timestamp(root: Path):
    s = subprocess.check_output(["git", "show", "-s", "--format=%cI", "HEAD"],
                                cwd=root, text=True, timeout=10).strip()
    return datetime.fromisoformat(s).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(db, row, seq: int, source: str, observed_at: str, scope="hexMatrix"):
    event = "hexEvent" + str(seq).zfill(6)
    addEvent(db, event, "canonHexAudit", source, scope, "lum", seq,
             (seq - 1) % 8 + 1, observed_at)
    for k, v in row.items():
        if isinstance(v, bool) or v is None:
            putBoolean(db, event, k, v)
        elif isinstance(v, int):
            putNumeric(db, event, k, "integer", v)
        else:
            data = v if isinstance(v, str) else canonical_json(v)
            if len(data) > 16384:
                raise RuntimeError("RED_FIELD_EXCEEDS_SQL_BOUND")
            putText(db, event, k, data)
    return event


def build(root: Path, db_path: Path, scales=(256,), expected_source=None):
    actual = exact_git_sha()
    if expected_source is not None and expected_source != actual:
        raise ValueError("RED_EXACT_SOURCE_MISMATCH")
    if not scales or any(x not in SCALES for x in scales) or len(set(scales)) != len(scales):
        raise ValueError("RED_INVALID_SCALE_SET")
    if not (root / "LICENSE").is_file() or "GNU GENERAL PUBLIC LICENSE" not in (root / "LICENSE").read_text(encoding="utf8")[:300]:
        raise ValueError("RED_UNVERIFIED_ROOT_LICENSE")
    snapshots = [assess(scale, actual) for scale in scales]
    observed = timestamp(root)
    refs = collected_refs(root)
    commits = history(root)
    db_path = db_path.resolve()
    if db_path == root.resolve() or root.resolve() in db_path.parents:
        raise ValueError("RED_SQL_OUTPUT_INSIDE_SOURCE_TREE")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".canon-hex-", suffix=".db", dir=str(db_path.parent))
    os.close(fd)
    os.chmod(name, 0o600)
    temp = Path(name)
    try:
        db = openStub(str(temp))
        try:
            seq = 0
            checkpoints = []
            for matrix in snapshots:
                cells = matrix["cells"]
                if len(cells) != matrix["scale"] or len(cells) % 64:
                    raise RuntimeError("RED_MATRIX_INCOMPLETE")
                previous = "0" * 64
                for offset in range(0, len(cells), 64):
                    batch = cells[offset:offset + 64]
                    if len(batch) != 64:
                        raise RuntimeError("RED_PARTIAL_CHECKPOINT")
                    for cell in batch:
                        seq += 1
                        append(db, {"recordKind": "hexSlot", "scale": matrix["scale"],
                                    "hexSlot": cell["hex"], "packageFamily": cell["family"],
                                    "profileId": cell["profile"], "stage": cell["stage"],
                                    "controlId": cell["control"], "verdict": cell["status"],
                                    "evidenceRefs": cell["evidenceRefs"],
                                    "verifiedSourceOnly": cell["status"] == "GREEN_SOURCE" if cell["status"] == "GREEN_SOURCE" else None},
                               seq, actual, observed)
                    counts = dict(sorted(Counter(c["status"] for c in batch).items()))
                    digest_value = digest({"sourceRef": actual, "scale": matrix["scale"],
                                           "batch": batch, "prior": previous})
                    seq += 1
                    append(db, {"recordKind": "checkpoint64", "scale": matrix["scale"],
                                "checkpointIndex": offset // 64 + 1,
                                "hexFirst": batch[0]["hex"], "hexLast": batch[-1]["hex"],
                                "checkpointDigest": digest_value, "previousDigest": previous,
                                "statusCounts": counts, "releaseApproved": False},
                           seq, actual, observed, "hexCheckpoint")
                    checkpoints.append({"scale": matrix["scale"], "checkpoint": offset // 64 + 1,
                                        "hexFirst": batch[0]["hex"], "hexLast": batch[-1]["hex"],
                                        "sha256": digest_value, "prior": previous, "counts": counts})
                    previous = digest_value
            for sha, sig in commits:
                seq += 1
                append(db, {"recordKind": "commitMetadata", "observedCommitSha": sha,
                            "gitSignatureCode": sig, "isCurrentSource": sha == actual,
                            "signatureVerified": True if sig == "G" else None,
                            "signingEvidence": "GIT_STATUS_ONLY_NOT_CERTIFICATE_PROOF"},
                       seq, actual, observed, "gitHistory")
            for path, pointer, field, h in refs:
                seq += 1
                append(db, {"recordKind": "sourceDigestMetadata", "digestHex": h,
                            "digestBits": len(h) * 4, "fieldId": field,
                            "evidenceRef": path + "#" + pointer,
                            "historicalRefNotLiveProof": True,
                            "cryptographicVerification": None},
                       seq, actual, observed, "canonHashes")
            seq += 1
            append(db, {"recordKind": "tlsPolicy", "certificateIssuerVerified": None,
                        "selfSignedLeaf": None, "publicChainVerified": None,
                        "signingPerformedByThisTool": False,
                        "metadataSource": "doctrine/belldandyPkiCorporateSecretaryV1.json",
                        "verdict": "AMBER_LIVE_TLS_RECEIPT_REQUIRED"},
                   seq, actual, observed, "pkiMetadata")
            seq += 1
            append(db, {"recordKind": "licensePolicy", "rootLicense": "GPL-3.0",
                        "requestedCompatibility": "Apache-2.0",
                        "relicensingApproved": None,
                        "verdict": "AMBER_RIGHTSHOLDER_REVIEW_REQUIRED"},
                   seq, actual, observed, "licenseAudit")
            seq += 1
            event = append(db, {"recordKind": "agentManifestProposal", "actualWorkerExecution": False,
                                "verdict": "PLAN_ONLY_QUARANTINED"},
                           seq, actual, observed, "agentManifest")
            manifest = {"schema": "luhmOs.aiTaskManifest.v2", "taskId": "canonHexAudit",
                        "sourceRef": actual, "scopeId": "agentManifest", "providerId": "deterministicLocal",
                        "capabilityId": "sourceEvidenceIndex", "inputRefs": ["doctrine/hydraHexReleaseMatrixV1.json"],
                        "requiredOutputSchema": "luhmOs.hexEvidenceReceipt.v1",
                        "budget": {"maxRequests": 0, "maxParallel": 0, "maxPasses": 1},
                        "stopConditions": ["scopeComplete", "sourceMismatch", "evidenceConflict"],
                        "authority": {"mutation": False, "green": False, "crown": False}}
            putManifest(db, event, manifest)
            db.commit()
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("RED_SQL_INTEGRITY_CHECK")
            counts = {r[0]: r[1] for r in db.execute("SELECT textValue,count(*) FROM textStream WHERE fieldName='recordKind' GROUP BY textValue")}
        finally:
            db.close()
        temp.replace(db_path)
        os.chmod(db_path, 0o600)
        result = {"schema": "luhmOs.canonHexLedgerReceipt.v1", "sourceRef": actual,
                  "scales": list(scales), "observedAt": observed, "recordCounts": counts,
                  "checkpointCount": len(checkpoints), "checkpoints": checkpoints,
                  "matrixCounts": {str(m["scale"]):m["counts"] for m in snapshots},
                  "rootLicense": "GPL-3.0", "apache2Alignment": "RIGHTSHOLDER_REVIEW_PENDING",
                  "tlsChain": "UNVERIFIED", "selfSignedLeaf": "UNVERIFIED",
                  "signingPerformed": False, "databaseSha256": hashlib.sha256(db_path.read_bytes()).hexdigest(),
                  "databaseLocation": "LOCAL_EPHEMERAL_ONLY", "dbPersistedRemote": False,
                  "agentExecution": False, "releaseAuthority": False, "crownStatus": "STOP"}
        return result
    finally:
        if temp.exists():
            temp.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--slots", type=int, choices=SCALES, default=256)
    parser.add_argument("--all-scales", action="store_true")
    parser.add_argument("--source-ref")
    args = parser.parse_args()
    report = build(ROOT, args.db, SCALES if args.all_scales else (args.slots,), args.source_ref)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k != "checkpoints"}, sort_keys=True))


if __name__ == "__main__":
    main()
