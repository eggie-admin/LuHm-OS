# LuHm-OS Firefox Antenna First · Debian Minimal / X11 / MMO patcher concept

**Status: PROPOSED SOURCE-ONLY; runtime, installed extension, Debian/X11,
Firefox kiosk, network and device measurements UNVERIFIED. CROWN STOP.**

## The problem and the smallest solution

User intent: Debian minimal server plus X11 kiosk, Firefox-focused front end,
an independent LuHm-OS Firefox WebExtension update widget, and a small
MMO-style installation/updater flow. **Antenna first** means discovery and a
read-only local handshake, not installer, streaming agent, or patch launcher.

Firefox **ESR for desktop** is the target on Debian. **Firefox Focus** is a
distinct privacy-focused mobile browser, not this X11 WebExtension target.
The independently developed LuHm extension is **not** OpenAI's official
browser extension and cannot claim to turn a browser into a ChatGPT plugin.
Keep the pre-existing **ChatGPT MCP plugin** and its stable remote update
manifest as a separate product integration.

## Stack and size budget

1. Debian minimal, patched OS and non-root kiosk user, managed separately.
2. Xorg + minimal window manager (e.g. Openbox) + Firefox ESR.
3. Python 3 stdlib antenna bound to `127.0.0.1:8765`, on demand, no proxy.
4. Reused `plugins/luhm-firefox-antenna/popup.html`, CSS and JS.
5. Optional Firefox toolbar popup in ordinary browser mode. In kiosk mode
   browser chrome is hidden, so open the **same UI** at the local homepage.
6. Later: verified update catalog, separate staged patch cache, atomic
   replace/rollback. No unattended update installation in this milestone.

**100 MB target:** decimal 100,000,000 bytes for the LuHm *application shell*
and its approved assets. Stage zero measures the four extension source files.
This number excludes Debian, Xorg, window manager, Firefox ESR, Python,
system dependencies, local media, and downloaded patches. No claim that the
complete host fits within 100 MB. Record installed sizes with `du`, `dpkg-query`,
`free`, and measured memory/CPU before accepting a device budget.

Current sample layout:

```
Debian (installed by the owner)
  user-session Xorg -> window manager -> firefox-esr --kiosk
        |
        +--> 127.0.0.1:8765/      local status cockpit
                 |
                 +--> /antenna/v1/status   GET/HEAD only
        |
        +--> normal Firefox add-on popup (same HTML/CSS/JS)
                 |
                 +--> localhost read-only fetch
Existing LuHm-OS ChatGPT plugin/MCP != browser WebExtension
```

## Sample local smoke (not installation proof)

On a Debian test VM / disposable machine, after reviewing the package plan:

```sh
sudo apt update
sudo apt install --no-install-recommends python3 xserver-xorg-core xinit openbox firefox-esr
# Install driver, font and input packages only if your device requires them.
# Under the unprivileged kiosk user, in a full repo checkout:
python3 host/antenna/luhmLocalAntenna.py
# Another terminal:
curl -fsS --max-time 3 http://127.0.0.1:8765/antenna/v1/status
curl -I --max-time 3 http://127.0.0.1:8765/
# In an existing X11 user session:
sh host/antenna/startFirefoxKiosk.sh
```

For a display-less console, create a user-owned `~/.xinitrc` and call the
launch helper from that session. Do not launch the browser or Xorg as root.
Use the local X authority and seat permissions supplied by the distribution.
A service manager and X11 auto-login are **not** installed/configured by
this PR; those require device-specific review and startup proof.

## Optional temporary WebExtension test

In standard desktop Firefox open `about:debugging` -> **This Firefox** ->
**Load Temporary Add-on**, choose
`plugins/luhm-firefox-antenna/manifest.json`. Click the toolbar antenna and
then *Check local antenna*. Temporary loading is a development test, not a
signed or persisted extension installation. Production distribution requires
Mozilla add-on review/signing, stable extension ID and explicit release
consent. Firefox kiosk hides browser chrome so use localhost homepage there.

The only requested origin is `http://127.0.0.1:8765/*`, no blanket site
permissions, content-script injection, cross-browser scraping, shell commands,
OpenAI credentials, remote executable code, native messaging, or runtime agents.

## MMO-style future update FSM (not implemented)

```text
BOOT_STATIC -> ANTENNA_CHECK -> COMPARE_SIGNED_CATALOG
     UNKNOWN / OFFLINE / BAD_SIG -> HOLD_OLD_SHELL
     SAME_VERSION -> READY
     APPROVED_UPDATE -> STAGE_CONTENT_ADDRESSED_BYTES
       -> VERIFY_DIGEST_AND_SIGNATURE
       -> ATOMIC_ACTIVATE -> HEALTH_CHECK
       -> GOOD: RETAIN_RECEIPT
       -> BAD: ROLLBACK_TO_PREVIOUS_GOOD
```

Future checks use immutable digest paths, a trusted pinned verifier/key,
monotonic versions, size limits, per-artifact provenance and rights, no
path traversal, allowlisted content classes, no extension-controlled shell.
A SHA-256 alone verifies bytes **only against a trusted digest**. The update
catalog must be authenticated before the browser may recommend installation.
Always preserve an immutable last-known-good package and rollback receipt.

Three non-interchangeable update lanes:
- **WebExtension:** Firefox add-on's signed XPI, using Firefox's own add-on
  distribution/update security mechanism. Not silently replaced by the local
  HTTP antenna.
- **LuHm-OS artwork and UI assets:** separately verified content-addressed
  packs, with rights/provenance checks and a staged activation boundary.
- **ChatGPT MCP plugin:** existing stable remote manifest and host contract.
  An MCP schema change may require explicit host refresh/reinstall; a Firefox
  XPI cannot silently update the ChatGPT-hosted plugin.

## Backend/hardening alignment

- `doctrine/selfHostedRemoteUpdatesV1.json`: existing remote source manifest
  remains unmodified and is **not** fetched by this local service.
- `doctrine/samsungAntennaV1.json`: distinct Termux/X11/Shizuku Samsung
  field antenna, physical proof still pending, not replaced by Debian path.
- `doctrine/storageTopologyV1.json`: database holds metadata/pointers;
  binaries belong in private durable file storage and in bounded local cache.
- `doctrine/everlastingCovenantV1.json`: task/source/scope chain stays
  intact; no promotion through absent source, rights, signing, or device proof.
- `doctrine/companyWideOperationalQuarantineV1.json`: all 15 real agent
  execution lanes remain quarantined.
- No public network bind, remote CORS allowlist, credential endpoints,
  incoming webhook, SQL DDL, host root privileges, JavaScript updates,
  daemon installation, plugin signing, or external deployment.

## Verify and report

```sh
python3 -m unittest discover -s tests -p testFirefoxAntenna.py -v
python3 -m py_compile host/antenna/luhmLocalAntenna.py
git diff --check
```

Classification: source checks can be **GREEN_FOR_SCOPED_SOURCE** only.
Browser add-on actual load, X11 kiosk startup, JavaScript behavior,
Mozilla signing, complete host disk/memory budget, ChatGPT host integration,
and any future update/install/rollback require independent receipts.
