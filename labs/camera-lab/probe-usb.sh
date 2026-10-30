#!/usr/bin/env bash
# Read-only diagnostics. Never flashes, mounts, roots, or switches device modes.
echo '=== HYDRA USB / ROOT PROBE ==='
date -u 2>/dev/null || :
echo '[Identity]'; id 2>/dev/null || :
echo '[Kernel]'; uname -a 2>/dev/null || :
echo '[USB devices]'; (command -v lsusb >/dev/null && lsusb) || echo 'Install usbutils for lsusb'
echo '[V4L2 device nodes]'; ls -l /dev/video* 2>/dev/null || echo 'No video nodes accessible'
echo '[Gadget config paths]'; ls -ld /config/usb_gadget /sys/kernel/config/usb_gadget 2>/dev/null || :
echo '[Possible UVC kernel support]'
for p in /proc/config.gz /vendor/etc/config.gz; do
  if [ -r "$p" ]; then
    gzip -dc "$p" 2>/dev/null | grep -Ei 'CONFIG_USB_VIDEO_CLASS|CONFIG_MEDIA_USB_SUPPORT|CONFIG_USB_CONFIGFS_F_UVC|CONFIG_USB_F_UVC' || :
  fi
done
echo '[FFmpeg capture devices, if present]'
if command -v ffmpeg >/dev/null; then
  ffmpeg -hide_banner -devices 2>&1 | grep -Ei 'v4l2|video4linux' || echo 'No V4L2 input shown'
fi
echo '[UVC sysfs driver]'; ls -ld /sys/bus/usb/drivers/uvcvideo 2>/dev/null || :
echo '[End: no changes made. Do not share unique device serials.]'
