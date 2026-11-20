# LuHm-OS · Existing Site App in-chat MCP resource repair gate

**Status:** source-only diagnostic candidate. The existing Project Hydra integration has working read-only tool calls, but a successful MCP tool response is **not** proof that ChatGPT mounted its interactive widget. Prior user-visible failures must remain RED until a new owner click/touch receipt is observed.

## Distinguish the two independent surfaces

- **Existing Site integration:** the installed Plugin Creator binding `plugin_asdk_app_sites_02c066d0b6bc8191ad41051ed5878040` remains **USER / PRIVATE**, version 1.0.14 when last inspected, with rollback releases retained. The **separate Site backend** was observed with a **PUBLIC Site audience** in an owner-side receipt on 2026-10-27; do not confuse that with plugin discoverability or publish private assets. Its `luhm_open_cockpit` contract points at `ui://luhm-os/cockpit-site-v3.html`. Neither a GitHub PR nor a Plugin Creator skill update edits this backend.
- **Portable GitHub MCP/Render harness:** `host/mcp/luhmHarness.py` registers `ui://luhm-os/cockpit-v2.html` as its own resource with `text/html;profile=mcp-app`. That distinct URI is not by itself an error. Do not deploy the portable harness as a substitute for diagnosing the Site.
- **Mobile Site tool:** `luhm_open_mobile_cockpit` currently returns source data with a `ui://luhm-os/mobile-cockpit-v1.html` locator; successful transport is not owner visual-touch proof.

## Real Site MCP evidence collection

Only an authorized backend/Sites editor or introspection tool for the **same actual Site MCP endpoint** can collect matching sanitized `tools/list` and `resources/read` outputs. A `resources/list` capture is optional: the MCP Apps specification explicitly permits UI-only resources to be omitted from discovery listings. Never commit host tokens, cookies, private media, raw personal information, server secrets, or unreviewed proprietary artwork. Obtain exact tool metadata (especially `_meta.ui.resourceUri` or `_meta["openai/outputTemplate"]`), resource MIME `text/html;profile=mcp-app`, and nonempty HTML from `text` **or base64 `blob`**. MCP Apps allows `ui.csp` to be omitted (the host applies restrictive defaults); when supplied, CSP must be a valid object of domain lists. The resource must be registered on the same connected endpoint advertised by the tool. A `<script>` tag is only a structural hint and **never proof of a working MCP bridge**.

The cockpit guard supplements the already-merged **mobile** Site guard (`tools/siteCastMountGuard.py`). It deliberately does not replace its `luhm_open_mobile_cockpit` validations or regression tests. Both tools require real same-Site endpoint evidence, but examine distinct resource URIs. The cockpit guard checks consistency and fails closed:

```bash
python3 tools/siteCastCockpitResourceGuard.py --self-test
python3 tools/siteCastCockpitResourceGuard.py \
  --tools /path/to/sanitized-tools-list.json \
  --resource-read /path/to/sanitized-resource-read.json
# Optional, only if the Site MCP endpoint exposes UI resource discovery:
python3 tools/siteCastCockpitResourceGuard.py --tools /path/to/sanitized-tools-list.json \
  --resources /path/to/sanitized-resources-list.json \
  --resource-read /path/to/sanitized-resource-read.json
```

Without the required **tools/list and resources/read** captures, it reports `UNKNOWN_SITE_ENDPOINT_NOT_CAPTURED`; a missing resources/list is not a failure. With consistent metadata it reports **CAPTURE_CONSISTENT**, not a ChatGPT in-app mount or mobile touch pass. Structural checks alone cannot prove JavaScript initialization or visible interactions; this is governed by the official [MCP Apps specification](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx). Actual ChatGPT owner inline card appearance, controls, Undo/Redo, and Samsung UI proof must be separately observed.

## Blocker and authorized repair

**Access correction (owner-side receipt, 2026-10-27 18:02Z):** the existing Site was owner-editable using Sites `get_site`, `create_source_repository_write_credential`, and its source helper. `BLOCKED_SITE_EDITOR_UNAVAILABLE` is superseded for that observed surface. The Project Hydra cockpit tools in this ChatGPT connector surface remain **read only** and do not themselves expose those Sites editor actions or raw same-endpoint MCP capture. If Sites actions are absent in a given run, record `SITE_EDITOR_NOT_EXPOSED_IN_CURRENT_TOOL_SURFACE`, not a global assertion that no editor exists. Site version 12 was saved and a deployment was still **publishing** at the previous receipt; inspect its terminal status before any additional deployment. A direct `resources/read` HTTP 401 from a service-access token without visitor identity is **not** proof that the host's registered resource is broken. Collect an authenticated, same-endpoint capture instead. Do not create a duplicate app, change permissions, claim public listing, or substitute Render for the actual Site.

For an approved actual Site edit: repair the existing MCP server in place so the tool resource URI matches the registered UI resource, MIME, CSP and MCP UI bridge; then test the existing owner account in ChatGPT and collect one visible touch/Undo receipt. Public invitation/discovery is an entirely separate review gate. CROWN remains STOP.

## Private test and publication checklist (unfulfilled until separately evidenced)

- Preserve the installed plugin ID, USER/PRIVATE visibility, release 1.0.14, previous release rollback and original Site binding. Do not alter the Site's separately observed audience without specific permission.
- Confirm the existing Site deployment reaches a terminal healthy state; record version, exact source SHA, deployment ID and rollback before another candidate deploy.
- Capture same-endpoint `tools/list`, optional `resources/list`, authenticated `resources/read`, exact `ui://` match, `text/html;profile=mcp-app`, valid optional CSP and initialized MCP bridge. An HTTP 401 from an unauthenticated caller is inconclusive.
- Test actual ChatGPT owner inline mount and mobile 320/390/960 widths, readable labels, no overlap, at least 44px touch targets, keyboard focus, Escape, and visible touch/Undo. Source fixtures and DIL previews cannot replace host evidence.
- Prepare only no-secret, rights-safe demo text and metadata for review. Do not expose private character assets, create guest access, switch plugin visibility, submit a public listing or incur paid usage without separate authorization.
- Keep `CHATGPT_INLINE_MOUNT=UNVERIFIED` and `CROWN=STOP` until the independent owner-host and release gates are met.

### Rights-safe metadata and demo draft (review only, not installed)

- **Existing compatibility display name:** Project Hydra. **Product identity:** LuHm OS / Project Premonition. Do not rename the installed app as part of a mount repair.
- **Proposed short description:** "Private LuHm OS studio cockpit for read-only project status and supervised creative planning."
- **Proposed longer description:** "Inspect connected LuHm OS project status and open the mobile studio cockpit inside ChatGPT when supported. Creative actions, device operations and publishing require separately verified capabilities and approval."
- **Demo script:** In the existing owner account, call `luhmConnectionStatus`, open `luhm_open_cockpit`, then `luhm_open_mobile_cockpit`; distinguish tool text from an actually rendered ChatGPT card. If a card appears, use a visible non-destructive control, keyboard focus/Escape and Undo, and record a sanitized owner-only acceptance receipt. If no card appears, show the read-only text fallback and report `RED_HOST_MOUNT` rather than staging a fake success.
- **Media and permissions:** Use generic original text and blank/synthetic demo content only. No private goddess art, Drive originals, access tokens, visitor identities, guest invites, scope changes, paid provider calls, public listing or promotional claims of a verified host mount.

