# One-agent media desk and two visible chat lanes

**Proposal only** · Source anchor `8865dc9756ede173017b56b40a2eb0760649f0a0`. The chat-visible companion has one supervised coordinator, Lum. **Zero autonomous agents run while company-wide quarantine remains active.** These are two UI lanes in one MCP App surface, not two independent threads/processes/ChatGPT sessions.

## Reconciled map

| Existing component | Canon place | Decision |
| --- | --- | --- |
| Browser HTML5 audio/video | `doctrine/localMediaDeckV1.json` | Primary phone/tablet local picker, no upload, no external server. |
| FFmpeg/ffprobe | `host/ai-ffmpeg/ai-ffmpeg.py`, `tools/premonitionMediaPreview.py` | Local inspection and separately approved edits. |
| VLC | `doctrine/premonitionMediaPreviewV1.json` | Optional desktop VLC handoff only when armed. No NPAPI/HTTP server, no claim LibVLC is in APK. |
| Kodi, formerly XBMC | Optional external media-center *adapter* | No Kodi install or JSON-RPC control port by default. Local library browsing later only with explicit access; do not expose Kodi TCP/WebSocket to internet. |
| Plex | Optional external owner-authorized library *adapter* | No Plex server installed. No embedded account token or unauthorized remote library access. |
| Sourcegraph Cody | Optional external IDE code-review assistant | Not connected here; does not become the sole LuHm agent. Personal plan eligibility requires verification. |
| Lum + pet | `characterPetPresentationV1`, `agentLoadingSpriteManifestV1` | Static original fallback glyph and truthful activity bubble; no pretend independent worker. |
| Monitoring | `chatActivityPresentationV1`, `currentSourceTruthV3` | Top pane displays observations only after tool result or user-requested same-origin check. No hidden polling. |

## One-agent / two-lane composition

**TOP / monitorThread:** pinned first and compact; read-only source truth and actual connection result. Default VERIFY; no simulated green light, polling, cron, token refresh, background model run or invented percentage. User may request a same-origin source check in the standalone harness. In-chat MCP widget reads its already-received tool result; it cannot control the host ChatGPT UI.

**BOTTOM / petChatThread:** shows Lum's original fallback companion with a three-line bubble. The bubble can show IDLE, VERIFY or BLOCKED, with an accessible visible speaker/expression. A user gesture sends a chat follow-up where host supports it. Loading animation can only mean the current UI is awaiting a response, not model/agent progress. Reduced-motion settings disable ornamental animation. No third-party anime likeness or unapproved private artwork is shipped.

## Real execution law

`Professor → ChatGPT single Lum-coordinated turn → read-only tool evidence → Yume/Skuld/Urd/Belldandy as *in-chat role labels* → Professor decision`

Any genuine worker release or publishing follows Canon's exact-source tool proof, quarantine exit receipt, CI/device tests, and Professor authority. No new remote daemon, web player plugin, Kodi controller, Plex media server, credential cache, or background inference is needed for the working first slice.

## Hardening and acceptance

- Check two visual lanes on mobile and desktop, top above bottom, keyboard/ARIA, no overflow, reduced-motion, and crash-safe fallback.
- Render no `PASS` without actual tool proof. The current on-demand check can establish only *harness availability*, not GitHub CI, device, or agent runtime.
- Preserve existing studio, Godot, media picker, video, artist projects and private masters.
- Keep existing same-origin CSP, explicit user input, HTTPS/allowlist, and media license gates.
- Source-only tests must pass on the exact branch. Deployed MCP resource and mobile ChatGPT rendering require separate receipts.

**Status:** CANDIDATE / Crown STOP. Source file: `doctrine/oneAgentMediaTwoLaneV1.json`.
