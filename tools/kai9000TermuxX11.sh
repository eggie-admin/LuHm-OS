#!/usr/bin/env bash
# KAI9000 native Termux:X11 / XFCE desktop, no root and no public listener.
set -euo pipefail
umask 077

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "$HERE/.." && pwd -P)"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/luhm-kai9000"
DISPLAY_ID=":1"
TAG="kai9000"
PORT=8765
SERVER="$HERE/kai9000LocalCockpit.py"

usage() {
  cat <<'USAGE'
KAI9000 Samsung Lite local desktop
  bash tools/kai9000TermuxX11.sh doctor           read-only prerequisites check
  bash tools/kai9000TermuxX11.sh setup            explicit one-time package and jQuery staging
  bash tools/kai9000TermuxX11.sh desktop          start native XFCE in Termux:X11
  bash tools/kai9000TermuxX11.sh cockpit          start local HTML and open Android browser
  bash tools/kai9000TermuxX11.sh status           inspect owned session processes
  bash tools/kai9000TermuxX11.sh stop             stop only this session
  bash tools/kai9000TermuxX11.sh help
Prerequisite: install Termux:X11 Android APK from official termux/termux-x11 release.
USAGE
}

die() { printf 'KAI9000_BLOCKED: %s\n' "$*" >&2; exit 2; }
msg() { printf 'KAI9000: %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing $1 (run setup or install it first)"; }
ensure_state() { mkdir -p -- "$STATE"; chmod 700 -- "$STATE"; }

# Never kill a recycled PID or a process owned by another application.
owned_pid() {
  local path="$1" marker="$2" pid cmdline
  [[ -f "$path" ]] || return 1
  IFS= read -r pid < "$path" || return 1
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  [[ -r "/proc/$pid/cmdline" ]] || return 1
  cmdline="$(tr '\0' ' ' < "/proc/$pid/cmdline")"
  [[ "$cmdline" == *"$marker"* ]] || return 1
  printf '%s\n' "$pid"
}

stop_one() {
  local file="$1" marker="$2" pid
  if pid="$(owned_pid "$file" "$marker")"; then
    kill "$pid" 2>/dev/null || true
    msg "stopped owned $marker (pid $pid)"
  else
    msg "no verified owned $marker process (unrelated processes untouched)"
  fi
  rm -f -- "$file"
}

is_termux() {
  [[ "${PREFIX:-}" == */com.termux/files/usr ]]
}

doctor() {
  msg "device target = Samsung Android / unrooted / local only"
  if is_termux; then msg 'Termux prefix = OK'; else msg 'Termux prefix = NOT DETECTED'; fi
  local item
  for item in pkg termux-x11 xfce4-session dbus-launch python3 node npm git termux-open-url; do
    if command -v "$item" >/dev/null 2>&1; then msg "$item = found"; else msg "$item = missing"; fi
  done
  if command -v /system/bin/pm >/dev/null 2>&1; then
    if /system/bin/pm path com.termux.x11 2>/dev/null | grep -q '^package:'; then
      msg 'Termux:X11 Android app = installed'
    else
      msg 'Termux:X11 Android app = not detected (install official APK manually)'
    fi
  fi
  if [[ -f "$ROOT/frontEnd/vendor/jquery-3.7.1.min.js" ]]; then
    msg 'pinned local jQuery asset = present'
  else
    msg 'pinned local jQuery asset = missing (setup stages it)'
  fi
}

setup() {
  is_termux || die 'setup must run inside normal Termux, not proot, Android shell, or Secure Folder'
  need pkg
  msg 'Installing official Termux packages (no root, no kernel mutation).'
  pkg install -y x11-repo
  pkg install -y termux-x11-nightly xfce dbus python git nodejs-lts
  need npm
  [[ -f "$ROOT/frontEnd/package-lock.json" ]] || die 'pinned frontEnd/package-lock.json missing'
  (cd "$ROOT/frontEnd" && npm ci --ignore-scripts --no-audit --no-fund && npm run stage:jquery && npm run check)
  python3 "$SERVER" --root "$ROOT/frontEnd" --check
  msg 'Setup complete. Android Termux:X11 companion APK still needs owner installation if absent.'
}

desktop() {
  is_termux || die 'desktop must run inside the normal Termux installation'
  need termux-x11
  need xfce4-session
  ensure_state
  if owned_pid "$STATE/x11.pid" 'termux-x11' >/dev/null; then
    msg 'desktop already running; reopening tagged window'
  else
    rm -f -- "$STATE/x11.pid"
    local startup='xfce4-session'
    if command -v dbus-launch >/dev/null 2>&1; then
      startup='dbus-launch --exit-with-session xfce4-session'
    fi
    # no proot, VNC, permissive X11 access control, remote X11 TCP, or additional Android permissions.
    nohup termux-x11 "$DISPLAY_ID" -tag "$TAG" -xstartup "$startup" >"$STATE/x11.log" 2>&1 </dev/null &
    printf '%s\n' "$!" > "$STATE/x11.pid"
    msg 'started Termux:X11 display :1 with native XFCE'
  fi
  if command -v am >/dev/null 2>&1; then
    am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity -d "$TAG" >/dev/null 2>&1 ||
      msg 'Open Termux:X11 Android app yourself if the activity did not appear.'
  fi
}

cockpit() {
  is_termux || die 'cockpit must run inside the normal Termux installation'
  need python3
  ensure_state
  python3 "$SERVER" --root "$ROOT/frontEnd" --check
  if owned_pid "$STATE/http.pid" 'kai9000LocalCockpit.py' >/dev/null; then
    msg 'local cockpit server already running'
  else
    rm -f -- "$STATE/http.pid"
    nohup python3 "$SERVER" --root "$ROOT/frontEnd" --port "$PORT" >"$STATE/http.log" 2>&1 </dev/null &
    printf '%s\n' "$!" > "$STATE/http.pid"
    # A quick failed-bind check avoids opening a different program on the port.
    sleep 1
    owned_pid "$STATE/http.pid" 'kai9000LocalCockpit.py' >/dev/null ||
      die "local cockpit failed to bind; see $STATE/http.log"
  fi
  msg "local cockpit: http://127.0.0.1:$PORT/ (Android browser, not remote)"
  if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "http://127.0.0.1:$PORT/" || msg 'Open the local URL manually in Android Chrome.'
  fi
}

status() {
  if owned_pid "$STATE/x11.pid" 'termux-x11' >/dev/null; then msg 'desktop = RUNNING'; else msg 'desktop = NOT VERIFIED'; fi
  if owned_pid "$STATE/http.pid" 'kai9000LocalCockpit.py' >/dev/null; then msg 'cockpit = RUNNING_LOCAL'; else msg 'cockpit = NOT VERIFIED'; fi
  msg 'public listener = NOT REQUESTED (127.0.0.1 only for cockpit)'
  msg 'physical tablet acceptance = NOT VERIFIED BY SCRIPT'
}

stop() {
  ensure_state
  stop_one "$STATE/http.pid" 'kai9000LocalCockpit.py'
  stop_one "$STATE/x11.pid" 'termux-x11'
  if command -v am >/dev/null 2>&1; then
    am broadcast -a com.termux.x11.ACTION_STOP -p com.termux.x11 --es document_tag "$TAG" >/dev/null 2>&1 || true
  fi
  msg 'no uninstall, data wipe, process-wide pkill, or Android setting changes performed'
}

case "${1:-help}" in
  doctor) doctor ;;
  setup) setup ;;
  desktop|start) desktop ;;
  cockpit) cockpit ;;
  status) status ;;
  stop) stop ;;
  help|-h|--help) usage ;;
  *) usage >&2; die "unknown command" ;;
esac
