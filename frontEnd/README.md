# LuHm OS Android Web3 Cockpit Front End

This directory is the **candidate authoritative user-facing cockpit surface** for the LuHm `androidWeb3Cockpit` milestone. The codename means Android System WebView hosting packaged local LuHm assets. It is not blockchain/Web3 and it is not a claim about a WebView product version.

## Locked visual contract

- full-screen Lum companion / 3D scene is the primary surface
- compact Ubuntu MATE-inspired top panel
- roughly 70% scene / 30% bottom-docked chat composition
- chat is the default interaction surface
- Library and Memories remain lightweight navigation affordances
- backend authority stays behind one explicit backend/system-layer entry point
- magenta/cyan accents on a dark, low-chrome desktop shell

The approved mockup is pinned by hash and dimensions in `reference.md`. The prototype reserves `[data-luhm-lum-viewport]` for the live 3D Lum renderer instead of baking a screenshot into runtime code.

## Four mutations sealed here

1. **Layout spec** — top desktop panel, immersive Lum scene, bottom chat dock.
2. **Widget/plugin map** — stable DOM slots and event boundaries for small modules.
3. **Prototype structure** — dependency-light HTML/CSS baseline plus optional jQuery plugin lane.
4. **Backend bridge** — the backend control dispatches `luhm:backend:open`; it does not embed privileged backend logic.

## Runtime target

The target runtime is a packaged Android System WebView shell loading this directory from an app-owned local origin such as `WebViewAssetLoader`. Remote runtime content and arbitrary navigation are forbidden by the milestone contract.

For desktop/static development only, this directory may still be served from a local static HTTP server and opened as `index.html`.

The baseline works without jQuery. Community jQuery plugins are quarantined under `plugins/incoming/` until audited. Approved plugins can then be adapted behind the plugin contract described in `plugins/README.md`.

## Trust boundary

Front-end code must never contain API keys, credentials, model secrets, arbitrary shell execution, direct database credentials, or privileged device actions. Consequential actions remain Crown-gated behind the typed native/Godot boundary. The WebView cockpit itself has no shell, signing, publication, release, or Crown authority.


## npm CAST human-in-the-loop preview

This repo reuses the existing `frontEnd` npm workspace, its locked jQuery version, and its existing Python source gates. No extra npm dependency, production service, or runner is installed for CAST.

From `frontEnd/`:

```bash
npm run cast:preview
npm run cast:preview -- -v --tier 0 --intent "review the phone cockpit"
npm run cast:preview -- -d
npm run cast:preview -- -h
npm run cast:preview -- -f --tier 3
npm run cast:check
npm run --silent cast:preview -- --json
```

The default is read-only `castBridge` phase, tier `0`, using the exact local Git checkout HEAD, with canonical existing queue tasks `mobileMainHost` and `chatGptInlineMount`. The tool shows source identity, queued tasks, required evidence, and the next approval boundary. `--intent` labels a human request for review; it is not evaluated as code. `--verbose` includes expected evidence. `--docs` displays the authority contract.

`-f` / `--force` records an escalation **request**, never an override; `--tier 3` raises audit depth, not privileges. No npm command here dispatches a GitHub CAST, installs the ChatGPT plugin, deploys, signs, publishes, or grants Crown. The live release requires its independently approved exact-source CAST, host proof, device proof, and human promotion. For machine-readable JSON use `npm run --silent` to suppress npm's standard script banner.
