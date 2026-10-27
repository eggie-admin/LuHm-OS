# LuHm OS: hardware → hardware-human → human-sorta → full-human

**Working status:** PROPOSED_SOURCE_ONLY; Professor directs the milestone. This guide is useful without pretending physical hardware or independent AI workers have been tested. It inherits the current GitHub source and does **not** supersede the seven-plane stage or the four-layer package architecture.

## Why these names?

The stages describe **distance from metal to real human creative control**, not four software components, mythical authority levels, or progressively more human AI. We can develop their source contracts in parallel, but maturity advances only with observed proof.

| Step | What a person gets | Source you can reuse | Exit proof before declaring usable |
| --- | --- | --- | --- |
| 0. Hardware layer | Verified kernel/platform adapters, repeatable builds and safe rollback | `modularSourceArchitectureV1`, Linux host, Samsung stock GKI, Godot/Gradle sources | Exact source + tests + a real build artifact/boot receipt for target machine |
| 1. Hardware-human layer | Real touchscreen or keyboard app: accessible Samsung companion/Godot beta | `samsungTabletInstallV1`, `androidWeb3CockpitV2`, signing workflow | Signed compatible APK and **physical Samsung install/upgrade** proof, or target desktop proof |
| 2. Human-sorta layer | Intuitive stage, conversation, art tools, readable UI and usable feedback | `humanCenteredIntentRouterV2`, `layeredStageCanonV1`, `inChatExperienceV1` | Android touch, accessibility, real UI/host mount, opt-in 3D and static fallback |
| 3. Full-human layer | Artists own choices, authorship, consent and community; funding supports development | `artistFirstArtToolCanonV1`, `patronageCampaignV1`, `publicArtReleaseReadinessV1` | Signed-off rights/credits, human approvals, accessible workbench proof, truthful fundraising/publication |

## What already exists versus what is not proven

- **Known source:** `eggie-admin/LuHm-OS`, `currentSourceTruthV3`, four source modules, seven visual planes, Godot 4 Android source and a manually gated signed-beta workflow.
- **Do not claim:** a signed downloadable APK, Samsung install or update, Live2D character rig, fully working ChatGPT mobile MCP-app mount, unrestricted Yume media rights, automatic social publishing, or a live and funded business. Each needs its own independently verifiable receipt.
- **Android distinction:** the established owner-signed `art.eggiebagelface.luhmos.beta` lane makes the **Godot beta**. The campaign companion source package `art.eggiebagelface.luhmos.campaignpreview` is a **separate** project candidate and must not silently inherit the beta's package/update history.
- **Linux distinction:** Ubuntu host kernel/build stack is separate from Samsung's Android GKI/vendor modules. Never flash an Ubuntu kernel onto stock Samsung hardware to satisfy a milestone. Bootable USB and VM are distinct prospective build targets.
- **No public identity leaks:** protect user and collaborator names, family and health background, private Drive directory identifiers, unpublished designs, keystores and credentials.

## The 20-second human help command

```sh
python3 tools/hardwareHumanMilestoneAudit.py
```

This script checks whether the **source milestone contract is coherent**. Its `PASS` is **not** an APK, live widget, F-Droid, signer or funding acceptance receipt. For a machine-readable report use:

```sh
python3 tools/hardwareHumanMilestoneAudit.py --json
```

## Bounded CAST route

1. **Hear:** identify the smallest stage and the concrete output the Professor wants.
2. **Resolve:** read exact current `main`, relevant doctrine, current app/site/device evidence and open blockers. Historical checkmarks are research leads.
3. **Act:** perform one source-only change, test or review in a scoped draft branch; prefer deterministic work and standard-free existing CI. Preserve originals and owner-held signer.
4. **Verify:** record exact commit, CI, APK fingerprint, host interaction, accessibility test, rights and on-device evidence **separately**. Only the relevant proven dimension goes green.
5. **Promote:** dependent steps require current evidence, collaborator/Professor rights and final exact artifact review. No source PR can auto-sign, unquarantine agents, charge, publish or rewrite Drive permission authority.

The present Drive-first handoff is [Task #421](https://github.com/eggie-admin/LuHm-OS/issues/421). GitHub proposed-canon restoration is [Task #422](https://github.com/eggie-admin/LuHm-OS/issues/422). Funding-first campaign remains a [draft PR #423](https://github.com/eggie-admin/LuHm-OS/pull/423). Owner-signed APK duties remain independent [#388](https://github.com/eggie-admin/LuHm-OS/issues/388) → [#389](https://github.com/eggie-admin/LuHm-OS/issues/389).

**Canonical rule:** AI proposes. Policy authorizes. CI proves. Human promotes. Only one human decision owner: Professor.
