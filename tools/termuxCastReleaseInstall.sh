#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="eggie-admin/LuHm-OS"
WORKFLOW="android-testing-build.yml"
MILESTONE="androidWeb3Cockpit"
CAST_WORD="${1:-}"
TAG="${2:-android-web3-0.1.0-rc1}"
TASK_ID="${3:-android-web3-cockpit-cast-001}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

die() {
  printf 'LUHM_CAST_RELEASE_INSTALL=RED\nreason=%s\n' "$*" >&2
  exit 2
}

[ "$CAST_WORD" = "cast" ] || die "first argument must be the exact Professor word: cast"
command -v gh >/dev/null || die "GitHub CLI missing; install/authenticate gh in Termux first"
command -v git >/dev/null || die "git missing"
command -v su >/dev/null || die "root su missing"
gh auth status >/dev/null 2>&1 || die "GitHub CLI is not authenticated"

case "$TAG" in
  *[!A-Za-z0-9._-]*|'') die "release tag may contain only A-Z a-z 0-9 . _ -" ;;
esac

SOURCE_REF="$(gh api "repos/$REPO/branches/main" --jq '.commit.sha')"   || die "could not resolve canonical main"
[ -n "$SOURCE_REF" ] || die "canonical main SHA empty"

printf 'CAST source: %s\n' "$SOURCE_REF"
printf 'Release tag: %s\n' "$TAG"

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  die "release tag already exists; refusing overwrite"
fi

gh workflow run "$WORKFLOW"   --repo "$REPO"   --ref main   -f cast=cast   -f milestoneId="$MILESTONE"   -f taskId="$TASK_ID"   -f sourceRef="$SOURCE_REF"   -f releaseTag="$TAG"   -f publishPrerelease=true   || die "workflow dispatch failed"

printf 'Waiting for exact workflow run to appear...\n'
RUN_ID=""
for _ in $(seq 1 30); do
  RUN_ID="$(gh run list     --repo "$REPO"     --workflow "$WORKFLOW"     --event workflow_dispatch     --limit 20     --json databaseId,headSha,status,createdAt     --jq ".[] | select(.headSha == \"$SOURCE_REF\") | .databaseId"     | head -n 1)"
  [ -n "$RUN_ID" ] && break
  sleep 2
done
[ -n "$RUN_ID" ] || die "could not resolve dispatched exact-source run"

printf 'Watching run %s...\n' "$RUN_ID"
gh run watch "$RUN_ID" --repo "$REPO" --exit-status   || die "CAST build/release workflow failed"

printf 'Waiting for GitHub prerelease %s...\n' "$TAG"
for _ in $(seq 1 30); do
  if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1   || die "workflow succeeded but prerelease is not visible"

printf 'GitHub prerelease is visible. Starting rooted virgin install...\n'
exec "$SCRIPT_DIR/termuxVirginInstall.sh" "$TAG"
