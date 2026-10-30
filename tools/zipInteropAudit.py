#!/usr/bin/env python3
"""Bounded, platform-neutral ZIP inspection, no extraction or privilege escalation.

Python 3.10+ compatible: ZIP_DEFLATED is deliberately used rather than the
Python 3.14 ZIP_ZSTANDARD feature because Java/Android readers must interoperate.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path, PurePosixPath
import stat
import zipfile

MAX_ENTRY_BYTES=2_000_000
MAX_TOTAL_BYTES=6_000_000
MAX_FILES=96
MAX_ARCHIVE_BYTES=6_000_000
MAX_EXPANSION_RATIO=200
ROOT_NAME="luhmos-dev/"
HEX40=re.compile(r"^[a-f0-9]{40}$")
# Cross-platform DEV source ZIPs deliberately use portable ASCII paths.
# Windows device aliases, alternate streams, and casefold collisions are not
# safe when an archive is later handled by Java, Android, macOS or Windows.
PORTABLE=re.compile(r"^[A-Za-z0-9._/-]+$")
WINDOWS_DEVICES={*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10)),
                 "CON","PRN","AUX","NUL"}

def portable_name(name:str)->bool:
    if not isinstance(name,str) or not PORTABLE.fullmatch(name):
        return False
    for part in name.split("/"):
        if part.endswith((".", " ")) or part.split(".",1)[0].upper() in WINDOWS_DEVICES:
            return False
    return True

def safe_name(name:str)->bool:
    if not isinstance(name,str) or len(name)>240 or not name.startswith(ROOT_NAME):
        return False
    if "\\" in name or "\x00" in name or "//" in name:
        return False
    p=PurePosixPath(name)
    return (not p.is_absolute() and len(p.parts)>1 and
            all(part not in (".","..","") for part in name.split("/"))
            and not re.match(r"^[A-Za-z]:",name))

def verify_dev_archive(path:Path, expected_paths:list[str], *, source_ref:str)->dict:
    path=Path(path)
    if not HEX40.fullmatch(source_ref):
        raise ValueError("EXACT_SHA_REQUIRED")
    if not path.is_file() or path.is_symlink():
        raise ValueError("ZIP_MISSING_OR_SYMLINK")
    if not 0<path.stat().st_size<=MAX_ARCHIVE_BYTES:
        raise ValueError("ZIP_ARCHIVE_SIZE_LIMIT")
    wanted={ROOT_NAME+rel for rel in expected_paths}
    if len(wanted)!=len(expected_paths):
        raise ValueError("ZIP_SOURCE_ALLOWLIST_DUPLICATE")
    entries=[]
    with zipfile.ZipFile(path,"r") as z:
        infos=z.infolist()
        if not 0<len(infos)<=MAX_FILES or len(infos)!=len(wanted):
            raise ValueError("ZIP_FILE_COUNT")
        if len({i.filename for i in infos})!=len(infos):
            raise ValueError("ZIP_DUPLICATE_MEMBER")
        if len({i.filename.casefold() for i in infos})!=len(infos):
            raise ValueError("ZIP_PORTABLE_CASE_COLLISION")
        total=0
        for info in infos:
            if not safe_name(info.filename) or not portable_name(info.filename) or info.filename not in wanted:
                raise ValueError("ZIP_UNSAFE_OR_UNLISTED_ENTRY")
            if info.is_dir():
                raise ValueError("ZIP_DIRECTORY_DISALLOWED")
            typ=stat.S_IFMT((info.external_attr>>16)&0xffff)
            if typ not in (0,stat.S_IFREG):
                raise ValueError("ZIP_NON_REGULAR_ENTRY")
            if info.compress_type!=zipfile.ZIP_DEFLATED or info.flag_bits&1:
                raise ValueError("ZIP_COMPRESSION_OR_ENCRYPTION")
            if info.file_size<0 or info.file_size>MAX_ENTRY_BYTES:
                raise ValueError("ZIP_ENTRY_TOO_LARGE")
            if info.compress_size<1 and info.file_size>0:
                raise ValueError("ZIP_INVALID_COMPRESSED_SIZE")
            if info.file_size>MAX_EXPANSION_RATIO*max(1,info.compress_size):
                raise ValueError("ZIP_EXPANSION_RATIO")
            if info.date_time != (1980,1,1,0,0,0):
                raise ValueError("ZIP_TIMESTAMP_NONDETERMINISTIC")
            total+=info.file_size
            if total>MAX_TOTAL_BYTES:
                raise ValueError("ZIP_TOTAL_TOO_LARGE")
            h=hashlib.sha256()
            got=0
            with z.open(info,"r") as f:
                for chunk in iter(lambda:f.read(64*1024),b""):
                    got+=len(chunk)
                    if got>MAX_ENTRY_BYTES:raise ValueError("ZIP_STREAM_ENTRY_LIMIT")
                    h.update(chunk)
            if got!=info.file_size:
                raise ValueError("ZIP_ENTRY_SIZE_DRIFT")
            entries.append({"path":info.filename,"sha256":h.hexdigest(),"bytes":got})
    if {e["path"] for e in entries}!=wanted:
        raise ValueError("ZIP_ENTRIES_MISMATCH")
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(64*1024),b""):
            h.update(chunk)
    return {"schema":"luhmOs.devZipReceipt.v1","lane":"dev","sourceRef":source_ref,
      "filename":path.name,"sha256":h.hexdigest(),"bytes":path.stat().st_size,
      "fileCount":len(entries),"uncompressedBytes":total,
      "entries":sorted(entries,key=lambda x:x["path"]),
      "compression":"ZIP_DEFLATED","java17CompatibleFormat":True,
      "authority":"SOURCE_CANDIDATE_ONLY","releaseAllowed":False,
      "crownStatus":"STOP"}
