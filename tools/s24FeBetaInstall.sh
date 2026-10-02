#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="eggie-admin/LuHm-OS"
PACKAGE="art.eggiebagelface.luhmos.testing"
EXPECTED_MODEL="SM-S721U1"
EXPECTED_ANDROID="16"
EXPECTED_ABI="arm64-v8a"
TAG="${1:-}"
WORK="${TMPDIR:-$HOME/.cache}/luhm-s24fe-beta-install"
APK_NAME="${2:-}"
SHA_NAME="${3:-}"

die() {
  printf 'LUHM_S24FE_BETA_INSTALL=RED\nreason=%s\n' "$*" >&2
  exit 2
}

command -v curl >/dev/null || die "curl missing"
command -v sha256sum >/dev/null || die "sha256sum missing"

mkdir -p "$WORK"
rm -f "$WORK"/*

MODEL="$(getprop ro.product.model 2>/dev/null || true)"
DEVICE="$(getprop ro.product.device 2>/dev/null || true)"
ANDROID="$(getprop ro.build.version.release 2>/dev/null || true)"
SDK="$(getprop ro.build.version.sdk 2>/dev/null || true)"
ABI="$(getprop ro.product.cpu.abi 2>/dev/null || true)"

printf 'Device: %s (%s) Android %s SDK %s ABI %s\n' "$MODEL" "$DEVICE" "$ANDROID" "$SDK" "$ABI"

[ "$MODEL" = "$EXPECTED_MODEL" ] || die "target model mismatch: expected $EXPECTED_MODEL got $MODEL"
[ "$ANDROID" = "$EXPECTED_ANDROID" ] || die "target Android mismatch: expected $EXPECTED_ANDROID got $ANDROID"
[ "$ABI" = "$EXPECTED_ABI" ] || die "target ABI mismatch: expected $EXPECTED_ABI got $ABI"

if [ -z "$TAG" ]; then
  TAG="$(curl -fsSL "https://api.github.com/repos/$REPO/releases?per_page=30" \
    | python -c 'import json,sys; r=json.load(sys.stdin); print(next(x["tag_name"] for x in r if x.get("prerelease") and "s24fe-beta" in x["tag_name"]))')" \
    || die "could not resolve newest S24 FE beta prerelease"
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

printf 'Resolving prerelease: %s\n' "$TAG"
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

ROOT_READY=0
if command -v su >/dev/null 2>&1 && su -c id 2>/dev/null | grep -q 'uid=0'; then
  ROOT_READY=1
fi

if [ "$ROOT_READY" -eq 1 ]; then
  printf 'Install mode: rooted package-scoped virgin install\n'

  if su -c "pm path '$PACKAGE'" >/dev/null 2>&1; then
    su -c "am force-stop '$PACKAGE' || true"
    su -c "pm clear '$PACKAGE' || true"
    su -c "pm uninstall '$PACKAGE'" | tee "$WORK/uninstall.txt"
    grep -q 'Success' "$WORK/uninstall.txt" || die "package uninstall did not report Success"
  fi

  for p in "/sdcard/Android/data/$PACKAGE" "/sdcard/Android/obb/$PACKAGE"; do
    su -c "test ! -e '$p' || rm -rf -- '$p'"
  done

  STAGED="/data/local/tmp/$APK_NAME"
  su -c "rm -f '$STAGED'"
  su -c "cp '$APK' '$STAGED'"
  su -c "chmod 0644 '$STAGED'"

  su -c "pm install -t '$STAGED'" | tee "$WORK/install.txt"
  grep -q 'Success' "$WORK/install.txt" || die "pm install did not report Success"

  su -c "pm path '$PACKAGE'" >"$WORK/package-path.txt" 2>&1 || die "installed package cannot be resolved"
  MAIN_COMPONENT="$(su -c "cmd package resolve-activity --brief '$PACKAGE'" | tail -n 1)"
  [ -n "$MAIN_COMPONENT" ] && [ "$MAIN_COMPONENT" != "No activity found" ] || die "launcher activity could not be resolved"

  su -c "am start -n '$MAIN_COMPONENT'" | tee "$WORK/launch.txt"

  printf 'LUHM_S24FE_BETA_INSTALL=GREEN\n'
  printf 'installMode=root\n'
  printf 'tag=%s\n' "$TAG"
  printf 'apk=%s\n' "$APK_NAME"
  printf 'package=%s\n' "$PACKAGE"
  printf 'launcher=%s\n' "$MAIN_COMPONENT"
else
  printf 'Install mode: Android package installer handoff (root not proven)\n'
  command -v termux-open >/dev/null || die "termux-open missing; install Termux:API integration or open $APK manually"
  termux-open --view "$APK"
  printf 'LUHM_S24FE_BETA_INSTALL=AMBER_USER_CONFIRM\n'
  printf 'installMode=androidPackageInstaller\n'
  printf 'tag=%s\n' "$TAG"
  printf 'apk=%s\n' "$APK_NAME"
  printf 'package=%s\n' "$PACKAGE"
  printf 'next=approve Android package installer, then return for launch receipt\n'
fi

printf 'deviceModel=%s\n' "$MODEL"
printf 'deviceCode=%s\n' "$DEVICE"
printf 'android=%s\n' "$ANDROID"
printf 'sdk=%s\n' "$SDK"
printf 'abi=%s\n' "$ABI"
