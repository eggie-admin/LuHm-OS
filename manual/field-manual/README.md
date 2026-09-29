# LuHm OS Manual Forge Source

This is the editable source project extracted from the 2026-09-27 real manual candidate.

## Edit here

- `chapters/*.md` — Professor lectures and Lum field notes.
- `scenes/*.yaml` — acted dialogue and scene metadata.
- `assets/assets.yaml` — art inventory, hashes, dimensions, and print-resolution state.
- `generated/*` — doctrine-derived blocks. Regenerate these from current doctrine; do not hand-edit them.
- `book.yaml` — chapter order and build contract.

## Rule

The repository source project is the editable manual. PDF, DOCX, and HTML are generated artifacts. Google Drive should hold verified recovery/distribution copies, not become source authority by accident.

## Current gate

Content/source structure is ready for editing. Current sealed scene plates remain AMBER for true 17x11 300-ppi press output.

**AI proposes. Policy authorizes. CI proves. Human promotes.**

## Source / art split

Git is the editable source of truth for prose, dialogue, manifests, doctrine references, and the build validator. The sealed high-weight comic plates remain in Google Drive and are bound to this source by `assets/assets.yaml`.

A source-only checkout can validate the editable structure and Drive/hash bindings without materializing art. Full artifact validation remains separate and requires the sealed image bytes. A full local bundle with matching art hashes validates GREEN.

