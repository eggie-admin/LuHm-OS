#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
umask 077

EXPECTED_BASE="cb0f53c9dfc8aedf6852a77e60f41634f8d18bab"
MUTATION_BRANCH="candidate/secure-folder-shizuku-termux-20261001"
REPO_URL="https://github.com/eggie-admin/LuHm-OS.git"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="${TMPDIR:-${PREFIX:-/data/data/com.termux/files/usr}/tmp}/luhm-secure-folder-bootstrap-${STAMP}"

die(){ printf 'RED: %s\n' "$*" >&2; exit 1; }
note(){ printf ':: %s\n' "$*"; }

[[ "${PREFIX:-}" == *"termux"* || "${PREFIX:-}" == *"/com.termux/"* ]] || die "Run this in Termux."

UID_NOW="$(id -u)"
ANDROID_USER_ID=$(( UID_NOW / 100000 ))
note "Termux uid=$UID_NOW androidUserId=$ANDROID_USER_ID"

if ! command -v git >/dev/null 2>&1; then
  pkg install -y git
fi

rm -rf "$TMP"
git clone --filter=blob:none --no-checkout "$REPO_URL" "$TMP/repo"
git -C "$TMP/repo" fetch --prune origin \
  "+refs/heads/${MUTATION_BRANCH}:refs/remotes/origin/${MUTATION_BRANCH}"

HEAD_SHA="$(git -C "$TMP/repo" rev-parse "refs/remotes/origin/${MUTATION_BRANCH}")"
BASE_SHA="$(git -C "$TMP/repo" merge-base "$EXPECTED_BASE" "$HEAD_SHA")"
[[ "$BASE_SHA" == "$EXPECTED_BASE" ]] || die "Secure Folder mutation is not descended from reviewed roleplay base $EXPECTED_BASE."

git -C "$TMP/repo" checkout --detach "$HEAD_SHA"
PROBE="$TMP/repo/scripts/termux/luhm-secure-folder-shizuku-probe.sh"
INSTALLER="$TMP/repo/scripts/termux/install-luhm-dev.sh"

[[ -s "$PROBE" && -s "$INSTALLER" ]] || die "Mutation branch missing Secure Folder scripts."
bash -n "$PROBE"
bash -n "$INSTALLER"
chmod 700 "$PROBE" "$INSTALLER"

note "Capturing Secure Folder/Shizuku diagnostics"
mkdir -p "$HOME/.luhm/receipts"
"$PROBE" "$HOME/.luhm/receipts/secure-folder-preflight-${STAMP}.json"

note "Starting explicit Secure Folder experimental install"
export LUHM_SECURE_FOLDER_EXPERIMENT=1
export LUHM_SECURE_FOLDER_PROBE="$PROBE"
exec bash "$INSTALLER"
