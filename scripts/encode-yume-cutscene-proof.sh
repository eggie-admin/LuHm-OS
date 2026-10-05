#!/usr/bin/env bash
set -euo pipefail

framesDir="${1:-}"
outFile="${2:-}"
fps="${3:-30}"

if [[ -z "$framesDir" || -z "$outFile" ]]; then
  echo "usage: $0 /path/to/frames /path/to/review.mp4 [fps]" >&2
  exit 2
fi

command -v ffmpeg >/dev/null || { echo "ffmpeg required" >&2; exit 3; }
command -v ffprobe >/dev/null || { echo "ffprobe required" >&2; exit 3; }

pattern="$framesDir/shot%08d.png"
firstFrame="$framesDir/shot00000000.png"
audioFile="$framesDir/shot.wav"

[[ -f "$firstFrame" ]] || { echo "missing first movie frame: $firstFrame" >&2; exit 4; }
mkdir -p "$(dirname "$outFile")"

if [[ -f "$audioFile" ]]; then
  ffmpeg -hide_banner -loglevel error -y     -framerate "$fps" -i "$pattern" -i "$audioFile"     -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p     -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$outFile"
else
  ffmpeg -hide_banner -loglevel error -y     -framerate "$fps" -i "$pattern"     -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p     -movflags +faststart "$outFile"
fi

echo "ENCODE_OK=$outFile"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$outFile"
