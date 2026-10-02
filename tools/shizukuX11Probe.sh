#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DISPLAY_ID="${DISPLAY_ID:-:1}"

json_bool() { [ "$1" = "1" ] && printf true || printf false; }
has_cmd() { command -v "$1" >/dev/null 2>&1; }

MODEL="$(getprop ro.product.model 2>/dev/null || true)"
ANDROID="$(getprop ro.build.version.release 2>/dev/null || true)"
SDK="$(getprop ro.build.version.sdk 2>/dev/null || true)"

SHIZUKU_APP=0
/system/bin/pm path moe.shizuku.privileged.api >/dev/null 2>&1 && SHIZUKU_APP=1 || true

X11_APP=0
/system/bin/pm path com.termux.x11 >/dev/null 2>&1 && X11_APP=1 || true

X11_CMD=0
has_cmd termux-x11 && X11_CMD=1 || true

PROOT_DISTRO=0
has_cmd proot-distro && PROOT_DISTRO=1 || true

RISH=0
has_cmd rish && RISH=1 || true

X11_PROC=0
pgrep -f '(^|/)termux-x11([[:space:]]|$)' >/dev/null 2>&1 && X11_PROC=1 || true

SHIZUKU_UID="unknown"
SHIZUKU_STATE="unknown"
if [ "$RISH" -eq 1 ]; then
  if UID_OUT="$(rish -c id -u 2>/dev/null | tr -d '\r\n')" && [ -n "$UID_OUT" ]; then
    SHIZUKU_UID="$UID_OUT"
    case "$UID_OUT" in
      0) SHIZUKU_STATE="runningRoot" ;;
      2000) SHIZUKU_STATE="runningAdb" ;;
      *) SHIZUKU_STATE="runningOtherUid" ;;
    esac
  fi
elif [ "$SHIZUKU_APP" -eq 1 ]; then
  SHIZUKU_STATE="installedPermissionUnknown"
else
  SHIZUKU_STATE="notInstalled"
fi

X11_PAIR="notInstalled"
if [ "$X11_APP" -eq 1 ] && [ "$X11_CMD" -eq 1 ]; then
  X11_PAIR="pairedInstalled"
elif [ "$X11_APP" -eq 1 ]; then
  X11_PAIR="appOnly"
elif [ "$X11_CMD" -eq 1 ]; then
  X11_PAIR="companionOnly"
fi

cat <<JSON
{
  "schema":"luhmOs.shizukuX11Probe.v1",
  "device":{"model":"$MODEL","android":"$ANDROID","sdk":"$SDK"},
  "shizuku":{"appPresent":$(json_bool "$SHIZUKU_APP"),"rishPresent":$(json_bool "$RISH"),"state":"$SHIZUKU_STATE","uid":"$SHIZUKU_UID","permissionState":"unknownUnlessRishCommandSucceeded"},
  "termuxX11":{"appPresent":$(json_bool "$X11_APP"),"companionPresent":$(json_bool "$X11_CMD"),"pairState":"$X11_PAIR","displayId":"$DISPLAY_ID","serverProcessObserved":$(json_bool "$X11_PROC"),"renderObserved":false},
  "proot":{"prootDistroPresent":$(json_bool "$PROOT_DISTRO"),"sharedTmpObserved":false},
  "authority":{"greenAuthority":false,"crownStatus":"stop"}
}
JSON
