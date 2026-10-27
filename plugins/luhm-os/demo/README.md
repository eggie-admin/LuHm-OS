# LuHm-OS plugin-local CAST demo (source candidate)

This is a **private npm build workspace inside the existing ChatGPT/MCP plugin**, not a new production Node backend, npm publication, Godot replacement, public build or Crown grant.

## Build and test (Node 22+)

```bash
cd plugins/luhm-os/demo
npm ci --ignore-scripts --no-audit --no-fund
npm run demo:build
npm run demo:check
```

The only npm dependency is pinned `three@0.186.1`. The package has a lockfile, no npm lifecycle scripts, and no Babylon/Three dual-engine loading. The build stages `index.html`, `main.mjs`, and only the two Three.js browser ES modules the scene requires, plus a SHA256/byte-count manifest under untracked `dist/`. No external CDN is used at runtime.

When those assets are built **on the same existing MCP host**, its candidate GET path is `/harness/cast-demo/`. The route refuses unknown paths, applies a restrictive CSP, and returns 503 rather than pretending the demo exists if `dist/` is absent. Building this source in GitHub Actions does **not** install the assets on Render or establish an in-chat widget mount.

## First proof

The scene uses generated ring geometry and three color markers, orbit dragging, pause/reset, WebGL2 detection, visibility-aware rendering, reduced-motion support, pixel-ratio budgeting and a safe no-WebGL fallback. There are no agents, secret keys, remote requests, private character/art bytes, vendor AI calls or output publication.

## Live-Cast promotion gate

This candidate remains a read-only rehearsal. Next stages are: exact-head npm build proof; existing MCP host configured to include reviewed `dist/` bytes at a pinned source revision; a real browser/phone scene interaction receipt; a separate in-chat plugin UI proof; and the applicable Professor-authorized single-use CAST and promotion decisions. The canonical `luhm_open_cockpit` experience remains the source of truth and is not replaced.

Use this one scene engine only for the optional web demo. The existing Godot scene stays a separate, independently validated runtime. If Babylon.js is later chosen for a specific feature, switch the renderer behind the module boundary after measuring real load cost, instead of shipping both.
