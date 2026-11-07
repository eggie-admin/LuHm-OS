#!/usr/bin/env python3
"""CAST Bridge: local, read-only SHA-256 inventory for Canon.

Usage:
    python3 scripts/libraryCanonDedupe.py /path/to/export --out inventory.json

This does not have access to the ChatGPT Library API. Never upload generated
inventories to a public repository without reviewing filenames and paths.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".cache"}
PROTECTED_WORDS = ("canon", "original", "master", "recovery", "snapshot",
                   "source-of-truth", "source_of_truth", "private", "rights",
                   "backup", "evidence", "proof", "quarantine", "secret")

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()

def walk(root):
    if root.is_file():
        if not root.is_symlink():
            yield root
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs
                         if name not in SKIP_DIRS
                         and not (Path(base) / name).is_symlink())
        for name in sorted(files):
            item = Path(base) / name
            if item.is_file() and not item.is_symlink():
                yield item

def protected(path):
    parts = [x.lower() for x in path.parts]
    return any(word in part for part in parts for word in PROTECTED_WORDS)

def scan(roots):
    records = []
    errors = []
    seen_paths = set()
    for root in roots:
        for path in walk(root):
            try:
                resolved = path.resolve(strict=True)
                if str(resolved) in seen_paths:
                    continue
                seen_paths.add(str(resolved))
                size = path.stat().st_size
                records.append({
                    "path": str(resolved),
                    "sizeBytes": size,
                    "sha256": sha256_file(path),
                    "protected": protected(resolved),
                })
            except (OSError, PermissionError) as error:
                errors.append({"path": str(path), "error": type(error).__name__})

    groups = defaultdict(list)
    for item in records:
        groups[(item["sizeBytes"], item["sha256"])].append(item)
    duplicate_groups = []
    for (size, digest), copies in sorted(groups.items()):
        if len(copies) < 2:
            continue
        copies = sorted(copies, key=lambda x: (not x["protected"], x["path"]))
        duplicate_groups.append({
            "sizeBytes": size,
            "sha256": digest,
            "copies": copies,
            "extraCopyCount": len(copies) - 1,
            "disposition": "REVIEW_ONLY",
            "note": "Identical content; different directories may be intentional backups."
        })
    return {
        "schema": "luhmOs.castBridge.libraryInventory.v1",
        "generatedUtc": datetime.now(timezone.utc).isoformat(),
        "source": "LOCAL_FILES_ONLY",
        "sourceAuthority": "GitHub Canon; file originals remain where stored",
        "status": "EVIDENCE_ONLY_NOT_CROWN",
        "canModifyChatGptLibrary": False,
        "policy": "no deletion, movement, network, publication or agent activation",
        "fileCount": len(records),
        "totalBytes": sum(x["sizeBytes"] for x in records),
        "duplicateGroups": len(duplicate_groups),
        "redundantCopies": sum(x["extraCopyCount"] for x in duplicate_groups),
        "duplicates": duplicate_groups,
        "errors": errors,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path, help="Local export directories")
    parser.add_argument("--out", type=Path, default=Path("cast-library-inventory.json"))
    args = parser.parse_args()
    for root in args.roots:
        if not root.exists():
            parser.error(f"not found: {root}")
    output = scan(args.roots)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"files={output['fileCount']} duplicates={output['duplicateGroups']} "
          f"extraCopies={output['redundantCopies']} errors={len(output['errors'])} "
          f"inventory={args.out}")
    return 0 if not output["errors"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
