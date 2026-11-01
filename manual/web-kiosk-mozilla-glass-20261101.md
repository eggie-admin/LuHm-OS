# LuHm-OS | Mozilla-grade Web Kiosk: DOM first, graphics on demand

**State:** proposed, source-only and sandboxed. No OS-level kiosk lockdown, no Android APK, no remote renderer, no NVIDIA driver, no actual Firefox/Samsung GPU receipt.

The existing glassWorld Babylon + Vue + jQuery prototype is retained. The new **kiosk.html** is a second Vite entry and uses only browser DOM, CSS and original SVG at startup. It loads **zero** Babylon/Vue/jQuery modules until the user presses **Enter 3D studio**. The original `index.html` prototype is unchanged.

## Four rendering layers × four review dimensions

- **0 DOM:** HTML5 forms, text, SVG, accessible UI and 12 bounded local primitive labels. No WebGL needed.
- **1 Illustrated 2D:** SVG, static prerendered backdrops, short animation if allowed. No required 3D engine. Godot's existing First Night fixed-camera 2.5D stage is a *separate game*, not this web renderer.
- **2 Babylon/WebGL:** Babylon owns local 3D geometry, Vue 3 owns inspector, jQuery owns a typed, non-privileged event bridge. Rendering is a 30 fps target, is paused when hidden, tracks WebGL context-loss/restoration and releases meshes/materials on removal and all GPU resources on close. Page unload also releases media `blob:` URLs and Vue/renderer resources.
- **3 Unreal remote candidate:** Later high-fidelity Unreal 5.8 Pixel Streaming from a GPU host over WebRTC, never assumed to be browser-native WebGL. Needs network authorization, identity controls, persistent GPU worker budget, signalling, HTTPS, encoder support, privacy review, latency and cost measurements, and real remote rendered-frame proof. Disabled in this version.

Each tier is reviewed across **source/rights**, **runtime capability**, **input/accessibility**, and **failure/recovery**. Hex `0x00..0x0F` IDs are logical audit coordinates, *not* physical registers, WebGL enum values or kernel addresses.

## Browser safety and host requirements

- `kiosk.html` uses a strong **meta CSP** that limits scripts/styles to same-origin, rejects objects, frames, workers and outbound `connect-src` requests, and permits local `blob:` media for selected local previews. Production hosting should additionally set a strict HTTP CSP, COOP/COEP only when the selected runtime requires them, `X-Content-Type-Options: nosniff`, HTTPS and versioned immutable assets.
- No **inline script**, `eval`, host-wide overlay, microphone, clipboard or camera permissions. The page remains normal web content, not Android Lock Task mode or Chrome managed kiosk. Browser fullscreen is optional and must remain escapable.
- Prefer WebGL2 when available; WebGL1 is permitted as an observed fallback. No GPU means an independent DOM-only scene that still accepts shape placement/clear.
- On context loss, show the DOM fallback and release the heavy renderer. Re-entering 3D requires an explicit page reload/capability check; do not hide the fault. Hidden browser tabs stop the Babylon rendering loop. 30 FPS is a **target**, not a measured performance guarantee.
- No asset URL input, remote GLB import, unrestricted HTML injection, direct AI tool call, public media upload, Unity/Unreal embed or privileged WebView Android bridge. Artist masters and rights remain under the original Canon.

## Dependencies and upgrade notes

Current isolated, exact-pinned package+lock: `@babylonjs/core@9.32.0`, `vue@3.5.44`, `jquery@3.7.1`, `vite@8.3.5`. **Don't upgrade or introduce another framework merely to be current**. Per jQuery upstream as of 2026, jQuery 4.x is fully supported and 3.x receives critical-only fixes. A separate API/deprecation/CSP compatibility test and lockfile review must precede a 3→4 major upgrade. Vue's production build must be used in final Vite distribution, not a development CDN.

[MDN WebGL lost context](https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/isContextLost) • [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy) • [Babylon context recovery](https://github.com/BabylonJS/Documentation/blob/master/content/features/featuresDeepDive/scene/optimize_your_scene.md) • [Vue production deployment](https://vuejs.org/guide/best-practices/production-deployment) • [jQuery 4 upgrade](https://jquery.com/upgrade-guide/4.0/) • [Unreal Pixel Streaming](https://dev.epicgames.com/documentation/unreal-engine/pixel-streaming-in-unreal-engine).

## Minimal test

```sh
cd frontEnd/prototypes/glassWorld
npm ci --ignore-scripts --no-audit --no-fund
npm test
npm run build
# Preview the production output from a loopback-only HTTP server:
npx vite preview --host 127.0.0.1
# Open http://127.0.0.1:4173/kiosk.html
```

The source CI must prove **both** `dist/index.html` and `dist/kiosk.html` are present, the kiosk has CSP and no third-party script/style URL, and the pure fallback/close/context-loss negative tests pass. Only the actual physical tablet/browser can prove touch, FPS, thermal resilience, true GPU recovery and a complete art pipeline.

**Installation boundary:** This static kiosk is **not** the Google Play package, nor the ChatGPT plugin's live native game. Keep First Night PR #475 as the parent; merge/adopt only after real tests and separate approval.

**Crown STOP**: no remote Unreal host, no store upload, no public CDN or automatic deploy.
