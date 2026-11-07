#!/usr/bin/env bash
# LuHm CAST Bridge private host transfer. NO deletions, NO release authority.
set -Eeuo pipefail
umask 077

mode="${1:---dry-run}"
if [[ "$mode" != "--dry-run" && "$mode" != "--apply" ]]; then
  echo "Usage: luhmCanonSync.sh [--dry-run|--apply]" >&2
  exit 64
fi
need() { command -v "$1" >/dev/null || { echo "MISSING_TOOL=$1" >&2; exit 69; }; }
need rsync
need python3
need flock
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_dir="$(cd -- "$script_dir/.." && pwd -P)"
source_ref="$(git -C "$repo_dir" rev-parse HEAD 2>/dev/null || true)"
if [[ ! "$source_ref" =~ ^[a-f0-9]{40}$ ]]; then
  echo "NO_EXACT_SOURCE_REF" >&2
  exit 65
fi

# Configure these paths in a private, mode-0600 host EnvironmentFile.
source_dir="${LUHM_INGRESS_DIR:-$HOME/LuHmInbox}"
stage_dir="${LUHM_STAGING_DIR:-$HOME/LuHmState/staging}"
state_dir="${LUHM_STATE_DIR:-$HOME/LuHmState/state}"
remote_source="${LUHM_RSYNC_SOURCE:-}"
remote_dest="${LUHM_RCLONE_DEST:-}"

safe_path() {
  local raw="$1"
  if [[ "$raw" != /* || "$raw" == "/" || "$raw" == "$HOME" || "$raw" == *"/../"* || "$raw" == *"/./"* ]]; then
    echo "UNSAFE_LOCAL_PATH" >&2; exit 65
  fi
}
safe_path "$source_dir"; safe_path "$stage_dir"; safe_path "$state_dir"
source_dir="$(realpath -m -- "$source_dir")"
stage_dir="$(realpath -m -- "$stage_dir")"
state_dir="$(realpath -m -- "$state_dir")"
for val in "$source_dir" "$stage_dir" "$state_dir"; do
  if [[ "$val" == "/" || "$val" == "$HOME" ]]; then
    echo "UNSAFE_RESOLVED_PATH" >&2; exit 65
  fi
done
if [[ "$stage_dir" == "$source_dir" || "$stage_dir" == "$source_dir/"* ||
      "$source_dir" == "$stage_dir/"* || "$state_dir" == "$stage_dir/"* ]]; then
  echo "OVERLAPPING_SYNC_ROOTS" >&2; exit 65
fi

if [[ -n "$remote_source" ]]; then
  # Strict SSH source syntax. Keys and pinned host identities live outside Git.
  if [[ ! "$remote_source" =~ ^[A-Za-z_][A-Za-z0-9_-]*@[A-Za-z0-9._-]+:/[A-Za-z0-9_./-]+/$ ||
        "$remote_source" == *".."* ]]; then
    echo "UNSAFE_REMOTE_SOURCE" >&2; exit 65
  fi
  input="$remote_source"
else
  [[ -d "$source_dir" && ! -L "$source_dir" ]] || { echo "INGRESS_MISSING" >&2; exit 66; }
  input="$source_dir/"
fi

if [[ "$mode" == "--apply" ]]; then
  [[ "${LUHM_SYNC_ARMED:-NO}" == "YES" ]] || { echo "NOT_ARMED" >&2; exit 78; }
  need rclone
  # Deliberately restrictive destination; never mirror an entire Drive root.
  if [[ ! "$remote_dest" =~ ^[A-Za-z0-9_-]+:LuHm-OS-Private(/[A-Za-z0-9_-]+)*$ ||
        "$remote_dest" == *".."* ]]; then
    echo "UNSAFE_DRIVE_DESTINATION" >&2; exit 65
  fi
fi

mkdir -p -- "$stage_dir/data" "$state_dir"
chmod 700 "$stage_dir" "$stage_dir/data" "$state_dir"
exec 9>"$state_dir/canon-sync.lock"
flock -n 9 || { echo "SYNC_ALREADY_ACTIVE" >&2; exit 75; }

rsync_flags=(
  --archive --checksum --no-links --no-owner --no-group
  --no-perms --no-devices --no-specials --partial --delay-updates
  --exclude=.git/ --exclude=.cache/ --exclude=node_modules/
  --exclude=__pycache__/ --exclude='*.tmp' --exclude='*.part'
  --exclude='*.partial' --exclude='*.crdownload'
  --exclude='.ssh/' --exclude='secrets/' --exclude='private-keys/'
  --exclude='.env' --exclude='.env.*' --exclude='*.pem'
  --exclude='*.key' --exclude='*.p12' --exclude='*.pfx'
  --exclude='*.keystore' --exclude='id_rsa' --exclude='id_ed25519'
  --exclude='*credentials*.json' --exclude='*token*.json'
  --quiet
)
if [[ -n "$remote_source" ]]; then
  rsync_flags+=(--rsh="ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=15")
fi
if [[ "$mode" == "--dry-run" ]]; then
  rsync --dry-run "${rsync_flags[@]}" -- "$input" "$stage_dir/data/"
  echo "CANON_SYNC_DRY_RUN_GREEN noTransfer=true noDelete=true"
  exit 0
fi

# Append/copy only: never add --delete, sync, move, purge, or prune.
rsync "${rsync_flags[@]}" -- "$input" "$stage_dir/data/"
stamp="$(date -u +%Y%m%dT%H%M%SZ)-$$"
index="$state_dir/index-$stamp.json"
python3 "$repo_dir/tools/canonTransferIndex.py" "$stage_dir/data" \
  --out "$index" --source-ref "$source_ref"

rclone_flags=(
  --checksum --immutable --transfers 2 --checkers 2
  --tpslimit 2 --tpslimit-burst 2 --retries 5
  --low-level-retries 10 --log-level ERROR
)
rclone copy "$stage_dir/data" "$remote_dest" "${rclone_flags[@]}"
# Mandatory proof: source files exist in Drive and match by hash when available.
rclone check "$stage_dir/data" "$remote_dest" --one-way --checksum --checkers 2 --log-level ERROR
# Mark only the exact private manifest whose transferred files passed remote check.
python3 - "$index" <<'PY'
import json
import os
import sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
if data["status"] != "LOCAL_VERIFIED_PENDING_REMOTE_CHECK":
    raise SystemExit("UNEXPECTED_MANIFEST_STATE")
data["status"] = "REMOTE_HASH_CHECK_VERIFIED"
temporary = path.with_suffix(".writing")
temporary.write_text(json.dumps(data, indent=2) + "\\n", encoding="utf-8")
os.chmod(temporary, 0o600)
temporary.replace(path)
PY
rclone copyto "$index" "$remote_dest/_control/index-$stamp.json" \
  --immutable --log-level ERROR
echo "CANON_SYNC_VERIFIED sourceRef=$source_ref transfer=copy-only delete=false crown=STOP"
