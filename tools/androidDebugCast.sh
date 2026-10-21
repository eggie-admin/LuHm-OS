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
CURRENT="$(gh api "repos/$REPO/branches/main" --jq .commit.sha)"
[[ "$CURRENT" == "$SOURCE" ]] || die "main changed after approval; retry with a fresh source SHA"
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
RUN_SOURCE="$(gh run view "$RUN" --repo "$REPO" --json headSha --jq .headSha)"
[[ "$RUN_SOURCE" == "$SOURCE" ]] || die "Selected run has a different source commit"
gh run watch "$RUN" --repo "$REPO" --exit-status || die "Build failed; inspect run logs"
OUT="build/android-debug-$RUN"
[[ ! -e "$OUT" ]] || die "Destination already exists; refusing to mix build artifacts"
mkdir -p "$OUT"
gh run download "$RUN" --repo "$REPO" --name "luhm-os-universal-samsung-cast-$MILESTONE" --dir "$OUT"
APK="$(find "$OUT" -type f -name '*.apk' -print -quit)"
[[ "$(find "$OUT" -type f -name '*.apk' | wc -l)" -eq 1 ]] || die "Expected exactly one APK"
[[ -s "$OUT/sha256.txt" && -s "$OUT/signature.txt" && -s "$OUT/zipalign.txt" ]] || die "Missing APK verification receipts"
EXPECTED="$(awk -v file="$(basename "$APK")" '$2 == file || $2 == "build/android/"file {print $1}' "$OUT/sha256.txt")"
[[ "$EXPECTED" =~ ^[a-f0-9]{64}$ ]] || die "Missing or malformed expected APK SHA256"
[[ -n "$APK" && -s "$APK" ]] || die "Workflow completed but no APK artifact was downloaded"
ACTUAL="$(sha256sum "$APK" | cut -d " " -f1)"
[[ "$ACTUAL" == "$EXPECTED" ]] || die "APK SHA256 does not match workflow receipt"
echo "APK: $APK"
sha256sum "$APK"
echo "Workflow verification receipts present; APK checksum matched."
echo "DEBUG CAST BUILT: NOT INSTALLED ON SAMSUNG; NOT PRODUCTION SIGNED."
