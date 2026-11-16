# LuHm-OS: Creative RPG Module Forge (private source-only candidate)

This is the minimal original interactive-story engine for Project Premonition. It is not a published tabletop game, a Foundry plugin, an automated Nexus downloader, or a running mini-agent mesh.

## Four-stage, four-lane plan

| Data lane | R1 source | R2 rights | R3 offline | R4 owner |
|---|---|---|---|---|
| rulesRoleplay | versioned original or rights-proven rules reference | verify CC attribution | bounded dice and JSON graph tests | approved rule/content release |
| worldModules | original encounters, factions and dialogue | credit/source asset review | stdout module template | approved Godot/browser conversion |
| artAvatars | original layers, SVG, Daz reference | per-file rights, Live2D SDK conditions | transform plan, never convert proprietary model automatically | human-approved Blender rig and export |
| communitySignals | explicit GitHub or RSS document bytes | Nexus author/mod rights | offline XML parser and digest receipt | opt-in refresh or separate license review |

Project Canon uses `doctrine/creativeModuleForge4x4V1.json`. The four existing typed SQL lanes and existing two logical CAST timelines remain separate from these content disciplines. The proposal doesn't spawn additional threads or mutate the source-locked SQL schema.

## Original JS RPG rules and script language

`packages/luhm-creative-module-forge` is a private, zero-dependency Node ESM package. It provides a tiny, declarative JSON scene language rather than JavaScript scripts supplied by players. Allowed content is `dialogue`, `encounter`, and `ending` nodes, with text, up to four menu choices, bounded dice checks `NdM±K`, optional resource grant, and jumps to prevalidated node IDs. There is no `eval`, `new Function`, dynamic imports, JavaScript expressions in JSON, shell, HTTP, database access or filesystem mutation. A deterministic seed makes tests reproducible; that generator is **not** secure or fair randomness for competitive play or money.

Sample original module: `packages/luhm-creative-module-forge/examples/moonlit-archive.json`. The JSON carries an all-zero example sourceRef placeholder; real CAST receipts must substitute the exact source commit and prove the content's rights before use in a release.

Try locally from the repository root:

```sh
npm test --prefix packages/luhm-creative-module-forge
node packages/luhm-creative-module-forge/bin/cli.mjs demo
node packages/luhm-creative-module-forge/bin/cli.mjs scaffold moonlit-archive
node packages/luhm-creative-module-forge/bin/cli.mjs dice '2d6+2'
```

The `scaffold` subcommand **prints** JSON; no untrusted path is written. To save a private original template, a human can redirect the output to a chosen source-controlled file. A later, separately reviewed Godot import adapter can transform these identifiers into scene labels and dialogue. No Godot gameplay runtime is claimed installed or tested in this pass.

### D&D compatibility

Wizards of the Coast publishes **SRD 5.2.1** under CC BY 4.0; reuse only the portions it authorizes and include the prescribed attribution when actual SRD content is incorporated. D&D trademarks, named settings, characters, many iconic creatures and separately published adventure text are not freely included. The present original sample copies no SRD text or published adventure. Foundry's D&D 5e system is useful as a structural example: MIT software, CC-licensed SRD content and mixed asset terms. We have not forked or bundled it.

Sources: https://www.dndbeyond.com/srd and https://github.com/foundryvtt/dnd5e

## Community Git and RSS intake

`tools/creativeCommunityAudit.py` validates four content lanes, presents license/provenance HOLD receipts and parses **caller-provided** RSS 2.0 and Atom XML **in memory**. The 64 KiB / 32-entry limit rejects DTD, XML entities, unsafe link schemes, local file URLs and malformed markup. It never requests a feed, schedules polling, scrapes a website, invokes GitHub APIs or downloads files. Author-controlled Nexus mods need per-file permission, and Nexus API quotas do not imply download or republishing rights.

Reference research includes GitHub Foundry/dnd5e, community generator OpenDnD, Blender, Live2D SDK, Nexus and retro emulation documentation. No upstream repository or binary is copied into the package, and a license string provided by an untrusted source is never treated as independent rights proof.

## Art pipeline

**2D workflow:** owned PSD/SVG layer sets → artistic rig/parameter mapping → Live2D-compatible concept and animation references. **3D workflow:** separately rigged Blender scene → reviewed glTF/GLB candidate → Godot importer. They can share expressions, timelines and controller semantics, but **a Live2D model cannot be assumed to become a fully rigged 3D model automatically**.

If “Desuzi” refers to **Daz Studio**, the official Daz-to-Blender Bridge source is Apache-2.0. That does not relicense purchased Daz characters, textures, morph packs, or Live2D materials. The Live2D SDK contains proprietary components and publication rules for extensible applications. Therefore actual Daz/Live2D execution, proprietary asset extraction and redistribution stay held. No external plugin auto-run or Blender Python auto-execution is performed by this source-only planner.

Source references: https://github.com/daz3d/DazToBlender and https://www.live2d.com/en/sdk/license/

## Safety and proof

GitHub owns source; Python handles bounded intake; JavaScript owns the original scene DSL; SQL stores bounded receipts; Blender/GIMP and Godot remain external authorized creative tools; FFmpeg handles separately approved render/compositing. Use the machine Forge synthetic IPS inspector only for legitimate homebrew metadata. No ROM/BIOS/ISO, copyrighted game character data, retailer mods or paid service is part of this RPG template.

Checks:
```sh
python tools/creativeCommunityAudit.py
python -m unittest discover -s tests -p 'testCreativeCommunityAudit.py' -v
npm test --prefix packages/luhm-creative-module-forge
```

The dedicated CI verifies source-only validators and original fixtures. Release requires exact Git SHA, owner review, actual client and rights proof, not merely successful CI.
