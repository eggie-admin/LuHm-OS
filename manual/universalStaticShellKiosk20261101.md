# LuHm-OS universal static cockpit: kernel to browser source plan

**State:** DRAFT_SOURCE_ONLY. Protected `main`, installed devices, production DNS,
MCP host, public stores, publication and signed releases are unchanged.
This is a source-level extension to the existing `frontEnd/` jQuery cockpit.
Related Pi kiosk candidate: draft PR #480, stacked on #479/#478/#477.
Do not copy its loopback server, duplicate CI workflows, or merge its stack blindly.

## System boundary, not a custom kernel

| Layer | Shared contract | Environment-specific choice | Evidence required |
| --- | --- | --- | --- |
| 0. Firmware and kernel | Use OEM-supported boot and kernel, least privilege; no hexadecimal register writes | Raspberry Pi EEPROM/config.txt/device tree; Linux distribution kernel; Android vendor kernel; Apple-managed kernel | Real model, architecture, firmware version and supported boot test |
| 1. OS/userspace | Reproducible pinned assets and service separation | Raspberry Pi OS Desktop or Lite; supported Debian/Ubuntu; Android WebView; macOS/iOS Safari; ChromeOS browser | Exact OS/package versions, resource limits and boot/recovery |
| 2. Display manager/compositor | Optional human GUI, not required for headless backend | Raspberry Pi labwc/Wayland default; opt-in X11 on legacy-compatible images; Xwayland where a specific app requires it | Physical local login, input, keyboard exit, monitor and GPU result |
| 3. Browser static shell | Same-origin `frontEnd/index.html`, pinned jQuery + namespaced plugins, CSP/meta fallback | Firefox/Gecko, Safari/WebKit, Chromium/Blink, ChromeOS web app, Android System WebView | Separate visual, interaction and accessibility smoke receipts |
| 4. Typed native/MCP boundary | Browser stays unprivileged, scoped capabilities and exact-source receipts | Optional Android `LuHmNative` adapter; separately authorized backend | Native input validation, origin/auth/capability proof and rollback |

**VDM:** Not yet a uniquely identified LuHm executable or vendor product. If it
means *virtual display manager*, treat it as a candidate session/virtual-display
adapter under layer 2, not permission to install a VNC server, replace an OS
display manager or expose screen captures. Confirm the desired VDM implementation
and source/license before adoption.

## Raspberry Pi choices

- **Recommended:** Raspberry Pi OS Desktop with its supported Wayland/labwc
  session, Chromium or Firefox in a user-started window/fullscreen. The current
  Raspberry Pi documentation recommends Wayland over the X11 switch.
- **Headless:** Raspberry Pi OS Lite, no display manager. Run the existing
  loopback-only static preview from the scoped candidate in PR #480 if and
  only if that stack is independently tested and reviewed.
- **X11 fallback:** Only on a specifically supported legacy/X11 desktop
  image where a physical browser smoke requires it. No silent system-wide
  switch, autologin, xhost +, root browser, forced `--no-sandbox`, blanket
  udev permissions, public bind, or uncontrolled VNC access. Preserve a
  physical exit path and a rollback to the supported graphical session.
- **Pi image architecture:** Pick the actual Pi model/64-bit compatibility and
  use a supported image. Do not install the generic x86 Debian kernel on Pi,
  or imply that virtual-machine proof is Pi hardware proof.

## Browsers and ChromeOS

- **Firefox:** Test the actual pinned frontend in Gecko, keyboard navigation,
  responsive dimensions, reduced motion, strict CSP and local asset loading.
- **Safari:** Test current supported WebKit on macOS/iOS/iPadOS separately.
  CSS `100vh` falls back when `100dvh` is unavailable. No Chrome extension
  APIs, USB/microphone assumption, device privileged calls or user-agent
  string-based OS routing.
- **Chromium/Chrome:** Test Blink and dynamic viewport, asset paths, CSP,
  JS errors and on-screen kiosk exit. Browser fullscreen is not an OS
  security boundary.
- **ChromiumOS vs managed ChromeOS:** This repository only supplies a web
  shell candidate. Actual managed ChromeOS kiosk mode is configured through
  Google Admin and may require a management license. Prefer standard
  websites/PWAs (or separately reviewed IWA) over legacy Chrome Apps.
  ChromeOS enterprise-enrolled kiosk sessions may auto-grant web permissions:
  do not request camera, mic or external origins without a specific review.
  Do not claim ChromiumOS inherits managed ChromeOS device administration.

## HTML and plugin encapsulation

1. Use the approved local `jquery@3.7.1` source from the lockfile and
   `npm ci --ignore-scripts`; serve JavaScript/CSS on the same origin.
2. Keep `luhmCockpit`, `luhmCastIntent`, roleplay and parallax behind
   namespaced jQuery interfaces; no remote CDN injection, dynamic eval or
   arbitrary host/plugin loading. Incoming community plugins remain quarantined.
3. A static CSP meta element blocks inline scripts, executable objects and
   unapproved cross-origin script/network fetches during source previews.
   It does **not** enforce `frame-ancestors`, replace a host HTTP CSP or
   prove the live Render headers. The static host must separately set
   strict CSP, frame/embed policy, `nosniff`, referrer and permissions policy.
4. Only three known event types can reach the optional Android native adapter:
   `cockpit_ready`, `world_requested`, `oni_requested`.
   Oni names must be canonical lower-camel IDs, at most 32 characters.
   The native host must independently authenticate its origin and enforce
   allowlisted actions. A browser without a native bridge degrades safely.
5. A visible keyboard skip link, focus treatment, reduced motion,
   `100vh` fallback and `100dvh` enhancement are baseline accessibility
   checks, not a WCAG or per-device certification.

## Run and acceptance

From a clean committed checkout at the exact SHA:

```bash
cd frontEnd
npm ci --ignore-scripts --no-audit --no-fund
npm run stage:jquery
npm run check
```

Existing `.github/workflows/frontend-jquery-dryrun.yml` and
`.github/workflows/in-chat-html-check.yml` provide CI paths. The
`tools/universalShellAudit.mjs` check and tests reject remote imports,
inline scripts/events, weakened CSP, missing keyboard fallback and
unbounded native messages. The source audit writes no private data,
does not call a vendor API, and cannot promote CAST or prove a kiosk.

For each proposed physical platform, record **separately** the exact source
SHA, browser engine/version, kernel+OS version, real GPU/display/input,
local origin and headers, devtools console result, HTTPS/MCP connection
when relevant, basic render, keyboard/touch navigation, pause/resume,
reduced-motion accessibility, kiosk escape, and recovery. Then verify
Rebel's first eight-second edit/draft in the real interface. Keep originals
and private media off public GitHub.

**Promotion remains:** DRAFT -> exact-head CI -> reviewed testing ->
real platform/browser acceptance -> separately approved deployment.
Final CAST, Android signing, Google Play and public social posting are
independent human-approved gates.

## Official upstream references

- Raspberry Pi OS and supported desktop/Linux display choices:
  https://www.raspberrypi.com/documentation/computers/os.html
  and https://www.raspberrypi.com/documentation/computers/configuration.html
- ChromeOS kiosk/PWA and managed permission boundaries:
  https://developers.google.com/chromeos/app-development/learn/kiosk
  and https://support.google.com/chrome/a/answer/9781496
- Browser progressive enhancement and CSP:
  https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
  and https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement
