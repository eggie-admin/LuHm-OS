#!/usr/bin/env python3
"""Read-only two-by-two Canon alignment. No renaming, execution or promotion."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/canonLikeTermPairsV1.json"
RELATIONS = {"supersedes", "aliasOnly", "specializes", "differentAxes", "implements", "complements"}
GUARDS = (
    "liveDeviceProof", "permissionChange", "automaticMerge", "automaticRename",
    "deleteHistoricalReceipts", "automaticPromotion"
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_file(root: Path, rel: str):
    if not isinstance(rel, str) or not rel or "\\" in rel:
        return None
    parts = PurePosixPath(rel).parts
    if not parts or any(part in {"..", "."} for part in parts) or PurePosixPath(rel).is_absolute():
        return None
    path = root.joinpath(*parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        return None
    return path


def audit(root: Path = ROOT, contract: dict | None = None) -> dict:
    errors = []
    warnings = []
    if contract is None:
        contract = load_json(root / CONTRACT)
    if contract.get("schema") != "luhmOs.canonLikeTermPairs.v1":
        errors.append("BAD_SCHEMA_ID")
    if contract.get("status") != "PROPOSED_SOURCE_ONLY" or contract.get("promotion") is not False:
        errors.append("PROMOTION_GUARD")
    if contract.get("crownStatus") != "STOP":
        errors.append("CROWN_GUARD")
    guards = contract.get("evidenceCeiling") or {}
    for key in GUARDS:
        if guards.get(key) is not False:
            errors.append("UNSAFE_EVIDENCE_CEILING:" + key)
    if guards.get("textualSourceProofOnly") is not True:
        errors.append("SOURCE_PROOF_BOUNDARY")

    rows = contract.get("pairs")
    if not isinstance(rows, list) or not rows:
        errors.append("NO_PAIR_INVENTORY")
        rows = []
    seen_pairs = set()
    relation_counts = Counter()
    domain_counts = Counter()
    observed = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"INVALID_ROW:{index}")
            continue
        rid = row.get("pairId")
        domain = row.get("domain")
        relation = row.get("relation")
        a, b = row.get("anchorPath"), row.get("peerPath")
        if not isinstance(rid, str) or not rid:
            errors.append(f"MISSING_PAIR_ID:{index}")
        if relation not in RELATIONS:
            errors.append(f"INVALID_RELATION:{index}")
        if not isinstance(domain, str) or not domain:
            errors.append(f"INVALID_DOMAIN:{index}")
        if not isinstance(a, str) or not isinstance(b, str):
            errors.append(f"INVALID_PATH:{index}")
            continue
        key = tuple(sorted((a, b)))
        if a == b or key in seen_pairs:
            errors.append(f"DUPLICATE_OR_SELF_PAIR:{index}")
        seen_pairs.add(key)
        path_a, path_b = safe_file(root, a), safe_file(root, b)
        if path_a is None or path_b is None:
            errors.append(f"MISSING_OR_UNSAFE_PATH:{index}")
            continue
        ids = {}
        anchor_payload = None
        for rel, path in ((a, path_a), (b, path_b)):
            if path.suffix.lower() == ".json":
                try:
                    payload = load_json(path)
                except (OSError, ValueError) as exc:
                    errors.append(f"INVALID_LINKED_JSON:{rel}:{type(exc).__name__}")
                    continue
                if not isinstance(payload, dict) or not isinstance(payload.get("schema"), str):
                    errors.append(f"NO_LINKED_SCHEMA:{rel}")
                    continue
                ids[rel] = payload["schema"]
                if rel == a:
                    anchor_payload = payload
        # An explicit supersedes relation must already be recorded by the anchor itself.
        if relation == "supersedes" and (
            not isinstance(anchor_payload, dict)
            or b not in json.dumps(anchor_payload, sort_keys=True)
        ):
            errors.append(f"UNSUPPORTED_SUPERSESSION:{index}")
        relation_counts[relation] += 1
        domain_counts[domain] += 1
        observed.append({"pairId": rid, "domain": domain, "relation": relation,
                         "anchorPath": a, "peerPath": b, "schemaIds": ids})

    schema_locations = defaultdict(list)
    statuses = Counter()
    scanned = 0
    bad_json = []
    missing_schema = []
    doctrine = root / "doctrine"
    if doctrine.is_dir():
        for path in sorted(doctrine.glob("*.json")):
            if path.is_symlink():
                warnings.append("SYMLINK_SKIPPED:" + path.name)
                continue
            scanned += 1
            try:
                obj = load_json(path)
            except (OSError, ValueError):
                bad_json.append(path.name)
                continue
            if not isinstance(obj, dict) or not isinstance(obj.get("schema"), str):
                missing_schema.append(path.name)
                continue
            schema_locations[obj["schema"]].append(path.name)
            statuses[str(obj.get("status", "UNDECLARED"))] += 1
    else:
        warnings.append("DOCTRINE_DIRECTORY_UNAVAILABLE")
    collisions = {schema: files for schema, files in schema_locations.items() if len(files) > 1}
    if bad_json:
        warnings.append(f"DOCTRINE_JSON_PARSE_REVIEW:{len(bad_json)}")
    if missing_schema:
        warnings.append(f"DOCTRINE_SCHEMA_ABSENT_REVIEW:{len(missing_schema)}")
    if collisions:
        warnings.append(f"NON_UNIQUE_DECLARED_SCHEMA_IDS_REVIEW:{len(collisions)}")

    head = None
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                       capture_output=True, text=True, check=False)
    if p.returncode == 0 and len(p.stdout.strip()) == 40:
        head = p.stdout.strip()
    else:
        warnings.append("EXACT_SOURCE_REF_UNAVAILABLE")

    return {
        "schema": "luhmOs.canonLikeTermPairsReceipt.v1",
        "auditedSourceRef": head,
        "verdict": "RED_PAIRWISE_INDEX" if errors else "AMBER_PROPOSED_SOURCE_ONLY",
        "scope": "explicitTermPairs_and_nonAuthoritativeDoctrineInventory",
        "pairCount": len(observed),
        "domains": dict(sorted(domain_counts.items())),
        "relations": dict(sorted(relation_counts.items())),
        "doctrineJsonFilesScanned": scanned,
        "doctrineRootStatuses": dict(sorted(statuses.items())),
        "unparsedDoctrineJson": bad_json[:15],
        "doctrineFilesWithoutDeclaredSchema": missing_schema[:15],
        "duplicateDeclaredSchemaIds": dict(list(sorted(collisions.items()))[:15]),
        "observedPairs": observed,
        "errors": errors,
        "warnings": warnings,
        "renamedFiles": 0,
        "deletedFiles": 0,
        "liveRuntimeVerified": False,
        "releaseAuthority": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=None,
                   help="Optional local JSON receipt path; no network or source mutation")
    p.add_argument("--details", action="store_true")
    a = p.parse_args()
    report = audit()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not a.details:
        report = {k: v for k, v in report.items() if k not in ("observedPairs", "doctrineRootStatuses")}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
