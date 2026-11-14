# Project Hydra → Project Premonition: Google Play lanes

Status: PROPOSED only. No Google Play publication or install is claimed.

## Product split
- Project Hydra: build automation, Godot creative studio, integration and testing foundation.
- Project Premonition: first installable game/app vertical slice, branded product and future feature releases.

## 4×4 escalation
1. Machine-machine: reproducible exact-SHA build, dependency audit, isolated signing, performance and Android smoke.
2. Human-machine: mobile cockpit commands, feedback capture, concise release decisions, accessible configuration.
3. Human-human: contributor guidelines, licensing/asset provenance, issue/PR templates, code of conduct and tester communication.
4. Automated studio: playable Godot scene, art/video pipeline, content index with asset licenses, crash reporting and update verification.

Each layer goes concept → prototype → test → proposed → CAST; proceed upward only with evidence and make downward compatibility sweeps after integration. Stop on a meaningful blocker; do not use pass count as proof.

## Release lanes
- dev: per-branch checks; ephemeral artifacts.
- nightly: scheduled read-only audits and unsigned/debug artifacts; never public release.
- testing: verified APK smoke on Android hardware, signed only where necessary.
- proposed: exact-source release candidate, SBOM/license review, provenance, performance and security checks.
- Play internal: **AAB** generated and validated with dedicated Play app identity, stable upload key, verified Play App Signing and Play Console internal testing authorization.
- Play closed: tester feedback, store disclosures, privacy policy, content rating, data safety and pre-launch reports.
- production: owner-approved managed rollout, staged percentage and rollback strategy with Play releases.
- LTS: patches and supported compatibility matrix, backport only after regression checks.

## Stop conditions for Play install
- AAB pipeline not yet verified.
- Play Console and Play App Signing owner status not independently verified.
- Internal test distribution and real device install not yet proven.
- Verify the real app package identity, versionCode increments, SDK compliance, signing identity and update continuity.
- Do not silently reuse F-Droid signature or beta app ID; decide one supported package/signing lineage for Play.
- Verify legal rights to shipped assets and contributor code, privacy disclosures, age targeting and content rating.
- No public indexing until product pages/robots/sitemap are checked and public assets are safe.
- Separate public indexing (discoverability) from internal Google Play testing (restricted).

## Minimum functional prototype
Launch screen → one playable Godot interaction → save/load → exit/relaunch → one successful version upgrade without losing save. Capture a physical Samsung device receipt. Next add media and game features via feature flags.

## Human involvement
Bot: repeat audits, compile, inspect dependencies, propose fixes, assemble evidence, prepare draft PRs.
Owner: supply developer account, control signing, approve first Play internal rollout, sensitive scopes, public visibility and production CAST.
