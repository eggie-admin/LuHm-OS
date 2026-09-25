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

## Android identity

- app: `LuHm OS Clean Play`
- package: `art.eggiebagelface.luhmos.cleanplay`
- version: `1.0.11-cleanplay.1`
- versionCode: `111`
- signer: disposable debug signer in CI only

The package is side-by-side with the frozen golden beta and cannot overwrite it.

## Repository migration

Legacy repositories are selectively transplanted by evidence, not merged wholesale and not merged by unrelated Git history. Exact source pins and exclusions are recorded in `doctrine/REPO_MIGRATION.json`.

The pre-unification LuHm-OS main is preserved at `snapshot/pre-unification-20260925`.

## Agent mesh candidate

The bounded OpenAI/LuHm orchestration contract lives under `agents/luhm-agent-mesh/` and `skills/luhm-agent-mesh/`.

- Lum is the single conversational boss.
- Context, Build, and Research are the default read-only Oni helpers.
- Critic is conditional for audit/security/release/architecture risk.
- Kanabo Gate is the deterministic executor for approved side effects.
- helper parallelism is capped at 3 and delegation depth at 1.
- GitHub remains canonical source history; cloud providers are replaceable worker lanes.

The contract is audited by `scripts/auditAgentMesh.py` and `.github/workflows/agent-mesh-audit.yml`.

## Run locally

Open the repository in Godot 4.7.2 and run `scenes/Main.tscn`.

Desktop: WASD / arrow keys. Android: on-screen D-pad. Tap `WORLD MODE` to enter the native 3D world and `CATHEDRAL` to restore the cockpit.

For the browser front-end concept, serve `frontEnd/` over a local static HTTP server and open `frontEnd/index.html`.

## Source law

AI proposes. Policy authorizes. CI proves. Human promotes.
