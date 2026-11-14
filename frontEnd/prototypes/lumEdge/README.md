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

## Yume source-only graphics hardening
- WebGL2 defaults to a bounded 512px shadow map on coarse-pointer devices and 1024px on desktop, with a visible Shadows on/off control. The WebGL1 fallback remains unshadowed; this is not Vulkan.
- Babylon's glTF 2.0 material importer may render embedded normal and metallic/roughness texture maps. The local intake now validates image/texture indexes and reports map slot counts only, not successful shading.
- No private GLB/texture is uploaded or bundled. WebGL performance, GPU shadows and physical Samsung rendering remain unverified until device smoke.
- Godot 4 native Vulkan and Godot WebGL2 Compatibility remain separate runtime adapters; no Godot export or Site plugin deployment is implied.

## Yume Aramoor browser world, private proof
- The second bundled page is `aramoor.html` (alongside the existing Lum `index.html`).
- Both import the existing pinned Vue/Babylon/npm dependencies; `aramoor.html` reads `game/world/aramoorArchipelagoV1.json` directly from canonical source. No copied or competing authoring registry.
- Nine regions, twelve traversable bridges, seeded procedural geometry, two tide palettes, PBR material with a locally generated 128x128 normal map, bounded Chromium WebGL shadow and glow effects, character/encounter *locations* without borrowed character art.
- In the atlas, tap a neighboring region or use the list to cross a bridge, use **Ghost Tide** to regenerate the alternative scene, and **World View** to reset the camera. Keyboard: **T** toggles tide; **Escape** resets the camera.
- Godot remains the game logic/world authority. Babylon is a private browser **visualization** of the same topology, not a Godot Web export, Live2D/Cubism runtime, or playable end-game.
- Screenshot proof is gated by `.github/workflows/yume-aramoor-chromium-proof.yml`: real Chromium WebGL creation, scene mesh count, click travel, both tide states and two screenshot digests. A GitHub Actions screenshot is not a Samsung physical-device proof.
- The world is a new original atmospheric adaptation inspired by *The Ghosts of Aramoor* (JunkyardTornado, CC BY-SA 4.0). The source module PDF is not included/inspected, so original adventure map/encounters are not claimed. Private-only; any later text redistribution must preserve attribution/ShareAlike and separate character-asset rights.
