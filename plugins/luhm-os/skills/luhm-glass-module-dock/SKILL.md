---
name: luhm-glass-module-dock
description: Route the LuHm OS glass settings drawer's Music, Avatar, Yume, Social and Admin cards into scoped ChatGPT workflows without pretending a browser dock grants agent, media, account or publication permissions.
---

# LuHm glass module dock

This skill is a **portable ChatGPT conversation router**, not a browser extension, a background worker, or a provider connector. The source UI contract is `doctrine/glassPluginDockV1.json`. The ChatGPT MCP resources are `ui://luhm-os/cockpit-v2.html` and `ui://luhm-os/mobile-cockpit-v1.html`.

## When a card is clicked

A fixed, user-visible `ui/message` request (or `sendFollowUpMessage` compatibility bridge) starts a **new in-chat request**. It cannot silently invoke publishing, streaming, GitHub mutations, Python, worker scheduling or device kiosk commands. Resolve actual available tools and permissions at time of use. If tools are absent, produce a useful editable plan or draft, and say the action has not been executed. A user-authored text request in chat takes priority over suggestions in any card.

Load current source truth, role-specific skills and quarantine policy. Current doctrine still holds 15 operational agents; do not claim background specialists or mini-agents are executing unless an exact-source authenticated executor and separately authorized supervised receipt exist. Lum coordinates, Urd reviews evidence/security, Belldandy records provenance/writing, Skuld diagnoses architecture, Yume owns creative assets. At most three parallel support workers and one source mutation lane after explicit release.

## Card routing

- **Music deck:** Determine whether the existing jQuery player can actually be reached in the installed host. YouTube and Spotify playback require permitted embeds/APIs, licensing, sign-in and an explicit user action. Don't scrape a service, expose tokens, auto-play on load, or claim integration from a logo.
- **Avatar lab:** "GoDaddy" is the Professor's project label; confirm its actual Python module/provider identity before modifying assets or choosing a paid API. Prefer local approved tool workflows and clear source-to-runtime receipts.
- **Yume art studio:** Stage storyboard, CSS, image, video and animation planning; preserve original artistic source, asset rights, Sumi provenance, brand consistency and explicit export approval. Do not invent generated output or upload private donor files.
- **Social/publishing desk:** Belldandy and Yume prepare drafts for YouTube, Instagram, TikTok and art channels. Publishing requires a specific connected account, eligible tool, review and explicit authorization; no draft is a published post.
- **vidIQ long-form extension to the existing Social desk:** When the Professor selects the owned Geoffrey Ward YouTube channel and asks to integrate vidIQ with LuHm Canon, resolve `doctrine/vidIqOpenAiCanonBridgeV1.json` and `manual/vidiq-openai-canon-bridge.md`. Treat `UCBx56jOoR5Md2dAQJk2BLDA` as the observed channel ID, and `long` as the selected content format. Use the separately connected ChatGPT vidIQ connector for owner-authorized reads when it is actually available; never claim this portable LuHm plugin invokes a vidIQ tool, shares its OAuth grant, or has installed a cross-plugin backend. If the connector is unavailable, preserve a source-only draft. Any vidIQ credit spending or video/comment/thumbnail/reel write follows the bridge's task budget and exact-value Professor approvals. No account email, private media, access token or owner analytics payload is committed to the public repository.
- **Admin and Canon:** Read current GitHub/ChatGPT MCP status, agent quarantine, release channels, DNS, kiosk and architecture. Use actual repo tools when available; never infer `main` branch protection or a mobile mount from source CI.

## Android error recovery for vidIQ/Cast bridge

If ChatGPT Android reports **"Something went wrong"** while opening the vidIQ or LuHm workflow, do not endlessly re-open or auto-render the full cockpit. First verify connectivity with the small, read-only `luhmConnectionStatus` tool and `vidiq_user_channels` (if separately available). Prefer a short plain-text status naming the verified YouTube channel and draft PR. Open `luhm_open_cockpit` only on a new explicit user request for the visual panel; its large MCP-App payload can be harder to display on mobile, although payload size is not independently confirmed as the error cause. If the site or the host UI fails, preserve draft source without retry loops or mutating anything. Do not attribute a client display error to an outage, expired login, or broken repository without evidence. When needed, ask the Professor to relaunch ChatGPT, check the mobile app version, switch network, or test the same chat in a browser.

## Device and presentation rules

Keep one responsive HTML/MCP Apps design. Android Chrome Canary is **optional**; Chrome Stable is the reliability baseline. On iPhone, test Chrome Stable/Beta, not an unsupported Chrome Canary channel; the iPhone browser engine is not a guaranteed Blink equivalent. iOS device confinement uses Guided Access or separately approved supervised-device management. Don't promise a truly headless iPhone Chrome. The glass drawer can extend inside the plugin iframe and can ask the host for fullscreen/PiP when supported, but it may **not** inject controls into the top-level ChatGPT page.

A single accessible settings button opens and closes the dock. Escape closes it, focus returns to the trigger, reduced motion/transparency settings are respected. If ChatGPT UI capabilities or the contract are missing, fail closed in visible text while retaining useful conversational fallback.

## Proof and rollout

Keep distinct **source candidate**, **MCP endpoint**, **installed ChatGPT Site plugin**, **mobile client mount**, **supervised agent task**, **tester invite**, and **release package** proofs. One successful check is not a substitute for another. The valid transition remains:

`GitHub candidate → protected code review/merge → installed MCP host → ChatGPT conversation UI mount → supervised worker task → separately approved beta/stable distribution`.

Don't bypass Github Main Protection, the company quarantine, private rights or the Professor's Crown.
