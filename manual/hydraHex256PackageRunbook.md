# Hydra Final Form: HEX 256 -> 512 -> 1024 and four package families

2026-11-14 source candidate. CROWN STOP. Current GitHub main and currentSourceTruthV3.json remain authoritative. Project Premonition is current development identity; Project Hydra is its historical alias.

## Correct mathematics

The legacy hardSystemAudit200.py is still a useful 200-check regression script. It is NOT the Final Form escalation scale. The machineCanonFourLoop.py source audit is still an independent 4x4 check.

Final Form counts assessments, NOT passing tests or AI workers:

| Scale | Shape | Hex | Meaning |
| 256 | 4 families x 1 profile x 4 gates x 16 controls | 0x000..0x0ff | base formats |
| 512 | 4 families x 2 profiles x 4 gates x 16 controls | 0x000..0x1ff | second distro / architecture |
| 1024 | 4 families x 4 profiles x 4 gates x 16 controls | 0x000..0x3ff | expanded distinct variants |

Each assessed slot has a package, profile, gate, control and evidence pointer. Assessed does not mean GREEN. The lifecycle gates are source, build, verify, release. Source-only checks may be GREEN_SOURCE; missing external proof stays AMBER; promotion is BLOCKED_CROWN.

## Shared package identities and evidence

- Debian/Ubuntu .deb: Architecture all, browser-only HTML/CSS/JS and local jQuery 3.7.1. Real unsigned CI candidate can be built by tools/buildHydraWebPackageCandidates.sh. No post-install hooks, daemon, APT repository, system installation or distro proof.
- macOS .dmg: tools/buildHydraMacDmgCandidate.sh is an opt-in macOS hdiutil recipe. It produces a static preview disk image, not a signed native .app, notarized package or deployed agent. Apple Silicon, Intel and universal release proofs are outstanding. No automatic paid Mac runner.
- Samsung/Android .apk: reuse the existing AndroidWeb3Plugin Gradle project and exact-CAST android-testing-build.yml. Historical debug artifact evidence binds only its old source SHA; library AAR is not APK, and device installation, stable signer and update are separate gates.
- npm .tgz: private static preview packaged from existing frontend scripts, never published to a registry. Preserve frontEnd private:true, the npm lockfile and minified jQuery LICENSE. Additional Glass World, Lum Edge, and portable plugin profiles are distinct and require separate evidence.

The 16 controls are: exactSource, canonAuthority, workerQuarantine, packageInputFiles, artifactDescriptor, toolchainAvailability, dependencyLock, browserRuntime, typedSqlJsonManifest, googleCompatibility, storageBoundary, rightsAndLicenses, artifactDigest, installAndRollback, deviceOrHostSmoke, professorRelease.

## Google and Canon source authority

GitHub is the exact source, PR and CI translator. Google Drive is durable private binary file storage, not source or Crown authority. The Drive master folder was externally observed with anyone/writer access; private binaries or SQLite must not be sent there until permission is restricted and verified. Google AI is an optional provider adapter; the current Canon proxy forbids live egress and model execution. OpenAI/Lum provides supervised chat orchestration. Fifteen registered worker routes remain quarantined.

Source law: AI proposes. Policy authorizes. CI proves. Human promotes.

## Fast build and receipt

On an exact clean checkout of the candidate commit:
- Run python3 -m unittest discover -s tests -p testHydraHexReleaseAudit.py -v
- For each slot count 256, 512, 1024 run tools/hydraHexReleaseAudit.py with --slots and --source-ref equal to git rev-parse HEAD.
- In frontEnd, run npm ci --ignore-scripts --no-audit --no-fund; then npm run stage:jquery.
- Back at repository root run bash tools/buildHydraWebPackageCandidates.sh /tmp/hydra-package-candidates.
- Verify SHA256SUMS, Debian contents and npm tarball file inventory. These are temporary CI candidates, not installed software or durable storage.
- The macOS DMG script runs only on an approved macOS machine. Android APK keeps its existing separately guarded workflow.

Continue the everlasting covenant states in order: sanityCheck, audit, ingest, mutation, test, apply, continue, deploy. A source change starts a new evidence identity. Snapshot and rollback do not create release authority.

Rollback branch: snapshot/hydra-before-hex256-unified-packages-7c27ba88.

Missing external receipts, rights review, Drive security, Google AI authentication, macOS signing, APK installation, private npm publication and physical-device tests remain independent AMBER/BLOCKED gates. CROWN STOP.
