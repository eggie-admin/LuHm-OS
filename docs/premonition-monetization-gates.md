# Project Premonition: Monetization Release Gate (PROPOSED)

This is a planning and verification gate, not proof of Google Play publication, billing integration, revenue or permission to spend money.

## Intent
Project Hydra maintains shared machine, creative studio and automation; Project Premonition is the first playable Android product.
Target a free internal-test game without payment functionality until first-run, save/load, update, user testing and signing provenance are verified.

## Four by four release gate
| Domain | Prototype | Test | Proposed | CAST |
|---|---|---|---|---|
| Machine | exact-SHA Android build | AAB and ABI/sdk checks | signing lineage, SBOM and device upgrade proof | owner sign-off |
| Human-machine | usable touch UI | accessible basic controls | data handling and error recovery | owner sign-off |
| Human-human | contributor onboarding | license and art provenance | support, privacy, ratings, store disclosures | owner sign-off |
| Studio | one playable loop | save/resume/regression | gameplay recording, release assets and store screenshots | owner sign-off |

## Monetization lanes
1. Free internal testing: purchases off, no live billing SKU.
2. Sandbox purchase testing: separate build flags, licensed Google Play Billing version, test accounts; purchases must never grant entitlement solely from client callback.
3. Closed beta: server-side validation and entitlement/revocation tests; refunds and cancellations; pricing and taxation reviewed by owner.
4. Public production: owner approves Play policy/store listing, staged rollout, monitoring and support.

## Fail-closed criteria
- Do not ship paid DLC, subscriptions, virtual currency or other digital goods without policy-compliant Play Billing where required.
- No production purchases without reliable entitlement verification, acknowledgment/consumption, refund/revoke handling and fraud protections.
- Do not claim a Google Play install from an APK or F-Droid receipt; verify AAB, Play Console testing track and real device install.
- Do not infer Google Play Console access, app signing, developer identity, merchant setup, tax status, testing eligibility or account verification from source code.
- No release of private assets or unlicensed contributor work. Record license/provenance and inspect asset manifests before external indexing.
- Capture age-targeting, data safety, privacy policy, content rating and advertising disclosures before launch. Review mature content separately.
- Public search indexing and GitHub repository discoverability require deliberate owner review. An internal test can remain unindexed.
- Production publication, payment activation and merges require separate owner authorization.

## Minimal weekly developer experience
Edit one versioned build config → CI checks and builds → smoke device → draft candidate and receipts → owner CAST → Play internal rollout → user feedback.
Keep dev/nightly/proposed/internal/closed/production/LTS and rollback/update compatibility clear; never silently change package ID or release signing lineage.
