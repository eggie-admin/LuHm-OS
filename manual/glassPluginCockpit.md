# LuHm unified glass ChatGPT cockpit

Source contract: `doctrine/glassPluginDockV1.json`
Tools: `luhm_open_cockpit` (full studio), `luhm_open_mobile_cockpit` (small phone surface)
Resources: `ui://luhm-os/cockpit-v2.html`, `ui://luhm-os/mobile-cockpit-v1.html`

## Final intended experience

A single gear icon opens a translucent, sliding *inside-plugin* drawer over the LuHm studio. Its modules are attached cards, not separate apps, browser extensions or privileged background services:

| Module | Canon handoff | When activated through chat |
| --- | --- | --- |
| Music | Lum/jQuery media deck | Plan or control the existing approved player; YouTube and Spotify require supported APIs, user authentication and playback permissions |
| Avatars | Skuld's GoDaddy-labeled Python/avatar tools | Verify provider identity and capability before Python/avatar tool invocation |
| Yume | Yume studio, Sumi provenance and media team | Script, CSS, image, video and brand task cards under content rights and explicit rendering permission |
| Social | Belldandy, Yume and publication review | Draft Instagram/TikTok/YouTube/art posts, review rights and audience; no automatic account posting |
| Admin | Lum, Urd and Skuld | Source truth, GitHub/host releases, quarantine, architecture, rights and status diagnostics |

A module button sends a fixed, owner-visible request to **the current ChatGPT conversation**, using MCP Apps `ui/message` or the supported ChatGPT `window.openai.sendFollowUpMessage` alias when present. Buttons never call an external media/identity API themselves. Missing host capability shows BLOCKED. No autoplay, CDN secrets, remote scripts, unrestricted Python or media copy. All text is displayed using `textContent`, not injected markup.

This is a **modular task launcher**, not evidence that the associated jQuery player, provider plugin, publishing connectors, or model mini-agents are deployed. Unconfigured lanes remain source-only. The five-lead cabinet and full 15-agent roster remain operationally quarantined until individually supervised runtime receipts and Professor approval.

## Cross-device Chrome and kiosk portability

- **One responsive HTML/MCP Apps source** for Android and iPhone, without Safari as the test application requirement.
- Android: Chrome Stable is the reliability baseline; Canary is an optional early compatibility target. A native managed kiosk, pinned-screen mode or supported Chrome deployment policy may caged-app restrict it. Merely hiding browser controls is **not** kiosk security.
- iPhone: Chrome **Stable or Beta** as permitted by the device and availability. Google's official Chrome channels do not list Canary for iOS. On iOS, Chrome is not equivalent to Android Blink/Chromium; browser engines and entitlements vary by region and OS. Do not promise a universal Chromium runtime.
- iPhone single-app control: Apple's **Guided Access**, or supervised-device MDM Single App Mode after an independent management/security approval. A locked-down user-owned iPhone is not a headless browser and should retain a documented accessible unlock path.
- Desktop smoke tests may use headless Chrome for source/DOM automation. **Do not call a mobile/iPhone host "headless" just because the browser UI is concealed**.
- The plugin iframe cannot legally or technically draw arbitrary floating controls over the entire ChatGPT page. The drawer is restricted to its rendered widget; fullscreen and picture-in-picture are optional **host-controlled** modes invoked only by user gesture. If the host does not implement a mode, the drawer stays inline.
- Alex's private iPhone ChatGPT plugin testing remains separate from iPhone browser compatibility. A Chrome session alone cannot install the ChatGPT Site plugin into another account.

## Steps to actually finish deployment

1. Restore GitHub `main` pull-request/non-fast-forward/deletion rules; verify exact integrated CI, independent review and protected merge. Preserve branch identities and no Render/Codex usage.
2. Install the exact MCP version into the **actual connected ChatGPT Site host** or independently approved MCP endpoint. The current personal Project Hydra Site bridge still exposes read-only tools only; GitHub source commits do not alter that Site binding.
3. Prove live ChatGPT resource discovery, initial tool result, opening the gear drawer, five module cards, one user-clicked `ui/message` handoff, keyboard focus/Escape, fullscreen fallback and phone/browser viewport. Check Android Chrome and iPhone Chrome Stable/Beta separately.
4. Attach real approved jQuery media, avatar Python tool, social publishing provider and artwork/rendering adapters as discrete capabilities. Each module advertises only the permissions and provider evidence it actually has. No credentials bundled into source or prompt.
5. Prove **one** actual authorized Lum→specialist→Urd→Belldandy task with exact-source/tool/time evidence; then request the separate scoped agent quarantine release, expanding up to at most three support workers and one mutation lane. It cannot be silently activated by a UI click.
6. For the GitHub Proposed/Beta/Stable downloads use only the already staged verified CAST package and external acceptance gates. A public ZIP is **not** the iPhone ChatGPT plugin installation.

## Safety and accessibility

One obvious settings icon, minimum 44px targets, Escape-to-close, focus return, screen reader labels, reduced-motion support, reduced-transparency fallback, no hidden workers and no automatic user data transfer. Before declaring GREEN, use a current-device ChatGPT **mount receipt**, not merely a successful GitHub source check or MCP status call.

**Status:** `GLASS_DOCK_SOURCE_CANDIDATE` · `CHATGPT_HOST_MOUNT_UNVERIFIED` · `AGENT_EXECUTION_QUARANTINED` · `CROWN_STOP`.
