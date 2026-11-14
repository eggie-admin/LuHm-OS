# LuHm-OS: Vue + Babylon + npm + Cloudflare

Isolated application to preserve the existing Glass World size and vendor budgets.

## Use
```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run check
npm run dev
```

Open the local browser URL and choose a **self-contained .glb** from your device. The model is never packaged into the Cloudflare build, uploaded, or fetched from Google Drive automatically. The default scene uses original procedural geometry.

## Cloudflare Pages preview
- Root directory: `frontEnd/prototypes/lumEdge`
- Build: `npm ci --ignore-scripts --no-audit --no-fund && npm run build`
- Output directory: `dist`.
- CSP is supplied by `public/_headers`.
- Private Google Drive model and textures are intentionally excluded.

## Cloudflare Workers static assets alternative
`wrangler.toml` configures `[assets]` from `./dist`; no server-side model runtime or API. Do **not** deploy without authenticated Cloudflare account, review, rollback receipt and Professor Crown.

Cloudflare is a static delivery edge. Browser JavaScript/WebGL execution cannot bypass the ChatGPT iframe sandbox. Godot APK, native Samsung host, and OpenAI agent execution remain separate gates.
