# LuHm-OS | Thin-client Package Bridge: proposed

Purpose: one LuHm-owned JSON plan and static HTML cockpit, NOT an attempt to replace APT, dpkg, Synaptic, aptitude, npm, Gradle, Godot or Python. Existing backend services and studio tools remain separate, bounded runtimes.

**dpkg** inventories installed Linux packages and files; LuHm maintains a separate evidence inventory. **APT/aptitude** inspire dependency planning/conflict reviews. **Synaptic** inspires human review before any transaction. **npm** handles exact JS dependencies, lockfiles and static build artifacts. **Netplan** inspires declarative plan/try/apply, but real `netplan try` alters the network temporarily while our `try` stages only disposable JSON and verifies cleanup. **ComfyUI** offers a useful visual-node metaphor: distinguish editor-save JSON from API-execution JSON, quarantine imported custom nodes and keep its backend out of the phone.

From `packages/unified-ops`:

    npm ci --ignore-scripts --no-audit --no-fund
    npm run pkg:plan -- <exact-40-character-commit-sha>
    npm run pkg:try -- <exact-40-character-commit-sha>
    npm run pkg:apply -- <exact-40-character-commit-sha>  # deliberately blocked
    npm test

`plan` validates file presence, a dependency DAG and closed release policy. It does not prove that the caller-supplied SHA is current GitHub HEAD, and does not execute vendor code. `try` writes and removes one temp JSON receipt, without network/host/package changes. `apply` fails closed until a separately approved exact CAST+rollback/signer/runtime gate is implemented.

Reduction order: inventory/hash/license/notice -> quarantine unknown assets -> isolate heavy developer and media workers -> pin vendor versions -> compare true workflow behavior -> verify host/device+performance -> remove superseded source only after tested rollback. DO NOT delete 140 similarly named workflow files or bundle ComfyUI, npm, MariaDB, NGINX, Blender, FFmpeg and Python inside an Android APK.

Static HTML shows the receipt; typed service adapters own all privileged operations. Custom node graphs are data, never authority. **PROPOSED_SOURCE_ONLY, CROWN STOP.**
