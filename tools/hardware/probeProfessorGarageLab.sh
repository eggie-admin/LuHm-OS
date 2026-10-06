#!/usr/bin/env bash
set -uo pipefail

section() { printf '\n===== %s =====\n' "$1"; }
run() {
  printf '\n$'
  printf ' %q' "$@"
  printf '\n'
  "$@" 2>&1 || printf '[VERIFY] command failed or unavailable: %s\n' "$*"
}
maybe() {
  command -v "$1" >/dev/null 2>&1 || { printf '[VERIFY] missing command: %s\n' "$1"; return 0; }
  run "$@"
}

printf 'LUHM_PROFESSOR_GARAGE_LAB_PROBE=v1\n'
printf 'MODE=READ_ONLY\n'
printf 'UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

section "host"
run uname -a
maybe hostnamectl
maybe lsb_release -a
maybe cat /etc/os-release
maybe python3 --version
maybe git --version

section "cpu-memory"
maybe lscpu
maybe free -h

section "gpu-pci"
maybe lspci -nnk
maybe vulkaninfo --summary
maybe glxinfo -B

section "usb"
maybe lsusb
if command -v lsusb >/dev/null 2>&1; then run lsusb -t; fi

section "camera"
maybe v4l2-ctl --list-devices
maybe libcamera-hello --list-cameras
if command -v ffmpeg >/dev/null 2>&1; then run ffmpeg -hide_banner -devices; fi

section "scanner"
maybe sane-find-scanner
maybe scanimage -L

section "android-forge"
maybe adb version
maybe java -version
maybe gradle --version

section "android-device"
if command -v getprop >/dev/null 2>&1; then
  run getprop ro.product.model
  run getprop ro.build.version.release
  run getprop ro.build.version.sdk
  run getprop ro.build.fingerprint
  run uname -a
fi
if command -v termux-camera-info >/dev/null 2>&1; then run termux-camera-info; fi
if command -v termux-usb >/dev/null 2>&1; then run termux-usb -l; fi

section "boundary"
printf 'Codespaces/CI output is toolchain proof only, never physical USB/GPU/camera/scanner proof.\n'
printf 'A custom kernel build is not proof that any physical host booted it.\n'
printf 'UNKNOWN remains VERIFY until an exact receipt exists.\n'
