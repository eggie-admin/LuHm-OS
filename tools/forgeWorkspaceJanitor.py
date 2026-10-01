#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "doctrine" / "FORGE_TTL_POLICY_V1.json").read_text(encoding="utf-8"))
SENTINEL = POLICY["sentinelName"]
ITEM_META = ".forge-item.json"
HOLD = ".forge-hold"


def utc_now():
    return datetime.now(timezone.utc)


def parse_time(value: str):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def expand_allowed_roots():
    roots = []
    for raw in POLICY["allowedRootPatterns"]:
        expanded = os.path.expandvars(os.path.expanduser(raw))
        if "$" in expanded:
            continue
        roots.append(Path(expanded).resolve())
    return roots


def refuse(message):
    print(f"FORGE_JANITOR=REFUSED\nreason={message}")
    raise SystemExit(2)


def validate_root(root: Path):
    if root.is_symlink():
        refuse("Forge root may not be a symlink")
    root = root.resolve()
    home = Path.home().resolve()
    repo = ROOT.resolve()
    forbidden = {Path("/").resolve(), home, repo}
    if root in forbidden:
        refuse("filesystem/home/repository root is forbidden")
    if not any(root == allowed for allowed in expand_allowed_roots()):
        refuse(f"root {root} is not an approved Forge temporary root")
    sentinel = root / SENTINEL
    if not sentinel.is_file() or sentinel.is_symlink():
        refuse("Forge root sentinel missing or unsafe")
    try:
        payload = json.loads(sentinel.read_text(encoding="utf-8"))
    except Exception as exc:
        refuse(f"invalid Forge root sentinel: {exc}")
    if payload.get("schema") != "luhm.forge.root.v1" or payload.get("authority") != "TEMPORARY_ONLY":
        refuse("Forge root sentinel identity mismatch")
    return root


def bytes_under(path: Path):
    total = 0
    for p in path.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
        except FileNotFoundError:
            pass
    return total


def sweep(root: Path, apply: bool):
    root = validate_root(root)
    ttl = POLICY["ttlHours"]
    now = utc_now()
    receipts = []

    for item in sorted(root.iterdir()):
        if item.name == SENTINEL:
            continue
        if item.is_symlink():
            receipts.append({"targetRealpath": str(item), "result": "REFUSED_SYMLINK"})
            continue
        if not item.is_dir():
            continue
        meta_path = item / ITEM_META
        if not meta_path.is_file() or meta_path.is_symlink():
            receipts.append({"targetRealpath": str(item.resolve()), "result": "REFUSED_MISSING_METADATA"})
            continue
        if (item / HOLD).exists():
            receipts.append({"targetRealpath": str(item.resolve()), "result": "HELD"})
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            ttl_class = meta["ttlClass"]
            created = parse_time(meta["createdAt"])
        except Exception:
            receipts.append({"targetRealpath": str(item.resolve()), "result": "REFUSED_INVALID_METADATA"})
            continue
        if ttl_class not in ttl:
            receipts.append({"targetRealpath": str(item.resolve()), "result": "REFUSED_UNKNOWN_TTL_CLASS"})
            continue
        real = item.resolve()
        try:
            real.relative_to(root)
        except ValueError:
            receipts.append({"targetRealpath": str(real), "result": "REFUSED_PATH_ESCAPE"})
            continue
        age_hours = (now - created).total_seconds() / 3600.0
        threshold = float(ttl[ttl_class])
        if age_hours < threshold:
            continue
        size = bytes_under(item)
        result = "WOULD_DELETE"
        if apply:
            shutil.rmtree(item)
            result = "DELETED"
        receipts.append({
            "targetRealpath": str(real),
            "ttlClass": ttl_class,
            "ageHours": round(age_hours, 3),
            "reason": f"age >= {threshold}h",
            "bytesBefore": size,
            "deletedAt": now.isoformat() if apply else None,
            "result": result,
        })

    print(json.dumps({"schema": "luhm.forge.janitor-receipt.v1", "root": str(root), "apply": apply, "items": receipts}, indent=2))
    return 0


def init_root(root: Path):
    root = root.expanduser().resolve()
    allowed = expand_allowed_roots()
    if root not in allowed:
        refuse(f"root {root} is not an approved Forge temporary root")
    if root in {Path("/").resolve(), Path.home().resolve(), ROOT.resolve()}:
        refuse("unsafe Forge root")
    root.mkdir(parents=True, exist_ok=True)
    sentinel = root / SENTINEL
    sentinel.write_text(json.dumps({"schema": "luhm.forge.root.v1", "authority": "TEMPORARY_ONLY"}, indent=2) + "\n", encoding="utf-8")
    print(f"FORGE_JANITOR_ROOT=INITIALIZED\nroot={root}")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--init-root", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    root = Path(args.root)
    if args.init_root:
        return init_root(root)
    return sweep(root, args.apply)


if __name__ == "__main__":
    sys.exit(main())
