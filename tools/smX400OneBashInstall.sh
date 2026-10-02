#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="eggie-admin/LuHm-OS"
SOURCE_REF="b25cfad18051ba2799b19e27f035487366b256c9"
TAG="android-web3-b25cfad1-r37000025238"
APK_NAME="LuHmOS-AndroidWeb3-${TAG}-arm64-v8a.apk"
SHA_NAME="${APK_NAME}.sha256"
EXPECTED_APK_SHA256="2a030cd15f6409464b9fc0fcd65f39f60635dcdabfdc298db3e25ae51ee4e3c8"
WORK="${TMPDIR:-$HOME/.cache}/luhm-one-bash-install"
INSTALLER="${WORK}/termuxVirginInstall.sh"

die() {
  printf 'LUHM_ONE_BASH_INSTALL=RED\nreason=%s\n' "$*" >&2
  exit 2
}

command -v curl >/dev/null || die "curl missing"
command -v bash >/dev/null || die "bash missing"

mkdir -p "$WORK"
rm -f "$WORK/$SHA_NAME" "$INSTALLER"

BASE="https://github.com/$REPO/releases/download/$TAG"
RAW="https://raw.githubusercontent.com/$REPO/$SOURCE_REF/tools/termuxVirginInstall.sh"

printf 'LuHm one-bash install\n'
printf 'sourceRef=%s\n' "$SOURCE_REF"
printf 'tag=%s\n' "$TAG"

curl -fL --retry 4 --retry-all-errors -o "$WORK/$SHA_NAME" "$BASE/$SHA_NAME" \
  || die "could not fetch pinned release checksum"

RELEASE_SHA="$(awk 'NR==1 {print $1}' "$WORK/$SHA_NAME")"
[ "$RELEASE_SHA" = "$EXPECTED_APK_SHA256" ] \
  || die "pinned release checksum drift: expected $EXPECTED_APK_SHA256 got $RELEASE_SHA"

curl -fL --retry 4 --retry-all-errors -o "$INSTALLER" "$RAW" \
  || die "could not fetch exact-source virgin installer"
chmod 0700 "$INSTALLER"

printf 'Pinned release checksum matched. Entering exact-source installer...\n'
exec bash "$INSTALLER" "$TAG" "$APK_NAME" "$SHA_NAME"
