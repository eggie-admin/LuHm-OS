#!/usr/bin/env bash
# Explicit operator-installed systemd user service. Never run in PR CI.
set -euo pipefail

action="${1:-status}"
unitName="ai-ffmpeg.service"
unitPath="$HOME/.config/systemd/user/$unitName"
secretDir="$HOME/.secret/hydra"
secretFile="$secretDir/ai-ffmpeg.env"
outputDir="$HOME/hydra/media/candidates"
repoRoot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
worker="$repoRoot/host/ai-ffmpeg/ai-ffmpeg.py"

case "$action" in
  status)
    systemctl --user --no-pager status "$unitName" || true
    if command -v curl >/dev/null; then
      curl --max-time 3 --fail --silent --show-error http://127.0.0.1:8797/healthz || true
      printf '\n'
    fi
    ;;
  install)
    for tool in systemctl python3 ffmpeg ffprobe; do
      command -v "$tool" >/dev/null || { echo "RED_MISSING_TOOL: $tool" >&2; exit 3; }
    done
    [[ -f "$worker" ]] || { echo "RED_MISSING_CANDIDATE_WORKER" >&2; exit 3; }
    [[ ! -e "$unitPath" ]] || { echo "CROWN_STOP_UNIT_ALREADY_EXISTS: $unitPath" >&2; exit 4; }
    [[ "$repoRoot" != *%* ]] || { echo 'RED_UNSUPPORTED_SERVICE_PATH' >&2; exit 4; }
    umask 077
    mkdir -p "$secretDir" "$(dirname "$unitPath")" "$outputDir"
    chmod 700 "$secretDir"
    if [[ ! -e "$secretFile" ]]; then
      printf 'LUHM_FFMPEG_TOKEN=%s\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(36))')" > "$secretFile"
    fi
    chmod 600 "$secretFile"
    cat > "$unitPath" <<EOF
[Unit]
Description=LuHm AI-FFmpeg local CPU review worker
After=default.target

[Service]
Type=simple
EnvironmentFile=%h/.secret/hydra/ai-ffmpeg.env
ExecStart=/usr/bin/python3 "$worker" serve
WorkingDirectory="$repoRoot"
Restart=on-failure
RestartSec=5
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=%h/hydra/media/candidates
RestrictAddressFamilies=AF_UNIX AF_INET
IPAddressDeny=any
IPAddressAllow=localhost
MemoryMax=3G
CPUQuota=200%
TasksMax=64

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$unitName"
    if command -v curl >/dev/null; then
      curl --max-time 5 --fail --silent --show-error http://127.0.0.1:8797/healthz
      printf '\n'
    fi
    echo 'SERVICE_START_REQUESTED_LOCAL_ONLY; verify active state and health receipt.'
    ;;
  *)
    echo "usage: $0 {status|install}" >&2
    exit 2
    ;;
esac
