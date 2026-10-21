# Fast Samsung Tab S10 Lite F-Droid beta lane

**Goal:** One installable, update-capable LuHm OS Android beta for the SM-X400, eventually delivered through an independent F-Droid repository. This is the **minimum viable system harness**, not the final full private character pack.

## 1. Already solved in source

- Godot 4 Android with `AndroidWeb3Cockpit` WebView bridge is retained.
- Uses fixed **`art.eggiebagelface.luhmos.beta`** Android package identity, ARM64, target Android SDK 36, monotonic beta versionCode.
- **No Google Drive download or private Rebel/EVE donor archive required during the signed beta build.** The runtime uses existing procedural Lum if no approved GLB is present.
- Signed build still requires **owner-held persistent PKCS#12 Android signer** and a pinned signer certificate fingerprint. Owner keeps offline backup. The first signer used for this beta identity must be retained for updates.
- A direct F-Droid repository has its **own distinct persistent signing key**. Signing and DNS/CDN publication are separate from building the Android APK.

## 2. Fast local source gate

```bash
python3 tools/fdroidTabletSourceAudit.py
python3 tools/stageFdroidTabletBeta.py --self-test
python3 tools/samsung-lite-signed-beta-audit.py
```

The GitHub `samsung-lite-public-beta-source` PR workflow runs this same static gate without downloading Android SDK, Godot, private assets or keys. This test does **not** build or sign an APK.

## 3. Build one signed candidate using the existing Actions workflow

At `https://github.com/eggie-admin/LuHm-OS/actions/workflows/samsung-lite-signed-beta.yml`, run the workflow on **current main**. Provide `cast` and that full 40-character main SHA. This manually gated build has auto-deploy disabled and uses no public release action.

Required GitHub Actions **secrets**, configured only by the owner from the secure keystore:

- `LUHM_BETA_SIGNING_P12_B64`
- `LUHM_BETA_SIGNING_PASSWORD`
- `LUHM_BETA_SIGNING_ALIAS`
- `LUHM_BETA_SIGNER_SHA256` (public lower-case signer cert fingerprint)

If secrets are missing, it must fail closed. Never paste private keys/passwords into GitHub files, chat, a public gist, the public Android APK or an F-Droid index. Download the **private workflow artifact** named `samsung-lite-signed-beta-candidate`, which includes `samsung-lite-beta.apk` and `receipt.json`. CI must report owner signer match, nondedug release mode, correct package ID, 64-bit ABI, target SDK and digest. Keep its receipt and exact source SHA.

## 4. Stage it into an independent F-Droid repository

On an owner-controlled Linux workstation with Android `aapt` and `apksigner`, and the workflow artifact unpacked:

```bash
python3 tools/stageFdroidTabletBeta.py \
  --apk ./samsung-lite-beta.apk \
  --receipt ./receipt.json \
  --expected-signer YOUR_PUBLIC_64_HEX_CERT_SHA256
```

This verifies actual APK bytes and signature, and stages only the approved beta APK into `build/fdroid-beta-stage/repo/art.eggiebagelface.luhmos.beta_<versionCode>.apk`. The sidecar `stagingReceipt.json` is outside `repo/`.

**This does not run `fdroid init`, `fdroid update`, issue keys, approve publication, or claim F-Droid availability.** Configure an independently secured `fdroidserver` repository with its long-lived index signer; sign/update its index only after rights/privacy and owner approval. Host only the verified public repo files at the real HTTPS URL. Confirm repo URL, fingerprint, TLS, hash and an actual F-Droid index before presenting an install QR code.

## 5. Tablet acceptance, then updates

On actual SM-X400 (Android 16) install the candidate through the owner's chosen safe path, launch LuHm OS, check Godot scene, Lum fallback, WebView overlay, touch, rotation, background/foreground resume and network permissions. Capture nonprivate receipt of installed package/version/signer. Build **second release with same package/signer and increased versionCode**; verify Android update without uninstall or app-data clearing. Only then promote a public F-Droid repo installation/update claim.

**Current blockers:** owner-held signer existence/CI secrets, real signed artifact, F-Droid index signer, chosen HTTPS host, device launch/upgrade receipts and exact publication approval. No DNS, Cloudflare, Render or ChatGPT plugin changes are prerequisites for this source branch.

**Separate later enhancement:** A remote AI/Render harness session on the tablet requires a scoped authenticated HTTPS client and network permission. The source-only offline Android proof does not claim that integration already functions.
