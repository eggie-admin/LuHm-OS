# LuHm OS · OpenAI remote MCP Apps compatibility and debug lane

**Source-only staged:** 2026-10-26. **Goal:** make the existing LuHm artist cockpit work inside ChatGPT on Android, then admit one authorized outside tester. Do not invent an alternate Site, delete the owner plugin, route users to a website in place of the in-chat experience, or treat a passing GitHub Actions run as Android host proof.

## Official current integration contract

Read these current OpenAI references before changing MCP metadata or submission:
- [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server)
- [Add UI to your MCP server](https://developers.openai.com/plugins/build/chatgpt-ui)
- [Troubleshooting](https://developers.openai.com/plugins/deploy/troubleshooting)
- [Submission requirements](https://developers.openai.com/plugins/deploy/submission-errors)
- [UI guidelines](https://developers.openai.com/plugins/concepts/ui-guidelines)
- [Plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines)

The portable GitHub LuHm plugin references the existing Render **HTTPS Streamable HTTP** endpoint at `https://luhm-os-harness-green.onrender.com/mcp`. It is independently versioned from the private **Project Hydra** Site/App plugin, whose checked release is 1.0.13 and whose backend can only be edited through a supported Site editor. The release has an in-chat operating skill, **not** proof that the custom Site HTML renders.

## What the OpenAI source check enforces

- One existing remote MCP connection, HTTPS with `/mcp`, stable public endpoint, read-only tools and clear annotations.
- Exactly three starter prompts, each one line and at most 128 characters. Previous seven prompts are preserved in [the archive](pluginStarterPromptArchive.md).
- Five positive and three negative remote-MCP review scenarios; package title/description/developer name, branding, HTTPS website/support/privacy/terms.
- Actual tool-descriptor `_meta.ui.resourceUri` and optional `openai/outputTemplate` map to registered `ui://` resources with `text/html;profile=mcp-app`. No arbitrary external JavaScript, explicit CSP domains, narrow permissions.
- Standards-first MCP Apps `ui/initialize` and `ui/notifications/initialized`; make the component useful even if ChatGPT refuses to mount it by returning bounded human-readable data.
- Static source tests are **not** an OpenAI-host scan, domain verification, app-store approval, screen capture or end-device acceptance.

## Four isolation steps, in order

**1. Source and offline smoke.** Run `python3 tools/chatGptRemoteCompatibilityAudit.py`, `python3 -m unittest tests/testChatGptRemoteCompatibilityAudit.py tests/testLuhmMountProbeContract.py -v`, then the existing `tests/testMobileCockpitEvidenceContract.py`. The `LuHm OpenAI Remote MCP Apps Compatibility Audit` workflow checks exact PR head. Do not merge on unknown checks.

**2. Verify the actual GitHub-managed Render MCP separately.** Run the existing read-only `python3 tools/inChatLiveMcpProbe.py --report in-chat-public-mcp-probe.json` on approved CI. This performs `initialize`, `tools/list`, `resources/read`, checks MIME/HTML and scans the fixed HTTPS endpoints. Check the **report content** for failures; the observer intentionally returns 0 even when remote observations fail. Its verdict applies only to the GitHub-managed Render server, not the private Project Hydra Site.

**3. Isolate an MCP App mount, one small thing at a time.** Candidate tool `luhm_open_mount_probe` binds `ui://luhm-os/mount-probe-v1.html` to a tiny, isolated 2 KB static HTML page with a single tap target and a minimal host handshake. Distinguish:
- Tool call returns data but no UI card: inspect connected tool descriptor and resource attachment/ChatGPT client compatibility before touching large art.
- Card shows but handshake fails: inspect the host MCP Apps bridge and corresponding client logs.
- Card displays/handshake succeeds but studio fails: isolate the larger widget's JS, CSP, layout, external requests and iframe policy.
- Full studio renders but tap fails: isolate event handlers, touch targets, state hydration.
This diagnostic tool exists in **GitHub candidate source only**; it cannot be called from the current private Site bridge unless the supported Site editor actually registers a matching tool/resource.

**4. Verify the **same** installed private Site backend, not another MCP server.** Current Site tool reports `ui://luhm-os/cockpit-site-v3.html`; GitHub harness source registers `ui://luhm-os/cockpit-v2.html`. This difference may merely reflect separate backends. For the Site, inspect actual tool descriptor `_meta.ui.resourceUri`, `resources/list`, `resources/read` for precisely that URI, registered MIME, HTML bytes, UI CSP, initialization and mobile client console. Refresh/rescan the existing plugin **after** authorized tool metadata or URI changes. Do not rewrite its App ID or confuse a Plugin Creator skill update with a Site backend update.

## UI layout acceptance

OpenAI's inline surface is intentionally small: one purpose, at most two primary actions, avoid deep tabs/navigation and nested scrolling. Start with a simple branded **Open Studio** card or the mount probe; move extensive Winamp-like studio editing to supported fullscreen mode, and use Picture-in-Picture only where the host explicitly supports it. Preserve LuHm character identity while respecting host font, accessibility, contrast, reduced motion and sandbox boundaries. LuHm cannot skin ChatGPT's native thinking indicator or guarantee Android OS-level floating overlays.

## Before Alex testing or directory submission

External accounts cannot use the owner's `USER/PRIVATE` Site plugin merely by receiving a URL, nor does a GitHub invite install a plugin in ChatGPT. Resolve an eligible shared workspace plugin and **Site viewer grant**, or complete provider review/publication for a separately reviewed plugin. Do not solicit or log the tester's credentials. For an authenticated future private tool surface, implement OAuth 2.1, per-user permission and correct token lifetimes before granting access.

Additional required review receipts: verified organization/developer identity, plugin submitter permissions, validated domain challenge at the exact HTTPS challenge URL (no invented token), fresh `Scan Tools`, working Android/desktop UI, a reviewer-accessible demo recording, effective privacy policy including actual recipients and retention periods, rights-cleared original art, screenshots only if applicable, five positive and three negative tests, release notes and the Professor's publication decision. Nothing in this source lane fabricates these external receipts.

## Ownership, handoff and Stop

- GitHub: public-safe source, exact SHA CI, limited artifacts and rollback anchor.
- Render: existing server and independent deployed commit evidence. No deployment needed solely for a source-only audit.
- Cloudflare: root-domain `/mcp` and `/assets/` are separately proposed; do not change the working Render hostname or create a Worker until HTTPS/MCP streaming/caching are tested.
- Project Hydra Site: preserve private identity/version 1.0.13 and existing skills; backend editor is **not exposed in currently connected tools**.
- Android ChatGPT: owner-supplied screenshot is currently **RED**; no owner/touch acceptance claim.
- First outside tester: **BLOCKED** pending genuine sharing/access and owner GUI proof.

**Next dev debug action:** obtain supported existing Site backend edit capability, read the registered tool/resource pair and fix that pair in-place. No blind CAST loop. `CROWN=STOP`.
