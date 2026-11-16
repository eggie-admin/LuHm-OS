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

## November 16 private beta acceptance after scoped source merges

- Protected main at the start of this audit: `fe4cd2e423b84eb0f94606eaf604d8b4b0126530`. Signing hardening PR #572 and 4×4 escalation PR #573 are merged. No release-signed tablet APK or physical install follows automatically from these merges.
- Trigger the existing HEX 256/512/1024 workflow as an exact-source evidence assessment, **not** 1,024 passing physical tests. Its release cells deliberately stay `BLOCKED_CROWN`, and its stage/build/verify slots without external proof stay AMBER.
- The last separately verified installable APK remains the 83,586,114-byte debug-signed `art.eggiebagelface.luhmos.premonitionpoc` artifact from [run 43899856693](https://github.com/eggie-admin/LuHm-OS/actions/runs/43899856693), SHA-256 `5509f3619357c64c4c4c8d87df89b80d101485c3a0c6f4c089af890ecfc84b2d`. It is neither an owner-signed `.beta` build nor a proven upgrade path.
- The current intended steady-use package is `art.eggiebagelface.luhmos.beta`. Its `androidBetaReleaseBaselineV1.json` is `UNVERIFIED`. A persistent owner-held signer, protected environment reviewer, real beta APK and Samsung same-signer install/update receipt are separate required evidence.
- Repository branch names were enumerated at 811 total, including 344 candidate, 95 snapshot and 8 archive refs. Preserving potential unique commits and backups takes precedence over blind deletion; no claimed full-branch code audit or purge.
- Commercial-character and third-party rig archives remain in private source vault review; Android import, animations and distribution rights are **not** certified by this source audit. No donor binaries are being added here.

**Acceptance rule:** `GREEN_SOURCE` is only source consistency. `AMBER` requires a named external receipt, `RED` blocks relevant advancement, and release status is `CROWN_STOP` until the Professor can validate the exact signed package and physical tablet behavior.
