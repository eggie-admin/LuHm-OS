# Owner-signed Samsung Lite beta lane

Use .github/workflows/samsung-lite-signed-beta.yml for non-debug, upgrade-capable APK candidates. It is deliberately manual, source-pinned, and does not publish a public release. The new isolated package is art.eggiebagelface.luhmos.beta and does not overwrite the .testing developer preview.

Prepare one owner-held persistent Android signing PKCS12 keystore, store an offline backup securely, then configure GitHub Actions secrets LUHM_BETA_SIGNING_P12_B64 (base64-encoded binary), LUHM_BETA_SIGNING_PASSWORD, LUHM_BETA_SIGNING_ALIAS and LUHM_BETA_SIGNER_SHA256 (lowercase hex certificate fingerprint). Never paste keys or passwords into ChatGPT or Git. Godot release-keystore environment variables are used.

From Actions select samsung-lite-owner-signed-beta, Run workflow, CAST word cast, and current full main SHA. Verify run receipt, signer, APK digest, non-debug flag and version before install. Test install, touch, orientation, standby/resume and upgrade from the previous beta signed with the same certificate on an actual SM-X400. Review art rights/privacy/accessibility, then explicitly approve exact digest before publishing a public GitHub beta release. A signed CI APK alone is not beta runtime proof.
