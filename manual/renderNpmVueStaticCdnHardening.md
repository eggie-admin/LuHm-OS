# LuHm-OS Render / Python3 / npm / Vue3 / static CDN split

**Status:** source-contract hardening; source checks are not proof of dashboard synchronization. Existing services only. No new host, paid plan, Cloudflare DNS, certificate, reverse proxy, Access policy, credential, or agent privileges are requested.

## Existing Render production roles

- `luhm-os-harness-green`: Python 3 MCP/FastAPI-compatible public read-only interface, `/mcp`, `/harness/`, `/healthz`. Keep the build Python-only; it does **not** include the Godot export.
- `luhm-os-godot-harness-green`: Python 3 plus the SHA-verified `tools/buildGodotWebHarness.sh` compile/export pipeline. Godot Web runtime is available at `/harness/godot-export/index.html`; procedural public-safe models only. A good build does not prove every scene or animation.
- `luhm-os-publication-site`: existing Render *static* site. Render already supplies a global CDN and TLS on its .onrender.com origin. HTML and unversioned assets revalidate (`Cache-Control: no-cache`). Security header additions in `render.yaml` are desired state and **have not been applied to the live dashboard**.

`render.yaml` describes the three existing service identities. **Do not re-import blindly** because that could create duplicates; reconcile existing Render service settings first. Actual current web service healthCheckPath is empty; Blueprint `/healthz` is desired only. Maintain manual, source-SHA-gated deploy and rollback.

## JavaScript/npm and Vue 3

`frontEnd/package.json` and `package-lock.json` pin local `jquery@3.7.1`, install by `npm ci --ignore-scripts --no-audit --no-fund`, verify `npm run check`, and stage locally with `npm run stage:jquery`. Serve JavaScript and styles **same-origin**. No production jsDelivr/unpkg/CDN imports or unreviewed donor plugin code.

Vue 3 is **not yet bundled in canonical main**. The separate `eggie-admin/vue-headless-cms` is reference-only, and its old, loosely versioned dependencies are not automatically promoted. To add a Vue 3 island, create a separate private, exact-version npm-lockfile build with a content-hashed static output, verify `npm ci` and `npm run build` in CI, then publish *only* approved static assets via the existing publication site. Do not inject Vue into the Python MCP process or Godot runtime.

## Optional Cloudflare edge (unverified)

Keep `https://luhm-os-harness-green.onrender.com/mcp` direct on Render-managed TLS until streaming/chat-host proof allows an explicit separate proxy gate. Cloudflare public-assets proxy, if later activated, must pass account/DNS/TLS/rights proof. Never edge-cache `/mcp`, `/api`, `/healthz`, signed-in responses, cookies, keys, private Rebel art, Godot donor binaries, or unapproved APKs. Cache immutable for long periods only **content-hashed, rights-approved public artifacts**. DNS-only records do not activate CDN caching. No router port forwarding, no public .lan.

## The previous link fault

`publicationSite/pocketLab.html` used the Python-only harness for the 3D iframe. The player instead exists on the **dedicated Godot service**; the Play control and Open in New Tab must both point to the dedicated origin. `tools/renderEdgeStackAudit.py` checks these links, npm integrity, Render roles, source CDN policy, and five deliberate failure cases. `tools/godotEmbedReadinessAudit.py` also checks both links.

Promote source only after exact-head CI green. Updating `main` does **not** automatically update the existing publication branch or Render static site. Manually synchronize reviewed `pocketLab.html` to the publication branch and deploy that existing static site after green checks. Keep previous deploy as rollback.
