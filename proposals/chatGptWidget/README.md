# LuHm OS in-chat widget, proposed lane

**State:** PROPOSED_ONLY / PRIVATE_REVIEW / CROWN_STOP  
**Source branch:** `proposed/luhm-chat-cockpit-fallback-20261021`  
**Base GitHub main:** `9550701a1dab0830900118ea4cc7f7116c620be9`  
**Source:** `luhmCockpitFallbackV1.html` (single-file HTML/CSS/JavaScript candidate)  
**Owner:** Professor. No automatic promotion.

## Why this candidate exists

The installed *personal Site-backed* Project Hydra plugin can report `luhmConnectionStatus` and return a `luhm_open_cockpit` JSON payload. But the Android ChatGPT host **did not render the intended widget** when tested by the Professor. The runtime resource contract in `host/mcp/luhmHarness.py` declares `ui://luhm-os/cockpit-v2.html` with `text/html;profile=mcp-app`; the currently installed Site bridge is not independently proven to forward the correct resource metadata and HTML. The separate Render MCP app and the Site plugin must not be treated as identical transports.

## What's staged

- Five mobile tabs: Home, Pet, Goddesses, Studio, Tools.
- Layered dark-glass presentation with vertical-scroll parallax planes; reduced-motion handling.
- Local touch/click interaction, pet affection, and a seven-shot storyboard draft with user-triggered JSON export/copy/reset.
- Existing Godot Web player **link only**, not embedded gameplay.
- No external runtime fetches, tokens, personal data, audio/video ingest, cloud storage, privileged tool actions or automatic publishing.
- The interactive cast is a presentation only; autonomous workers remain quarantined.
- No claims that the proposed page is an installed ChatGPT MCP widget.

## Evidence, not promises

Local tests on the candidate source (before the copy into this branch):
- Python `html.parser`: PASS.
- One inline JavaScript block with Node `--check`: PASS.
- Expected five tabs, pet control and storyboard cards: FOUND.
- Android in-chat mount or touch handling: **NOT TESTED / NOT PROVEN**.
- Integrated Site bridge MCP App resource: **NOT CHANGED**.
- The only upload-time text changes were to replace demo status labels with PROPOSED labels.

## Blocked host-binding requirement

To make this work *inside ChatGPT* rather than in a standalone preview, the **existing** Site App `asdk_app_sites_02c066d0b6bc8191ad41051ed5878040` must expose a tool that advertises `_meta.ui.resourceUri` for the existing `ui://luhm-os/cockpit-v2.html` resource, and that resource must be readable by the ChatGPT MCP Apps host as `text/html;profile=mcp-app`. Alternatively bind the current site bridge to the already existing live MCP implementation, after inspecting the Site App source and its security boundary. An arbitrary JSON payload, a website link, or a Render 200 response does not replace the MCP resource and visible host mount.

No Site editor, host shim, credentials, or live plugin mutation has been applied by this proposed branch.

## Acceptance, in order

1. Verify the proposed HTML file from this exact branch and source digest.
2. Pass syntax/content/static scans, checking script injection surfaces and strict origin links.
3. Confirm the **existing** Site App bridge can serve the proper MCP tool metadata and widget resource, or stage a separately reviewed same-identity bridge patch.
4. Test `luhm_open_cockpit` **inside the actual Android ChatGPT app**. Confirm visible tabs, pet interaction, shot editing, and export/copy/recovery behavior.
5. Inspect source SHA, CI checks and any exact deployment receipts. Preserve old Render and plugin release as rollback anchors.
6. Professor explicitly reviews promotion. Never merge/deploy/publish based on this PR alone.

## Scope restrictions

No modification of `host/mcp/luhmHarness.py`, `host/harness/widget.html`, production Render, Site plugin release, default `main`, asset vault permissions, private media, Godot export, external tester access, billing, or agent quarantine. Current widget is intentionally a **fallback preview proposal**, not a certified in-chat solution.

### Related work

- Existing host problem: https://github.com/eggie-admin/LuHm-OS/issues/317
- External-plugin-stack task: https://github.com/eggie-admin/LuHm-OS/issues/366
- Current doctrine: `doctrine/currentSourceTruthV3.json`
- Existing independent MCP harness: `host/mcp/luhmHarness.py`
