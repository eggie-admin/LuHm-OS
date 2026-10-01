#!/usr/bin/env bash
set -euo pipefail

repoRoot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repoRoot"

searchRoots=(
  agents
  doctrine
  plugins
  tools
)

printHits() {
  local label="$1"
  local pattern="$2"
  shift 2
  printf '\n[%s]\n' "$label"
  grep -RInE \
    --exclude-dir=.git \
    --exclude='*.png' \
    --exclude='*.jpg' \
    --exclude='*.jpeg' \
    --exclude='*.webp' \
    -- "$pattern" "$@" || true
}

printf 'goddessTriad grep inventory\n'
printf 'mode=readOnly\n'
printf 'mutation=false\n'
printf 'build=false\n'
printf 'cast=NOT_ISSUED\n'

printHits \
  'legacyDoctorAlias' \
  '\b(Dr\.?[[:space:]]*Nao|DrNao|doctorOni)\b' \
  "${searchRoots[@]}"

printHits \
  'legacySecretaryAlias' \
  '\b(Secretary[[:space:]]+Oni|secretaryOni|Fumi|fumiSecretaryOni)\b' \
  "${searchRoots[@]}"

printHits \
  'unsafeAuthorityLanguage' \
  '\b(self[- ]?crown|auto[- ]?crown|agent[[:space:]]+approved|build[[:space:]]+without[[:space:]]+cast|implicit[[:space:]]+cast)\b' \
  "${searchRoots[@]}"

printHits \
  'truthVibesLanguage' \
  '\b(probably|seems|should[[:space:]]+be|basically)[[:space:]]+(green|deployed|installed|merged|published|proven)\b' \
  "${searchRoots[@]}"

printf '\nNOTE=grep hits are locators, not proof; Urd adjudicates context.\n'
