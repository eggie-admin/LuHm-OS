# Repair the existing Project Hydra Site-backed CAST mount

**Scope:** Owner-private ChatGPT Site/App, not GitHub's separate Render-hosted MCP
server. Keep the existing Site, App binding, plugin identity, and private scope.
Do not provision a replacement plugin or grant access to private Drive masters.

## Observed failure

A Site tool response can contain a JSON field named `resourceUri` while the
ChatGPT host has no renderable MCP App resource to mount. The owner previously
reported a *Couldn't open… Retry* UI. That is **RED_HOST_MOUNT**, even when the
tool returned a healthy roster. The GitHub/Render harness is a separate project
and cannot modify the Site app via a commit.

## Exact Site repair contract

On the **existing Site MCP backend**, inspect both `tools/list` and
`resources/read` from that same endpoint. The phone tool must declare:

- `name = luhm_open_mobile_cockpit`
- `_meta.ui.resourceUri = ui://luhm-os/mobile-cockpit-v1.html`
- `_meta["openai/outputTemplate"]` set to that same URI.
- `resources/read` must return one HTML body for that URI with
  `mimeType = text/html;profile=mcp-app`, an initialized MCP Apps bridge,
  and explicit resource `_meta.ui.csp`.

The GitHub implementation is in `host/mcp/luhmHarness.py` and
`host/harness/mobileCockpitWidget.html`. The Site owner may reuse the
*behavioral contract*, but GitHub files do not automatically edit the Site.

The hosted mobile resource on the GitHub candidate now declares the same
`_meta.ui.domain` origin pattern as the full studio resource, while leaving
an absent local-only origin to the host default. This closes a demonstrable
source parity gap. It is **not evidence** the Site backend has deployed the
same resource metadata. OpenAI's UI resource reference says the dedicated
origin is required for submitted UI plugins, and defaults to its sandbox
if omitted: https://developers.openai.com/plugins/reference .

## Branch the diagnosis on evidence, not retries

| Probe on the **existing Site** | Result | Next correction |
| --- | --- | --- |
| `tools/list` lacks `_meta.ui.resourceUri` | RED_BINDING | Register the UI resource URI on the tool descriptor; a similarly named field inside `structuredContent` does not count. |
| `resources/read` cannot read the same URI or returns wrong MIME | RED_RESOURCE | Register and serve the actual HTML resource with `text/html;profile=mcp-app`. |
| URI/MIME correct, but UI resource CSP/domain or bundle wrong | RED_RESOURCE_METADATA | Supply compatible `_meta.ui.csp`, the applicable HTTPS `_meta.ui.domain`, and check CSP/JavaScript errors. |
| Same-Site metadata passes; desktop works but Android fails | RED_MOBILE_HOST | Examine Android ChatGPT WebView or app version, client logs and mobile sandbox differences. |
| Same-Site metadata passes; both Android and desktop fail | RED_HOST_OR_BUNDLE | Isolate JS bridge initialization and ChatGPT host iframe errors, preserving the server's exact resource response. |

The `siteCastMountGuard.py` tests the first three server-side conditions.
It does **not** test real Android/WebView embedding. When the Site's MCP resource
or tool metadata changes, refresh that *same* Site-backed connection if its
provider offers a metadata refresh, and test once in a new ChatGPT conversation.
Do not attempt to fix a Site binding by changing GitHub/Render alone.

Official troubleshooting: https://developers.openai.com/plugins/deploy/troubleshooting .


Use `tools/siteCastMountGuard.py` on sanitized JSON replies **from the actual
Site endpoint**. It detects missing metadata, wrong HTML MIME, and missing
initialization, but intentionally never claims device acceptance.

## Required actual acceptance

1. Publish the resource/metadata fix **inside the existing Site editor** using
   an authorized Site MCP editor, preserving Site identities and rollback.
2. Reload this specific Site-backed plugin in a new ChatGPT Android conversation.
3. Invoke `luhm_open_mobile_cockpit`. Confirm a visible, touch-responsive
   **MCP App card**, not merely status text or a separate webpage.
4. Test switch/tap and correction/Undo; capture a private owner GUI receipt.
5. Keep `CHAT_CAST_PRESENTATION=RELEASED`,
   `RUNTIME_AGENT_EXECUTION=QUARANTINED`, and `CROWN=STOP` until independent
   host/device proof and separate human approvals.

**No Site editor connection?** Source prep may proceed, but declare
`BLOCKED_SITE_EDITOR_UNAVAILABLE`. Do not falsely report a visual fix after
updating plugin skills or shipping a GitHub pull request.

**Privacy:** Private mature artwork stays in owner-scoped Drive. Do not place
it in public GitHub, Render static hosting, issue attachments, or tool telemetry.
