# Nexus private sidecar lane

This directory defines a **local-only, permission-gated** import lane for Nexus Mods payloads.

Rules:

1. GitHub and public CI never download Nexus payloads.
2. `assets/nexus/incoming/` and `assets/nexus/runtime/` are ignored by Git.
3. Every staged file must have a manifest row with source identity, author, file hash, rights mode, and permission evidence.
4. Default rights mode is `PRIVATE_PERSONAL_REFERENCE`; it is never eligible for Git or a shared APK.
5. `REDISTRIBUTABLE_WITH_EVIDENCE` requires explicit file-specific permission evidence recorded by the Professor before staging.
6. Unknown rights fail closed.
7. Godot only consumes staged `.glb` files. Blender/FBX/OBJ sources belong in the local incoming lane and are normalized before Godot import.
8. No runtime network, no Nexus credentials, cookies, or API keys enter the APK, repository, logs, or manifests.

Use `manifest.example.json` as the shape, then run `tools/stageNexusAssets.py` locally against a Professor-owned download directory.
