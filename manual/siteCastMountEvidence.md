# LuHm-OS · Existing Site App in-chat MCP resource repair gate

**Status:** source-only diagnostic candidate. The installed private Project Hydra Site App has working read-only tool calls, but a successful MCP tool response is **not** proof that ChatGPT mounted its interactive widget. Prior user-visible failures must remain RED until a new owner click/touch receipt is observed.

## Distinguish the two independent surfaces

- **Existing private Site App:** private Plugin Creator / Sites-bound identity `plugin_asdk_app_sites_02c066d0b6bc8191ad41051ed5878040`, version 1.0.14 when last inspected. Its Site `luhm_open_cockpit` runtime contract points at `ui://luhm-os/cockpit-site-v3.html`. The owner-private website/server is not editable via a GitHub PR or Plugin Creator skill archive.
- **Portable GitHub MCP/Render harness:** `host/mcp/luhmHarness.py` registers `ui://luhm-os/cockpit-v2.html` as its own resource with `text/html;profile=mcp-app`. That distinct URI is not by itself an error. Do not deploy the portable harness as a substitute for diagnosing the Site.
- **Mobile Site tool:** `luhm_open_mobile_cockpit` currently returns source data with a `ui://luhm-os/mobile-cockpit-v1.html` locator; successful transport is not owner visual-touch proof.

## Real Site MCP evidence collection

Only an authorized backend/Sites editor or introspection tool for the **same actual Site MCP endpoint** can collect matching sanitized `tools/list` and `resources/read` outputs. A `resources/list` capture is optional: the MCP Apps specification explicitly permits UI-only resources to be omitted from discovery listings. Never commit host tokens, cookies, private media, raw personal information, server secrets, or unreviewed proprietary artwork. Obtain exact tool metadata (especially `_meta.ui.resourceUri` or `_meta["openai/outputTemplate"]`), resource MIME `text/html;profile=mcp-app`, and nonempty HTML from `text` **or base64 `blob`**. MCP Apps allows `ui.csp` to be omitted (the host applies restrictive defaults); when supplied, CSP must be a valid object of domain lists. The resource must be registered on the same connected endpoint advertised by the tool. A `<script>` tag is only a structural hint and **never proof of a working MCP bridge**.

The local guard checks consistency and fails closed:

```bash
python3 tools/siteCastMountGuard.py --self-test
python3 tools/siteCastMountGuard.py \
  --tools /path/to/sanitized-tools-list.json \
  --resource-read /path/to/sanitized-resource-read.json
# Optional, only if the Site MCP endpoint exposes UI resource discovery:
python3 tools/siteCastMountGuard.py --tools /path/to/sanitized-tools-list.json \
  --resources /path/to/sanitized-resources-list.json \
  --resource-read /path/to/sanitized-resource-read.json
```

Without the required **tools/list and resources/read** captures, it reports `UNKNOWN_SITE_ENDPOINT_NOT_CAPTURED`; a missing resources/list is not a failure. With consistent metadata it reports **CAPTURE_CONSISTENT**, not a ChatGPT in-app mount or mobile touch pass. Structural checks alone cannot prove JavaScript initialization or visible interactions; this is governed by the official [MCP Apps specification](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx). Actual ChatGPT owner inline card appearance, controls, Undo/Redo, and Samsung UI proof must be separately observed.

## Blocker and authorized repair

The currently connected Project Hydra tools are **read only**; they do not expose an authenticated Site backend editor or raw MCP `resources/read`. Therefore a GitHub code-only change cannot repair a broken Site runtime. Label this `BLOCKED_SITE_EDITOR_UNAVAILABLE` until a supported Sites editor is connected or the owner uses the actual site editor. Do not create a duplicate app, change permissions, claim public listing, or substitute a Render URL for the genuine ChatGPT experience.

For an approved actual Site edit: repair the existing MCP server in place so the tool resource URI matches the registered UI resource, MIME, CSP and MCP UI bridge; then test the existing owner account in ChatGPT and collect one visible touch/Undo receipt. Public invitation/discovery is an entirely separate review gate. CROWN remains STOP.
