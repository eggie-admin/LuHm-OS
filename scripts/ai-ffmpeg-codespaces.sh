#!/usr/bin/env bash
# GitHub Codespaces only; install FFmpeg and launch private remote lab preview.
set -euo pipefail
mode="${1:-status}"
secretDir="$HOME/.secret/hydra"
secretFile="$secretDir/ai-ffmpeg.env"
logFile="$secretDir/ai-ffmpeg-codespaces.log"
repoRoot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
worker="$repoRoot/host/ai-ffmpeg/ai-ffmpeg.py"

if [[ "${LUHM_WORKBENCH:-}" != "codespaces" || -z "${CODESPACES:-}" ]]; then
  echo 'CROWN_STOP_CODESPACES_RUNTIME_REQUIRED' >&2
  exit 3
fi

case "$mode" in
  setup)
    command -v sudo >/dev/null || { echo 'RED_SUDO_REQUIRED_FOR_CODESPACE_SETUP' >&2; exit 2; }
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpeg
    umask 077
    mkdir -p "$secretDir" "$HOME/hydra/media/candidates"
    chmod 700 "$secretDir"
    if [[ ! -e "$secretFile" ]]; then
      printf 'LUHM_FFMPEG_TOKEN=%s\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(36))')" > "$secretFile"
    fi
    chmod 600 "$secretFile"
    echo 'REMOTE_GARAGE_FFMPEG_SETUP_COMPLETE'
    ;;
  start)
    command -v ffmpeg >/dev/null || { echo 'RED_FFMPEG_MISSING_RUN_SETUP' >&2; exit 2; }
    [[ -f "$secretFile" ]] || { echo 'RED_TOKEN_MISSING_RUN_SETUP' >&2; exit 2; }
    [[ -f "$worker" ]] || { echo 'RED_WORKER_MISSING' >&2; exit 2; }
    if curl --max-time 2 --fail --silent http://127.0.0.1:8797/healthz >/dev/null; then
      echo 'REMOTE_GARAGE_FFMPEG_ALREADY_RESPONDING'
      exit 0
    fi
    set -a
    source "$secretFile"
    set +a
    nohup python3 "$worker" serve --input-root "$HOME/hydra/media" --output-root "$HOME/hydra/media/candidates" > "$logFile" 2>&1 < /dev/null &
    for attempt in 1 2 3 4 5; do
      if curl --max-time 2 --fail --silent http://127.0.0.1:8797/healthz >/dev/null; then
        echo 'REMOTE_GARAGE_FFMPEG_ALIVE_LOOPBACK'
        exit 0
      fi
      sleep 1
    done
    echo 'RED_CODESPACE_WORKER_NOT_HEALTHY' >&2
    exit 2
    ;;
  status)
    curl --max-time 3 --fail --silent --show-error http://127.0.0.1:8797/healthz
    printf '\n'
    ;;
  *)
    echo 'usage: bash scripts/ai-ffmpeg-codespaces.sh {setup|start|status}' >&2
    exit 2
    ;;
esac
