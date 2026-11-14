#!/usr/bin/env python3
"""Private SHA-256 inventory for the LuHm Canon transfer lane.

Never commit a generated inventory from personal storage into a public repo.
"""
import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKIP = {".git", ".cache", "__pycache__", "node_modules"}
EXCLUDE_SUFFIXES = (".part", ".partial", ".tmp", ".crdownload")

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def inventory(root: Path, source_ref: str) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("source must be an existing real directory")
    entries = []
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(base) / d).is_symlink())
        for name in sorted(names):
            path = Path(base) / name
            if path.is_symlink() or not path.is_file() or name.lower().endswith(EXCLUDE_SUFFIXES):
                continue
            rel = path.relative_to(root).as_posix()
            entries.append({
                "relativePath": rel,
                "sizeBytes": path.stat().st_size,
                "sha256": digest(path),
            })
    entries.sort(key=lambda x: x["relativePath"])
    by_digest = defaultdict(list)
    for item in entries:
        by_digest[(item["sizeBytes"], item["sha256"])].append(item["relativePath"])
    duplicates = [
        {"sha256": sha, "sizeBytes": size, "paths": paths}
        for (size, sha), paths in sorted(by_digest.items())
        if len(paths) > 1
    ]
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "luhmOs.castBridge.privateTransferIndex.v1",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sourceRef": source_ref,
        "sourceAuthority": "github",
        "fileServer": "googleDrive",
        "status": "LOCAL_VERIFIED_PENDING_REMOTE_CHECK",
        "promotionAuthority": False,
        "recordsSha256": hashlib.sha256(canonical).hexdigest(),
        "fileCount": len(entries),
        "byteCount": sum(e["sizeBytes"] for e in entries),
        "duplicateGroupCount": len(duplicates),
        "entries": entries,
        "duplicateGroups": duplicates,
    }

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-ref", required=True)
    args = ap.parse_args()
    if args.out.resolve() == args.source.resolve() or args.out.resolve().is_relative_to(args.source.resolve()):
        ap.error("manifest output must live outside the input tree")
    data = inventory(args.source, args.source_ref)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.chmod(args.out, 0o600)
    print("CANON_INDEX_OK files=%s bytes=%s duplicateGroups=%s" %
          (data["fileCount"], data["byteCount"], data["duplicateGroupCount"]))

if __name__ == "__main__":
    main()
