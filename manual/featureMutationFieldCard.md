# LuHm OS · staged feature mutation field card

Canonical root: `doctrine/currentSourceTruthV3.json`.
Source contracts: `doctrine/systemArchitectureBaselineV1.json` and `doctrine/featureMutationPipelineV1.json`.

## Default next-feature cycle

1. **Intake:** featureId, taskId, scopeId, exact 40-character sourceRef, targetSurface, proposed lane.
2. **Sanity + audit:** resolve source truth, source snapshot, dependency/secret/rights constraints, affected tests and host/device proof.
3. **Ingest:** classify external files and observations by hash. Never treat unverified memories, uploads, or previous CI as current execution.
4. **Mutate:** make one bounded candidate branch and retain an immutable rollback commit or snapshot.
5. **Test:** check exact candidate head, run feature-mutation and relevant domain audits, execute negative tests, check code/asset ownership.
6. **Apply:** merge only after all *required* exact-head checks pass; source promotion is not runtime/store promotion.
7. **Deploy:** update existing Render service only when authorized; require exact-commit live receipt, then endpoint smoke. Never duplicate infrastructure.
8. **Runtime:** bind live ChatGPT host, Android install, Godot playable Web, rights, signing and store distribution to distinct receipts.
9. **Seal:** packet includes sourceSha, workflow IDs, artifact digests, Render deploy ID, verified claims, blockers, rollback pointer and next human action.

## Prohibited shortcuts

No agents self-authorize, no hidden async Oni, no recursion, no stale GREEN transferred to a new commit, no unreviewed public release, no key bytes in source/ChatGPT, no automatic F-Droid or Google Play submission, no silent device installation. Professor alone promotes Crown-scoped outcomes.

While `doctrine/companyWideOperationalQuarantineV1.json` is QUARANTINED, all fifteen agent work routes remain non-executing. Belldandy is a read-only *role contract*, not a live worker. Source/CI audits remain permitted.

## Next scoped candidates

- `pythonKeyboardGui`: WYSIWYG Python3 keyboard, accessible controls, jQuery/Bootstrap-compatible cockpit and taskbar protocol.
- `godotWebPlayable`: reproducible Godot export plus actual browser controls, not placeholder HTML.
- `chatGptInChatCockpit`: host-side tool scan and real invocation, distinct from the Render HTTPS endpoint.
- `androidProductionRelease`: stable signing lineage, installed Samsung app receipt, rollback/upgrade tests.
- `fdroidSignedRepository`: independent F-Droid repository key, signed index, HTTPS route and owner approval.
- `assetCanonAndArtRights`: selected asset hashes, rights approval, public eligibility and runtime import receipts.

Run static preflight inside the repository with:

```bash
python3 tools/featureMutationGate.py --self-test
python3 tools/systemArchitectureAudit.py --self-test
python3 tools/belldandyOniDeploymentGate.py --self-test
```

A passing preflight means the **source workflow** is staged. It does not prove a public product release. 👑
