#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

def run(cmd):
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return proc.stdout

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def probe(path):
    raw = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ])
    return json.loads(raw)

def cmd_probe(args):
    p = Path(args.input).resolve()
    result = {"source": str(p), "sha256": sha256(p), "probe": probe(p)}
    print(json.dumps(result, indent=2))

def cmd_demux(args):
    src = Path(args.input).resolve()
    out = Path(args.output).resolve()
    frames = out / "frames"
    audio = out / "audio"
    receipts = out / "receipts"
    frames.mkdir(parents=True, exist_ok=True)
    audio.mkdir(parents=True, exist_ok=True)
    receipts.mkdir(parents=True, exist_ok=True)

    source_hash = sha256(src)
    metadata = probe(src)
    (receipts / "source-probe.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (receipts / "source.sha256").write_text(source_hash + "  " + src.name + "\n", encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-hide_banner", "-y", "-i", str(src),
        "-map", "0:v:0", "-vsync", "0", str(frames / "shot%08d.png")
    ], check=True)

    has_audio = any(s.get("codec_type") == "audio" for s in metadata.get("streams", []))
    if has_audio:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-y", "-i", str(src),
            "-map", "0:a:0", "-vn", "-c:a", "pcm_s24le", str(audio / "source.wav")
        ], check=True)

    print(f"DEMUX=PASS\nSOURCE_SHA256={source_hash}\nWORKSPACE={out}")

def cmd_contact(args):
    src = Path(args.input).resolve()
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-y", "-i", str(src),
        "-vf", f"fps={args.sample_fps},scale=240:-1,tile={args.cols}x{args.rows}",
        "-frames:v", "1", str(out)
    ], check=True)
    print(f"CONTACT_SHEET=PASS\nOUTPUT={out}")

def cmd_remux(args):
    frames = Path(args.frames).resolve()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    pattern = str(frames / "shot%08d.png")
    audio_map = []
    metadata = probe(source)
    if any(s.get("codec_type") == "audio" for s in metadata.get("streams", [])):
        audio_map = ["-map", "0:v:0", "-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k"]

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-framerate", str(args.fps), "-i", pattern,
        "-i", str(source),
        *audio_map,
        "-c:v", "libx264", "-preset", "slow", "-crf", "15",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-shortest", str(output)
    ]
    subprocess.run(cmd, check=True)
    print(f"REMUX=PASS\nOUTPUT_SHA256={sha256(output)}\nOUTPUT={output}")

def cmd_hash(args):
    p = Path(args.input).resolve()
    print(f"{sha256(p)}  {p.name}")

def main():
    parser = argparse.ArgumentParser(description="Professor Garage FFmpeg AI repair bay")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe")
    p.add_argument("input")
    p.set_defaults(func=cmd_probe)

    p = sub.add_parser("hash")
    p.add_argument("input")
    p.set_defaults(func=cmd_hash)

    p = sub.add_parser("demux")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=cmd_demux)

    p = sub.add_parser("contact-sheet")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--sample-fps", type=float, default=1.0)
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--rows", type=int, default=2)
    p.set_defaults(func=cmd_contact)

    p = sub.add_parser("remux")
    p.add_argument("--frames", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--fps", type=float, required=True)
    p.set_defaults(func=cmd_remux)

    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    args.func(args)

if __name__ == "__main__":
    main()
