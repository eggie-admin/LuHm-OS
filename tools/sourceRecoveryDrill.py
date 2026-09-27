#!/usr/bin/env python3
"""Deterministic LuHm OS tracked-source backup/restore drill.

This proves Git-tracked source recovery only. It never claims to restore private
Drive assets, signing keys, host credentials, device data, or Nexus sidecars.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine/sourceRecovery-20260927.json"


def fail(msg: str) -> None:
    raise SystemExit("RED_SOURCE_RECOVERY:" + msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked_paths() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    items = [Path(x.decode("utf-8")) for x in raw.split(b"\0") if x]
    return sorted(items, key=lambda p: p.as_posix())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    doctrine = load(DOCTRINE)
    if doctrine.get("product") != "LuHm OS" or doctrine.get("scope") != "FULL_GAME":
        fail("doctrine_scope")
    if doctrine.get("recovery_scope") != "GIT_TRACKED_FULL_GAME_SOURCE":
        fail("doctrine_recovery_scope")
    if doctrine.get("method", {}).get("network_required") is not False:
        fail("network_boundary")

    head = git("rev-parse", "HEAD")
    if head != args.source_sha:
        fail(f"source_head_mismatch:{head}")

    paths = tracked_paths()
    if not paths:
        fail("empty_tracked_set")

    entries: list[dict] = []
    regular_paths: list[Path] = []
    total_bytes = 0
    for rel in paths:
        src = ROOT / rel
        if src.is_symlink():
            entries.append({"path": rel.as_posix(), "type": "symlink", "target": str(src.readlink())})
            continue
        if not src.is_file():
            continue
        data = src.read_bytes()
        mode = src.stat().st_mode
        entries.append({
            "path": rel.as_posix(),
            "type": "file",
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "executable": bool(mode & stat.S_IXUSR),
        })
        regular_paths.append(rel)
        total_bytes += len(data)

    critical = [Path(x) for x in doctrine.get("critical_paths", [])]
    tracked_set = {p.as_posix() for p in regular_paths}
    missing_critical = [p.as_posix() for p in critical if p.as_posix() not in tracked_set]
    if missing_critical:
        fail("critical_not_tracked:" + ",".join(missing_critical))

    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.archive, mode="w") as tf:
        for entry in entries:
            rel = Path(entry["path"])
            src = ROOT / rel
            ti = tarfile.TarInfo(name=rel.as_posix())
            ti.mtime = 0
            ti.uid = 0
            ti.gid = 0
            ti.uname = ""
            ti.gname = ""
            if entry["type"] == "symlink":
                ti.type = tarfile.SYMTYPE
                ti.linkname = entry["target"]
                ti.mode = 0o777
                ti.size = 0
                tf.addfile(ti)
            else:
                data = src.read_bytes()
                ti.type = tarfile.REGTYPE
                ti.mode = 0o755 if entry["executable"] else 0o644
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))

    manifest_bytes = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest_sha = sha256_bytes(manifest_bytes)
    archive_sha = sha256_file(args.archive)

    with tempfile.TemporaryDirectory(prefix="luhm-source-restore-") as td:
        restore = Path(td)
        with tarfile.open(args.archive, mode="r") as tf:
            try:
                tf.extractall(restore, filter="data")
            except TypeError:
                tf.extractall(restore)
        restored = 0
        for entry in entries:
            rel = Path(entry["path"])
            dst = restore / rel
            if entry["type"] == "symlink":
                if not dst.is_symlink() or str(dst.readlink()) != entry["target"]:
                    fail("symlink_restore_mismatch:" + rel.as_posix())
                continue
            if not dst.is_file():
                fail("restore_missing:" + rel.as_posix())
            if dst.stat().st_size != entry["bytes"]:
                fail("restore_size_mismatch:" + rel.as_posix())
            if sha256_file(dst) != entry["sha256"]:
                fail("restore_hash_mismatch:" + rel.as_posix())
            restored += 1
        for rel in critical:
            if not (restore / rel).is_file():
                fail("restored_critical_missing:" + rel.as_posix())

    receipt = {
        "schema": "luhm-os.source-recovery-receipt.v1",
        "status": "LUHM_GIT_TRACKED_SOURCE_RECOVERY_GREEN",
        "product": "LuHm OS",
        "scope": "FULL_GAME",
        "source_sha": args.source_sha,
        "archive_file": args.archive.name,
        "archive_sha256": archive_sha,
        "manifest_sha256": manifest_sha,
        "tracked_entry_count": len(entries),
        "tracked_regular_file_count": len(regular_paths),
        "restored_regular_file_count": restored,
        "tracked_source_bytes": total_bytes,
        "critical_path_count": len(critical),
        "critical_paths_green": True,
        "network_required": False,
        "private_drive_asset_vault_restored": False,
        "persistent_signing_key_restored": False,
        "openai_host_credential_restored": False,
        "physical_samsung_data_restored": False,
        "private_nexus_sidecar_restored": False,
        "canonical_main_promoted": False,
        "kai9000_widget_authority": False,
        "unknown_is_not_green": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SOURCE_RECOVERY_DRILL=PASS files={restored} bytes={total_bytes} archive_sha256={archive_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
