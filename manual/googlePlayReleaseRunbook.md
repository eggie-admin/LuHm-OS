# LuHm-OS · Google Play app delivery (source-gated candidate)

**Scope:** existing Godot 4.7 JRPG, layered cockpit and owner-controlled 2D/3D library. No game rewrite, no account creation, no staged key in Git. **Status:** PRIVATE WEB BUILD VERIFIED / STORE RELEASE NOT READY. **Authority:** Professor.

## Latest observed receipts

- The Professor's exact PR #411 candidate `55a10a74f4101ae557d37081cc671de1ceb74ff1` passed private CAST authorization and Godot Web export run [40240408431](https://github.com/eggie-admin/LuHm-OS/actions/runs/40240408431).
- Two artifacts were uploaded: browser proof and private Godot Web export. Neither is an Android package or device installation receipt. Chromium canvas and keyboard dispatch are not four-character gameplay, Samsung touch, or ChatGPT-host proof.
- The existing `Android Proposed` export preset is a disposable testing APK: `art.eggiebagelface.luhmos.testing`, versionCode 116, source target SDK 36, ARM64 and blank dedicated launcher icon fields. It is **not** a Play AAB and must not be relabeled.
- Original Lum biped and running-clip GLBs live in private Drive; release rights and final artwork approval are pending. Urd, Belldandy and Skuld have design sources but no reconciled accepted game-ready 3D bodies. Public Web uses a procedural fallback intentionally.
- The existing GitHub Android workflow uses a freshly created disposable testing keystore and explicitly disables public prerelease publication. Do not reuse this identity for Google Play.
- Render services exist, but their `main` previews are not automatically redeployed from PR #411 or its private CAST output.

## A. Play artifact and identity

1. Preserve existing `Android Proposed` APK for isolated device testing. Do not overwrite the `.testing` package or uninstall/clear app data as an upgrade shortcut.
2. Get Professor approval of **one immutable stable package ID**, candidate `art.eggiebagelface.luhmos`. This is a separate identity from `.testing` or `.beta`. Check Play Console availability before locking it.
3. In a **separate scoped source PR**, add a Godot Android **Google Play Release** export preset using Gradle/custom build and AAB output, with target SDK >= 36. Godot docs require AAB for new Play apps. Never claim a valid AAB merely because source options or a debug APK exist.
4. Use a durable owner-controlled release upload key via an approved secret store. No keystore material, passwords, signing secrets or private donor GLBs in Git, GitHub PR descriptions, public CI logs, ChatGPT messages or public binaries.
5. Produce a new reviewed AAB from exact source. Independently record AAB SHA-256, package/application ID, versionCode, min/target SDK from the actual artifact, signing certificate lineage, exported permissions and component visibility. Bind those receipts to one source commit and build run. Keep the signer stable across upgrades.
6. Verify dedicated branded launcher icons (including adaptive icons), game start, Back/Exit path, minimum contrast, touch controls, rotation and resumed-game recovery. Preserve existing JRPG skeleton and seven-plane UI.

## B. Device before storefront

- Prefer one **non-root physical Samsung** install of a separately signed developer/beta APK with SHA-256 and Android package identity checked.
- Test cold launch, scene entry, character TALK/DANCE, save/bond and quest continuity, hardware/software Back, immersive mode recovery, background/resume, audio controls and performance. Record bounded proof video/screenshots and crash logs with no secrets or private family media.
- Install the **next** same-ID higher-version beta over the existing beta **without uninstalling**, proving signer lineage and intact data. First install alone is not an update proof.
- Art / licensing lane: inventory each private Blender/GLB/Live2D-style source; map SHA-256, license/author, likeness and visual canon approval before any public integration. Do not silently substitute public third-party copyrighted character art or soundtrack.

## C. Google Play Console gates

- Android 16 target API 36 is required for new handset apps and updates from August 31, 2026. Verify against the built AAB and the current Play submission rules.
- Complete developer identity, payments/organization requirements if relevant, Play App Signing, privacy-policy URL, Data safety, target audience, content rating, ads declaration, app-access instructions, store artwork and screenshots, support contact and Play policy review.
- For **new personal Play developer accounts created after November 13, 2023**, Google requires a closed test with at least **12 continuously opted-in testers for 14 days** before applying for production access. Actual account type/eligibility is unknown; do not claim the condition is satisfied.
- Google Play **internal test first**, then closed test/production only after actual Play Console status and Professor's reviewed release decision. There is currently **no Play Console upload receipt**.

## D. Commands and stop line

Run the read-only source gate:

```bash
python3 tools/googlePlayReadiness.py --self-test
python3 tools/googlePlayReadiness.py --require-ready
```

The first command should pass its negative controls while truthfully listing missing evidence. The `--require-ready` command intentionally exits nonzero until independent release proofs actually exist. It is *not* a substitute for evaluating the final AAB.

**Prime law:** AI proposes. Policy authorizes. CI proves. Human promotes. A Web CAST never authorizes an Android release, store submission or publication.

## Authoritative external requirements (verify again at submission)

- Godot Android export / AAB / stable keystore: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html
- Google Play target API: https://support.google.com/googleplay/android-developer/answer/11926878
- New personal-account test: https://support.google.com/googleplay/android-developer/answer/14151465
- App content declarations: https://support.google.com/googleplay/android-developer/answer/9859455
