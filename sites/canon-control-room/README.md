# LuHm-OS Canon Control Room

**Status:** source-only candidate, NOT a deployed Site, ChatGPT widget, Godot plug-in, installed APK, active agent network or Crown promotion.

This is a small, dependency-free static interactive web app for the existing **LuHm-OS / Project Premonition** repository. `Project Hydra` is retained as a legacy reference, not silently renamed. It does not replace Canon doctrine. The authoritative pointer is `doctrine/currentSourceTruthV3.json`, while `canonSnapshotV1.json` is a **dated derived inspection** with explicit open items. GitHub is the source of truth for source, branches, review, hashes and receipts. Private binary masters remain in authorized owner-controlled Drive.

## Run locally

From the repository root:

```sh
git fetch origin candidate/canon-control-room-20261114
git switch candidate/canon-control-room-20261114
python3 -m http.server 8765 --directory sites/canon-control-room
```

Open `http://127.0.0.1:8765/`. No npm, accounts, API key, cloud worker or remote server is required. On another device, use a LAN-accessible development host *only on a trusted network* and keep the preview local to your testing environment. Do not expose the development server publicly.

The app loads `canonSnapshotV1.json` over same-origin HTTP, so opening `index.html` directly with `file://` is not a supported install path.

## Features

- **Overview:** counts and a clearly labeled illustrated Lum viewport placeholder with mock chat dock, not a real 3D renderer or LLM chat.
- **System map:** grounded links for Godot 4, local WebView install, ChatGPT app boundary, 2D/3D Lum, XMBI, D&D, bar objects, BodySlide morph study, EVE, and LLMOS.
- **Assets:** safe public inventory metadata only. No private binary contents, private Drive IDs, source ZIPs or images.
- **Agents:** Lum-led source role cabinet, Yume, Oni twins and read-only mini-agent distinctions. No independent workers are started.
- **Compliance:** browser-local review checklist that cannot grant CI, runtime, rights or Crown proof.
- **Gaps:** filter by implemented/tentative/missing/blocked, edit local statuses and evidence notes.
- **Audit:** the existing `sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy` order. The deploy gate remains blocked in the UI.
- **Build / deploy:** separate source, local smoke, Godot/APK, plugin install, worker runtime and Render surfaces.
- **XMBI interaction:** swipe **vertically on the navigation rail** or use **Alt + Up/Down** (or arrow buttons). The control-room gesture is a prototype, not native Godot integration.

Edits are stored in browser `localStorage` under `luhmOs.canonControlRoom.localState.v1`; they do **not** write to GitHub or change official source truth. Export an explicit `canonControlRoom-localState.json` backup. Import merges valid versioned state, preserves unrelated local keys, and sanitizes status and notes. The imported file is never treated as authority. Browser storage may be cleared; export regularly.

## Source and review gates

```text
doctrine/currentSourceTruthV3.json     CANON SOURCE POINTER
doctrine/projectChatCanonV1.json       HISTORICAL ALIAS / CHAT BOOTSTRAP
doctrine/namingNamespaceCanonV1.json   camelHump MACHINE IDENTITIES
doctrine/agentSystemDeploymentV1.json  15 SOURCE-REGISTERED ROLE CONTRACTS
doctrine/storageTopologyV1.json        PRIVATE DRIVE BINARY BOUNDARY
frontEnd/index.html                    EXISTING ANDROID WEBVIEW CANDIDATE
sites/canon-control-room/              NEW DERIVED REVIEW UI ONLY
```

**Source law:** AI proposes. Policy authorizes. CI proves. Human promotes.

Verify the baseline before promoting any local status. Propose scoped changes through a PR with a pinned source SHA, targeted tests, provenance/rights checks, host/device receipts where applicable and rollback notes. Never auto-merge or auto-deploy. Do not use candidate statuses as proof of installed models, browser plugin host permissions, physical Android success, production signing, public rights or actual autonomous workers.

## Suggested smoke test

1. Serve over localhost and confirm all eight tabs render.
2. Swipe the rail up/down; test arrow buttons and Alt + Up/Down.
3. Filter systems and gaps, search assets, review a compliance item and edit one gap note.
4. Refresh the page; verify local edits persist.
5. Export and re-import local state; verify it merges and no source snapshot is overwritten.
6. Verify no secret tokens, private Drive URLs, unsafe scripts, network writes or public asset downloads appear in the browser.
7. Run `python3 -m unittest tests/testCanonControlRoomSource.py -v` from repository root.
8. Separately test `frontEnd/`, Godot 4 and actual ChatGPT plugin host only when permitted; never infer them from this web app's green browser UI.

## Sanest next slice

1. **Pin source**: compare the new UI and evidence paths with `currentSourceTruthV3`.
2. **Local preview**: static HTTP smoke on desktop/Android browser.
3. **Typed XMBI bridge**: small reversible event contract for up/down navigation to the existing front-end, then actual Godot boundary smoke.
4. **Private asset intake**: review approved rig/GLB/morph and D&D-bar scene provenance in owner-controlled storage.
5. **Harden plugin**: exact-source package, negative tests, SHA-256, ChatGPT host installation, mobile acceptance and rollback; Professor authorizes CAST separately.

**No authority escalation:** this site is an inspection and planning surface, never an agent runner, release agent or Canon promotion engine.
