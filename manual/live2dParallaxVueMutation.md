# LuHm original layered 2D / parallax / Vue 3

Status: source candidate until exact-head CI plus production Render deployment. This is an original 2D vector puppet, not Live2D Cubism and not a licensed downloadable 3D rig.

Existing Python3 Render harness /harness/ contains a real original Lum-inspired SVG character with hair, face, eyes, body, hand and halo layers. CSS custom properties power pointer-only tilt; animation is single-frame scheduled and bounded. Buttons trigger blink, smile, wave, pause. Keyboard accessible, touch scroll not hijacked. Reduced motion, blur and hidden tabs disable pose updates; pagehide removes pointer, visibility and preference events, cancels the frame and clears timers. No external JavaScript, microphone/camera, API calls, downloads, private donor assets or backend mutations.

Existing frontEnd WebView dry-run candidate includes a reusable, chainable $.fn.luhmParallax() plugin, destroyable via $.fn.luhmParallax("destroy"). It uses only locally pinned jquery@3.7.1 and CSS variables and cleans up on destroy/pagehide. This is not proof of a Samsung APK install.

Vue stage: frontEnd/vue/LumLayeredPuppet.vue is a genuine Vue 3 Composition API single-file component (reactive expressions, head pose, pointer clamps, unmount cleanup and reduced motion). It is reference source for a later, reviewed, locally bundled Vue island; it is not injected into production or loaded from an external CDN. The canonical npm lockfile still pins only jquery@3.7.1, and historical vue-headless-cms dependencies are not permitted in the production runtime without exact versions, npm integrity, build receipts and rights review.

Gate: python3 tools/live2dParallaxAudit.py, node --check, npm ci --ignore-scripts plus npm run check; existing desktop Playwright Chromium test also verifies controls and reduced motion in the real Python harness. Live Render, mobile Chrome and ChatGPT-host visual proof are separate from passing source/CI.

Do not change Cloudflare records, DNS, TLS, Render billing, Godot export or autonomous agent permissions for this update.
