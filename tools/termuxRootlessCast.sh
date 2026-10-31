#!/data/data/com.termux/files/usr/bin/bash
# Rootless, package-minimal private browser cockpit. Not an APK install operation.
set -euo pipefail
umask 077
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"
command -v python3 >/dev/null || { echo 'Install Python with: pkg install python' >&2; exit 2; }
command -v git >/dev/null || { echo 'Install Git with: pkg install git' >&2; exit 2; }
MODE="${1:-start}"
case "$MODE" in
  check)
    python3 -m tools.rootlessCastCockpit --check
    printf 'ROOTLESS_CAST=SOURCE_CHECKED_ONLY\n'
    ;;
  start)
    python3 -m tools.rootlessCastCockpit --check
    printf '\nOpen http://127.0.0.1:8787/ in the Samsung browser.\n'
    printf 'In browser, Add to Home Screen for a local launcher shortcut.\n'
    printf 'Keep this Termux session running. No root, APK install or cloud API.\n\n'
    exec python3 -m tools.rootlessCastCockpit --port 8787
    ;;
  *) printf 'Usage: bash tools/termuxRootlessCast.sh [check|start]\n' >&2; exit 2 ;;
esac
