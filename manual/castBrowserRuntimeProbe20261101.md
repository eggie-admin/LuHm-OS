# LuHm-OS | CAST browser-to-Linux runtime probe, proposed candidate

This change adds a **user-triggered**, read-only diagnostics card to the existing Babylon Glass World prototype. It is not another graphics engine, background daemon, OS emulator, Linux container, device benchmark, or Samsung APK.

## Vertical adapters

1. **Browser UI:** keep the existing HTML/DOM, Vue scene inspector, Babylon WebGL 2 world, and optional Godot Web export. The probe checks the existing WebGL context, WebAssembly, browser storage features and main-thread animation frame cadence only after a click. Nothing is transmitted or persisted.
2. **Browser storage:** use IndexedDB for typed scene/event records, OPFS for origin-private working blobs if needed, and Cache Storage with a versioned service worker only for reviewed immutable public assets. Quotas and browser eviction apply; never treat OPFS as Google Drive. Cookies are session state, not asset storage. Local file pickers require an actual user gesture and explicit permission. Neither picker nor storage writes are attempted in this probe.
3. **Native Linux:** use vendor-supported kernel and Wayland/Chromium kiosk where a display exists. Native creative jobs use separately approved SDL/Godot, Python, Blender and FFmpeg processes; connect them to the web UI through a narrow authenticated loopback/IPC adapter. File permissions via portals and XDG locations; avoid host-wide mounts, privileged processes, or unconditional background jobs.
4. **Android:** same browser assets may be hosted by the existing WebView shell. File selection flows through Android's SAF; native services need separate permissions and a reviewable lifecycle. A Linux container is not assumed or claimed inside the browser. Samsung compatibility requires actual device proof.

## Four typed transport lanes (existing Canon)

Numeric, text, Boolean/tri-state, and AI manifest events retain the existing `taskId`, `sourceRef`, `scopeId`, `sequenceId`, and `evidenceRef`. Attach optional `contentType`, `byteLength` and `sha256` for binary object references. JSON carries *control metadata*. A SHA-256 digest validates bytes. Base64 is an optional textual encoding when binary transport is unavailable and adds ~33% byte overhead; do not put large media or secret tokens in JSON/SQLite.

## Resource policy

- Idle: a static cockpit only. User starts 3D, media, workers and filesystem chooser explicitly.
- Visible 3D: one WebGL scene; scene and UI share the JS main-thread budget. Canvas pauses when hidden. Real framerate, battery, memory and thermal behavior must be measured on the target phone.
- Offline: read-only shell and approved cached public assets only. Never cache authenticated JSON, personal responses or unreleased media. No service worker is installed by this candidate.
- Linux supervision: inspect `systemctl --user`, `systemd-cgtop`, `ps`, and actual cgroup CPU/RSS only on the authorized local host. A browser cannot enumerate host background daemons. Benchmark before trimming services; leave security updates, portal services, TLS and OS drivers intact.
- Profile with cold/warm page-load, asset bytes, memory RSS, CPU per service, p50/p95 interaction latency, JS frame cadence and GPU frame time separately. No hard performance GREEN from a feature-detection flag.

## Local validation

From `frontEnd/prototypes/glassWorld`, run `node --test tests/runtime-diagnostics.test.mjs` and existing `npm test` / `npm run build` checks with pinned dependencies. Open the page and click **Inspect browser locally**. Verify no browser permission prompt, no network upload, safe text-only diagnostic JSON and static fallback. On Linux and Samsung, compare results with OS-level measurements and preserve exact-source SHA in receipts.

**STATUS: PROPOSED SOURCE ONLY.** No production deployment, cloud mutation, live device capture, release signing, plugin installation or headless agent activation. Source law: AI proposes. Policy authorizes. CI proves. Professor promotes.
