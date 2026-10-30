# Four-Source Forge Field Manual | 2026-10-30

**Draft source only.** The actual Google/Oracle VM, Raspberry Pi, Linux Mint host, Samsung devices and six cameras have not been connected in this mutation. No Certbot certificates, private login provider registrations, IMAP polling or remote Blender render exists. Crown STOP.

## The four sources, four presentation profiles, and 4/4 audit
Sources: (1) VM headless services; (2) Samsung/Raspberry hardware presentation; (3) HTML5/JavaScript source-only UI; (4) GitHub/npm/DEV/DMG/APK build receipts. These are not interchangeable trust zones.
Modes: headless/Reaper shorthand = no-display control plane; Witching Hour = presentation wrapper only; corporate = operations review; GitHub Development = reproducible build/review. All inherit the same canonical 0–3 escalation kernel, Hear/Resolve/Act/Verify rhythm and Professor's final approval. 'Sanders' is interpreted as sane, evidence-driven gating, not a new privilege role.

## Debian and Raspberry Pi kiosk vs Ubuntu headless
- Debian 13 physical kiosk: supervised dedicated user/seat on Wayland Cage plus packaged HTML5 Chromium UI, allowlisted paths, minimal session, restart policy and accessible exit. The example systemd unit is not enabled. A headless cloud VM should **never** run a kiosk display server just to render Blender.
- Raspberry Pi OS physical kiosk: Raspberry Pi recommends labwc Wayland autostart/Chromium kiosk on the desktop variant. The OS Lite variant is headless and has no graphical kiosk until a compositor/browser is installed. Confirm actual Pi model, PSU, SD/SSD wear and thermal throttling.
- Ubuntu 26.04 LTS headless VM: Netplan renderer **networkd** after interface inspection. The sample enp1s0 name is NOT the actual VM NIC. Check cloud-init and running renderer first; use only `netplan generate --root-dir TEMP` for CI, then console-backed `netplan try` for an explicit future migration. Desktop/Mint generally uses NetworkManager; Debian/Raspberry can use other managers and should not be overwritten.
- apt and dpkg are host package-management tools, not npm, Android APK package managers or app runtime dependencies. Pin versions, verify sources/signatures and use dry-run or exact command receipts before altering the machine.

## BlueZ / virtual peripherals
BlueZ's `btvirt` can create synthetic controllers for protocol test environments. It neither creates a real USB adapter nor guarantees Bluetooth audio, pairing, radio permissions, HFP microphone return channels or the unknown 3.5 mm jack. PipeWire/WirePlumber on Linux require actual hardware and consented route tests.
Samsung stock Android and Shizuku optional permission bridge are separate; no VM Bluetooth adapter can silently operate a phone's Bluetooth chip.

## Certbot + DNS
Cloudflare remains the public authority. Private BIND9/dnsmasq from the Kernel 500 PR stay loopback-only. DNS-01 with certbot-dns-cloudflare is a future manual operation with restricted API token in a secret-only root-owned file. Automatic renewal needs separate test proof. No cert or DNS record was issued or modified.

## Base64url, Base44, JSON -> SQL -> JS
Base64url wraps a UTF-8 JSON source manifest with a **44 KiB decoded limit**. Base64 is an encoding, not encryption/signature; Base44 is an optional commercial AI app builder, not a transport or authorization standard.
`tools/unifiedForgePipeline.py` checks canonical exact source SHA, no unexpected keys, local-only provider/capability, 0 network requests, 0 worker concurrency, 4 approved modes, 0–3 tier and all three authority booleans false. It inserts the manifest with **parameterized SQL** into the existing `host/api/typedLanesV1.sql` SQLite STRICT / JSON1 tables in memory and reads back a safe projection. The browser adapter `frontEnd/forgeSourceProjection.mjs` accepts only that projection and uses `textContent`, never HTML injection. MariaDB remains optional and unconnected; do not expose a network SQL listener or automatically copy databases.

## Four login choices, not four authority levels
GitHub OAuth or GitHub App user authorization code + PKCE S256 + unguessable state; Google OIDC authorization code + PKCE + nonce/issuer/audience/signature; Apple Sign in with Apple with nonce/state/JWT validation and private relay email considerations; LuHm-native proposed WebAuthn/passkey with separate recovery. Each requires registered clients, exact redirect URIs, server-only token exchange, CSRF/session controls, logout/revocation, rate limits, independent role authorization and compliance review. **None is implemented as a working login in this candidate.**
Do not use email-address string equality as the only authentication check. Apple relay mail may obscure original address; the authorized identity is issuer+subject, not email.

## Read-only email check on the future VM
`python3 tools/ownerImapUnreadCheck.py` is a **no-network dry run**. For a later explicitly approved mailbox, environment variables `LUHM_IMAP_HOST`, `LUHM_IMAP_USER`, `LUHM_IMAP_OAUTH_TOKEN` and owner-invoked `--check` can request *only an unseen count* over TLS IMAP using XOAUTH2. It never fetches bodies, marks read, sends email or autostarts polling. No mailbox, VM, user or token was connected here. An actual scheduler and host secret store would require another separately authorized deployment.

## Professional Blender / six-camera plan
Blender headless background rendering is possible on a host with appropriate CPU/RAM/storage; an Oracle Always Free A1 VM is not a verified professional GPU renderer and may be too small for substantial scenes. Use your Linux studio for heavy rendering until real remote timing and quotas are proven. Godot/FFmpeg optional, NPM build-time only.
Six UVC cameras: use a powered hub and dedicated USB host controllers where possible; test bandwidth per bus, MJPEG vs raw frame sizes, permission prompts, power budget, USB cable stability, sustained 30 fps, timestamp jitter and disconnect/reconnect behavior. No physical six-camera capture has been executed. Android external camera APIs MAY support multiple cameras, but this is not a guarantee for the Galaxy Tab S10 Lite.
**Verified Samsung warning:** Galaxy Tab S10 Lite is **not compatible with standalone DeX, Wireless DeX, or HDMI output** in Samsung documentation. Deliver a DeX-inspired K9000 workspace in normal Android instead. S24 FE DeX is a separate capability requiring device proof. Galaxy Tab A8 is a companion device, not a passive HDMI display.

## Existing plugin census
GitHub source tree audit found two top-level LuHm plugin manifests: `plugins/luhm-os/plugin.json` and `plugins/luhm-android-beta/plugin.json`; also a quarantined incoming jQuery Oni Summoner plugin under `frontEnd/plugins/incoming`, the AndroidWeb3Cockpit Godot editor add-on, and agent skill folders. Existing approved jQuery source identities are retained. An inventory is NOT a claim that every plugin is installed in ChatGPT or can execute on a VM. Community plugins require SPDX/license/provenance, source review, build pin and isolated runtime tests before promotion.

## Reproducible source checks
python3 tools/unifiedForgePipeline.py
python3 -m unittest tests/testUnifiedForgePipeline.py -v
node --test tests/fourSourceProjection.test.mjs
python3 tools/ownerImapUnreadCheck.py
python3 tools/fourSourceForgeAudit.py
GitHub CI runs `netplan generate --root-dir` on an isolated runner directory and never `netplan apply`.

Primary references:
https://netplan.io/ ; https://github.com/canonical/netplan/blob/main/doc/netplan-generate.md
https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
https://www.samsung.com/us/support/answer/ANS10003426/
https://source.android.com/docs/core/camera/external-usb-cameras
https://bluez.github.io/ ; https://certbot-dns-cloudflare.readthedocs.io/en/stable/
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
https://developer.apple.com/documentation/signinwithapple/authenticating-users-with-sign-in-with-apple
