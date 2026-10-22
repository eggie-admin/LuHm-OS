#!/usr/bin/env python3
"""Offline archive intake for LuHm OS. Never writes to GitHub, Drive, or release services."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import pathlib
import re
import stat
import tarfile
import zipfile

TYPE_EXTENSIONS = {
    "androidApk": {".apk"},
    "artRaster": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".exr"},
    "artVector": {".svg"},
    "binaryWebAssembly": {".wasm"},
    "codePython": {".py"},
    "codeSql": {".sql"},
    "codeWeb": {".js", ".jsx", ".ts", ".tsx", ".html", ".htm", ".css"},
    "configYaml": {".yaml", ".yml"},
    "dataChecksums": {".sha256", ".md5"},
    "dataJson": {".json"},
    "dataTables": {".csv", ".tsv", ".sqlite", ".sqlite3", ".db"},
    "docsMarkdown": {".md"},
    "docsText": {".txt", ".rst", ".log"},
    "gameGodot": {".tscn", ".tres", ".gd", ".godot", ".pck"},
    "gameUnrealPackages": {".uasset", ".umap"},
    "models3d": {".blend", ".fbx", ".glb", ".gltf", ".obj", ".mtl", ".stl", ".dae"},
    "video": {".mp4", ".mkv", ".mov", ".webm", ".avi"},
    "videoSubtitles": {".srt", ".vtt", ".ass"},
    "audio": {".wav", ".flac", ".mp3", ".ogg", ".opus", ".mid", ".midi"}
}
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_TOTAL = 2 * 1024 * 1024 * 1024
MAX_ENTRIES = 10000
VALID = re.compile(r"^[A-Za-z0-9_. -]+$")

class IntakeError(ValueError):
    pass

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def category(name: str) -> str:
    suffix = pathlib.PurePosixPath(name).suffix.lower()
    for group, extensions in TYPE_EXTENSIONS.items():
        if suffix in extensions:
            return group
    return "reviewUnclassified"

def clean_name(name: str) -> str:
    path = pathlib.PurePosixPath(name.replace("\\", "/"))
    if (not name or name.startswith(("/", "\\")) or len(path.parts) > 32
            or any(part in (".", "..", "") for part in path.parts)
            or any(":" in part or "\x00" in part for part in path.parts)):
        raise IntakeError("unsafe member path")
    return "/".join(path.parts)

def zip_members(path: pathlib.Path):
    with zipfile.ZipFile(path) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        if len(infos) > MAX_ENTRIES:
            raise IntakeError("too many archive entries")
        seen, size = set(), 0
        for info in infos:
            name = clean_name(info.filename)
            if name in seen:
                raise IntakeError("duplicate member name")
            seen.add(name)
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) in (stat.S_IFLNK, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFIFO):
                raise IntakeError("non-regular zip member")
            if info.flag_bits & 1:
                raise IntakeError("encrypted zip requires separate review")
            if info.file_size > MAX_FILE_BYTES:
                raise IntakeError("oversized member")
            size += info.file_size
            if size > MAX_ARCHIVE_TOTAL:
                raise IntakeError("oversized archive")
        for info in infos:
            with z.open(info, "r") as fp:
                data = fp.read(MAX_FILE_BYTES + 1)
            if len(data) != info.file_size:
                raise IntakeError("size mismatch")
            yield clean_name(info.filename), data

def tar_members(path: pathlib.Path):
    with tarfile.open(path, "r:*") as archive:
        infos = archive.getmembers()
        if len(infos) > MAX_ENTRIES:
            raise IntakeError("too many archive entries")
        files, seen, total = [], set(), 0
        for info in infos:
            if info.isdir():
                continue
            if not info.isfile():
                raise IntakeError("links/devices are not supported")
            name = clean_name(info.name)
            if name in seen:
                raise IntakeError("duplicate member name")
            seen.add(name)
            total += info.size
            if info.size > MAX_FILE_BYTES or total > MAX_ARCHIVE_TOTAL:
                raise IntakeError("archive size limit")
            files.append(info)
        for info in files:
            fp = archive.extractfile(info)
            if fp is None:
                raise IntakeError("unreadable member")
            with fp:
                data = fp.read(MAX_FILE_BYTES + 1)
            if len(data) != info.size:
                raise IntakeError("size mismatch")
            yield clean_name(info.name), data

def rar_members(path: pathlib.Path):
    try:
        import rarfile
    except ImportError as exc:
        raise IntakeError("RAR requires optional rarfile + approved extractor; no implicit install") from exc
    with rarfile.RarFile(path) as archive:
        infos = [x for x in archive.infolist() if not x.isdir()]
        if len(infos) > MAX_ENTRIES:
            raise IntakeError("too many archive entries")
        seen, total = set(), 0
        for info in infos:
            name = clean_name(info.filename)
            if name in seen:
                raise IntakeError("duplicate member")
            seen.add(name)
            if info.is_symlink():
                raise IntakeError("rar symlink")
            total += info.file_size
            if info.file_size > MAX_FILE_BYTES or total > MAX_ARCHIVE_TOTAL:
                raise IntakeError("rar limits exceeded")
        for info in infos:
            with archive.open(info) as fp:
                data = fp.read(MAX_FILE_BYTES + 1)
            if len(data) != info.file_size:
                raise IntakeError("RAR mismatch")
            yield clean_name(info.filename), data

def is_archive(path: pathlib.Path) -> bool:
    name = path.name.lower()
    return name.endswith((".zip", ".tar", ".tgz", ".tar.gz", ".rar"))

def open_members(path: pathlib.Path):
    n = path.name.lower()
    if n.endswith(".zip"):
        return zip_members(path)
    if n.endswith((".tar", ".tgz", ".tar.gz")):
        return tar_members(path)
    if n.endswith(".rar"):
        return rar_members(path)
    raise IntakeError("unsupported archive")

def stage(input_root: pathlib.Path, output_root: pathlib.Path):
    input_root = input_root.resolve(strict=True)
    output_root = output_root.resolve()
    if not input_root.is_dir() or input_root == output_root or input_root in output_root.parents or output_root in input_root.parents:
        raise IntakeError("source and destination must be independent directories")
    archives = sorted(p for p in input_root.rglob("*") if p.is_file() and is_archive(p))
    reports, total = [], 0
    for arc in archives:
        receipt = {"archiveName":arc.name,"archiveSha256":sha256(arc.read_bytes()),"status":"STAGING_CANDIDATE","files":[]}
        planned = []
        try:
            for name, data in open_members(arc):
                group, digest = category(name), sha256(data)
                stem = pathlib.PurePosixPath(name).stem
                ext = pathlib.PurePosixPath(name).suffix.lower()
                base = re.sub(r"[^A-Za-z0-9.-]+", "-", arc.stem)[:56]
                safe = re.sub(r"[^A-Za-z0-9.-]+", "-", stem)[:70]
                target = output_root / "byType" / group / (base+"__"+safe+"__"+digest[:12]+ext)
                planned.append((name, data, target, group, digest))
            for name, data, target, group, digest in planned:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    if sha256(target.read_bytes()) != digest:
                        raise IntakeError("existing target collision")
                else:
                    with target.open("xb") as out:
                        out.write(data)
                receipt["files"].append({"originalMember":name,"typeFolder":group,"stagedName":target.name,"sha256":digest,"sizeBytes":len(data),"rights":"UNREVIEWED"})
            receipt["status"] = "STAGED_NO_PROMOTION"
            total += len(planned)
        except (OSError, ValueError, zipfile.BadZipFile, tarfile.TarError) as exc:
            receipt["status"] = "BLOCKED"
            receipt["errorType"] = type(exc).__name__
        reports.append(receipt)
    report = {"schema":"luhmOs.archiveIntakeReceipt.v1","status":"PRIVATE_STAGE_ONLY",
              "fileCount":total,"archiveCount":len(archives),"archives":reports,
              "githubAuthority":False,"driveWrite":False,"promotion":False,"crown":"STOP"}
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root/"intakeReceipt.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True, type=pathlib.Path)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    args = parser.parse_args()
    try:
        print(json.dumps(stage(args.input_root, args.output_root), indent=2))
        return 0
    except (OSError, IntakeError) as exc:
        print(json.dumps({"status":"RED_FAIL_CLOSED","error":str(exc)}))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
