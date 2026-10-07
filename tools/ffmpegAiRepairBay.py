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

def image_size(path):
    raw = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", str(path)
    ])
    data = json.loads(raw)
    streams = data.get("streams", [])
    if not streams:
        raise RuntimeError(f"no image stream: {path}")
    return int(streams[0]["width"]), int(streams[0]["height"])

def frame_path(root, frame):
    return root / f"shot{frame:08d}.png"

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

def cmd_rebuild_window(args):
    source_frames = Path(args.source_frames).resolve()
    repair_frames = Path(args.repair_frames).resolve()
    output_frames = Path(args.output_frames).resolve()

    if args.end_frame < args.start_frame:
        raise SystemExit("end-frame must be >= start-frame")
    if output_frames.exists():
        raise SystemExit(f"output frames directory already exists: {output_frames}")

    source_files = sorted(source_frames.glob("shot*.png"))
    if not source_files:
        raise SystemExit("no source frames found")

    shutil.copytree(source_frames, output_frames)

    replacement_hashes = []
    for frame in range(args.start_frame, args.end_frame + 1):
        src = frame_path(source_frames, frame)
        rep = frame_path(repair_frames, frame)
        dst = frame_path(output_frames, frame)
        if not src.exists():
            raise SystemExit(f"source frame missing: {src.name}")
        if not rep.exists():
            raise SystemExit(f"repair frame missing: {rep.name}")
        if image_size(src) != image_size(rep):
            raise SystemExit(f"repair dimensions mismatch at frame {frame}")
        replacement_hashes.append({
            "frame": frame,
            "sourceSha256": sha256(src),
            "repairSha256": sha256(rep)
        })
        shutil.copy2(rep, dst)

    receipt = {
        "schema": "luhmOs.ffmpegAiRepairWindowReceipt.v1",
        "sourceFrames": str(source_frames),
        "repairFrames": str(repair_frames),
        "outputFrames": str(output_frames),
        "startFrame": args.start_frame,
        "endFrame": args.end_frame,
        "replacementCount": len(replacement_hashes),
        "replacementHashes": replacement_hashes,
        "untouchedFramesCopiedForward": True,
        "professorApproval": False,
        "crownAuthority": False
    }
    receipt_path = output_frames.parent / "repair-window-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"REBUILD_WINDOW=PASS\nREPLACEMENTS={len(replacement_hashes)}\nRECEIPT={receipt_path}")

def cmd_remux(args):
    frames = Path(args.frames).resolve()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    pattern = str(frames / "shot%08d.png")
    metadata = probe(source)
    has_audio = any(s.get("codec_type") == "audio" for s in metadata.get("streams", []))

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-framerate", str(args.fps), "-i", pattern,
        "-i", str(source),
        "-map", "0:v:0"
    ]
    if has_audio:
        cmd += ["-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k"]
    cmd += [
        "-c:v", "libx264", "-preset", "slow", "-crf", "15",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart"
    ]
    if has_audio:
        cmd += ["-shortest"]
    cmd += [str(output)]

    subprocess.run(cmd, check=True)
    print(f"REMUX=PASS\nOUTPUT_SHA256={sha256(output)}\nOUTPUT={output}")

def cmd_compare(args):
    before = Path(args.before).resolve()
    after = Path(args.after).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run([
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(before), "-i", str(after),
        "-filter_complex", "[0:v][1:v]hstack=inputs=2[v]",
        "-map", "[v]", "-map", "1:a:0?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", str(output)
    ], check=True)
    print(f"COMPARE=PASS\nOUTPUT_SHA256={sha256(output)}\nOUTPUT={output}")

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

    p = sub.add_parser("rebuild-window")
    p.add_argument("--source-frames", required=True)
    p.add_argument("--repair-frames", required=True)
    p.add_argument("--output-frames", required=True)
    p.add_argument("--start-frame", type=int, required=True)
    p.add_argument("--end-frame", type=int, required=True)
    p.set_defaults(func=cmd_rebuild_window)

    p = sub.add_parser("remux")
    p.add_argument("--frames", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--fps", type=float, required=True)
    p.set_defaults(func=cmd_remux)

    p = sub.add_parser("compare")
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    args.func(args)

if __name__ == "__main__":
    main()
