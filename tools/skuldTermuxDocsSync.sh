#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${HOME}/luhm-vendor-docs/termux"
mkdir -p "$ROOT"

fetch() {
  local rel="$1" url="$2"
  local out="$ROOT/$rel"
  mkdir -p "$(dirname "$out")"
  curl -fL --retry 4 --retry-all-errors -o "$out" "$url"
  sha256sum "$out"
}

fetch "termux-app/README.md" "https://raw.githubusercontent.com/termux/termux-app/master/README.md"
fetch "termux-app/debug_build.yml" "https://raw.githubusercontent.com/termux/termux-app/master/.github/workflows/debug_build.yml"
fetch "termux-api/README.md" "https://raw.githubusercontent.com/termux/termux-api/master/README.md"
fetch "termux-packages/README.md" "https://raw.githubusercontent.com/termux/termux-packages/master/README.md"
fetch "proot-distro/README.md" "https://raw.githubusercontent.com/termux/proot-distro/master/README.md"

cat > "$ROOT/README.quickstart.txt" <<'TXT'
LuHm Termux vendor docs cache

App lane:
- Keep Termux + plugins in one signing/source family.
- GitHub preview builds are per-commit Actions artifacts.
- Android 7+ uses apt-android-7; S24 FE prefers arm64-v8a.

Core:
  pkg update
  pkg upgrade
  termux-info

PRoot:
  pkg install proot-distro
  proot-distro search ubuntu
  proot-distro install ubuntu:24.04
  proot-distro login ubuntu

Mirrors:
  termux-change-repo

This cache is reference material, not LuHm source authority.
TXT

printf 'SKULD_TERMUX_DOCS_SYNC=GREEN_REFERENCE_CACHE\n'
printf 'root=%s\n' "$ROOT"
