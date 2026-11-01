# LuHm-OS · Google Play app delivery (source-gated candidate)

**Scope:** existing Godot 4.7 JRPG, layered cockpit and owner-controlled 2D/3D library. No game rewrite, no account creation, no staged key in Git. **Status:** PRIVATE WEB BUILD VERIFIED / STORE RELEASE NOT READY. **Authority:** Professor.

## Latest observed receipts

- The Professor's exact PR #411 candidate `55a10a74f4101ae557d37081cc671de1ceb74ff1` passed private CAST authorization and Godot Web export run [40240408431](https://github.com/eggie-admin/LuHm-OS/actions/runs/40240408431).
- Two artifacts were uploaded: browser proof and private Godot Web export. I inspected the downloaded browser proof: `rehearsalStage.png` shows four visible **procedural stand-ins** at the Cathedral stage, and `rehearsalInteractions.png` shows BOND 1/9. `proof.json` records `GREEN_REHEARSAL_RUNTIME_INTERACTIONS` plus `LUHM_REHEARSAL_TALK_ROUTE:lum`, `LUHM_REHEARSAL_DANCE_ROUTE:lum` and `LUHM_REHEARSAL_TALK_ROUTE:urd`. It also explicitly reports `playableQuestProgressProven: false`, `touchOnSamsungProven: false`, and `chatGptHostProven: false`. This is not a finished character body, Android installation or store release receipt.
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


## Project Premonition closed-beta delivery decision — 2026-11-01

Status: PROPOSED RESEARCH AND RELEASE PREPARATION ONLY. This update does not certify a built AAB, branding assets, physical phone, Console access, or a live invitation link. It extends PR #425 instead of creating another engine migration branch.

### One app, four bounded responsibilities

| Responsibility | Proposed implementation | Acceptance evidence |
| --- | --- | --- |
| Automation and production | Python for source checks, asset manifests, Blender/FFmpeg orchestration and reproducible receipts | Exact input/output hashes, deterministic checks, preserved editable masters |
| Playable phone app | Existing Godot Android runtime and Java/Gradle integration | Release AAB plus Play-delivered APKs; touch, save/load, resume and offline scene tests |
| Store and release | Google Play internal testing, then an invite-only closed track | Console processing/review status, supported device catalog, actual tester opt-in/install |
| Human creative control | Professor approves character appearance, branding and final release scope; testers report real-device failures | Approved asset provenance, reviewed listing and reproducible feedback |

This is an architectural recommendation based on the existing repository, not a claim that the four layers are deployed. Keep a single product identity and shared data contracts; universal does not mean embedding multiple game engines or running desktop Python tools inside every phone.

### Python-to-Unreal vendor findings

- CPython's Android documentation describes embedding the interpreter in an Android app. It lists packaging helpers including Briefcase, Buildozer and Chaquopy. Adding Python to the phone introduces its own interpreter and native dependency packaging; it is unnecessary merely to reuse Python build scripts.
- Panda3D's 1.11 documentation provides an Android AAB route for Python/C++ applications. It is a credible isolated experiment if a specific Python gameplay need emerges, but it is not a drop-in replacement for existing Godot scenes or evidence that this project builds under Panda3D. Verify the chosen release and dependencies before a prototype.
- Godot already has the project's runtime and Android export work. Finish that vertical slice first. GDScript is its own language; Python source is not automatically compatible.
- Epic's current Unreal Python documentation places Python in editor automation and content production, not cooked gameplay. A later Unreal runtime uses its native gameplay systems such as Blueprint/C++, while Python can continue to prepare assets and automate the editor.
- Preserve engine-neutral dialogue/quest JSON with versioned schemas, original media, animation manifests, units/axis conventions, asset hashes and licensing records. Validate a representative asset import in each target engine; do not promise lossless Godot-to-Unreal conversion.
- Defer an Unreal migration until a measured feature or rendering requirement justifies it and a Samsung prototype meets a defined memory, frame-time, thermal and package-size budget. Engine licensing and the existing open-source preference require separate review before adoption.

