# KAI9000 antenna / light candidate

This is an isolated Vue entry point added to the existing Glass World prototype.
It does not replace the working harness, chat plugin, native APK or PR #505's
read-only localhost server. It adds no dependencies and changes no device settings.

## Run

From `frontEnd/prototypes/glassWorld`:

```sh
npm ci --ignore-scripts
npm test
npm run build
python3 ../../../tools/kai9000Antenna.py --root dist
```

Open `http://127.0.0.1:8766/antenna.html`. Build on a development machine or
finite CI job and transfer the resulting `dist` directory to a low-memory tablet;
Node/npm need not run there. The Python command is for local prototype review,
not a LAN/Internet deployment. The existing KAI9000 allowlist does not serve this
new build; it must not be widened blindly.

## Execution profiles

| Profile | Client work | Remote work | Status |
|---|---|---|---|
| antenna | Vue controls, links, request envelopes | Existing service UI opened explicitly | Implemented launcher; remote connectivity unverified |
| light | Optional existing Babylon scene and HTML5 local media | Prefer remote heavy jobs | Existing studio opens on demand |
| Godot Web | Browser executes downloaded WebAssembly and WebGL2 | Static host supplies export files | Not integrated here; not remote GPU execution |
| native studio | Thin control/stream client | Blender/GIMP/FFmpeg/Godot and optional inference | Requires separate worker, transport and device proof |

Antenna loads no Babylon, jQuery, model, video or Godot runtime. Its page does
not fetch configured endpoints or persist addresses. Remote links accept HTTPS,
or literal localhost HTTP only, with no URL credentials, query or fragment.
Opening a service does not prove embedding, shared authentication or playback.
VLC Android and desktop require distinct adapters. Godot Web uses Compatibility /
WebGL2; Vulkan is a separately tested native runtime capability.

## Four-tier and seven-plane preservation

Core contracts -> tool adapters -> Vue widgets -> external boundaries retain
the four internal architecture tiers. The seven compositor planes in
`doctrine/layeredStageCanonV1.json` remain unchanged in the existing harness.
The antenna utility page does not claim to implement that compositor.

The browser emits `luhm:antenna:intent` on `window` with schema
`luhmOs.antennaIntent.v1`. Allowed actions are `inspectCapabilities`, `openMedia`,
`openGodot`, `inspectJob`; allowed targets are `tablet`, `raspberryPi`,
`remoteStudio`. Each request has a unique request ID and `authority: requestOnly`.
No command text, credentials or execution proof is accepted by this contract.
This event is an adapter seam, not an MCP call or an independently running worker.

## Next bridge slice

The included loopback Python adapter serves the built assets and exposes
`GET /api/capabilities`. Click Inspect local Python bridge to use it. It reports
command presence and architecture without running those commands. Host, Origin,
cross-site requests and asset paths are restricted; there is no write or job API.
Implement a separately reviewed remote adapter next.
Use authenticated HTTPS/WSS across machines, explicit origin checks, a bounded
operation allowlist, request IDs, timeouts and versioned JSON responses. Keep
provider tokens host-side. The chat widget and standalone Vue page may share
contracts/assets, but their host transports and permissions remain separate.
Do not assume a ChatGPT iframe can reach tablet localhost.

The later job contract should include source commit, target, asset reference,
size/hash, status and result evidence. Use SQLite for typed metadata and file
references, not video/model blobs. XML is an adapter format for tools that need it.

JSON is the default control encoding. Base64 is optional encoding for small binary
payloads in text-only channels: it adds roughly one-third size and provides no
encryption, integrity, authentication or retry semantics. Large assets stay files;
validate SHA-256 and size at the receiver. Any Base64 decoder must bound both
encoded and decoded sizes and reject malformed input before allocating work.

## Acceptance and stopping rules

Policy tests cover profile budgets, URL scheme/credential restrictions and action
allowlists. Build output must keep the antenna entry free of Babylon/jQuery/scene
imports. Samsung touch, background lifecycle, Pi execution, VLC authentication,
Godot loading and actual ChatGPT host invocation remain device/host acceptance.

Repeat only on a new failure, changed source or unresolved proof target. A count
of repeated passes is not evidence. No flashing, Odin, Shizuku, root, kernel
changes, auto-deploy, merge or release is performed by this candidate.
