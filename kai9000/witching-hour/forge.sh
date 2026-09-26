#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$ROOT/bin"

banner() {
  cat <<'TXT'
╔══════════════════════════════════════════╗
║  KAI 9000 // WITCHING HOUR LOCAL FORGE ║
║  Lum + Kiri + Tetsu + Momo + Shiori    ║
║  Kugi executes only what you choose.    ║
╚══════════════════════════════════════════╝
TXT
}

help_text() {
  cat <<'TXT'
Commands:
  audit                    Read-only 10-pass runtime audit
  snapshot --crown         Local rollback snapshot, never auto-uploaded
  ollama --crown           Foreground loopback-only Ollama
  vnc --crown              On-demand localhost-only TigerVNC
  update-plan              Show upgrades from current metadata, apply nothing
  update-plan --refresh --crown
                           Refresh metadata, then show plan, apply nothing
  play                     Interactive toy/operator menu

Source law: AI proposes. Policy authorizes. Deterministic probes prove. Human promotes.
TXT
}

run_cmd() {
  case "${1:-help}" in
    audit) shift; exec bash "$BIN/kai-doctor.sh" "$@" ;;
    snapshot) shift; exec bash "$BIN/kai-snapshot.sh" "$@" ;;
    ollama) shift; exec bash "$BIN/kai-ollama.sh" "$@" ;;
    vnc) shift; exec bash "$BIN/kai-vnc.sh" "$@" ;;
    update-plan) shift; exec bash "$BIN/kai-update-plan.sh" "$@" ;;
    help|-h|--help) banner; help_text ;;
    *) echo "Unknown command: $1"; help_text; exit 64 ;;
  esac
}

play() {
  banner
  echo 'Kiri: Scope locked to KAI 9000. LuHm OS native Android stays untouched.'
  echo 'Tetsu: Headless services first. GUI is optional.'
  echo 'Momo: Package freshness is reviewed, never blindly applied.'
  echo 'Shiori: Runtime GREEN requires receipts, not vibes.'
  echo 'Kugi: I only execute the numbered choice you make.'
  echo
  while true; do
    cat <<'MENU'
[1] Audit current state
[2] Make local rollback snapshot
[3] Start Ollama foreground
[4] Start TigerVNC operator lane
[5] Generate update plan
[6] Refresh metadata + generate update plan
[q] Quit
MENU
    printf '> '
    IFS= read -r choice
    case "$choice" in
      1) bash "$BIN/kai-doctor.sh" || true ;;
      2) bash "$BIN/kai-snapshot.sh" --crown ;;
      3) bash "$BIN/kai-ollama.sh" --crown ;;
      4) bash "$BIN/kai-vnc.sh" --crown ;;
      5) bash "$BIN/kai-update-plan.sh" ;;
      6) bash "$BIN/kai-update-plan.sh" --refresh --crown ;;
      q|Q) exit 0 ;;
      *) echo 'Kugi: blocked unknown choice.' ;;
    esac
    echo
  done
}

if [ "${1:-}" = 'play' ]; then
  play
else
  run_cmd "$@"
fi
