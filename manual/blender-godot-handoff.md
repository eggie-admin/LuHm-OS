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

## Single-cockpit creative studio

`host/blender/luhm-cockpit.py` is the **one Blender entrypoint** for an artist workstation. Its expandable LuHm sidebar now mounts:

- **Studio Workspaces:** native Blender Layout, Modeling, Sculpting, UV Editing, Texture Paint, Shading, Animation, Rendering, Compositing, Geometry Nodes, Scripting and Video Editing workspaces.
- **Python + IDE + Terminal:** opens the three known repository Python files in Blender's native Text Editor **without executing them**; provides explicit launch buttons for an already-installed VS Code/VSCodium, `xterm`, Godot 4 editor, and GIMP.
- **Video + Animation:** entry to Blender's built-in Video Sequence Editor, character animation, rendering and compositor. Edit/render operations remain normal deliberate Blender UI actions.
- **Community + Plugins:** opens Blender Preferences for extensions, and fixed official links for Blender Extensions, Blender Manual, and Godot docs. It **does not download, install, activate or execute a community extension**.
- **Existing proof checks:** environment probe, local-only MariaDB probe, Godot availability, and the disposable procedural-GLB handoff.

This is intentionally a **single control surface, not a single giant process**. Blender hosts native editors. An installed IDE, terminal, Godot or GIMP opens as a local user application when explicitly clicked. It may show a separate desktop window. Launch buttons do not grant subprocess execution to arbitrary downloaded scripts, internet add-ons, AI workers or plugins.

To open the cockpit, start Blender in an interactive display session, load `host/blender/luhm-cockpit.py` in the native Text Editor, click **Run Script**, return to the 3D View and open the **LuHm** sidebar. The installed Blender workstation image is headless by default. The remote display, Samsung tablet interaction, Codespace GUI and full video-production acceptance **remain unverified**.

Native **Scripting** provides Text Editor and Python Console. The Python Console is a full local Python interpreter, **not a restricted sandbox**; use only code you trust. The optional terminal is a local full shell for the signed-in machine user, not a remotely exposed service. New community material should be reviewed for license, source, version, checksum and API permission before anyone enables it.

## Blender cockpit button

The **Export Demo Marker (Local)** button on the existing LuHm Blender sidebar invokes the same procedural exporter only when clicked. It refuses to operate in Edit/Pose/Sculpt mode, never exports the user's selected objects, and creates an out-of-repo temporary directory. The Blender console prints the resulting `LUHM_HANDOFF_MANIFEST=...` path for a separately authorized Godot verification. No command silently runs Godot or deploys a game.

This initial smoke is **not** proof of a usable Blender-to-Lum rig, animation export, Godot playable viewport, Samsung touch, in-chat Project Hydra rendering, a public rights-clean release, signing, or deployment. Existing public Godot asset firewall and private-art quarantine remain authoritative.

**CROWN: STOP. Build/runtime acceptance: NOT EXECUTED in this source preparation step.**
