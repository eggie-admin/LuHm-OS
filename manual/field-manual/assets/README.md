# Manual Forge art assets

The editable manual source lives in Git. The sealed full-size comic plates live in the designated Google Drive art vault.

`assets/assets.yaml` is the canonical bridge between the two. Each asset records its expected local path, Drive file ID, pixel dimensions, SHA-256 hash, and current press-resolution gate.

For a full local build, materialize each Drive asset to its listed `path` and verify SHA-256 before rendering.

A missing local plate is allowed for source-only editing and should remain AMBER until materialized. A hash mismatch is RED.

Do not replace art silently. Update the asset manifest and receipts together.
