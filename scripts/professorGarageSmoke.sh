#!/usr/bin/env bash
# Read-only, repeatable proof of the image's actual installed toolchain.
set -euo pipefail
source /etc/os-release
[[ "${ID:-}" == ubuntu && "${VERSION_ID:-}" == 26.04 ]] || {
  echo 'RED_UBUNTU_2604_REQUIRED' >&2; exit 1;
}
required=(python3 git node npm ffmpeg blender gimp godot certbot nginx mariadb mariadbd xvfb-run)
for binary in "${required[@]}"; do
  command -v "$binary" >/dev/null || { echo "RED_MISSING_$binary" >&2; exit 1; }
done
test -f /etc/mysql/mariadb.conf.d/99-luhm-private.cnf
grep -q '^skip-networking=1$' /etc/mysql/mariadb.conf.d/99-luhm-private.cnf
python3 --version
node --version
npm --version
ffmpeg -hide_banner -version | head -n 1
blender --version | head -n 1
gimp --version
godot --headless --version
certbot --version
mariadb --version
nginx -v 2>&1
printf 'GREEN_PROFESSOR_BASEMENT_TOOLCHAIN_INSTALLED_AND_SQL_NETWORK_DISABLED\n'
printf 'NOT_PROVEN: Codespace persistence, server daemon readiness, plugin cockpit, GABE, real GPU, public deployment\n'
