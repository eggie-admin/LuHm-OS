#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/.garage-smoke}"
rm -rf "$OUT"
mkdir -p "$OUT"/{job/repairs,artifact}

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
python3 --version

SOURCE="$OUT/artifact/smoke-source.mp4"
FIXED="$OUT/artifact/smoke-fixed.mp4"
COMPARE="$OUT/artifact/smoke-compare.mp4"
CONTACT="$OUT/artifact/smoke-contact.jpg"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "testsrc2=size=320x568:rate=30:duration=8" \
  -f lavfi -i "sine=frequency=440:sample_rate=48000:duration=8" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset veryfast \
  -c:a aac -b:a 128k -shortest "$SOURCE"

python3 "$ROOT/tools/ffmpegAiRepairBay.py" probe "$SOURCE" > "$OUT/artifact/source-probe.json"
python3 "$ROOT/tools/ffmpegAiRepairBay.py" demux "$SOURCE" "$OUT/job"
python3 "$ROOT/tools/ffmpegAiRepairBay.py" contact-sheet "$SOURCE" "$CONTACT" --sample-fps 1 --cols 4 --rows 2

for n in $(seq 117 123); do
  src="$(printf '%s/job/frames/shot%08d.png' "$OUT" "$n")"
  dst="$(printf '%s/job/repairs/shot%08d.png' "$OUT" "$n")"
  ffmpeg -hide_banner -loglevel error -y -i "$src" \
    -vf "drawbox=x=18:y=18:w=284:h=532:color=red@0.55:t=fill,drawbox=x=42:y=230:w=236:h=108:color=black@0.75:t=fill" \
    -frames:v 1 "$dst"
done

python3 "$ROOT/tools/ffmpegAiRepairBay.py" rebuild-window \
  --source-frames "$OUT/job/frames" \
  --repair-frames "$OUT/job/repairs" \
  --output-frames "$OUT/job/rebuilt" \
  --start-frame 117 \
  --end-frame 123

python3 "$ROOT/tools/ffmpegAiRepairBay.py" remux \
  --frames "$OUT/job/rebuilt" \
  --source "$SOURCE" \
  --output "$FIXED" \
  --fps 30

python3 "$ROOT/tools/ffmpegAiRepairBay.py" compare \
  --before "$SOURCE" \
  --after "$FIXED" \
  --output "$COMPARE"

cp "$OUT/job/repair-window-receipt.json" "$OUT/artifact/"
cp "$OUT/job/receipts/source.sha256" "$OUT/artifact/"
cp "$OUT/job/receipts/source-probe.json" "$OUT/artifact/demux-source-probe.json"

SOURCE_FRAMES=$(find "$OUT/job/frames" -maxdepth 1 -name 'shot*.png' | wc -l)
REBUILT_FRAMES=$(find "$OUT/job/rebuilt" -maxdepth 1 -name 'shot*.png' | wc -l)
REPAIRS=$(find "$OUT/job/repairs" -maxdepth 1 -name 'shot*.png' | wc -l)

test "$SOURCE_FRAMES" -eq 240
test "$REBUILT_FRAMES" -eq 240
test "$REPAIRS" -eq 7

python3 - "$OUT/artifact/smoke-receipt.json" "$SOURCE" "$FIXED" "$COMPARE" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path

receipt_path, source, fixed, compare = map(Path, sys.argv[1:])

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def duration(path):
    p = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],
        check=True,capture_output=True,text=True
    )
    return round(float(p.stdout.strip()), 3)

receipt = {
    "schema": "luhmOs.professorGarageMediaSmokeReceipt.v1",
    "sourceFrames": 240,
    "replacementStartFrame": 117,
    "replacementEndFrame": 123,
    "replacementCount": 7,
    "sourceSha256": sha256(source),
    "fixedSha256": sha256(fixed),
    "compareSha256": sha256(compare),
    "sourceDuration": duration(source),
    "fixedDuration": duration(fixed),
    "compareDuration": duration(compare),
    "result": "PASS",
    "runtimeScope": "githubActionsUbuntuRunner",
    "codespaceRuntimeProven": False,
    "providerEntitlementProven": False,
    "crownAuthority": False
}
receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
PY

echo "PROFESSOR_GARAGE_MEDIA_SMOKE=PASS"
echo "ARTIFACT_DIR=$OUT/artifact"
