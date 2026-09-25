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

## Run locally

Open the repository in Godot 4.7.2 and run `scenes/Main.tscn`.

Desktop: WASD / arrow keys. Android: on-screen D-pad. Tap `WORLD MODE` to enter the native 3D world and `CATHEDRAL` to restore the cockpit.

## Source law

AI proposes. Policy authorizes. CI proves. Human promotes.
