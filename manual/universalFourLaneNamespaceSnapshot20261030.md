# LuHm-OS | One-frontend four-release namespace and private-edge snapshot | 2026-10-30

**Candidate source contract, not physical or cloud deployment.** Canonical source: `eggie-admin/LuHm-OS`; keep `project-hydra` separate. This mutation builds on Samsung CAST500 PR #453, vendor/ZIP PR #452, Four-Source PR #451, four-package PR #450, kernel VM500 PR #449, and Kai Blender PR #448. No main merge, DNS switch, VM provision or agent unquarantine.

## The decisions

**One frontend:** K9000 HTML5 application on packaged Android WebView, iOS/Safari website or WKWebView adapter, macOS desktop DMG, Linux local kiosk, and browser. Native wrappers expose *only consented bounded capabilities*, not privileged Linux APIs. The Samsung Tab S10 Lite remains DeX-*inspired*, **not** DeX capable. A low-end browser gets static read-only scene/health/status, not automatic multi-camera or WebXR.

**Four release lanes, distinct from role escalation and artifact formats:**

1. `nightly`: disposable reviewed SHA, unsigned artifact, newest test-only browser and package version **after** dependency review. No firmware upgrades.
2. `beta`: consented test-device APK, stable recovery evidence, Android/WebKit/Chrome Beta and browser regressions. No One UI enrollment by CI.
3. `lts`: stock OS kernel and carefully pinned stable dependency set, reproducible DEV/npm/DMG/APK outputs and rollback/backup receipts. This is the supported delivery target.
4. `legacy`: HTML5 capability-reduced view, read-only status and asset transfer; avoid mounting an insecure obsolete kernel/network daemon. Prefer browser compatibility over keeping an unpatched OS in production.

The **DEV / npm / DMG / APK** formats are independently tracked within each compatible release lane. Neither these support channels nor the Hear-Resolve-Act-Verify 0–3 escalation tiers grant Crown authority.

## Four transport choices and the four HTTP security stages

| Route | Today | Where used |
| --- | --- | --- |
| `currentRenderDirect` | **Current canonical MCP contract:** ChatGPT -> Render-managed TLS -> LuHm read-only MCP. Cloudflare is not silently interposed. | Keep until host-side SSE/streaming and auth proof supports cutover |
| `candidateCloudflareTunnel` | **Not deployed.** Candidate K9000 web origin: client -> Cloudflare DDoS/WAF -> Access identity -> outbound `cloudflared` tunnel -> private loopback reverse proxy -> scoped Python API. | Future Oracle/Google VM or home host, owner-approved DNS and credentials |
| `privateStudioLoopback` | **Not deployed by this mutation.** Local UI -> scoped localhost Python -> consented UVC/audio/Blender worker. | Linux Mint studio |
| `offlineFallback` | Candidate offline K9000 bundled HTML5, source-only status, no device permission. | Samsung, browser/iOS, low-spec kiosk |

Four security stages: (1) Cloudflare DDoS/WAF, (2) owner/MFA or scoped machine-service identity, (3) private loopback NGINX *or* Apache httpd reverse proxy, (4) application authorization, input bounds, logs and rate budgets. Avoid putting Cloudflare Access in front of the active public ChatGPT MCP until the host/streaming contract is proven. Zero Trust, rate limits and bot protection **depend on available plan**; Free Bot Fight Mode may challenge legitimate API traffic, so do not enable it on MCP without compatibility tests. Cloudflare bot score is an Enterprise feature, not assumed available free.

The edge cannot substitute for app authorization; never expose SQLite, Java/Gradle bridge, cameras, ADB, Bluetooth, or raw shell. A one-VM deployment doesn't need a paid global load balancer until traffic and redundancy warrant it. NGINX open-source is BSD-like; Apache httpd is Apache-2.0; choose one loopback reverse proxy, don't run redundant Apache+NGINX+XAMPP. XAMPP is a development bundle, never the public remote security boundary.

**Location/geolocation:** do not request GPS or store client location for bot detection by default. IP geolocation can be inaccurate and is **not identity**. Require explicit user consent and an actual feature justification for location collection. Defend with authentication, anomaly thresholds, privacy-preserving logs and rate limits instead.

## OS/network tools by trust zone

- `OpenSSL` = cryptographic library/TLS commands; `OpenSSH` / `sftp` = owner-controlled remote access/file transfer; `OpenVPN` = optional VPN, not automatically combined with Tunnel; `Netplan` = Ubuntu host-network configuration, never applied by CI; `Certbot` = owner-approved cert issuance/renewal, not automatic public DNS writes; `cron` or systemd timer = post-deployment scheduled job with one chosen scheduler and lock/timeout.
- Google Sentry is **unresolved**, not an assumed security service or active identity provider. Existing Cloudflare doctrine is primary for the public zone.
- Debian/Pi, Windows+WSL/Wine, iOS, macOS, and Samsung One UI are compatibility boundaries, not packages to install into one VM or replace with a universal kernel. The firmware, GRUB and GParted write gates in the previous Samsung CAST 500 remain.
- `uv` is Astral's Python project manager. It can maintain a locked `pyproject.toml` / `uv.lock` after audited dependencies; **do not** `uv sync` the system Python, nor infer it is installed. Raspberry Pi ARM support differs by version. **Pi Forge** and **Lightning Script** are unverified name aliases; preserve them in the ledger and require exact source location before integrating.

