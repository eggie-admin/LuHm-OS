#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="eggie-admin/LuHm-OS"
PACKAGE="art.eggiebagelface.luhmos.testing"
TAG="${1:-}"
WORK="${TMPDIR:-$HOME/.cache}/luhm-virgin-install"
APK_NAME="${2:-}"
SHA_NAME="${3:-}"

die() {
  printf 'LUHM_VIRGIN_INSTALL=RED\nreason=%s\n' "$*" >&2
  exit 2
}

command -v curl >/dev/null || die "curl missing"
command -v sha256sum >/dev/null || die "sha256sum missing"
command -v su >/dev/null || die "root su missing"

if ! su -c id 2>/dev/null | grep -q 'uid=0'; then
  die "Termux does not currently have usable root"
fi

mkdir -p "$WORK"
rm -f "$WORK"/*

MODEL="$(getprop ro.product.model 2>/dev/null || true)"
DEVICE="$(getprop ro.product.device 2>/dev/null || true)"
ANDROID="$(getprop ro.build.version.release 2>/dev/null || true)"
SDK="$(getprop ro.build.version.sdk 2>/dev/null || true)"
FINGERPRINT="$(getprop ro.build.fingerprint 2>/dev/null || true)"

printf 'Device: %s (%s) Android %s SDK %s\n' "$MODEL" "$DEVICE" "$ANDROID" "$SDK"

if [ -z "$TAG" ]; then
  TAG="$(curl -fsSL "https://api.github.com/repos/$REPO/releases?per_page=20"     | python -c 'import json,sys; releases=json.load(sys.stdin); print(next(r["tag_name"] for r in releases if not r.get("draft")))' )"     || die "could not resolve newest non-draft GitHub Release tag"
fi

if [ -z "$APK_NAME" ]; then
  APK_NAME="LuHmOS-AndroidWeb3-${TAG}-arm64-v8a.apk"
fi
if [ -z "$SHA_NAME" ]; then
  SHA_NAME="${APK_NAME}.sha256"
fi

BASE="https://github.com/$REPO/releases/download/$TAG"
APK="$WORK/$APK_NAME"
SHA="$WORK/$SHA_NAME"

printf 'Resolving release: %s\n' "$TAG"
curl -fL --retry 4 --retry-all-errors -o "$APK" "$BASE/$APK_NAME"
curl -fL --retry 4 --retry-all-errors -o "$SHA" "$BASE/$SHA_NAME"

(
  cd "$WORK"
  sha256sum -c "$SHA_NAME"
) || die "release checksum verification failed"

case "$APK_NAME" in
  *.apk) ;;
  *) die "unexpected release asset name" ;;
esac

OLD_PRESENT=0
if su -c "pm path '$PACKAGE'" >/dev/null 2>&1; then
  OLD_PRESENT=1
  printf 'Existing LuHm package found, removing user install...\n'
  su -c "am force-stop '$PACKAGE' || true"
  su -c "pm clear '$PACKAGE' || true"
  UNINSTALL_LOG="$WORK/uninstall.txt"
  su -c "pm uninstall '$PACKAGE'" >"$UNINSTALL_LOG" 2>&1 || {
    cat "$UNINSTALL_LOG" >&2
    die "package uninstall failed"
  }
  grep -q 'Success' "$UNINSTALL_LOG" || die "package uninstall did not report Success"
fi

# LuHm-owned external app directories only. No broad storage deletion.
for p in   "/sdcard/Android/data/$PACKAGE"   "/sdcard/Android/obb/$PACKAGE"
do
  su -c "test ! -e '$p' || rm -rf -- '$p'"
done

STAGED="/data/local/tmp/$APK_NAME"
su -c "rm -f '$STAGED'"
su -c "cp '$APK' '$STAGED'"
su -c "chmod 0644 '$STAGED'"

printf 'Installing exact verified release APK...\n'
INSTALL_LOG="$WORK/install.txt"
PACKAGE_PATH_LOG="$WORK/package-path.txt"
LAUNCH_LOG="$WORK/launch.txt"

su -c "pm install -t '$STAGED'" >"$INSTALL_LOG" 2>&1 || {
  cat "$INSTALL_LOG" >&2
  die "pm install failed"
}
cat "$INSTALL_LOG"
grep -q 'Success' "$INSTALL_LOG" || die "pm install did not report Success"

su -c "pm path '$PACKAGE'" >"$PACKAGE_PATH_LOG" 2>&1   || die "installed package cannot be resolved"

DUMP="$(su -c "dumpsys package '$PACKAGE'")"
printf '%s\n' "$DUMP" | grep -E 'versionName=|versionCode=' | head -n 4 || true

MAIN_COMPONENT="$(su -c "cmd package resolve-activity --brief '$PACKAGE'" | tail -n 1)"
if [ -z "$MAIN_COMPONENT" ] || [ "$MAIN_COMPONENT" = "No activity found" ]; then
  die "launcher activity could not be resolved"
fi

printf 'Launching %s\n' "$MAIN_COMPONENT"
su -c "am start -n '$MAIN_COMPONENT'" >"$LAUNCH_LOG" 2>&1 || {
  cat "$LAUNCH_LOG" >&2
  die "launch failed"
}
cat "$LAUNCH_LOG"

printf 'LUHM_VIRGIN_INSTALL=GREEN\n'
printf 'tag=%s\n' "$TAG"
printf 'apk=%s\n' "$APK_NAME"
printf 'package=%s\n' "$PACKAGE"
printf 'oldPackageRemoved=%s\n' "$OLD_PRESENT"
printf 'staged=%s\n' "$STAGED"
printf 'launcher=%s\n' "$MAIN_COMPONENT"
printf 'deviceModel=%s\n' "$MODEL"
printf 'deviceCode=%s\n' "$DEVICE"
printf 'android=%s\n' "$ANDROID"
printf 'sdk=%s\n' "$SDK"
printf 'fingerprint=%s\n' "$FINGERPRINT"
