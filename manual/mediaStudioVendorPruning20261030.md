# LuHm-OS media cathedral: 4×4 reconciliation / 2026-10-30
**Exact source:** draft PR #463. Contract source only. The 16 matrix cells are NOT 16 hardware or media runtime passes.

## Actual vendor reduction
On the isolated Babylon/Vue Glass World prototype only, replace two jQuery event hooks with browser-native `CustomEvent`. Remove `jquery@3.7.1` from that subpackage's package.json + lockfile (one direct runtime dependency and one locked install record). **Do not remove or rewrite** the separately accepted `frontEnd/jquery/` cockpit and its existing jQuery workflows. Retain the old `jquery-bridge.js` filename as a source compatibility shim, but it now has **zero jQuery imports**. Re-measure compiled bundle size in CI. No new Python, WebGL renderer, package manager, CDN, or streaming library introduced.

## Static WebP and media editing
The isolated HTML5 media deck accepts private local MP4/WebM/audio and WebP/PNG/JPEG/AVIF images through a file picker using `blob:` URLs. Reject SVG/script MIME, overly large files, and fake URL filenames. Revoke object URLs on replacement/pagehide; no automatic upload or playback. This is a preview, **not a media transcoder or validation of bitstream content**. WebP is for compressed/animated preview derivatives, not replacing Blender files or lossless alpha/rotoscope PNG masters. Real Samsung decoding is untested.

## VLC as full embedded program
VLC desktop app/browser plugin ≠ libVLC runtime. Chrome NPAPI plugin support is removed. `<video>`/`<audio>` are the only embedded **browser** playback engines. **libVLC Android** is the target for future native integration once an owner-approved and hardware-proven Android build uses `org.videolan.android:libvlc-all` (or a reproducibly built .aar) with ABI, version, LGPL compliance, plugin license, vulnerability/SBOM, APK size and same-signer upgrade checks. Do not load or distribute the entire desktop VLC APK as if it were an embedded web player; do not expose VLC HTTP/RC/control ports or bypass rootless Android sandbox.

Official docs: https://videolan.videolan.me/vlc/master/libvlc.html ; https://github.com/videolan/vlc-android ; https://developer.chrome.com/docs/apps/manifest/requirements/ ; https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Image_types .

## 4×4 axis coverage
Rows: AI, 3D, StaticWeb, Runtime. Columns: source identity, rights/security, performance, fallback. `tools/mediaStudioAudit.py` validates all 16 labels and negative controls, the actual package+lock pruning, preserved original legacy jQuery, HTML5 image preview wiring, asset origin restrictions, and separate non-proven libVLC gate. A zero-network CI test checks `/api/health` source only through the existing rootless cockpit tests; do NOT enable remote arbitrary ping/ICMP or provider API scans.

## Chain
Blender editable sources -> approved FFmpeg grayscale roto/mask PNG -> WebP/AVIF preview candidate -> Babylon static world -> Godot proof -> Unreal final EULA-compatible project; libVLC native media optional after a separate AAR/source, size, license and Samsung performance pass; Python stdlib, SQLite and Android remain app-sandbox userspace. Google/OpenAI and other AI remain permission-gated with no unapproved bills, training or uploading private media.

```sh
python3 -m unittest tests.testMediaStudioAudit -v
python3 tools/mediaStudioAudit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/media-studio.json
cd frontEnd/prototypes/glassWorld && npm ci --ignore-scripts --no-audit --no-fund && npm test && npm run build
```
**Evidence rule:** source tests and npm sizes do not imply a Samsung native player, an installed libVLC AAR, a real WebP decoder test, a 3D avatar, or public release. Crown STOP.
