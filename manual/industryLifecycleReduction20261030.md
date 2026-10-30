# LuHm-OS: Project Premonition | Industry lifecycle reduction, 2026-10-30

**State:** source-only candidate at PR #460. This is a precise *plan and read-only audit*, not actual infrastructure cleanup, Canon promotion, signed beta or marketing publication. Crown STOP.

## Product and release identity
- Product: **LuHm-OS** (case-sensitive). Active development identity: **Project Premonition**.
- Legacy historical identity: **Project Hydra**; preserve provenance, code routes and prior receipts rather than mass-renaming or merging old unrelated histories.
- Publisher: **Eggie Bagelface**. Film imprint: **PIRATE DADDIES FILM**.
- Roleplay/character names are fictional/supervised presentation, not independent agents and not cleared trademarks, likenesses or playable features.

## Six semantic lanes, three operational environments
Legacy -> Testing -> Proposed -> Private Beta -> Public Beta -> Stable.
Operate only three actual environments until evidence proves a need for more:
(1) immutable source/donor vault and isolated test workers; (2) Proposed staging preview; (3) a future scoped beta runtime.
**Branch name is not an environment, and previous independent git histories are not mergeable release trains by default.**

## Supported to bleeding edge
- **Node**: 20/23/25 are end-of-life research only; continue 22 compatibility while upgrading build jobs to supported 24; verify 26 as newer LTS in testing, not automatic production. Pin toolchain and lockfile; separate npm from Android runtime.
- **Python**: 3.10 is EOL (Oct 2026), 3.11-3.13 security-only; target supported 3.14 only after dependency/ABI checks; test 3.15 separately. Do not replace OS Python on a live host.
- **Android**: for new Google Play submissions starting Aug 31 2026, target API 36+ (subject to platform exceptions and Google Play account rules). Confirm final manifest and actual Play/F-Droid route, not just a source pin.
- **Godot/Blender**: retain exact source-tested versions and build a small verified vertical slice before updating the engine, rigs or procedural material pipeline.
- **Linux**: keep distro-supported Python/SSL/kernel packages. Run headless CI in short-lived images, no root-only driver mutations; Debian/dpkg packages only for the Linux service target.
**Compatibility is measured**; support schedule is not proof of running code.

## Industry control families
1. NIST AI RMF: manage scope, use-case, failure and human-approval evidence, separate model outputs from application permissions.
2. OWASP LLM/Agentic: untrusted input and prompt injection, sensitive information, tool least privilege, excessive autonomy, dangerous tool outputs and unbounded costs. Mandatory offline negative fixtures.
3. SLSA 1.2 and GitHub supply chain: source review, pinned CI actions or verified workflow locks, immutable artifact provenance, integrity/attestation, SBOM and code-scoped permissions.
4. Evaluation-driven AI: version prompts/models/tools, run deterministic fixture suites for hallucinations, unsafe commands, refusal, tool calls, latency and cost ceilings. Golden examples and repeated regressions before changes.
5. Software support: vendor release schedule -> compatibility matrix -> isolated upgrade -> benchmark -> rollback -> deprecate old versions; *never* upgrade everyone in one patch.
6. Release rollout: exact manifest, policy/privacy and art license review, stable signer/update path, actual install/input/FFmpeg output, opt-in testers, feedback and rollback, explicit publisher approval.

## Real workflow reduction: measured first
**Live inventory before this patch:** 129 workflow YAML files on protected main; 140 on the current stacked Proposed branch. 53 open PRs. These are *counts*, not proofs of duplicate logic or 140 active runtime services.
The source-only script `tools/industryLifecycleReductionAudit.py` computes:
- exact duplicate workflow contents (SHA-256), coarse responsibility families, review candidates for action ref pinning, privileged GitHub events, writes, floating runner, EOL Node references and extra manual dispatch.
- counts and candidate metadata without executing workflows; scripts do **not** automatically delete, disable, merge or claim equivalence.
Reduction order: exact duplicates -> shared audit code/extract reusable jobs -> redundant PR path triggers -> superseded test lanes -> retired releases. First review source diffs, secrets/permissions, required checks, CI economics, and rollback per workflow.

## Canon and release evidence contracts
Keep identity/provenance names stable, use signed receipts for runtime artifacts; use existing `doctrine/currentSourceTruthV3.json`, `doctrine/premonitionEnterpriseBrandV1.json`, `doctrine/finalFormPublicReleaseGateV1.json` and `doctrine/crown... ` only if they actually exist. Never fabricate new canonical authority.
- One real rights-cleared Blender -> GLB -> headless Godot import -> interactive Samsung proof remains the minimum game slice.
- One current official web bundle with a locked npm dependency graph, same-origin static assets and browser/device proof.
- One owner-controlled Android signer and verified APK upgrade/rollback.
- One private Linux Python+SQLite service; no SQL listener exposed to public web, no credentials in database/media receipts.
- Explicit grants for marketing, ad spend, app-store listing, public artwork and names; none follow from CI.

## Advertising and public beta readiness handoff
**Private creative brief, not approved copy:** artist-first, original interactive worlds, creative control on modest hardware, moving-image production and documented reproducible builds. Demonstrate rather than promise.
Needed assets: cleared wordmark/logo, app icon, landing page screenshots of verified builds, 10-20 second actual gameplay capture, creator credits, platform compatibility, plain-language privacy policy, support channel, tester eligibility, rights-cleared score and motion, exact release notes and installation/update path.
Never imply verified Samsung playback, sponsor affiliation, trained autonomous staff, finished character rights, release availability or monetization before evidence. Split internal concept trailers from public claims. Professor authorizes exact creatives and any spend.

## CI proof and handoff
`python3 -m unittest tests/testIndustryLifecycleReduction.py -v`
`python3 tools/industryLifecycleReductionAudit.py --source-ref <exact_sha> --output /tmp/luhm-industry-lifecycle.json`
Reuses the existing **Unified Goddess Orchestra Four-Quarter Gate**. This audit is a *source policy check and review inventory*, not validation of package manager migrations, autonomous agents, real hardware, live secrets or working advertisements.
No main merge, no Cast, no Crown, no live posting. **Next independent evidence**: review coalesced workflow candidates and one complete Godot/Blender proof slice.

References:
- https://nodejs.org/en/about/previous-releases
- https://devguide.python.org/versions/
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- https://genai.owasp.org/llm-top-10/
- https://slsa.dev/spec/v1.2/
- https://docs.github.com/en/actions/reference/security/secure-use
- https://mlflow.org/docs/latest/genai/datasets
- https://developer.android.com/google/play/requirements/target-sdk
