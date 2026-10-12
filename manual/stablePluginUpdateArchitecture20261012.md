# LuHm-OS Stable Host Update Architecture

Status: PROPOSED_SOURCE_ONLY. Authority: Professor. Crown: STOP.

## The repair

The previous package lifecycle unnecessarily linked every SVG, WebP, CSS, and cockpit update to a new ChatGPT plugin ZIP and clean reinstall. Install the read-only plugin host adapter once when compatible, then use separate approved release lanes. The existing plugin points to the unchanged https://luhm-os-harness-green.onrender.com/mcp endpoint, with stable luhm_open_cockpit and luhm_open_godot_player names. Backward-compatible server updates can be deployed independently of the host ZIP. Host caches or changed schemas may still require refreshing or reconnecting.

## Four asset layers

Vector SVG editable pixel masters; indexed PNG and animated WebP bitmaps; CSS styling; npm-locked jQuery compatibility wrapped by the LuHmOS interaction layer. These art layers are distinct from the 0-3 escalation audit tiers and the Chat/IC/OOC/IRL conversation modes.

## Live update metadata

The new GET and HEAD /harness/update-manifest.json route produces a static, read-only asset allowlist with SHA-256 for each asset, an asset-set digest, canonical compatible plugin tool names and resource ID, and optional validated Render Git SHA. Missing deploy SHA is UNVERIFIED. It supports ETag/If-None-Match and no-cache revalidation. It does not fetch Drive, accept uploads, call shell commands, inject scripts, serve credentials, write production source, or grant Crown.

Current /harness/assets/ remains same-origin on Render. Existing unversioned files are revalidated and must not be cached as immutable. Only approved assets with content-hashed paths can be made long-lived immutable once audited and promoted. Cloudflare CDN activation is unverified and separate from existing direct Render MCP transport.

## Update lifecycle

| Lane | Change | Host reinstall | Required evidence |
| --- | --- | --- | --- |
| 0 | Approved sprites, artwork, CSS, copy | No | Original rights, art review, hash, browser proof |
| 1 | Compatible MCP tool response and HTML resource | No; refresh may be needed | Exact-SHA CI, Render deploy, live MCP test |
| 2 | Plugin manifest, permissions, breaking/new tool schema | Possible | New package and ChatGPT host proof |
| 3 | DNS, Cloudflare proxy/tunnel, certificate, signing, publication | Independent Crown gate | Explicit Professor approval and runtime receipt |

## Sanity and rollback

Skuld checks compatibility and npm; Urd audits risk and evidence; Belldandy records hash, source and deploy; Yume validates asset canon; Lum orchestrates; Professor alone promotes. The existing Render service stays intact, with no duplicate infrastructure. A failed rollout redeploys the last known healthy commit after a receipt; no DNS, token or certificate mutation occurs as part of an asset rollback.

This candidate adds no public assets and does not prove current ChatGPT installation, Cloudflare CDN, Render live route or Godot playback. Source proof is not runtime proof.
