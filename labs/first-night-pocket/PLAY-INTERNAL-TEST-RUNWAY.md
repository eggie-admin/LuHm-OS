# First Night • proposed → Google Play internal sharing (no fake install links)

**Current state:** draft source only, not a store-hosted beta. Owner: Professor. This is a **link-to-install runway**, not permission to publish or activate signing. Protected main, private assets and existing beta keys are unchanged.

## Simplest route for one Samsung test

1. **Source:** Review draft PR #475. First Night HTML5 sketch and Godot 2.5D fixed-camera stage are distinct; the Godot app hub has a proposed 2.5D launch button. The five-step First Night Godot quest remains canonical in `game/story/firstNightQuest.json`. All stage art is newly authored geometric placeholder art.
2. **Prove source:** Run the existing `Gameplay Vertical Slice Source Audit`, including HTML state machine, Godot import, 2.5D scene smoke and inspect game-hub route. Treat green only for the exact commit.
3. **Build a fresh Android binary:** An approved and reproducible GitHub Actions Android job must export a **new ARM64 APK from that exact approved source**, using a disposable testing signer (for first-install Internal App Sharing) or owner-owned signer (for updates/long-term beta). Inspect APK SHA-256, signature, package ID, target SDK, ABI, included scene, debuggable flag and file set. Do not reuse historic October 5 Android Web3 prerelease: its notes say functional smoke tests were intentionally skipped, signer was disposable and release intended rooted virgin-install tests.
4. **Google Play Internal App Sharing:** An authorized Play Console uploader uploads the validated APK at the [official Internal App Sharing interface](https://play.google.com/console/about/internalappsharing/). Internal App Sharing re-signs the APK with its own app sharing key and returns a **real unique** installation URL. Store that observed URL only in a private receipt. It does not mean the app is approved for public Play.
5. **Phone:** On Professor's non-root Android device, enable Play Store internal app sharing via Play Store Settings → About → tap Play Store version seven times → enable Internal app sharing. Open the actual link returned by Play Console; install and launch. Confirm visible 2.5D stage, 3D actor movement, return button, original First Night quest, rotation, pause/resume, permissions, battery/thermal and no unwanted upload. Use screenshots, benign device logs and installed package/version/signature receipt for proof.
6. **Iteration:** If the first install works, move from Internal App Sharing to Google Play *Internal testing* using a **proper release AAB** and stable upload/update identity, with compatibility and actual tester approvals. The app ID becomes sticky after uploading a release. Do not promise updates between arbitrary debug-signed APKs, internal sharing re-signing and an owner-signed beta.
7. **Samsung Galaxy Store:** Keep an independent optional beta path. A Seller Portal owner must register app/binary and open/closed tester access to obtain the Galaxy Store beta download URL. Do not assume a Google Play installation can be moved across stores with a different signer.

## Real blockers, not checkboxes to wave away

- The existing `export_presets.cfg` has **Android Proposed**, ARM64 and targetSdk 36, but the current source lane does **not** supply a signed, tested, current-head APK/AAB for PR #475.
- `samsung-lite-signed-beta.yml` uses an owner-controlled long-lived keystore. Earlier exact-source attempts showed four signing inputs absent; PR #465 adds diagnostics but doesn't create secrets. Do not paste credentials in chat or source.
- The Android debug testing-build workflow is historically configured but includes a private art staging step and uses owner CAST, so cannot be silently repurposed for a publishable first install.
- PR #425 separately tracks Google Play AAB production readiness. It is draft; neither branch is implied merged.
- Native Android 16 KiB page compatibility, package/certificate lineage, accessibility, content rating/privacy declarations, rights reviews, Play upload and actual Samsung installation remain separate proof gates.
- `artAssets/` starter ZIP/private Drive is not for direct public publication; no Fallout/Skyrim/Resident Evil copyrighted media or mods are bundled.

## Four-layer 2.5D architecture

| Layer | In place | Still missing for Play link |
| --- | --- | --- |
| 0 Machine | Stock Android ABI path; GPU/CPU/memory/firmware source contracts; no root | Real non-root device / driver and performance proof |
| 1 Engine | Godot GL Compatibility path, original SVG fixed backdrop, 3D capsule actor, input buttons; HDMI/engine not required | APK must include stage, actual Android tap/frame proof |
| 2 Studio | HTML5 scene editor, existing Godot canonical game; Blender/FFmpeg workflow, JSON/SQLite manifests | Rights-reviewed final scene assets and remote build/asset provenance |
| 3 Orchestration | ChatGPT + GitHub draft PR + exact-head CI; Play Internal App Sharing available externally | Signed validated binary, authorized uploader, observed store link and tester opt-in |

**ScummVM/ResidualVM inspiration:** Fixed camera and prerendered art + realtime character mesh, copied as a technique only. Unreal, Nvidia RTX, Bethesda Creation Kit and modding frameworks are potential desktop authoring/reference adapters after this minimum playable mobile engine has evidence. Never require an Nvidia driver for Samsung hardware or present Unreal runtime as already integrated.

**Source law:** AI proposes. Policy authorizes. CI proves. Professor promotes. **CROWN STOP.**
