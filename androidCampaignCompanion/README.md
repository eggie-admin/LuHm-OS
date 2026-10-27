# LuHm OS Samsung campaign companion (SOURCE CANDIDATE)

**This wrapper is not a signed APK, F-Droid release, approved public character pack or real device-install receipt.**

- Separate development package `art.eggiebagelface.luhmos.campaignpreview`; never overwrite `art.eggiebagelface.luhmos.beta` or infer update/signer continuity from other package identities.
- Gradle Android Java WebView shell, `WebViewAssetLoader` local `https://appassets.androidplatform.net/assets/index.html` origin and first-party `publicationSite` source-assets. The current public site is an **art-free interim fallback**, NOT the final interactive goth campaign artwork.
- Android only gets a browser for external links. No file scheme, mixed content, remote shell, credentials or automatic video playback.
- The chat-generated private campaign mockup and rights-pending Lum/Big Daddy character masters are **not** included. Stage only an approved campaign HTML/art bundle after #421 private Drive rights and #422 canon gates.
- The signed GitHub Godot beta workflow does **not** build this APK. A companion-specific environment-protected signing job must be independently reviewed before use. Keep the existing owner signer/certificate unchanged; use a separate signer identity only with verified first-install baseline and proper authorization.
- Future signing readiness must verify package ID, versionCode, `apksigner` digest, APK hash, build source, key continuity and Samsung launch/update.
- Minimum development gates: `python3 tools/campaignCompanionSourceAudit.py` then `campaign-companion-source-audit` GitHub Actions `assembleRelease` on exact PR source; this produces only a **not-yet-signed build candidate**.

The companion is independent of the private Project Hydra ChatGPT Site app; GitHub source edits do not fix that Site's in-chat MCP mount.
