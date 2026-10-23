# LuHm OS | Self-Hosted Remote Updates (candidate)

**Authority:** GitHub `eggie-admin/LuHm-OS#main` owns code. OpenAI/ChatGPT remains compatibility layer one and GitHub layer two. This source change is a review candidate, not an Android, CDN, or public release.

## One stable plugin, one update spine
- Existing read-only `/harness/update-manifest.json` (v1) remains unchanged.
- New `GET/HEAD /harness/updates/v2/manifest.json` enumerates audited current-deploy files, exact SHA-256, MIME and bounded-cache content-addressed paths.
- `GET/HEAD /harness/updates/v2/assets/{sha256}/{filename}` serves only exact current-deployment allowlisted bytes. Invalid digest, symlink, active SVG, remote CSS import, missing asset or policy drift fails closed.
- Both endpoints are **metadata and static bytes only**. No POST, executable update instructions, dynamic plugin installation, remote JS bootstrap, service-worker takeover, file-write API, or remote code loader.
- Current deploy does **not** retain prior versions indefinitely, so hashed URLs revalidate after 300 seconds and **are not called immutable forever**. Durable immutable CDN retention is separately gated.

## Fonts, vector and CDN
- The original `luhmSigil.svg` contains inert author-created vector shapes. SVG script, event handlers, foreign objects and external references are rejected. Served with restrictive SVG CSP.
- `fontStack.css` uses a fast local OS stack. No live third-party font domain, `@import`, font redistributions or downloads. Adding WOFF2 requires a rights-cleared, same-origin, hashed asset with recorded provenance and tests.
- `assets.eggiebagelface.art` stays **unactivated** until Cloudflare DNS, TLS, content hash, private-art exclusion and cache proof pass. Existing Render-managed TLS is the live transport.
- Vue/npm/Live2D Cubism runtimes are **not** upgraded by this feed; when approved, they require pinned vendored local bundles, license review and browser/device proofs.

## Android and distribution boundary
- `/harness/updates/v2/manifest.json` reports Android release status as unavailable; it intentionally contains **no APK URL**.
- Proposed signed repo path: `https://art.eggiebagelface.art/fdroid/repo/`, **not live**. Only the Professor-approved index signed by its own repository key, fixed application ID, stable APK signature lineage, verified exact APK SHA, monotonic versionCode, physical install and same-signer upgrade can activate the release lane.
- No automatic APK install, no Android privilege escalation, no distro upgrade, no SQL migration and no production signing from this change.
- Existing single-use Forge CAST requirements apply separately to any APK build.

## Acceptance
`python3 -m unittest tests/testLuhmUpdateSpine.py tests/testSelfHostedRemoteUpdates.py -v`

GitHub CI plus Render exact SHA deploy, HTTPS GET/HEAD and a **ChatGPT-host UI mount** are different proofs. No staging-only source receipt turns those green. Rollback: deploy the previously verified Render commit with the original stable MCP endpoint. `CROWN STOP`.
