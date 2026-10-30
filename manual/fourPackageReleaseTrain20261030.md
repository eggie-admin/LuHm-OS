# Four independent packages | LuHm-OS Crown Cathedral, 2026-10-30

**Source-only candidate. Public release STOP.** One immutable Git SHA flows to four different artifact formats. A CI source green is not a signed package or device proof.

| Lane | Output | Build/authority | Dependencies and readiness |
| --- | --- | --- | --- |
| DEV | `luhmos-dev-source.zip` | GitHub Ubuntu runner, automated | Curated first-party K9000/Python/dev-doc source allowlist. This is a **developer toolkit**, not an APK or playable full Godot game. No private arts/media. |
| npm | `luhmos-k9000-web-0.1.0-candidate.0.tgz` | GitHub Ubuntu runner, automated | Node 22, npm lockfile v3, Vite 8.3.5, Babylon Core 9.32.0, Vue 3.5.44, jQuery 3.7.1. `npm ci --ignore-scripts`, measured bundle audit, source-staging allowlist, `npm pack`. Registry publication OFF. |
| DMG | `K9000-development.dmg` | Owner-triggered GitHub macOS runner only | Godot 4.7.2 stable verified binary/templates, macOS universal preset, built-in ad hoc signature, no notarization. Actual .dmg and executable must pass macOS host testing. |
| APK | Testing APK package `art.eggiebagelface.luhmos.testing` | **Existing CAST-gated** `.github/workflows/android-testing-build.yml` | Java 17, Android SDK 36, Gradle 8.13, Godot 4.7.2, Android Webkit 1.17.1, disposable debug signer. Separate release signing/F-Droid gate. |

## GitHub dependencies
- Protected `main` remains source truth. This draft branches from Kernel 500. PR workflows check the **exact candidate SHA**, not a synthesized merge commit.
- DEV and npm artifact jobs run automatically on PR changes and upload short-lived private CI artifacts with hashes. CI uploads are temporary transport, not the durable archive; Google's Drive is the existing explicit archive after approval.
- macOS **development DMG** workflow runs only with manual `build_dmg=true` and the owner GitHub actor. It is ad hoc signed, not notarized or publicly distributable.
- Android APK remains at the owner/CAST authorization boundary. This package train verifies the existing dedicated workflow and Android build pins; it does not create a second, less protected signer path or publish an APK.
- All build, package and metadata actions run without production credentials. No scripts execute from `frontEnd/plugins/incoming`; don't remove their accepted historical sources.

## Local or CI commands
```sh
python3 tools/fourPackageTrain.py audit
python3 tools/fourPackageTrain.py build-dev
cd frontEnd/prototypes/glassWorld
npm ci --ignore-scripts --no-audit --no-fund
npm run check
cd ../../..
python3 tools/vendorReductionAudit.py --dist frontEnd/prototypes/glassWorld/dist
python3 tools/fourPackageTrain.py stage-npm
npm pack --ignore-scripts --pack-destination build/fourPackage/npm --prefix build/fourPackage/npm/stage
```
`--prefix` on npm CLI may have different behavior across versions; the canonical GitHub workflow runs `npm pack` from the staged directory with a pinned Node setup. Neither `npm pack` nor `npm ci` publishes.

## Release gates
1. Each file is hashed against the same immutable `sourceRef`, recorded as DEV/npm/DMG/APK type.
2. Check licenses, dependency lock, asset hash/provenance, and public rights allowlist before any public deployment.
3. DMG production distribution requires Apple Developer ID signing and notarization; debug/ad hoc signing does not satisfy that gate.
4. APK requires distinct stable release key and physical Samsung install/update proof; a GitHub test run does not imply user device readiness.
5. Owner may elevate individual tracks only after CI, artifact and device proof. No automatic agent unquarantine, cloud provisioning, Github Release, Play Store/F-Droid submission, or npm registry publication.

References: https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_macos.html ; https://docs.npmjs.com/cli/v11/commands/npm-ci ; https://docs.npmjs.com/cli/v11/commands/npm-pack .
