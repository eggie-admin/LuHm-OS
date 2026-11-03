# KAI9000 Samsung Lite local Termux:X11 desktop (proposed)

Goal: owner-controlled, unrooted Termux:X11 desktop on Samsung Lite Android tablet. Retain the stock Samsung kernel and Android permissions. This is not a second Android image, a signed LuHm APK, a rooted Linux chroot, a public web service, or a deployed 3D game.

## One-time preparation

1. Install Termux from its official F-Droid or GitHub channel. Do not replace an already installed Termux APK with one signed by a different distributor without backing up your existing data. Run the setup in ordinary Termux, outside Secure Folder.
2. Install the separate Termux:X11 Android application from the official termux/termux-x11 nightly GitHub Release. The normal universal-debug APK is compatible with F-Droid Termux. The sharedUid variant is only compatible with matching GitHub-signed Termux; never silently swap APKs or uninstall the existing installation.
3. Permit Termux:X11 notifications when Android asks. This is user-controlled; do not auto-toggle Android background or battery policy.
4. In Termux, install Git and check out the candidate from the public LuHm-OS repository:

    pkg install git
    git clone https://github.com/eggie-admin/LuHm-OS.git
    cd LuHm-OS
    git switch candidate/kai9000-termux-x11-lite-20261102
    bash tools/kai9000TermuxX11.sh doctor
    bash tools/kai9000TermuxX11.sh setup

The setup command uses the official Termux package manager to install x11-repo, termux-x11-nightly, xfce, dbus, python, git and nodejs-lts. It then stages local pinned jQuery 3.7.1 with npm ci --ignore-scripts --no-audit --no-fund, npm run stage:jquery and npm run check. A network connection is required for one-time package installation. Node/npm are not continuously running for the desktop or cockpit.

## Local switch commands

    bash tools/kai9000TermuxX11.sh desktop
    bash tools/kai9000TermuxX11.sh cockpit
    bash tools/kai9000TermuxX11.sh status
    bash tools/kai9000TermuxX11.sh stop

Desktop launches Termux:X11 display :1 with the independent kai9000 Android window tag and native XFCE session. Cockpit serves the LuHm static HTML/CSS/jQuery interface at http://127.0.0.1:8765/ and opens Android's browser. These are two separate surfaces: Chrome is not embedded in the X11 desktop, and the current static cockpit does not connect to live ChatGPT or issue shell commands. Godot remains a separate development/runtime integration.

## Security and evidence limits

* The desktop requires neither root nor Shizuku. No kernel, SELinux, firmware, bootloader, partition, or Secure Folder changes.
* The browser server binds ONLY literal IPv4 loopback 127.0.0.1. It serves eight allowlisted files plus health; no directory browsing, uploads, external command endpoint, secrets, or wildcard/LAN listener.
* Content-security-policy disallows network fetches, forms, remote scripts, framing and plugin objects. Paths outside the allowlist respond 404, and POST/PUT/DELETE respond 405.
* Session PID files and logs stay under the app-private Termux ~/.local/state/luhm-kai9000, with restrictive permissions. The stop command validates process cmdline before killing owned PIDs and sends the tagged X11 shutdown broadcast. It cannot guarantee Android background-process persistence.
* No autostart, app-store publication, environment mutation except explicitly invoked setup, or automatic Godot/game deployment.
* Physical Samsung tablet X11/touch/rotation performance and crash resilience remain UNVERIFIED. Exact source code and offline tests do not prove installation. CROWN STOP; development candidate only.

## Troubleshooting

If the X11 activity is black, inspect the private x11.log and try upstream's -legacy-drawing option, then -force-bgra separately if needed. If the cockpit reports missing jQuery, rerun setup from the checkout and verify the local vendor file exists. If port 8765 is occupied, the service refuses to attach to an unrelated listener. If Android suspends the session, inspect battery policy manually instead of disabling security mechanisms.

Official upstream instructions: https://github.com/termux/termux-x11

## Offline smoke test

    bash -n tools/kai9000TermuxX11.sh
    python3 -m unittest discover -s tests -p testKai9000LocalCockpit.py -v

Unprivileged tests validate strict localhost HTTP behavior and static script boundaries, not a physical phone.