## Audio, cameras, motion and professional render

**Linux studio first**, K9000 as operator. Discover local ALSA, PipeWire/WirePlumber, BlueZ, V4L2/UVC, USB controllers, mic sample rates, Bluetooth HFP/A2DP profile and permissions *read-only*. Avoid claiming six simultaneous webcam streams, six synchronized microphones or Bluetooth microphone return audio without a live host test. Six UVC cameras need powered hubs, USB bandwidth, frame clock alignment and reprojection calibration. Bluetooth audio is not a replacement for precise multichannel hardware sync. Never start a microphone or camera implicitly.

**Existing FFmpeg:** `host/ai-ffmpeg/ai-ffmpeg.py` already implements a bounded local FFmpeg render candidate with approved argument arrays and timeouts; reuse rather than write another shell-execution AI renderer. First try synthetic visual markers and WAV clap alignment, then real consented footage; use signed/allowlisted file handles, redacted logs, no arbitrary user-supplied filtergraph at the server boundary.

**Creative pipeline:** Linux UVC/audio -> bounded Python manifest + local SQLite JSON1 -> FFmpeg preprocessing -> Blender armature/camera compositing -> rights-cleared GLB/glTF -> Godot4 runtime and Babylon web preview -> K9000. Vue runs the UI; Three.js is an alternate web-render adapter, not a reason to bundle Babylon and Three in the APK. Unity and Unreal may consume compatible glTF/FBX via reviewed adapters but must not be baked into LuHm OS as duplicate runtimes. Blender EEVEE is GPU-based, whereas Cycles can use CPU/GPU; no free Oracle A1/E2-micro GPU guarantee or headless EEVEE claim. Review Unity/Unreal license terms before adding their tools to a redistribution.

## Six proposed goddess roles, still zero active workers

Six **views** over the existing 15 quarantined canonical roles, not six spawned cloud agents:
- Lum: human-facing routing/consent.
- Skuld: vendor research/compatibility.
- Tetsu: source/rights provenance.
- Kaji: build evidence only after CAST.
- Yume: storyboard/3D asset coordination.
- Belldandy: review, privacy and evidence.

They share exact `taskId + sourceRef + scopeId`, a 44 KiB capped Base64url JSON envelope, typed SQLite receipts, bounded JavaScript projection and existing Crown STOP. **Base44 is a separate external app-building platform, not an encoding, signature, worker model, or free source library.** LLaMA models have per-model weight licenses; no model weights are imported. No automatic worker resumption.

## Tested source implementation

`doctrine/universalFourLaneV1.json` and `infra/universal-four-lane/four-lane.yaml` define four channels, four process layers, four security stages and no privileged changes. `tools/universalFourLanePlan.py` returns a source-SHA-bound planned route for one read-only capability, verifies its data using **parameterized in-memory SQLite STRICT/JSON1**, and reports `routeAvailable=false`. `frontEnd/universalRouteProjection.mjs` checks the exact keys/source/role/lane, uses `textContent` and refuses mutation flags. CI executes all sixteen lane/transport combinations and both negative tests and legacy source gates. This is **not an authenticated service deployed to a VM or a proof of production Kubernetes/load balancing**.

## Next evidence needed

1. A read-only Android/Samsung Macrobenchmark and Linux Mint capabilities receipt, including Bluetooth controller profiles, mic sample-clock drift, six UVC buses, browser DeviceMotion/WebXR support.
2. A tiny synthetic FFmpeg -> Blender -> GLB -> Godot/Babylon sample, benchmarked on actual Linux studio hardware; do not ship stock/public artwork accidentally.
3. Verified Oracle/Google account eligibility, off-VM backup/restore, one authorized TLS+MCP canary, and rollback before optional Cloudflare Tunnel cutover.
4. Any public Apache-2.0 migration remains blocked pending copyright ownership/provenance; GPL, MPL, LGPL and Unreal/Unity conditions cannot be discarded.

## Primary docs

Cloudflare Tunnel https://developers.cloudflare.com/tunnel/concepts/ ; WAF/Bot Fight https://developers.cloudflare.com/waf/feature-interoperability/ ; uv locks https://docs.astral.sh/uv/concepts/projects/sync/ ; DeviceMotion https://developer.mozilla.org/en-US/docs/Web/API/Device_orientation_events/Detecting_device_orientation ; WebXR compatibility https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API ; FFmpeg filters https://ffmpeg.org/ffmpeg-filters.html ; Blender EEVEE https://docs.blender.org/manual/en/latest/render/eevee/index.html ; Godot glTF https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html ; Unreal license https://www.unrealengine.com/license .
