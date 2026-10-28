#!/usr/bin/env python3
"""Local FFmpeg output inspection and optional user-armed desktop VLC invocation.
No HTTP listener, no arbitrary URL, no root, no media transcoding or publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ALLOWED = {".mp4", ".webm", ".mp3", ".wav", ".ogg", ".m4a"}
MAX_BYTES = 2_000_000_000

def safeMediaPath(root: Path, path: str) -> Path:
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("RED_LOCAL_MEDIA_PATH")
    rel = Path(path)
    if rel.is_absolute() or any(s in ("..", ".") for s in rel.parts):
        raise ValueError("RED_LOCAL_MEDIA_PATH")
    root = root.expanduser().resolve(strict=True)
    file = (root / rel).resolve(strict=True)
    if not file.is_relative_to(root) or file.is_symlink() or file.suffix.lower() not in ALLOWED or not file.is_file():
        raise ValueError("RED_MEDIA_SCOPE")
    if file.stat().st_size <= 0 or file.stat().st_size > MAX_BYTES:
        raise ValueError("RED_MEDIA_SIZE")
    return file

def sha256(file:Path) -> str:
    digest=hashlib.sha256()
    with file.open("rb") as source:
        for chunk in iter(lambda:source.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def inspectMedia(file: Path, *, probeExe: str | None = None) -> dict:
    exe = probeExe or shutil.which("ffprobe")
    if not exe: raise RuntimeError("HOLD_FFPROBE_NOT_INSTALLED")
    try:
        result = subprocess.run([exe,"-v","error","-show_entries",
          "format=duration:stream=codec_type,codec_name","-of","json",str(file)],
          check=True,capture_output=True,text=True,timeout=12)
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError):
        raise RuntimeError("RED_FFPROBE_FAILED") from None
    try: detail=json.loads(result.stdout)
    except (ValueError,TypeError): raise RuntimeError("RED_FFPROBE_JSON") from None
    streams=[{"kind":stream.get("codec_type"),"codec":stream.get("codec_name")}
             for stream in detail.get("streams",[]) if stream.get("codec_type") in ("audio","video")]
    return {"schema":"luhmOs.mediaPreviewReceipt.v1","product":"LuHm-OS",
      "sha256":sha256(file),"sizeBytes":file.stat().st_size,
      "formatExtension":file.suffix.lower(),"streams":streams,
      "durationSeconds":detail.get("format",{}).get("duration"),
      "backend":"local-ffprobe","playbackVerified":False,"originalPreserved":True,
      "publication":False,"crownStatus":"STOP"}

def playVlc(file: Path, *, armed: bool=False, vlcExe: str | None=None) -> int:
    if not armed: raise ValueError("HOLD_USER_APPROVAL_REQUIRED")
    exe=vlcExe or shutil.which("vlc")
    if not exe: raise RuntimeError("HOLD_VLC_NOT_INSTALLED")
    # Intentionally no --extraintf http, HTTP credentials, or network input.
    process=subprocess.Popen([exe,"--no-video-title-show",str(file)],
      stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
      close_fds=True)
    return process.pid

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--file",required=True,help="Relative approved local file; never an URL")
    parser.add_argument("--play-vlc",action="store_true",help="Optional external local VLC player")
    parser.add_argument("--approved",action="store_true",help="Explicit human playback approval")
    args=parser.parse_args()
    try:
        file=safeMediaPath(args.root,args.file)
        receipt=inspectMedia(file)
        if args.play_vlc:
            playVlc(file,armed=args.approved)
            receipt["vlcLaunchRequested"]=True
            receipt["playbackVerified"]=False
        print(json.dumps(receipt,indent=2))
        return 0
    except (ValueError,RuntimeError,OSError) as error:
        print(str(error),file=sys.stderr)
        return 2

if __name__=="__main__":raise SystemExit(main())
