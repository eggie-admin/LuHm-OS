#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
GARAGE_CACHE="${PROFESSOR_GARAGE_CACHE:-$HOME/.cache/luhm/professor-garage}"
mkdir -p "$GARAGE_CACHE"/{frames,audio,repairs,contact-sheets,receipts,tmp}

if command -v sudo >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build clang gdb pkg-config \
    python3-dev python3-venv python3-pip pipx \
    ffmpeg imagemagick mediainfo libimage-exiftool-perl \
    blender gimp \
    jq sqlite3 bc tree parallel \
    rsync rclone openssh-client git-lfs curl wget unzip zip \
    shellcheck
  sudo apt-get clean
  sudo rm -rf /var/lib/apt/lists/*
fi

git lfs install --skip-repo || true

python3 tools/professorGarageAudit.py --runtime

cat <<'EOF'
PROFESSOR_GARAGE=READY_CANDIDATE
CROWN_STATUS=STOP
GODOT=PINNED_INSTALL_AVAILABLE_VIA_tools/professorGarageInstallGodot.py
NOTE=Codespace setup proves the workshop toolchain only. It does not prove provider entitlement, Drive credentials, deployment, publication, or Crown approval.
EOF