References, checked 2026-11-01:
- https://docs.python.org/3/using/android.html
- https://docs.panda3d.org/1.11/python/distribution/building-for-android
- https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html
- https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python

### Branded closed-test preparation

Proposed store title: **Project Premonition**. LuHm OS remains the platform identity. Draft short description: **Explore an early creative world and help shape Project Premonition.**

These are review drafts, not published metadata. Final description and release notes must enumerate only features demonstrated by the submitted build. Do not advertise a completed community RPG, remote AI, finished 3D cast, or video editor without corresponding acceptance evidence.

Prepare a dedicated original launcher icon and store icon, feature graphic and real phone screenshots using approved project artwork. Capture the launch screen, one playable interaction, and settings/accessibility from the exact release candidate. Label procedural stand-ins honestly. Final assets remain pending; an illustration or mockup cannot substitute for a gameplay screenshot. Supply a verified support contact and privacy-policy URL, and derive Data safety declarations from actual application and SDK behavior.

Google documents that listing assets apply across testing tracks. Closed testers join an email list or Google Group and opt in through the real Console-provided link. Before an open test or production release, closed-test users cannot discover the app through ordinary Play search. Do not invent a package URL or invite link. The 12-testers/14-days rule applies to production-access eligibility for qualifying new personal accounts; it is not a waiting period before creating a closed test.

References:
- https://support.google.com/googleplay/android-developer/answer/9845334
- https://support.google.com/googleplay/android-developer/answer/14151465
- https://support.google.com/googleplay/android-developer/answer/9866151

### Signing and phone acceptance

Play uses an upload key for the submitted AAB and an app-signing key for APKs delivered to users. Record both fingerprints separately. A locally signed beta APK is not proof of the Play-installed signature. Confirm package identity and signing strategy before the first upload; distribution through Play and a custom F-Droid repository requires an explicit compatible certificate strategy or separate package IDs. Never assume an upload-key-signed APK can update a Play-installed app.

For the submitted handset build, verify target API against current Google policy (API 36 or higher observed on 2026-11-01), ARM64/native dependency compatibility, permissions and actual supported devices. Collect real Samsung cold-start, frame-time, memory, storage/cache-growth and thermal observations. Test Bluetooth audio reconnection and any supported controller/USB workflow, permission denial, background/resume and a same-channel update preserving saves. Mark unsupported peripherals out of scope rather than passing them.

Normal tester installation should use Google Play on an unrooted phone. GParted, firmware modification, bootloader unlocking and permanent developer-mode changes are not release prerequisites. Developer diagnostics are optional engineering procedures, not onboarding.

References:
- https://developer.android.com/studio/publish/app-signing
- https://support.google.com/googleplay/android-developer/answer/11926878

### Current bounded handoff

- Canonical main observed: f0cb6ee54066b490c0e80efc2c96200fec76ee2d.
- Existing Play proposal before this documentation update: PR #425 at 456b600e6985637108f3edb3ce988fc57cb5dc63. It is not merged into main.
- Latest observed signed Samsung beta run 39907957047 failed at owner-held keystore with all four signing inputs empty. This historical run proves that attempt failed; current secret values were not accessed.
- PR #378 protected signing hardening remains open and reported mergeable=false. PR #465 adds early diagnostics but does not replace signing protection.
- No usable Play Console publishing integration was found in the plugin discovery results. Account identity, app record, package reservation, upload-key registration and track state remain unverified.
- Next implementation priority: reconcile the protected signing work and add/validate the distinct Play AAB export against the chosen immutable package identity. Then perform an internal Play install before opening the closed test.
- No new build, key provisioning, merge, store submission, invitation sending or deployment occurred in this research update. Roll back this documentation change by reverting its commit; previous code and release gates remain intact.
