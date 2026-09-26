#!/usr/bin/env bash
set -euo pipefail
umask 077

STATE_DIR="${KAI_STATE_DIR:-$HOME/.local/state/kai9000}"
PLAN_DIR="$STATE_DIR/update-plans"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
PLAN="$PLAN_DIR/update-plan-$STAMP.txt"
mkdir -p "$PLAN_DIR"

refresh=false
crown=false
for arg in "$@"; do
  [ "$arg" = '--refresh' ] && refresh=true
  [ "$arg" = '--crown' ] && crown=true
done

if $refresh && ! $crown; then
  echo 'Refreshing package metadata is a mutation. Use: kai-update-plan.sh --refresh --crown'
  exit 64
fi

{
  echo 'KAI 9000 // STAGED UPDATE PLAN'
  echo "timestamp=$STAMP"
  echo 'apply_upgrades=false'
  echo 'source_migration=false'
  echo
  echo '## current packages'
  command -v dpkg-query >/dev/null 2>&1 && dpkg-query -W -f='${binary:Package}\t${Version}\n' || true
  echo
  echo '## configured repositories'
  for f in "${PREFIX:-}/etc/apt/sources.list" "${PREFIX:-}/etc/apt/sources.list.d"/*.list; do
    [ -f "$f" ] || continue
    echo "### $f"
    cat "$f"
  done
} >"$PLAN"

if $refresh; then
  echo 'Crown-approved metadata refresh only. No package upgrade will be run.' | tee -a "$PLAN"
  pkg update 2>&1 | tee -a "$PLAN"
fi

{
  echo
  echo '## proposed upgrades from current metadata'
  if command -v apt >/dev/null 2>&1; then apt list --upgradable 2>/dev/null || true; elif command -v pkg >/dev/null 2>&1; then pkg list-upgradable 2>/dev/null || true; fi
} >>"$PLAN"

sha256sum "$PLAN" >"$PLAN.sha256"
printf 'UPDATE PLAN READY. NO UPGRADES APPLIED.\n%s\n' "$PLAN"
