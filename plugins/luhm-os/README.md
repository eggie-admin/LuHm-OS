# LuHm OS ChatGPT Plugin

## Android / F-Droid distribution is a different lane

The `art.eggiebagelface.*` Android package identifier family does not itself deliver remote APK updates. The separately proposed `https://art.eggiebagelface.art/fdroid/repo/` location would host a stable-signed LuHm-OS APK and independently signed F-Droid repository index **only after** exact FQDN, TLS, signing, upgrade and Professor-publication proof. Neither this repository location nor the ChatGPT MCP plugin is currently authorized to auto-update or auto-publish the Android app. The existing testing/beta application IDs are not stable public APK identities.

## The actual product: art creation inside ChatGPT

LuHm-OS is an **artist-first creation tool**, not primarily a deployment dashboard or MUD. The existing `luhm_open_cockpit` MCP App resource is the ChatGPT-facing studio surface. On the current **proposed branch**, it hosts a seven-shot *Into the Warp* storyboard editor. The Professor can alter visual direction and durations, undo/redo, reset and explicitly export the private working draft as JSON. Edits are deliberately in-widget memory only, not cloud persistence. The sealed source script is never sent in the widget payload. Belldandy's Codex history stays in shot 401, while shot 500 is a callback to the same record.

This candidate does not yet provide drawing/painting tools, actual multi-frame motion editing, media file persistence, a running remote FFmpeg queue, or verified ChatGPT-host visual interaction. The published/manual-upload package remains 0.5.2 until separately approved and packaged. Creative use does not authorize a new transport, OAuth bypass, account writes, provider uploads or public posting.

LuHm OS 0.5.2 is built for a clean manual upload. It packages portable LuHm workflow skills, explicit coding-roleplay behavior, and the canonical read-only MCP connection.

## Virgin install

Uninstall the older LuHm OS plugin before uploading this package.

The new package does not migrate or require prior plugin state, prior chat state, local developer MCP settings, tokens, private keys, or private connection files.

Upload the ZIP exactly as built. Its archive root contains `plugin.json`.

After installation, start a new chat and ask LuHm OS to inspect current source truth. Normal ChatGPT is the default mode. LuHm coding roleplay starts only when explicitly requested or when continuing an active scene. OOC, IRL, direct corrections, and real project control instructions return to plain conversation.

## Current endpoint

The plugin now connects to the hardened read-only MCP service. Its Godot viewer proposes a narrowly allowlisted iframe of the separate, existing Godot HTTPS export; it never builds Godot or proves ChatGPT iframe playback. Host connection refresh and real input proof remain separate.

The manual package contains one MCP connection source:

`https://luhm-os-harness-green.onrender.com/mcp`

Custom DNS, Cloudflare proxy changes, certificate issuance, and public directory publication remain separately evidence-gated and Professor-controlled.

## Portable plugin root

The manual upload contains:

- `plugin.json`
- `mcp.json`
- `README.md`
- `VIRGIN_INSTALL.md`
- `PRIVACY.md`
- `TERMS.md`
- `review-tests.json`
- `assets/`
- `skills/luhm-agent-workflow/`
- `skills/belldandy-housekeeping/`
- `skills/luhm-coding-roleplay/`
- `skills/luhm-glass-module-dock/` (modular music/avatar/Yume/social/admin chat workflows, source-only)
- `LICENSE` (canonical GPLv3 text)
- generated `SOURCE_MAP.json`
- generated `BUILD_RECEIPT.json`

Developer-only local/private MCP profiles and deployment/review working files are intentionally excluded from the manual upload artifact.

## Cross-device glass plugin dock (candidate only)

The mobile and full in-chat MCP widgets use a **single gear button** to reveal five source-registered cards: music, avatars/Python, Yume art, social publishing and admin. A card sends a requested workflow into the ChatGPT conversation when the host provides MCP Apps `ui/message` or the compatible ChatGPT helper. It does not embed unauthorized YouTube/Spotify playback, install a Python executor, post to social networks or activate quarantined Oni.

Android Chrome Canary is an optional compatibility target; iPhone Chrome Stable/Beta is the supported testing assumption. There is no official Canary iPhone release channel. iPhone single-app confinement uses Guided Access/approved MDM, not a hidden unsupported headless Chromium build. The drawer is **inside** the sandboxed ChatGPT MCP App, not a global browser-page injection.

The GitHub package skill is portable instructions only. The actual installed Project Hydra private Site backend must independently receive the new source and pass Android/iPhone ChatGPT mount tests before claiming the feature is live.

## Coding roleplay boundary

ChatGPT stays outside the tiny goth MUD unless Professor explicitly enters or continues a scene.

Roleplay is presentation only. It cannot create GREEN, mutation authority, merge, publication, deployment, signing, DNS/TLS changes, secret rotation, certificate issuance, or Crown.

The portable roleplay skill and connected cockpit both resolve behavior from current LuHm doctrine/source truth rather than requiring remembered state from an older install.

## Authority

The plugin exposes read-oriented source truth, roster, housekeeping, routing, help, escalation planning, proof contracts, and the read-only cockpit.

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**
