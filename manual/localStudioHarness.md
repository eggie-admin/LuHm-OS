# LuHm-OS local studio

LuHm-OS is the Canon product name. `lumEdge`, `lumAvatar`, `lumLocalModel`
and `localStudioHarness` are lower camelHump machine identifiers, not new brands.
Required external spellings (`package.json`, npm package names, `_headers`,
GitHub workflow paths, and HTTP headers) retain their protocol namespaces.

## Run locally without administrator access

From the repository root, with Node 22 and Python 3.10 or later:

```sh
npm --prefix frontEnd/prototypes/lumEdge ci --ignore-scripts --no-audit --no-fund
npm --prefix frontEnd/prototypes/lumEdge run check
python3 tools/localStudioHarness.py
```

Open `http://127.0.0.1:8789/` in the browser on that same machine.
Stop with Ctrl+C. This starts a static preview, not an installed background
service, ChatGPT plugin, native Godot engine, or device-control agent.
It needs no sudo, inbound firewall opening, or provider credentials.
It accepts GET/HEAD only, validates Host, blocks hidden/traversal and escaped
symlink paths, disables directory listings, and uses the compiled CSP.
Do not replace the fixed loopback bind with a public interface.

## Layer sanity check

| Layer | Current scope |
| --- | --- |
| Static HTML | Loading and no-script fallback; compiled output served locally |
| Edge delivery | Static deployment bundle and `_headers`; not a live CDN receipt |
| EdgeHTML | Legacy engine, not a supported modern rendering target |
| JavaScript / Vue / Babylon | Pinned lockfile; tested local model validation and production build |
| jQuery | Existing cockpit dependency; not a second Vue DOM owner |
| Three.js | Not implemented in this viewer; do not claim it is integrated |
| Fonts / CDN | Same-origin font policy and local system fallback; no third-party font dependency |
| Custom domain | Source names `assets.eggiebagelface.art`; live DNS/CDN unverified; do not invent `achiebagelface.art` aliases |
| Godot 4 | Existing native project and separate export lane; this Babylon preview is not Godot gameplay |
| ChatGPT Library | User-directed asset/recovery transfer, not a public CDN or command-execution service |

The existing Godot build remains `tools/buildGodotWebHarness.sh`. Its export,
runtime smoke, hosted behavior and physical device acceptance need separate
receipts. A browser view cannot grant native engine or ChatGPT sandbox access.

Official compatibility references:
- https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html
- https://learn.microsoft.com/en-us/lifecycle/products/microsoft-edge-legacy

## Evidence and rollback

Restart baseline: `384327c13617e9f7543016f80713018c5a8f1a87`.
Existing edge branch was reconciled through merge `a11c119` without dropping
the newer package-build source. PR #541 remains the single implementation lane.
Local tests prove model input checks and HTTP boundaries; they do not prove
Samsung rendering, CDN configuration, production deployment or final approval.
Keep GREEN scoped to observed checks and AMBER for missing runtime proof.
Render deployment requires selection of the intended account workspace.
