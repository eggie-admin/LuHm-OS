# LuHm OS Front End

This directory is the approved user-facing shell for LuHm OS.

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

## Run the prototype

Serve this directory from any local static HTTP server and open `index.html`.

The baseline works without jQuery. Community jQuery plugins are quarantined under `plugins/incoming/` until audited. Approved plugins can then be adapted behind the plugin contract described in `plugins/README.md`.

## Trust boundary

Front-end code must never contain API keys, credentials, model secrets, arbitrary shell execution, direct database credentials, or privileged device actions. Consequential actions remain Crown-gated in the backend.
