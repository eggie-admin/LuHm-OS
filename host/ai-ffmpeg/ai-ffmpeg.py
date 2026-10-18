#!/usr/bin/env python3
"""LuHm local-only, review-gated FFmpeg candidate renderer. No LLM text is a shell command."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

schema = "luhm.aiFfmpegJob.v1"
sections = {"100", "200", "300", "400", "500"}
shotIds = ("100", "200", "300", "401", "402", "403", "500")
allowedExtensions = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mkv"}
imageExtensions = {".png", ".jpg", ".jpeg", ".webp"}
audioExtensions = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
capabilityFlags = ("-encoders", "-decoders", "-filters", "-formats", "-protocols", "-hwaccels", "-codecs", "-pix_fmts", "-sample_fmts", "-layouts", "-devices", "-bsfs", "-muxers", "-demuxers")
jobLock = threading.Lock()


def tool(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError("RED_MISSING_" + name.upper())
    return path


def execute(arguments, timeout=120):
    try:
        return subprocess.run(arguments, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, check=True)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("RED_RENDER_TIMEOUT") from exc
    except subprocess.CalledProcessError as exc:
        # Do not leak local file paths or metadata from FFmpeg's stderr to an HTTP caller.
        raise ValueError("RED_MEDIA_PROCESS_FAILED") from exc


def capabilities(full=False):
    exe = tool("ffmpeg")
    tool("ffprobe")
    version = execute([exe, "-version"], 10).stdout.decode("utf-8", "replace").splitlines()[0]
    result = {"schema": "luhm.aiFfmpegCapabilities.v1", "ffmpegVersion": version,
              "runtime": "THIS_HOST_ONLY", "encoderPreset": "libx264",
              "hardwareAcceleration": "DISCOVER_ONLY_NOT_PROVEN", "capabilities": {}}
    for flag in capabilityFlags:
        # FFmpeg's feature enumerations normally exit successfully; discovery never runs jobs.
        output = execute([exe, "-hide_banner", flag], 10).stdout.decode("utf-8", "replace")
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        result["capabilities"][flag[1:]] = lines if full else {"lines": len(lines)}
    if full:
        return result
    result["readyForCpuReview"] = "libx264" in execute([exe, "-hide_banner", "-encoders"], 10).stdout.decode("utf-8", "replace")
    result["renderPermission"] = False
    return result


def childPath(root, relative, mustExist):
    if not isinstance(relative, str) or not relative or "\x00" in relative or Path(relative).is_absolute():
        raise ValueError("RED_PATH_NOT_RELATIVE")
    root = Path(root).expanduser().resolve()
    filePath = (root / relative).resolve()
    if not filePath.is_relative_to(root) or filePath == root:
        raise ValueError("RED_PATH_ESCAPE")
    if mustExist and not filePath.is_file():
        raise ValueError("RED_INPUT_MISSING")
    return filePath


def validate(manifest, inputRoot, outputRoot):
    if not isinstance(manifest, dict) or manifest.get("schema") != schema:
        raise ValueError("RED_SCHEMA")
    required = {"schema", "jobId", "shots", "output", "reviewApproved"}
    optional = {"audioBed", "videoFadeOutSeconds"}
    if not required.issubset(manifest) or set(manifest) - required - optional:
        raise ValueError("RED_MANIFEST_FIELDS")
    if not isinstance(manifest["jobId"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", manifest["jobId"]):
        raise ValueError("RED_JOB_ID")
    if manifest["reviewApproved"] is not True:
        raise PermissionError("CROWN_STOP_REVIEW_REQUIRED")
    shots = manifest["shots"]
    if not isinstance(shots, list) or len(shots) != len(shotIds):
        raise ValueError("RED_SHOT_COUNT")
    validated = []
    total = 0.0
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict) or set(shot) != {"id", "source", "seconds", "fit"}:
            raise ValueError("RED_SHOT_FIELDS")
        if shot["id"] != shotIds[index]:
            raise ValueError("RED_SHOT_ORDER")
        sectionId = shot["id"][:1] + "00" if shot["id"].startswith("4") else shot["id"]
        if sectionId not in sections:
            raise ValueError("RED_SECTION")
        seconds = shot["seconds"]
        if type(seconds) not in (float, int) or not 0.5 <= seconds <= 20:
            raise ValueError("RED_SHOT_DURATION")
        total += seconds
        if shot["fit"] not in ("contain", "cover"):
            raise ValueError("RED_FIT")
        filePath = childPath(inputRoot, shot["source"], True)
        if filePath.suffix.lower() not in allowedExtensions or filePath.stat().st_size > 500 * 1024 * 1024:
            raise ValueError("RED_INPUT_TYPE_OR_SIZE")
        validated.append({**shot, "inputPath": filePath})
    if total > 120:
        raise ValueError("RED_TOTAL_DURATION")
    fadeOut = manifest.get("videoFadeOutSeconds", 0)
    if type(fadeOut) not in (float, int) or not 0 <= fadeOut <= 10 or fadeOut > shots[-1]["seconds"]:
        raise ValueError("RED_VIDEO_FADE")
    audio = None
    if "audioBed" in manifest:
        audio = manifest["audioBed"]
        if not isinstance(audio, dict) or set(audio) != {"source", "startSeconds", "volume", "fadeOutSeconds"}:
            raise ValueError("RED_AUDIO_FIELDS")
        audioPath = childPath(inputRoot, audio["source"], True)
        if audioPath.suffix.lower() not in audioExtensions or audioPath.stat().st_size > 500 * 1024 * 1024:
            raise ValueError("RED_AUDIO_TYPE_OR_SIZE")
        if type(audio["startSeconds"]) not in (float, int) or not 0 <= audio["startSeconds"] <= 3600:
            raise ValueError("RED_AUDIO_START")
        if type(audio["volume"]) not in (float, int) or not 0 <= audio["volume"] <= 1:
            raise ValueError("RED_AUDIO_VOLUME")
        if type(audio["fadeOutSeconds"]) not in (float, int) or not 0 <= audio["fadeOutSeconds"] <= 10:
            raise ValueError("RED_AUDIO_FADE")
        audio = {**audio, "inputPath": audioPath}
    output = childPath(outputRoot, manifest["output"], False)
    if output.suffix.lower() != ".mp4" or output.exists():
        raise ValueError("RED_OUTPUT_EXISTS_OR_TYPE")
    return validated, output, audio, float(fadeOut)


def probe(path):
    output = execute([tool("ffprobe"), "-v", "error", "-protocol_whitelist", "file,pipe",
                      "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height",
                      "-of", "json", "-i", str(path)], 15)
    return json.loads(output.stdout)


def render(manifest, inputRoot, outputRoot):
    validated, output, audio, videoFadeOut = validate(manifest, inputRoot, outputRoot)
    # All source files must be valid before any encoding work begins.
    totalDuration = sum(float(shot["seconds"]) for shot in validated)
    for shot in validated:
        streams = probe(shot["inputPath"]).get("streams", [])
        if not any(s.get("codec_type") == "video" for s in streams):
            raise ValueError("RED_INPUT_NO_VIDEO")
    if audio:
        audioInfo = probe(audio["inputPath"])
        if not any(s.get("codec_type") == "audio" for s in audioInfo.get("streams", [])):
            raise ValueError("RED_INPUT_NO_AUDIO")
        audioDuration = float(audioInfo.get("format", {}).get("duration", 0))
        if float(audio["startSeconds"]) + totalDuration > audioDuration + 0.05:
            raise ValueError("RED_AUDIO_TOO_SHORT")
        if float(audio["fadeOutSeconds"]) > totalDuration:
            raise ValueError("RED_AUDIO_FADE")
    if not jobLock.acquire(blocking=False):
        raise ValueError("RED_RENDER_BUSY")
    try:
        ffmpeg = tool("ffmpeg")
        encoderList = execute([ffmpeg, "-hide_banner", "-encoders"], 10).stdout.decode("utf-8", "replace")
        if "libx264" not in encoderList:
            raise RuntimeError("RED_LIBX264_UNAVAILABLE")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="ai-ffmpeg-") as temp:
            stage = Path(temp)
            normalized = []
            for index, shot in enumerate(validated):
                part = stage / f"shot-{index:02d}.mp4"
                aspect = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
                          "pad=1080:1920:(ow-iw)/2:(oh-ih)/2") if shot["fit"] == "contain" else (
                          "scale=1080:1920:force_original_aspect_ratio=increase,"
                          "crop=1080:1920")
                inp = (["-loop", "1", "-framerate", "30"] if shot["inputPath"].suffix.lower() in imageExtensions else [])
                filters = aspect + ",fps=30,format=yuv420p"
                if index == len(validated) - 1 and videoFadeOut > 0:
                    fadeStart = max(0.0, float(shot["seconds"]) - videoFadeOut)
                    filters += f",fade=t=out:st={fadeStart:.3f}:d={videoFadeOut:.3f}:color=black"
                arguments = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                             "-protocol_whitelist", "file,pipe", *inp, "-i", str(shot["inputPath"]),
                             "-t", f"{shot['seconds']:.3f}", "-vf", filters,
                             "-an", "-threads", "2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(part)]
                execute(arguments, timeout=180)
                normalized.append(part)
            # Paths here are generated by the service, not from the manifest.
            concatFile = stage / "inputs.txt"
            concatFile.write_text("".join("file '" + str(part) + "'\n" for part in normalized))
            temporaryOutput = stage / "episode.mp4"
            execute([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-f", "concat",
                     "-safe", "0", "-protocol_whitelist", "file,pipe", "-i", str(concatFile),
                     "-c", "copy", "-movflags", "+faststart", str(temporaryOutput)], 60)
            outputInfo = probe(temporaryOutput)
            if audio:
                duration = float(outputInfo.get("format", {}).get("duration", 0))
                audioFilter = (f"[1:a]apad=whole_dur={duration:.3f},atrim=duration={duration:.3f},"
                               f"asetpts=PTS-STARTPTS,volume={float(audio['volume']):.3f}")
                if audio["fadeOutSeconds"] > 0:
                    fadeStart = max(0.0, duration - float(audio["fadeOutSeconds"]))
                    audioFilter += f",afade=t=out:st={fadeStart:.3f}:d={float(audio['fadeOutSeconds']):.3f}"
                audioFilter += "[aout]"
                muxedOutput = stage / "episode-with-audio.mp4"
                execute([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                         "-i", str(temporaryOutput), "-ss", f"{float(audio['startSeconds']):.3f}",
                         "-protocol_whitelist", "file,pipe",
                         "-i", str(audio["inputPath"]), "-filter_complex", audioFilter,
                         "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
                         "-b:a", "192k", "-t", f"{duration:.3f}", "-movflags", "+faststart",
                         str(muxedOutput)], 180)
                temporaryOutput = muxedOutput
                outputInfo = probe(temporaryOutput)
            if not any(s.get("codec_type") == "video" for s in outputInfo.get("streams", [])):
                raise ValueError("RED_OUTPUT_NO_VIDEO")
            if audio and not any(s.get("codec_type") == "audio" for s in outputInfo.get("streams", [])):
                raise ValueError("RED_OUTPUT_NO_AUDIO")
            sha = hashlib.sha256(temporaryOutput.read_bytes()).hexdigest()
            shutil.move(str(temporaryOutput), str(output))
            receipt = {"schema": "luhm.aiFfmpegReceipt.v1", "jobId": manifest["jobId"],
                       "status": "CANDIDATE_RENDERED", "sha256": sha,
                       "bytes": output.stat().st_size, "shots": list(shotIds),
                       "durationSeconds": float(outputInfo.get("format", {}).get("duration", 0)),
                       "audioBedIncluded": audio is not None,
                       "videoFadeOutSeconds": videoFadeOut,
                       "publicationApproved": False, "driveArchived": False, "crown": "STOP"}
            # Kept next to the output, never inside the repo or public HTTP response.
            output.with_suffix(".receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
            return receipt
    finally:
        jobLock.release()


def serve(host, port, inputRoot, outputRoot):
    if host != "127.0.0.1":
        raise ValueError("RED_LOOPBACK_ONLY")
    token = os.getenv("LUHM_FFMPEG_TOKEN", "")
    if len(token) < 24:
        raise PermissionError("CROWN_STOP_LOCAL_TOKEN_REQUIRED")

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, value):
            body = json.dumps(value).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/healthz":
                self.reply(200, {"status": "ALIVE", "service": "ai-ffmpeg", "scope": "loopback",
                                 "renderReady": bool(shutil.which("ffmpeg") and shutil.which("ffprobe")),
                                 "publicationApproved": False})
            elif self.path == "/capabilities":
                self.reply(200, capabilities())
            elif self.path == "/presets":
                self.reply(200, {"profiles": ["portrait-seven-shot-review"], "sections": sorted(sections),
                                 "order": list(shotIds), "optionalAudioBed": True,
                                 "optionalFinalShotFadeToBlack": True})
            else:
                self.reply(404, {"error": "NOT_FOUND"})

        def do_POST(self):
            if self.path != "/render":
                return self.reply(404, {"error": "NOT_FOUND"})
            provided = self.headers.get("Authorization", "")
            if not hmac.compare_digest(provided, "Bearer " + token):
                return self.reply(403, {"error": "RED_AUTH"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 32768:
                    raise ValueError("RED_BODY_SIZE")
                payload = json.loads(self.rfile.read(size))
                result = render(payload, inputRoot, outputRoot)
                self.reply(200, result)
            except (ValueError, PermissionError, RuntimeError, json.JSONDecodeError) as exc:
                code = str(exc)
                self.reply(422, {"error": code if code.startswith(("RED_", "CROWN_STOP_")) else "RED_JOB"})

        def log_message(self, format, *args):
            # No authorization headers or user media paths in server logs.
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(json.dumps({"service": "ai-ffmpeg", "status": "LISTENING_LOOPBACK_ONLY", "port": server.server_port}), flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Local-first AI-FFmpeg candidate worker")
    parser.add_argument("action", choices=("doctor", "render", "serve"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--input-root", type=Path, default=Path.home() / "hydra/media")
    parser.add_argument("--output-root", type=Path, default=Path.home() / "hydra/media/candidates")
    parser.add_argument("--approve-render", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--port", type=int, default=8797)
    args = parser.parse_args()
    if args.action == "doctor":
        print(json.dumps(capabilities(args.full), indent=2))
    elif args.action == "serve":
        serve("127.0.0.1", args.port, args.input_root, args.output_root)
    else:
        if not args.approve_render or not args.manifest:
            raise PermissionError("CROWN_STOP_EXPLICIT_RENDER_APPROVAL_REQUIRED")
        print(json.dumps(render(json.loads(args.manifest.read_text()), args.input_root, args.output_root), indent=2))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, PermissionError) as exc:
        raise SystemExit(str(exc)) from None
