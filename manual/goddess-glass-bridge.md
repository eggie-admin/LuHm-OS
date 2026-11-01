# Goddess Glass: restrictive DOM → optional remote capability bridge

**This is an integration slice, not another operating-system architecture change.**

Run `publicationSite/goddessGlassStudio.html` as a self-contained interactive WebGL2 studio, with a 2.5D CSS fallback where WebGL is unavailable. Its characters are original preview geometry, not final Unreal or Godot character rigs. The browser never directly opens SQLite, MariaDB, kernel devices, the MCP admin API, or Cloudflare credentials.

The static DOM owns gestures, animation, glass lighting, text/dialogue and character selection. All effects work **offline**. The optional **Check optional bridge** button is the only trigger for same-origin capability discovery. From a local `file://` copy, it reports OFFLINE without a network request. From an authorized same-origin site, it first tries `./api/glass/capabilities` and then the static `./goddessGlassCapabilities.v1.json`; a missing remote service never blocks the stage.

The bridge descriptor is intentionally **not a permission document**. Its strict client whitelist is `glassViewer`, `assetCatalog`, `renderStatus`, `studioReceipts`. The JSON must declare `sqlAccess: BACKEND_ONLY`, `runtime: NOT_ATTESTED`, `writeAuthority: false`. The DOM uses `textContent` for results, not injected HTML, and never stores provider tokens. Fetch is read-only, opt-in, same-origin, no credentials, redirect-denied, time-limited and response-size-limited.

`host/edge/goddessGlassCapabilityWorker.mjs` is a Cloudflare Workers-compatible **source candidate** that serves exactly one public non-sensitive GET response at `/api/glass/capabilities`. No account, DNS route, KV, D1 database, SQL, upstream fetch, action endpoint or Worker deploy is performed. It returns 404 for every other path and 405 for mutations. Its existence in source does not mean the Cloudflare platform is necessary or active.

The actual database remains backend-side only: `host/api/premonitionAssetLedgerV1.sql` defines private asset metadata, and `host/api/typedLanesV1.sql` defines the canonical numeric/text/boolean/AI lanes. A future *authenticated* Python service can read its approved asset metadata and emit an independently reviewed public projection. **Do not expose private asset records, user media, SQL access, raw manifest JSON, or internal task/orchestration routes through the edge.** Browsers should request only public safe descriptors, while all sensitive operations stay behind the private, authenticated host and exact owner gate. Cloudflare may be added as an optional same-origin gateway, not a required compute provider.

HTML and SVG/XML are declarative **presentation and validated data formats**, not command runners. All executable logic stays in vetted local JS or server-side code. No remote scripts are injected into the DOM.

Run from the checked-out repository root:

```sh
node --test tests/goddessGlassDomBridge.test.mjs
```

Offline preview: `publicationSite/goddessGlassStudio.html`. When hosted with `publicationSite` as the site root, the static descriptor remains at `/goddessGlassCapabilities.v1.json`. Deployments and connection to live SQL are **not** authorized by source tests. The source-only UI is not proven installed in the currently connected ChatGPT plugin, and Samsung hardware acceptance remains separate.

**Promotion rule:** No cloud migration, frontend rebrand, schema rewrite, or new vendor just because a feature is requested. Add one narrowly scoped backend capability behind the established contract, test locally and in exact-source CI, then obtain owner approval to deploy it.
