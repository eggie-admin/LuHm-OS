# LuHm OS Pixel Sitter Pack

This directory is reserved for **original or license-audited** LuHm OS pixel-anime sitter assets.

Target vibe: cute, sexy, adult, playful, non-explicit pixel-anime wifey sprites and compact oni-pet role icons.

Required states: `idle`, `blink`, `talk`, `inspect`, `sleep`, `alert`, `drag`, `dismiss`.

Preferred production rules:

- 128x128 logical canvas per sitter
- transparent RGBA
- PNG/APNG or sprite sheets
- integer nearest-neighbor scaling
- no watermarked assets
- no ripped franchise sprites
- no community asset enters a shipping build without a provenance/license record
- no downloader or plugin executes third-party content automatically

The bounded agent/pet family is specified in:

- `assets/pet/oni/PET_ICON_SYSTEM.md`
- `assets/pet/oni/manifest.json`

The visual flow is intentionally staged:

1. generate or draw role-icon concepts
2. Professor approves or corrects the visual identity
3. Sumi records provenance and stable asset IDs
4. derive the eight runtime states
5. import the exact hashed asset into the target runtime
6. capture runtime evidence before calling the import GREEN

A future per-asset `provenance.json` should record, at minimum: asset id, creator/generation method, source/reference, license or ownership basis, modification notes, checksum, dimensions/format, approval state, and runtime receipt when proven.
