#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" != "--crown" ]; then
  echo 'Starting the GUI operator lane is Crown-gated. Re-run with: kai-vnc.sh --crown'
  exit 64
fi

VNC_BIN=''
for c in vncserver tigervncserver; do
  if command -v "$c" >/dev/null 2>&1; then VNC_BIN="$c"; break; fi
done
if [ -z "$VNC_BIN" ]; then
  echo 'TigerVNC launcher not found; no package mutation performed'
  exit 69
fi

PASSFILE="${VNC_PASSFILE:-$HOME/.vnc/passwd}"
if [ ! -f "$PASSFILE" ]; then
  echo "VNC password file missing: $PASSFILE"
  echo 'Create it manually with vncpasswd, then retry.'
  exit 78
fi
mode="$(stat -c '%a' "$PASSFILE" 2>/dev/null || printf unknown)"
case "$mode" in
  600|400) ;;
  *) echo "VNC password file mode is $mode; expected 600 or 400"; exit 77;;
esac

DISPLAY_NUM="${KAI_VNC_DISPLAY:-:1}"
echo "KAI 9000 // TigerVNC operator lane on $DISPLAY_NUM"
echo 'localhost-only enforced; this is optional and on-demand.'
exec "$VNC_BIN" "$DISPLAY_NUM" -localhost yes
