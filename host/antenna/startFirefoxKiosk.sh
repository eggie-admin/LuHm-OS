#!/bin/sh
# Source-only launch helper. Execute as an unprivileged desktop user.
# X11 must already exist; no login manager, package install or escalation.
set -eu
[ "$(id -u)" -ne 0 ] || { printf '%s\n' 'Refusing to run kiosk as root' >&2; exit 2; }
[ -n "${DISPLAY:-}" ] || { printf '%s\n' 'DISPLAY is unset: start a local X11 session first' >&2; exit 2; }
command -v firefox-esr >/dev/null 2>&1 || { printf '%s\n' 'firefox-esr missing' >&2; exit 2; }
exec firefox-esr --no-remote --kiosk http://127.0.0.1:8765/
