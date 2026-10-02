#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "RED_REMOTE_FORGE_BOOTSTRAP_OUTSIDE_CI: this bootstrap is GitHub Actions only" >&2
  exit 2
fi

export DEBIAN_FRONTEND=noninteractive
export CMAKE_GENERATOR=Ninja
export NINJA_STATUS='[%f/%t %o/sec] '

required=(
  build-essential
  ninja-build
  cmake
  pkg-config
  ccache
  curl
  git
  jq
  unzip
  zip
  python3
  python3-pip
)

sudo apt-get update -y
sudo apt-get install -y --no-install-recommends "${required[@]}"

command -v gcc >/dev/null
command -v g++ >/dev/null
command -v make >/dev/null
command -v ninja >/dev/null
command -v cmake >/dev/null
command -v ccache >/dev/null
command -v python3 >/dev/null
command -v git >/dev/null
command -v jq >/dev/null

mkdir -p build/forge
{
  echo "runner=${ImageOS:-unknown}"
  echo "gcc=$(gcc --version | head -n1)"
  echo "gxx=$(g++ --version | head -n1)"
  echo "cmake=$(cmake --version | head -n1)"
  echo "ninja=$(ninja --version)"
  echo "ccache=$(ccache --version | head -n1)"
  echo "python=$(python3 --version)"
  echo "git=$(git --version)"
} | tee build/forge/toolchainReceipt.txt
