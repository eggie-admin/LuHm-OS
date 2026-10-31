# LuHm-OS / Project Premonition: rootless Samsung CAST studio

**Status:** proposed branch preview, no signed APK or tablet proof. Distinct from the existing rooted legacy `tools/termuxCastReleaseInstall.sh` and `tools/termuxVirginInstall.sh`. Crown STOP.

## What works (source and CI boundaries)

A local browser cockpit, with original adult goth-oni vector art, three local visual lighting themes, a bounded character/dialogue rehearsal, HTML5/CSS and JavaScript, one **Python standard-library** server and an on-device SQLite3 database. The server listens **only on 127.0.0.1:8787**, denies browser cross-origin writes, uses prepared SQL and revision-checked transactions, no CDN, no cloud model calls or vendor installs. It never touches firmware or needs su. Local Python tests can exercise this functionality in CI, but **Samsung browser/touch/install proof still needs the actual tablet**.

## Run from unrooted Termux (after installing Termux from its official F-Droid/GitHub source)

For this draft only, choose the specific PR head. **Never run an unreviewed third-party script or paste secrets into a public repo**. This command sequence requires user-installed Termux and internet for the initial Git checkout:

```sh
pkg update
pkg install git python
cd ~
git clone https://github.com/eggie-admin/LuHm-OS.git
cd LuHm-OS
git fetch origin pull/463/head:hydra-cast-candidate
git switch hydra-cast-candidate
# Confirm the commit shown in GitHub PR #463 is the commit checked out:
git rev-parse HEAD
bash tools/termuxRootlessCast.sh check
bash tools/termuxRootlessCast.sh start
```

In a separate Samsung Chrome browser tab, open **http://127.0.0.1:8787/**. Browser menu -> **Add to Home screen** creates an app-like shortcut where offered. **This is a locally served web cockpit, not an independently installed APK; the Termux process must remain running to use it.** Optional standalone-display behavior varies by Chrome version and SVG icon support. No self-signed certificate or network port forwarding is required. Do not expose 8787 to Wi-Fi or tunnels.

## Shipping a proper Android APK later

The existing `.github/workflows/samsung-lite-signed-beta.yml` is the protected owner-dispatched route for ARM64/Godot, Android SDK 36, original procedural asset profile, signer verification and F-Droid candidate staging. It requires the exact `main` SHA, owner-held keystore and explicit CAST. Source branch CI success alone **cannot** produce or authorize a signed package. The old rooted scripts explicitly require su and must **not** be used on the unrooted target. Do not overwrite Android app data, delete prior installs, or automatically sideload an APK. The Android system package installer requires user approval when installing through a normal unrooted app.

## 4x4 → 36 and AI benchmarks

The 16-cell foundation maps source/policy/test/owner against authority/runtime/privacy/media. The 36 expansion gates span six domains: Canon, engines, Python, SQLite, AI evaluation, Android. This is a **36-gate contract inventory**, not 36 actual hardware benchmarks. The corresponding source audit is `tools/rootlessCast36Audit.py`, and HTTP/SQLite functionality has explicit local tests. Cross-vendor evaluations need a common private dataset and separate consent/credentials/cost and version stamps; relevant open frameworks include UK AISI Inspect, SWE-bench Verified, LiveCodeBench, OSWorld and Terminal-Bench. The OpenAI hosted Evals API is in deprecation as of late 2026; do not build a new hard dependency on it. New remote AI provider calls and adult-specific character chat require explicit approved plugin/task-scoped credentials and age/content policy; the present browser art and authored dialogue are only a companion **prototype**, not a live ChatGPT plugin.

## SQL boundary

SQLite lives inside the Termux **app sandbox**, not firmware. WAL improves bounded concurrent local access, and transactional revision checks prevent stale story choices. No Android root, bootloader unlock, system partition writes, SELinux bypass, or unsupported firmware database access is needed or authorized.

The source-only checks are:

```sh
python3 -m unittest tests.testRootlessCast36 tests.testRootlessCastCockpit -v
python3 -m tools.rootlessCastCockpit --check
python3 tools/rootlessCast36Audit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/luhm-rootless-cast-36.json
```
