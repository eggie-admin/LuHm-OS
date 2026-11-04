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

    # Reconcile exception types before calling a doctrine item broken.
    exceptions = contract.get("reviewedExceptions") or {}
    declared_defs = set(exceptions.get("jsonSchemaDefinitions") or [])
    declared_receipts = set(exceptions.get("datedHistoricalReceipts") or [])
    if not declared_defs or not declared_receipts:
        errors.append("MISSING_REVIEWED_EXCEPTION_CLASSIFICATION")
    if declared_defs & declared_receipts:
        errors.append("EXCEPTION_CLASSIFICATION_COLLISION")
    schema_locations = defaultdict(list)
    statuses = Counter()
    scanned = 0
    bad_json = []
    missing_schema = []
    resolved_defs = []
    resolved_receipts = []
    doctrine = root / "doctrine"
    if doctrine.is_dir():
        for path in sorted(doctrine.glob("*.json")):
            if path.is_symlink():
                warnings.append("SYMLINK_SKIPPED:" + path.name)
                continue
            scanned += 1
            rel = path.relative_to(root).as_posix()
            try:
                obj = load_json(path)
            except (OSError, ValueError):
                bad_json.append(path.name)
                continue
            if not isinstance(obj, dict):
                missing_schema.append(path.name)
                continue
            if not isinstance(obj.get("schema"), str):
                if (rel in declared_defs and isinstance(obj.get("$schema"), str)
                        and isinstance(obj.get("$id"), str) and obj.get("type") == "object"):
                    resolved_defs.append(rel)
                elif rel in declared_receipts and path.name.endswith("-20260925.json"):
                    resolved_receipts.append(rel)
                else:
                    missing_schema.append(path.name)
                continue
            schema_locations[obj["schema"]].append(path.name)
            statuses[str(obj.get("status", "UNDECLARED"))] += 1
    else:
        warnings.append("DOCTRINE_DIRECTORY_UNAVAILABLE")

    if declared_defs != set(resolved_defs):
        errors.append("JSON_SCHEMA_DEFINITION_REVIEW_DRIFT")
    if declared_receipts != set(resolved_receipts):
        errors.append("HISTORICAL_RECEIPT_REVIEW_DRIFT")
    collisions = {schema: files for schema, files in schema_locations.items() if len(files) > 1}
    reviewed_collisions = {}
    for item in exceptions.get("identicalLegacyTemplates") or []:
        if not isinstance(item, dict):
            errors.append("INVALID_LEGACY_DUPLICATE_ENTRY")
            continue
        a, b, schema = item.get("left"), item.get("right"), item.get("schemaId")
        pa, pb = safe_file(root, a), safe_file(root, b)
        if not pa or not pb or not isinstance(schema, str):
            errors.append("MISSING_LEGACY_DUPLICATE_FILE")
            continue
        expected = sorted([Path(a).name, Path(b).name])
        if (schema not in collisions or sorted(collisions[schema]) != expected
                or pa.read_bytes() != pb.read_bytes()):
            errors.append("LEGACY_DUPLICATE_BYTES_OR_SCHEMA_DRIFT:" + schema)
            continue
        current_manifest = load_json(root / "doctrine/aiManifestFormatV1.json")
        if schema in current_manifest.get("currentSchemas", []):
            errors.append("CURRENT_SCHEMA_MUST_NOT_BE_CLASSIFIED_LEGACY:" + schema)
            continue
        reviewed_collisions[schema] = collisions[schema]
    unknown_collisions = {s: v for s, v in collisions.items() if s not in reviewed_collisions}
    if bad_json:
        warnings.append(f"DOCTRINE_JSON_PARSE_REVIEW:{len(bad_json)}")
    if missing_schema:
        warnings.append(f"DOCTRINE_SCHEMA_ABSENT_REVIEW:{len(missing_schema)}")
    if unknown_collisions:
        warnings.append(f"NON_UNIQUE_DECLARED_SCHEMA_IDS_REVIEW:{len(unknown_collisions)}")

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
        "reviewedJsonSchemaDefinitions": sorted(resolved_defs),
        "reviewedDatedHistoricalReceipts": sorted(resolved_receipts),
        "reviewedIdenticalLegacyTemplateSchemas": reviewed_collisions,
        "duplicateDeclaredSchemaIds": dict(list(sorted(unknown_collisions.items()))[:15]),
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
