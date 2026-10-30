# Project Hydra | CAST 500 development-exit handoff | 2026-10-30

**Decision:** source evidence can graduate to a reviewed integration candidate; physical and public distribution cannot yet be declared released.

## Proven source lineage and merge plan

- Canonical repository: `eggie-admin/LuHm-OS`.
- Protected `main` baseline during staging: `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. Must be re-read before any release action.
- Stacked source PRs: #448 Kai Forge; #449 kernel; #450 packages; #451 four-source; #452 vendor/ZIP; #453 Samsung 500; #454 universal four lanes; #455 CAST source bridge; #456 private data/API LTS; #457 Goddess Orchestra; current CAST500 exit candidate.
- #447 is an older **parallel** candidate on main, not another sequential prerequisite. Compare it before choosing one public source train.
- Existing PR #457 had **10/10 exact-head CI success** at `4d405a1d8c3525f446fa1f2a82a3928936a358c7`. New candidate exact-head CI must be observed separately.
- The candidate branch inherits ancestor commits already, so stacking is a **source lineage**, not proof those PRs have been merged into their target bases or into main.
- Any source promotion must review the full diff against protected main, resolve parallel branch #447, review license/asset provenance, set required CI and review rules, then use human authorization at a precise commit. Do **not** merge blindly from the existence of passing jobs. A merge to main can trigger deploy/release workflows.

## What 500 means

**Five assessment targets** × **four domains** × **25 controls** = **500 unique evidence slots**. Domains: firmware/boot, OS/drivers, AI/media, forge/release. The existing `tools/samsungCast500Audit.py` is the canonical inventory; this candidate does not copy its source or create another incompatible 500 definition.

CI runs the existing 500 inventory using only GitHub runner read-only observations and a new `tools/cast500ExitDevelopment.py` source release-exit gate. This gate verifies every slot ID, target, control, verdict and evidence scope; it refuses physical-device PASS claims not actually observed. A Python test enumerates and checks each of the 500 slots individually, then rejects fake PASS status, duplicate rows and forged deployment states.

**500 assessed ≠ 500 passed ≠ a verified signed app.** Any UNVERIFIED state stays UNVERIFIED. The GitHub runner cannot prove three Samsung devices, six cameras, firmware, studio GPU, signing, a live Render release or ChatGPT host mounting.

## Mandatory exit criteria and authority boundaries

| Target | Source state | Independent evidence needed | Gate |
| --- | --- | --- | --- |
| Samsung Android | CI/source candidate | Owner CAST on **current main**; non-debug, correctly signed test artifact; exact SHA/package/signer and install/launch receipts on actual device | HOLD |
| Godot game | Source/build harness | Real exported files, playable input, Android touchscreen acceptance | HOLD |
| ChatGPT in-app CAST | Read-only tool responds | Same-source UI resource mount and current host visual acceptance; unqualified historical receipts don't count | HOLD |
| Render API | Historical deployed runtime | Owner-selected workspace, current service/branch, exact deployed commit, authenticated negative API checks, health and rollback | HOLD |
| Private data | Five of six previously inspected private docs had link-wide Editor access | Restrict permissions, independently re-read ACL, assess history and token exposure if relevant | HIGH-PRIORITY HOLD |
| Family/adult audience | Documented policy | Server-side ACL, platform-rule review, consent, release and media privacy tests | HOLD |
| Public brand/media | Studio planning allowed | Rights/attribution/age appropriate assets, explicit publication approval | HOLD |
| Agent workers | 15 quarantined | Separate supervised proof + explicit individual release, never CI auto-unquarantine | HOLD |
| LTS stable/public F-Droid | Candidate signing plan | Owner-held production signer, non-debug APK, signed update index, real install/update/rollback | HOLD |

## Security and vendor scope

Use existing `doctrine/dataProtectionLadderV1.json` for strong security appropriate to **data sensitivity**; no plaintext private footage or secrets on a supposedly local-only machine. Android remains stock/no root. Preserve the npm/Python/SQLite/YAML developer spine without adding runtime Node to Samsung. Keep Godot, Blender, FFmpeg, Vue/jQuery/Babylon; optional external vendors remain explicitly reviewed. No auto `/etc` trimming, GRUB writes, firmware flashing, public SQL ports or unpublished private assets.

## Source-staging implementation

- `doctrine/cast500ExitDevelopmentGateV1.json`: exact prior lineage, missing proof map, prohibited automatic operations, source-only review.
- `tools/cast500ExitDevelopment.py`: 500-slot proof integrity, canonical SQL in-memory negative controls, security and owner CAST gate reconciliation; source summary and strict production-stop option; emits no personal data.
- `tests/testCast500ExitDevelopment.py`: 500 slot-specific subtests plus negative mutation tests.
- `.github/workflows/cast500-exit-development.yml`: immutable checkout, existing actual 500 runner assessment, new 500 proof validation, previous gates and sanitized artifact retention.

## Release progression once independent evidence exists

1. **SOURCE INTEGRATION**: exact-head CI and full stacked diff reviewed. Draft PR becomes review-ready only through owner-approved review, with main protected and required status checks. No runtime claim.
2. **OWNER CAST / PRIVATE BETA**: after relevant changes are on the approved exact main SHA, owner-authored GitHub comment `/cast androidProposedDebug <40-char-current-main-sha>` triggers the specifically defined limited build. For other milestones use the exact known CAST grammar. A user message here is not a GitHub-actor-signed PR comment.
3. **PHYSICAL / HOST CANARY**: verify exact artifact/SHA on Samsung, playable Godot, private API permission denial tests and host version. Render workspace confirmation required before service mutation.
4. **FINAL RELEASE**: verify rights, audience, private ACLs, encryption/restore, stable signing, public media rights and full human approval. Only then is the label **OUT_OF_DEVELOPMENT** warranted.

### Final verdict

`SOURCE_CANDIDATE` until this exact head's CI passes; when it passes, `SOURCE_INTEGRATION_REVIEW_READY` only. `PRIVATE_BETA=HOLD`, `PUBLIC_RELEASE=HOLD`, `CHATGPT_FINAL_CAST=HOLD`; `CROWN_STOP`.

**No merges, production deployments, signing or release authority are performed by this evidence script.**
