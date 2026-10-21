#!/usr/bin/env bash
# Owner-authorized private Android debug beta. No release, root, keystore or publication.
set -euo pipefail
REPO="eggie-admin/LuHm-OS"
WORKFLOW="android-testing-build.yml"
MILESTONE="androidProposedDebug"
die() { printf 'LUHM_DEBUG_CAST=BLOCKED: %s\n' "$*" >&2; exit 2; }
command -v gh >/dev/null || die "GitHub CLI (gh) is required"
gh auth status >/dev/null 2>&1 || die "Run gh auth login first"
ACTOR="$(gh api user --jq .login)"
OWNER="$(gh api "repos/$REPO" --jq .owner.login)"
[[ "$ACTOR" == "$OWNER" ]] || die "Authenticate as repository owner ($OWNER), not $ACTOR"
SOURCE="$(gh api "repos/$REPO/branches/main" --jq .commit.sha)"
[[ "$SOURCE" =~ ^[a-f0-9]{40}$ ]] || die "Invalid current main SHA"
TASK="android-proposed-debug-${SOURCE:0:12}"
TAG="android-debug-${SOURCE:0:12}-$(date -u +%Y%m%d%H%M%S)"
echo "Owner: $ACTOR"
echo "Exact source: $SOURCE"
echo "Scope: PRIVATE disposable debug APK only; not a durable upgrade or F-Droid release."
echo "Build includes Google Drive Lum model download and may fail if assets are unavailable."
read -r -p 'Type cast to authorize one build: ' CAST
[[ "$CAST" == "cast" ]] || die "Not authorized"
START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
gh workflow run "$WORKFLOW" --repo "$REPO" --ref main \
  -f cast=cast -f milestoneId="$MILESTONE" -f taskId="$TASK" \
  -f sourceRef="$SOURCE" -f professorActor="$ACTOR" \
  -f castOriginRunId=direct -f releaseTag="$TAG" -f publishPrerelease=false
echo "Dispatched. Finding exact-source run..."
RUN=""
for _ in $(seq 1 30); do
  RUN="$(gh run list --repo "$REPO" --workflow "$WORKFLOW" --event workflow_dispatch \
    --limit 30 --json databaseId,headSha,createdAt \
    --jq ".[] | select(.headSha == \"$SOURCE\" and .createdAt >= \"$START\") | .databaseId" | head -n 1)"
  [[ -n "$RUN" ]] && break
  sleep 3
done
[[ -n "$RUN" ]] || die "Run not found; inspect GitHub Actions before retrying"
echo "Workflow: https://github.com/$REPO/actions/runs/$RUN"
gh run watch "$RUN" --repo "$REPO" --exit-status || die "Build failed; inspect run logs"
mkdir -p "build/android-debug-$RUN"
gh run download "$RUN" --repo "$REPO" --name "luhm-os-universal-samsung-cast-$MILESTONE" --dir "build/android-debug-$RUN"
APK="$(find "build/android-debug-$RUN" -type f -name '*.apk' -print -quit)"
[[ -n "$APK" && -s "$APK" ]] || die "Workflow completed but no APK artifact was downloaded"
echo "APK: $APK"
sha256sum "$APK"
echo "Confirm signature/identity in the workflow verification step before installing."
echo "DEBUG CAST BUILT: NOT INSTALLED ON SAMSUNG; NOT PRODUCTION SIGNED."
