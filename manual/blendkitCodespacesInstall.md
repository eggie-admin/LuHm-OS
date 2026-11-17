# LuHm-OS Codespaces | BlenderKit / Blendkit official add-on

## Source and scope

**Current brand:** Blendkit (formerly BlenderKit). Vendor: BlenderKit/Blendkit.
Version: `v3.21.5.261103` (official stable GitHub release, published 2026-11-06).
Archive: `blenderkit-v3.21.5.261103.zip` (32,628,967 bytes).
Official URL: https://github.com/BlenderKit/Blendkit/releases/download/v3.21.5.261103/blenderkit-v3.21.5.261103.zip
Pinned SHA-256: `58c437d20fc079f111a7c71a6fdc4c055e4459e1a4fb770e3446d7263c6ebc58`
BlenderKit setup: https://www.blendkit.com/get-blendkit/
GitHub source: https://github.com/BlenderKit/Blendkit

The provided Google image/search redirect did not resolve to a usable tutorial page. The install follows the official vendor's ZIP installer approach, adapted for a **headless Ubuntu Codespaces** Blender user profile. Do not treat this as verified execution of unknown redirected tutorial content.

## Automatic Codespaces setup

After opening or rebuilding the GitHub Codespace, `.devcontainer/devcontainer.json` runs:

```bash
python3 tools/blendkitSetup.py install
bash scripts/ai-ffmpeg-codespaces.sh setup
bash scripts/professorGarageSmoke.sh
```

The installer downloads the *official pinned release*, enforces exact SHA-256 and byte size, validates ZIP paths and module structure, queries Blender for its real current **per-user** add-ons directory, and installs `blenderkit` there. It enables the add-on inside Blender in background mode, saves user preferences, then produces a local installation receipt and a machine-readable console marker.

It **does not** check into GitHub vendor ZIPs, free-vs-paid models, user tokens, or downloaded marketplace content. It does not start provider AI workers, grant login, install the ChatGPT Site runtime, or sign a public release.

## Verify an existing Codespace

Run the following **inside the actual Codespace**:

```bash
python3 tools/blendkitSetup.py verify
blender --background --version
```

Expected markers:

- `LUHM_BLENDKIT_REGISTERED_AND_ENABLED` showing Blender loaded/activated `blenderkit`
- `GREEN_BLENDKIT_WORKSPACE_ADDON_PROOF; ASSET_SERVICE_AUTH_UNPROVEN`

A GitHub Actions proof confirms the add-on works inside a temporary CI image, **not** that a preexisting personal Codespace was rebuilt or that assets can be fetched from Blendkit's online library.

## Recover safely

`install` is idempotent only when the exact pinned receipt and add-on directory are present. If a preexisting **unmanaged** installation is found, the script refuses to overwrite it; review/manual-backup that version first rather than deleting it.

If ZIP metadata, hash, module layout, enablement, user profile, or network access fails, the script exits nonzero. Do not claim BlenderKit green or fabricate an API login.

## Community asset licensing

The GPL-licensed **add-on source** and marketplace **model/material rights** are separate. Every acquired asset needs its own usage/licensing/creator record before being embedded in LuHm-OS, Project Premonition, or *Into the Warp*. Fallout/Resident Evil/Nexus donor content remains reference-only unless the respective creator has granted the intended use; never copy or republish proprietary game meshes because an importer exists.

## Release gates

- GitHub source + workflow: check through PR and commit-specific Actions receipt
- Disposable Actions container installed/enabled: only if `image-build-smoke` passes its vendor-install step
- Existing personal Codespace: **unverified** until rebuilt or the user runs `verify` within it
- Godot 4 GLB import/render: separate
- BlenderKit service sign-in or paid entitlement: **not inferred**
- Publication / Lum agent runtime: **not changed**
