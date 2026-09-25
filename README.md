# LuHm OS

Canonical repository: `eggie-admin/LuHm-OS`.

This main line is the clean playable LuHm OS spine. The old Hydra/KAI/Vue/Termux repositories remain migration references, not runtime authorities.

## Play milestone

`CATHEDRAL -> WORLD MODE -> native Godot 3D -> move on phone -> CATHEDRAL`

The current playable source is intentionally small:

- Godot 4.7.2 native runtime
- Detroit riverwalk prototype
- Lum beacon
- touch D-pad + desktop movement
- side-by-side Android debug package
- deterministic GitHub Actions APK build

Not in the Android runtime: FastAPI/PySimpleGUI control planes, Termux execution bridges, Vue donor runtime, production signing secrets, or private reference assets.

## Front-end shell milestone

The approved front-end direction is sealed under `frontEnd/`:

- full-screen Lum companion scene
- compact Ubuntu MATE-inspired top desktop panel
- approximately 70% companion scene / 30% bottom chat dock
- minimal Chat / Library / Memories navigation
- one explicit backend/system-layer entry point
- quarantined jQuery plugin-ingest bay for audited community modules

`frontEnd/` is a browser prototype and design contract. It does not replace the canonical native Godot playable runtime yet, and it contains no privileged backend authority.

## Android candidate: one Samsung build

The proposed build contract is `doctrine/androidCandidate.json`. One workflow,
`android-testing-build.yml`, exports the same ARM64 APK for S24 FE and SM-X400.
Both pinned Lum models are ingested before compilation; the browser front end remains a prototype.

- package: `art.eggiebagelface.luhmos.testing`
- version: `1.0.15-samsungamber.1` / code `115`
- minimum Android API 24; target API 36
- exact source checkout, fail-closed runtime scan, negative controls, import and rig smoke checks
- APK signature, metadata, permission, ZIP and ELF alignment gates
- signer: disposable debug signer; **not a stable update channel**

Amber means CI compiled and verified the candidate, while physical-device proof,
16KB runtime testing, persistent signing custody and update continuity remain pending.
The workflow does not register an app with Google or claim Play Protect acceptance.
Compare installed certificate before installing; a different debug signer cannot update
an existing installation. Never automatically uninstall or erase app data.
Golden beta stays untouched. Main promotion remains separate.

Prior audit: `doctrine/universalSamsungAuditSeal-20260925.json`.
The cleanplay workflow is retired on this proposal branch to avoid a second payload.

## Repository migration

Legacy repositories are selectively transplanted by evidence, not merged wholesale and not merged by unrelated Git history. Exact source pins and exclusions are recorded in `doctrine/REPO_MIGRATION.json`.

The pre-unification LuHm-OS main is preserved at `snapshot/pre-unification-20260925`.

## Run locally

Open the repository in Godot 4.7.2 and run `scenes/Main.tscn`.

Desktop: WASD / arrow keys. Android: on-screen D-pad. Tap `WORLD MODE` to enter the native 3D world and `CATHEDRAL` to restore the cockpit.

For the browser front-end concept, serve `frontEnd/` over a local static HTTP server and open `frontEnd/index.html`.

## Source law

AI proposes. Policy authorizes. CI proves. Human promotes.
