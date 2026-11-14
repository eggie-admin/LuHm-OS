# Crown Cathedral: fork the proposed Ash Cathedral build

This repository is the public LuHm-OS workstation source tree. Its **full contents are
not a rights-cleared game-art distribution**. The independent, source-only Godot
prototype is under
`plugins/luhm-os/skills/premonition-combat-studio/assets/godot/`.

## Source-only fork export

From the repository root, run:

```sh
python3 tools/crownCathedralForkGate.py --self-test
python3 tools/crownCathedralForkGate.py --output build/fork/ash-cathedral-fork.zip
python3 tools/crownCathedralForkGate.py --verify build/fork/ash-cathedral-fork.zip
```

The ZIP contains only the reviewed Godot scene, script, project config, tests,
documentation, original GPL-3.0 license text, an art-exclusion notice and SHA-256
manifest. It is suitable as a *separate code fork/project*, not a complete
production game or certified build. Extract the ZIP, open `project.godot` in a
compatible Godot 4.6 editor, and run the included smoke/hardening tests.

CI builds and uploads a short-lived `crown-cathedral-source-fork` artifact.
Review GitHub Actions results for the **exact commit** before distributing it.
An artifact from a failing or unverified run is **not approved**.

## Protected art boundary

Your private Live2D files, 3D models, master PSDs, Blender rigs, reference
portraits, unreleased footage, audio, private HTML and character design masters
are **not included**. Keep those in owner-controlled private storage. Do not
assume a `.gitignore` retroactively protects anything already committed to
GitHub, including commit history or previous forks.

The exporter uses a strict file allowlist, checks `res://` dependencies,
refuses symlinks and unapproved references, and includes negative leakage tests.
It intentionally does not pull or inspect private Drive contents. Any public
art derivative needs its own traceable license/provenance/hash/eligibility and
Professor approval. Neither the source-only package nor this document grants
redistribution rights to original protected art or third-party game assets.

## Canon and release boundary

`doctrine/currentSourceTruthV3.json` remains the authority for the whole
system; `doctrine/crownCathedralPublicForkV1.json` defines this **narrow,
reviewable source-fork candidate**. No global `crownStatus: STOP` is rewritten.
The user-authorized code-review scope is not evidence of successful GitHub CI,
verified device installs, signed Android release, live plugin deployment, or
full public-art approval.

Do not merge or publish a full release while its actual checks are red or
unknown. GitHub branch rules and third-party requirements remain effective.
