#!/usr/bin/env bash
set -euo pipefail

mode="${1:-}"
sourceRef="${2:-}"
outRoot="${3:-}"
godotBin="${GODOT_BIN:-godot}"

if [[ "$mode" != "dayShift" && "$mode" != "afterHours" ]]; then
  echo "mode must be dayShift or afterHours" >&2
  exit 2
fi
if [[ ! "$sourceRef" =~ ^[0-9a-f]{40}$ ]]; then
  echo "sourceRef must be a 40-character git SHA" >&2
  exit 2
fi
if [[ -z "$outRoot" ]]; then
  echo "output root required" >&2
  exit 2
fi
if [[ "${LUHM_CAST:-}" != "cast" ]]; then
  echo "CAST_REQUIRED: set LUHM_CAST=cast for one explicit render attempt" >&2
  exit 5
fi

repoRoot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
actualRef="$(git -C "$repoRoot" rev-parse HEAD)"
if [[ "$actualRef" != "$sourceRef" ]]; then
  echo "SOURCE_DRIFT expected=$sourceRef actual=$actualRef" >&2
  exit 6
fi

command -v "$godotBin" >/dev/null || { echo "Godot executable not found: $godotBin" >&2; exit 3; }
command -v ffmpeg >/dev/null || { echo "ffmpeg required" >&2; exit 3; }

shotDir="$outRoot/$mode/frames"
mkdir -p "$shotDir"

echo "RENDER_START mode=$mode sourceRef=$sourceRef"
LUHM_PRESENTATION_MODE="$mode" "$godotBin"   --path "$repoRoot"   --fixed-fps 30   --resolution 1080x1920   --write-movie "$shotDir/shot.png"   res://scenes/YumeCutsceneFactoryProof.tscn

bash "$repoRoot/scripts/encode-yume-cutscene-proof.sh"   "$shotDir" "$outRoot/$mode/yumeCutsceneFactoryProof-$mode.mp4" 30

echo "RENDER_OK mode=$mode sourceRef=$sourceRef"
