# LuHm-OS Vue + Babylon Cloudflare edge candidate

- Existing frontEnd/prototypes/glassWorld stack: Vue 3, Babylon.js, Vite/npm.
- Cloudflare serves static JS/CSS/HTML; JavaScript executes inside the consenting visitor's browser, not in the edge worker and not by bypassing the ChatGPT host sandbox.
- Lum local GLB file: user selects the extracted file on their device. Input capped at 20 MiB; only glTF 2.0 binary with embedded resources and supported codecs passes the bounded intake. No automatic Google Drive fetch, server upload, telemetry, file persistence or public model included.
- World remains an original Babylon procedural preview. Imported Lum is a separate browser-local renderer. Godot / Android APK / OpenAI agent runtime are **not connected**.
- Cloudflare Pages project root: `frontEnd/prototypes/glassWorld`; build command `npm install --no-audit --no-fund && npm run build`; build directory `dist`. Prefer a PR preview, not production.
- Cloudflare Workers static assets alternative: from this folder run `npm install && npm run build && npx wrangler deploy` **only after auth, audit, approval, domain, rollback, and preview proof**. This candidate includes `wrangler.toml`, but no credential or deploy call.
- The Cloudflare Pages `public/_headers` file is copied into `dist` by Vite. Worker static asset handling of custom headers needs separate verification if choosing Workers instead of Pages.
- Strict CSP: same-origin scripts, no eval, no third-party script fetch, blob/data for local-file content. If the ChatGPT App iframe forbids script or WebGL, do **not** try to override the parent iframe policy. Open the independent HTTPS preview or use the previous static fallback.
- Source and CI do not imply private MCP UI mount or native Samsung/DeX validation.
- Safety: preserve existing Canon, quarantine 15 independent workers, leave Crown STOP, and avoid publishing private artwork.
