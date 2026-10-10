#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROFESSOR_GARAGE_EXTERNAL:-$HOME/.cache/luhm/professor-garage/external/re-engine-modder}"
OPEN="$ROOT/open-source"
REF="$ROOT/reference-only"
RECEIPTS="$ROOT/receipts"
mkdir -p "$OPEN" "$REF" "$RECEIPTS"

clone_exact() {
  local lane="$1"
  local name="$2"
  local url="$3"
  local branch="$4"
  local expected="$5"
  local dest="$lane/$name"

  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" fetch --depth 1 origin "$branch"
    git -C "$dest" checkout --detach FETCH_HEAD
  else
    git clone --depth 1 --filter=blob:none --branch "$branch" "$url" "$dest"
  fi

  local head
  head="$(git -C "$dest" rev-parse HEAD)"
  test "$head" = "$expected"
  printf '%s %s %s\n' "$name" "$head" "$url" | tee "$RECEIPTS/$name.head.txt"
}

clone_exact "$OPEN" reFramework https://github.com/praydog/REFramework.git master d1461375aee4ec3f313170f8eaad12064eb542d9
clone_exact "$OPEN" reRsz https://github.com/alphazolam/RE_RSZ.git main 871a1d5c4c7b81c60c966d73ee63f4c4413ab56e
clone_exact "$REF" reMeshNoesisPlugin https://github.com/alphazolam/fmt_RE_MESH-Noesis-Plugin.git main 7950d27bf521f90bf250a9d43239957018d2a294

cat <<EOF
RE_ENGINE_MODDER_SOURCE_PULL=PASS
OPEN_SOURCE_LANE=$OPEN
REFERENCE_ONLY_LANE=$REF
RECEIPTS=$RECEIPTS
NEXUS_BINARIES_DOWNLOADED=NO
CAPCOM_ASSETS_PROMOTED=NO
CROWN_STATUS=STOP
EOF
