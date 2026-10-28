# Blender to Godot: disposable handoff proof

This is a **source-only proposal on draft PR #429**, not a live demo, private character import, Android build, or Crown promotion.

## Why this exists

Before moving Lum's private Blender masters or anyone else's artwork, prove the smallest possible interchange: a newly generated cube and icosphere travel in one glTF 2.0 binary from Blender to Godot. Blender emits a SHA-256/size receipt; Godot checks the receipt, parses the GLB and requires exactly two mesh nodes.

## Proposed opt-in local smoke, after the relevant CAST gate

From the repository root in a reviewed local/Codespace workstation with Blender and Godot installed:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python host/blender/blender-godot-handoff.py \
  -- --output-dir /tmp/luhm-handoff-proof

LUHM_HANDOFF_MANIFEST=/tmp/luhm-handoff-proof/proof-manifest.json \
  godot --headless --path . --script res://tools/blender-godot-handoff.gd
```

The output folder is **outside the repo**, and the Blender command refuses to overwrite a prior marker or manifest. Use a fresh disposable directory for each run. Nothing is pushed to GitHub, published, uploaded to Drive, added to `res://`, or copied into an APK by these scripts. The Godot test only parses the external proof GLB; it does not add it to the active game scene.

Expected success lines **only after actual execution**:

```text
GREEN_BLENDER_PROCEDURAL_EXPORT_SOURCE_ARTIFACT
GREEN_GODOT_PROCEDURAL_GLB_IMPORT_MESHES_2
```

If the test fails, capture stderr and the exact source commit, then fix the candidate and rerun only under an appropriate new build/test authorization. A matching hash proves integrity relative to the locally generated receipt, **not rights clearance or provenance of arbitrary replacement media**.

## Naming and authority

New files and directory paths follow lowercase kebab-case:
- `host/blender/blender-godot-handoff.py`
- `tools/blender-godot-handoff.gd`
- `manual/blender-godot-handoff.md`

Engine-defined Python and GDScript identifiers, environment variables, and JSON wire keys follow their respective language/API contracts. Existing legacy code is not renamed casually.

This initial smoke is **not** proof of a usable Blender-to-Lum rig, animation export, Godot playable viewport, Samsung touch, in-chat Project Hydra rendering, a public rights-clean release, signing, or deployment. Existing public Godot asset firewall and private-art quarantine remain authoritative.

**CROWN: STOP. Build/runtime acceptance: NOT EXECUTED in this source preparation step.**
