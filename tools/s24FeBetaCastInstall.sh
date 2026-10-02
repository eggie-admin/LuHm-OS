#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="eggie-admin/LuHm-OS"
BRANCH="beta/yumeArtChatV1-20261002"
WORKFLOW="android-testing-build.yml"
MILESTONE="androidWeb3Cockpit"
CAST_WORD="${1:-}"
TAG="${2:-}"
TASK_ID="${3:-s24fe-beta-cast}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

die() {
  printf 'LUHM_S24FE_BETA_CAST=RED\nreason=%s\n' "$*" >&2
  exit 2
}

[ "$CAST_WORD" = "cast" ] || die "first argument must be the exact Professor word: cast"
command -v gh >/dev/null || die "GitHub CLI missing"
command -v git >/dev/null || die "git missing"
gh auth status >/dev/null 2>&1 || die "GitHub CLI is not authenticated"

PROFESSOR_ACTOR="$(gh api user --jq '.login')"
[ -n "$PROFESSOR_ACTOR" ] || die "could not resolve authenticated GitHub actor"

SOURCE_REF="$(gh api "repos/$REPO/branches/$BRANCH" --jq '.commit.sha')" \
  || die "could not resolve beta branch SHA"
[ -n "$SOURCE_REF" ] || die "beta source SHA empty"

SHORT_REF="${SOURCE_REF:0:8}"
if [ -z "$TAG" ]; then
  TAG="s24fe-beta-${SHORT_REF}"
fi

case "$TAG" in
  *[!A-Za-z0-9._-]*|'') die "release tag may contain only A-Z a-z 0-9 . _ -" ;;
esac

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  die "release tag already exists; choose a fresh tag or update the beta source"
fi

printf 'Professor: %s\n' "$PROFESSOR_ACTOR"
printf 'Beta branch: %s\n' "$BRANCH"
printf 'Exact source: %s\n' "$SOURCE_REF"
printf 'Release tag: %s\n' "$TAG"

DISPATCH_AFTER="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

gh workflow run "$WORKFLOW" \
  --repo "$REPO" \
  --ref "$BRANCH" \
  -f cast=cast \
  -f milestoneId="$MILESTONE" \
  -f taskId="$TASK_ID" \
  -f sourceRef="$SOURCE_REF" \
  -f professorActor="$PROFESSOR_ACTOR" \
  -f castOriginRunId=direct \
  -f releaseTag="$TAG" \
  -f publishPrerelease=true \
  || die "workflow dispatch failed"

printf 'Resolving exact workflow run...\n'
RUN_ID=""
for _ in $(seq 1 40); do
  RUN_ID="$(gh run list \
    --repo "$REPO" \
    --workflow "$WORKFLOW" \
    --branch "$BRANCH" \
    --event workflow_dispatch \
    --limit 30 \
    --json databaseId,headSha,status,createdAt \
    --jq ".[] | select(.headSha == \"$SOURCE_REF\" and .createdAt >= \"$DISPATCH_AFTER\") | .databaseId" \
    | head -n 1)"
  [ -n "$RUN_ID" ] && break
  sleep 2
done
[ -n "$RUN_ID" ] || die "could not resolve dispatched exact-source run"

printf 'Watching CAST run %s...\n' "$RUN_ID"
gh run watch "$RUN_ID" --repo "$REPO" --exit-status \
  || die "Android beta CAST workflow failed"

printf 'Waiting for prerelease %s...\n' "$TAG"
for _ in $(seq 1 40); do
  if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1 \
  || die "workflow succeeded but prerelease is not visible"

printf 'Prerelease visible. Starting S24 FE installer...\n'
exec bash "$SCRIPT_DIR/s24FeBetaInstall.sh" "$TAG"
