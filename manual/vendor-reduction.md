# LuHm-OS: Project Premonition | Vendor Reduction Mutation ③

**Source baseline:** main `b1ec72e508819e6d5f8532fdb96931826b867c29`. This mutation applies *dependency-profile and measured static-bundle budgets*; it does not uninstall any host packages, run `apt`, change the Android vendor kernel, or replace the accepted jQuery cockpit. The playable 3D creative goal takes priority over building an unnecessary microservices fleet.

## Current source facts, not hypothetical removals
- The Samsung target is a **signed Android app + packaged web assets**. The APK must not require Termux, a JavaScript/npm runtime, a Python daemon, MariaDB server, NGINX, DNSmasq, GParted, Rufus, Blender, VLC Desktop, or a Linux distribution install.
- The existing `.devcontainer/Dockerfile` is an intentionally heavy **Linux studio** containing Blender, GIMP, Godot, FFmpeg, NGINX and MariaDB. It is *not* the headless core or the APK; do not remove those tools from the studio without a usage and workflow analysis.
- The minimal **headless control profile** uses Python 3 standard library and optional SQLite, then routes to approved studio services only as needed. MariaDB server and DNSmasq are optional **Linux-host services**, never assumed to be Android APK services.
- The standalone Babylon/Vue/jQuery demo is an offline-capable **web bundle** with exact pinned npm dependencies and a committed npm lockfile. Node and Vite are **build-time tools**, not APK runtime requirements.
- **Direct npm dependencies:** Babylon Core 9.32.0, jQuery 3.7.1, Vue 3.5.44. **Build dependency:** Vite 8.3.5. The lockfile currently contains 61 non-root package records, including transitive and platform-specific build dependencies. These are **not all APK runtime dependencies**.
- The first Babylon prototype emitted a 7,002,826 byte main JS bundle; deeper module imports reduced that to 1,220,288 bytes (about 313 KB gzip). These measurements are from **CI source builds**, not Samsung runtime.
- License metadata and sha512 lockfile integrity are supply-chain inventory only. They do not replace a vulnerability scan, Android redistribution review, media codec clearance or reproducible APK verification.

## Remote CI and exact-source proof
```bash
python3 -m unittest discover -s tests -p 'testVendorReduction.py' -v
cd frontEnd/prototypes/glassWorld && npm ci --ignore-scripts --no-audit --no-fund && npm run build && cd ../../..
python3 tools/vendorReductionAudit.py --dist frontEnd/prototypes/glassWorld/dist --output build/vendor-reduction/receipt.json
```

The audit enforces:
- exact direct dependency and lockfile agreement; runtime/build dependency classification,
- license and integrity fields for locked packages, refusal of unexpected lifecycle hooks,
- Babylon deep imports (to prevent the earlier 7 MB barrel-import regression),
- no CDN scripts in packaged static HTML,
- deterministic file SHA256 and compressed-size receipt,
- `<1,600,000` bytes for main JavaScript; `<1,800,000` bytes total JS; `<20,000` bytes CSS.

**A passing audit means the source dependency and build-size policies were met.** It does **not** mean the Android device can load the 3D scene, has media codecs, or that Godot's native glass avatar composes correctly over the WebView.

## Artist-first subsequent gates
1. **Brand #435:** align exact case-sensitive `LuHm-OS: Project Premonition` and funding copy without rewriting historical identifiers.
2. **VLC #436:** HTML5 default media player, optional patched desktop LibVLC/Python bridge and verified FFmpeg output handoff; no VLC daemon or credentials exposed to browser.
3. **Babylon/Godot #439:** actual Samsung WebView FPS, alpha, avatar and object placement measured with approved assets.
4. **Final Cathedral:** signed Android APK, same-signer update and stable rights-reviewed demo with Professor acceptance.

**No infrastructure or source-only CI result grants final Crown.**
