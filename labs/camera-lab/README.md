# Hydra Camera Lab · Termux Prototype

A standalone Python 3 + browser UI for rooted or unrooted Android Termux: camera preview/snapshot/recording (only when the browser exposes a camera), read-only USB diagnostics, and optional local Ollama chat.

**Status:** experimental source, not a signed APK, not a macOS DMG, and not a proven Logitech USB capture driver. The public repository contains no private keys or child data. Use adult oversight for family use; an unfiltered local LLM is not automatically child-safe.

## Clone and run on the Samsung Galaxy Tab S10 Lite

```sh
pkg update
pkg install git python usbutils
git clone --depth 1 --branch feature/hydra-camera-lab-termux --single-branch https://github.com/eggie-admin/LuHm-OS.git
cd LuHm-OS/labs/camera-lab
bash probe-usb.sh
python server.py
```

Open **http://127.0.0.1:8765/** in Chrome on the **same tablet**. Press **Enable camera** and grant permission. You can take a snapshot or record a short WebM clip. No Python pip packages are required.

## Understanding the USB route

The Logitech C930e is a **USB UVC host input** when plugged into the tablet by USB-C OTG. The browser camera button uses Android Chrome's `getUserMedia`, which may expose only the tablet's **built-in** cameras. Seeing the tablet's selfie camera does **not** confirm external Logitech capture. For Logitech testing use the read-only diagnostic script and, if Chrome cannot see it, a separate Android UVC camera app. Root may help inspect devices, but root alone does not supply a missing UVC kernel driver.

USB gadget mode (Samsung presents itself to a PC as a webcam), USB storage mode (files), and USB host mode (Samsung receives Logitech video) are different jobs. USB Gadget Tool is a potential later gadget *output* module, not a ready-made USB camera *input* solution.

## Optional: Ollama on the local workstation

The server queries Ollama at `http://127.0.0.1:11434` by default. If Ollama runs on a workstation, open a second Termux session and establish an SSH tunnel:

```sh
pkg install openssh
ssh -N -L 11434:127.0.0.1:11434 USER@WORKSTATION
```

Back in the first session, with the tunnel open:

```sh
HYDRA_OLLAMA_MODEL=llama3.2:3b python server.py
```

Replace the model with one actually installed on the Ollama service. `OLLAMA_URL` may override the endpoint, but use only a trusted local/tunneled service. The prototype doesn't store transcripts, isn't a vetted safety filter, and doesn't use ChatGPT logins, browser automation, or OpenAI API keys.

## Diagnostic and security notes

`bash probe-usb.sh` only inspects devices/kernel and doesn't flash firmware, mount disks, switch gadget modes, or invoke `su`. Do not share USB serial numbers. The Python HTTP server binds **127.0.0.1 only** and rejects nonlocal Host headers and cross-origin POST requests. Don't change that to `0.0.0.0` for family use.

This is **not** a signed Android app. Signing a later Android WebView launcher requires an owner-controlled private signing key and a successful on-device camera/permission test. Keep signing credentials out of Git and separate from existing LuHm-OS release keys.

## First physical checks

1. With Logitech plugged in, run `bash probe-usb.sh`.
2. Tap Enable camera, select any offered sources, and identify whether any source is Logitech rather than the built-in camera.
3. Test snapshot/recording and the Ollama status indicator.
4. Report whether any `/dev/video*` node or UVC kernel support is visible. Avoid pasting unique device identifiers.

The target directory intentionally stays isolated from the LuHm-OS application and its signing/release pipelines.
