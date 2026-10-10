#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROFESSOR_GARAGE_EXTERNAL:-$HOME/.cache/luhm/professor-garage/external/fallout-body-mutation}"
OPEN="$ROOT/open-source"
REF="$ROOT/reference-only"
RECEIPTS="$ROOT/receipts"
mkdir -p "$OPEN" "$REF" "$RECEIPTS"

clone_or_update() {
  local lane="$1"
  local name="$2"
  local url="$3"
  local branch="$4"
  local dest="$lane/$name"

  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" fetch --prune origin
    git -C "$dest" checkout "$branch"
    git -C "$dest" pull --ff-only origin "$branch"
  else
    git clone --filter=blob:none --branch "$branch" "$url" "$dest"
  fi

  local head
  head="$(git -C "$dest" rev-parse HEAD)"
  printf '%s %s %s\n' "$name" "$head" "$url" | tee "$RECEIPTS/$name.head.txt"
}

clone_or_update "$OPEN" bodySlideOutfitStudio https://github.com/ousnius/BodySlide-and-Outfit-Studio.git dev
clone_or_update "$OPEN" openCbpFo4 https://github.com/rickmccl/OpenCBP_FO4.git master

clone_or_update "$REF" looksMenuF4ee https://github.com/expired6978/F4SEPlugins.git master
clone_or_update "$REF" radMorphingRedux https://github.com/LenAnderson/LenA_RadMorphing.git develop
clone_or_update "$REF" fallout4TechnicalGuides https://github.com/Rhivens/Fallout4-Technical-Guides.git main
clone_or_update "$REF" f4se https://github.com/ianpatt/f4se.git master

cat <<EOF
FALLOUT_BODY_MUTATION_SOURCE_PULL=PASS
OPEN_SOURCE_LANE=$OPEN
REFERENCE_ONLY_LANE=$REF
RECEIPTS=$RECEIPTS
NEXUS_FILES_AUTODOWNLOADED=NO
PRODUCTION_ASSETS_PROMOTED=NO
CROWN_STATUS=STOP
EOF
