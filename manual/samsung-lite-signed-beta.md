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

## Signing governance inspection (current required procedure)

Run this **on the owner-controlled authenticated checkout**, never in a public
workflow or by pasting credentials into chat:

```bash
gh auth status
bash tools/auditBetaSigningPolicy.sh
```

The helper reads only GitHub configuration and *secret names*, checks protected
`main`, required independent environment reviewers, no self-review and
protected branch deployment policy. It rejects repository-scoped copies of
release secrets. It does **not** inspect secret values or claim signing, an APK,
a Samsung install or F-Droid publication.

The signed build also requires a fifth **environment-only secret**:
`LUHM_SIGNING_POLICY_READ_TOKEN`, a fine-grained, short-lived token scoped to
`eggie-admin/LuHm-OS` with **Administration: read-only** and no write
permissions. GitHub's default `github.token` cannot attest protected
environment administrative settings. Rotate the policy token if exposed;
do not paste its value into source or chat. The job checks for independent
reviewers and a protected `main` before accessing the actual beta signer.

The repository owner's GitHub UI is needed to set the release-signing
environment, protection and private secrets. These settings cannot be inferred
from passing source tests. The owner must approve/review the exact intended
release and preserve the same signing identity for all in-place updates.

## 3. Owner approval of signing infrastructure and upgrade history

The owner must configure `luhm-beta-signing` as a **protected GitHub
environment** with required independent reviewers, prevent-self-review enabled,
and deployment restricted to protected branches. The canonical `main` branch
must also be protected. The workflow now checks the live environment and branch,
then fails closed until those settings exist.

Only environment secrets may hold the four stable signing inputs. The owner
provisioning script writes to `--env luhm-beta-signing`, not repo secrets.
Never generate a replacement signer if any prior `.beta` installation might
need upgrading. Keep the keystore and passphrase in owner-held secure custody.

Review `doctrine/androidBetaReleaseBaselineV1.json` and choose exactly one:
- `VERIFIED_FIRST_BETA`: affirm no `art.eggiebagelface.luhmos.beta`
  APK has ever been distributed for upgrading, set `initialReleaseApproved`
  true, keep prior fields null, and record a real evidenceRef.
- `VERIFIED_PREVIOUS_BETA`: record the prior distributed `.beta`
  APK's real versionCode, certificate SHA-256, APK SHA-256 and evidenceRef.
  The candidate versionCode must be **greater**, and the signer identical.

The committed baseline is `UNVERIFIED`, purposely preventing a signed
build until independently reviewed and approved. The guard is run before
export and again against the actual APK version. This static check **does
not prove** tablet upgrade behavior.

## 3. Build one signed candidate using the existing Actions workflow

At `https://github.com/eggie-admin/LuHm-OS/actions/workflows/samsung-lite-signed-beta.yml`, run the workflow on **current main**. Provide `cast` and that full 40-character main SHA. This manually gated build has auto-deploy disabled and uses no public release action.

Required protected **environment secrets**, configured only by the owner from the secure keystore (and the separate policy-inspection token above):

- `LUHM_BETA_SIGNING_P12_B64`
- `LUHM_BETA_SIGNING_PASSWORD`
- `LUHM_BETA_SIGNING_ALIAS`
- `LUHM_BETA_SIGNER_SHA256` (public lower-case signer cert fingerprint)

If secrets are missing, it must fail closed. Never paste private keys/passwords into GitHub files, chat, a public gist, the public Android APK or an F-Droid index. Download the **private workflow artifact** named `samsung-lite-signed-beta-candidate`, which includes `samsung-lite-beta.apk` and `receipt.json`. CI must report owner signer match, nondedug release mode, correct package ID, 64-bit ABI, target SDK and digest. Keep its receipt and exact source SHA.

## 4. F-Droid staging is now part of the same signed build

After the APK signature, digest, SDK, ABI and package checks pass, the **same owner-signed GitHub Actions run** executes `tools/stageFdroidTabletBeta.py` followed by `tools/prepareFdroidRepoCandidate.py`. The `samsung-lite-signed-beta-candidate` workflow artifact then contains `build/signed-beta/` (actual APK and signing proof) and `build/fdroid-beta-stage/` (only that APK, a private metadata draft, and fail-closed receipts). Nothing in this step signs or publishes an F-Droid index or grants public release authority.

The independent source preflight runs both tools with `--self-test` and fails on mismatched hashes, signer, source, version or publication claims. The signing credentials remain in protected GitHub Actions secrets, never in the staged files. If the owner needs to repeat this check offline from an independently acquired APK, the following manual commands remain supported.

## 4. Stage it into an independent F-Droid repository

On an owner-controlled Linux workstation with Android `aapt` and `apksigner`, and the workflow artifact unpacked:

```bash
python3 tools/stageFdroidTabletBeta.py \
  --apk ./samsung-lite-beta.apk \
  --receipt ./receipt.json \
  --expected-signer YOUR_PUBLIC_64_HEX_CERT_SHA256 \
  --expected-source YOUR_VERIFIED_40_HEX_SOURCE_SHA
```

This verifies actual APK bytes and signature, and stages only the approved beta APK into `build/fdroid-beta-stage/repo/art.eggiebagelface.luhmos.beta_<versionCode>.apk`. The sidecar `stagingReceipt.json` is outside `repo/`.

**This does not run `fdroid init`, `fdroid update`, issue keys, approve publication, or claim F-Droid availability.** Configure an independently secured `fdroidserver` repository with its long-lived index signer; sign/update its index only after rights/privacy and owner approval. Host only the verified public repo files at the real HTTPS URL. Confirm repo URL, fingerprint, TLS, hash and an actual F-Droid index before presenting an install QR code.

## 5. Tablet acceptance, then updates

On actual SM-X400 (Android 16) install the candidate through the owner's chosen safe path, launch LuHm OS, check Godot scene, Lum fallback, WebView overlay, touch, rotation, background/foreground resume and network permissions. Capture nonprivate receipt of installed package/version/signer. Build **second release with same package/signer and increased versionCode**; verify Android update without uninstall or app-data clearing. Only then promote a public F-Droid repo installation/update claim.

**Current blockers:** owner-held signer existence/CI secrets, real signed artifact, F-Droid index signer, chosen HTTPS host, device launch/upgrade receipts and exact publication approval. No DNS, Cloudflare, Render or ChatGPT plugin changes are prerequisites for this source branch.

**Separate later enhancement:** A remote AI/Render harness session on the tablet requires a scoped authenticated HTTPS client and network permission. The source-only offline Android proof does not claim that integration already functions.

## Receipt and doctrine contract

`doctrine/samsungTabletInstallV1.json` separates the historical debug virgin install, owner-signed offline beta, public F-Droid route, and ChatGPT plugin installation. The beta receipt is checked against `doctrine/schemas/signedSamsungBetaV1.schema.json`; malformed types, missing/unknown fields and unsupported schema constraints fail closed. Select `--expected-source` independently from the approved build source, not by copying the untrusted receipt. A matching SHA does not itself prove CI or installed runtime. The version floor is a staging constraint; a monotonic update still requires comparing the installed version and signer. Existing rooted Termux delivery remains an optional historical route.
