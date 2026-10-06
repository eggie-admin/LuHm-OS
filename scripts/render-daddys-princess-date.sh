#!/usr/bin/env bash
set -euo pipefail

srcDir="${1:-}"
outFile="${2:-}"

if [[ -z "$srcDir" || -z "$outFile" ]]; then
  echo "usage: $0 /private/source-clips /output/daddys-princess-date.mp4" >&2
  exit 2
fi

command -v ffmpeg >/dev/null || { echo "ffmpeg required" >&2; exit 3; }
command -v ffprobe >/dev/null || { echo "ffprobe required" >&2; exit 3; }

workDir="$(mktemp -d)"
trap 'rm -rf "$workDir"' EXIT

mapfile -t clips < <(find "$srcDir" -maxdepth 1 -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' \) | sort)

if (( ${#clips[@]} == 0 )); then
  echo "no source clips found in $srcDir" >&2
  exit 4
fi

listFile="$workDir/concat.txt"
: > "$listFile"

i=0
for clip in "${clips[@]}"; do
  i=$((i+1))
  norm="$workDir/clip-$(printf '%03d' "$i").mp4"
  ffmpeg -hide_banner -loglevel error -y -i "$clip" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p" \
    -af "aresample=48000,apad" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -shortest "$norm"
  printf "file '%s'\n" "$norm" >> "$listFile"
done

body="$workDir/body.mp4"
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$listFile" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k "$body"

bodyDur="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$body")"

brand="$workDir/brand.mp4"
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=1080x1920:r=30:d=6" \
  -f lavfi -i "anullsrc=r=48000:cl=stereo:d=6" \
  -vf "drawtext=font='Sans':text='PIRATE DADDIES FILM':fontcolor=white:fontsize=76:x=(w-text_w)/2:y=h*0.42,drawtext=font='Sans':text='Remember... All Daddies Love You':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=h*0.52" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$brand"

finalList="$workDir/final.txt"
printf "file '%s'\nfile '%s'\n" "$body" "$brand" > "$finalList"

ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$finalList" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart "$outFile"

echo "RENDER_OK=$outFile"
echo "BODY_SECONDS=$bodyDur"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$outFile"
