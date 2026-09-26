#!/usr/bin/env bash
set -euo pipefail
umask 077

if [ "${1:-}" != "--crown" ]; then
  echo 'Snapshot is a local mutation. Re-run with: kai-snapshot.sh --crown'
  exit 64
fi

STATE_DIR="${KAI_STATE_DIR:-$HOME/.local/state/kai9000}"
SNAPSHOT_DIR="$STATE_DIR/snapshots"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
WORK="$SNAPSHOT_DIR/snapshot-$STAMP"
ARCHIVE="$SNAPSHOT_DIR/snapshot-$STAMP.tar.gz"
mkdir -p "$WORK"

command -v termux-info >/dev/null 2>&1 && termux-info >"$WORK/termux-info.txt" 2>&1 || true
command -v dpkg-query >/dev/null 2>&1 && dpkg-query -W -f='${binary:Package}\t${Version}\n' >"$WORK/packages.tsv" || true
mkdir -p "$WORK/apt"
for f in "${PREFIX:-}/etc/apt/sources.list" "${PREFIX:-}/etc/apt/sources.list.d"/*.list; do
  [ -f "$f" ] || continue
  cp "$f" "$WORK/apt/$(basename "$f")"
done

# Local configuration snapshot only. Never upload this archive automatically.
if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/etc" ]; then
  tar -C "$PREFIX" -czf "$WORK/prefix-etc.tar.gz" etc
fi

{
  printf 'schema=kai9000.snapshot.v1\n'
  printf 'timestamp=%s\n' "$STAMP"
  printf 'scope=local_termux_config_and_package_manifest\n'
  printf 'auto_upload=false\n'
  printf 'human_authority=Professor\n'
} >"$WORK/snapshot.env"

( cd "$WORK" && sha256sum * 2>/dev/null || true ) >"$WORK/files.sha256"
tar -C "$SNAPSHOT_DIR" -czf "$ARCHIVE" "snapshot-$STAMP"
sha256sum "$ARCHIVE" >"$SNAPSHOT_DIR/snapshot-$STAMP.sha256"
rm -rf "$WORK"

printf 'SNAPSHOT GREEN\n%s\n' "$ARCHIVE"
printf 'Receipt: %s\n' "$SNAPSHOT_DIR/snapshot-$STAMP.sha256"
