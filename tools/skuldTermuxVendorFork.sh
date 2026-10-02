#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

OWNER="${1:-eggie-admin}"
ROOT="${HOME}/luhm-vendor"
mkdir -p "$ROOT"

command -v gh >/dev/null || { echo "GitHub CLI required" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "Authenticate gh first" >&2; exit 2; }

repos=(
  "termux/termux-app"
  "termux/termux-api"
  "termux/termux-api-package"
  "termux/termux-packages"
  "termux/proot-distro"
  "termux/termux-tools"
)

printf 'Skuld Termux vendor fork lane\n'
printf 'Owner: %s\n' "$OWNER"

for upstream in "${repos[@]}"; do
  name="${upstream#*/}"
  target="$OWNER/$name"

  if gh repo view "$target" >/dev/null 2>&1; then
    printf 'EXISTS %s\n' "$target"
  else
    printf 'FORK %s -> %s\n' "$upstream" "$target"
    gh repo fork "$upstream" --clone=false
  fi

  if [ ! -d "$ROOT/$name/.git" ]; then
    git clone --filter=blob:none "https://github.com/$target.git" "$ROOT/$name"
  fi

  git -C "$ROOT/$name" remote get-url upstream >/dev/null 2>&1 \
    || git -C "$ROOT/$name" remote add upstream "https://github.com/$upstream.git"

  git -C "$ROOT/$name" fetch --prune upstream master
  printf '%s %s\n' "$upstream" "$(git -C "$ROOT/$name" rev-parse upstream/master)"
done

printf 'SKULD_TERMUX_VENDOR_FORK=GREEN_SOURCE_SYNC\n'
printf 'runtimeAuthority=false\n'
printf 'crownStatus=stop\n'
