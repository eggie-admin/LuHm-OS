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

## After Hours voice cabinet candidate

- Normal chat remains the default. The user explicitly enters with **AFTER HOURS** before **C** becomes a scene-continue command. Outside that mode, C is ordinary chat text.
- **OOC** or **PAUSE** pauses the scene; **RESUME** restarts it; **EXIT** returns to normal chat. The scene is read-only and has no authority effect.
- A typed `namedEnsembleTurn` can render Lum, Urd, Belldandy, Skuld, and Yume as labeled transcript segments. If the host exposes browser speech synthesis, each speaker may use an installed device voice. Voice mappings are a local presentation preference; the named transcript remains the fallback.
- The cockpit publishes events for a future Lum-mediated agent adapter. **This source candidate does not attach an agent runtime, invoke ChatGPT Voice, or call an Edge Gallery endpoint.** The C control displays that limitation instead of pretending agents responded.
- See `../doctrine/voiceCabinetRendererV1.json` for the presentation boundary and `../doctrine/voiceCabinetBridgeV1.json` for the roster and proof requirements.

### Device Read Aloud and voice input

- Each visible Lum/ensemble message has a **Read aloud** control that uses the selected installed device voice when host speech synthesis is available.
- The microphone button uses the browser SpeechRecognition API when exposed by the host. It transcribes one utterance into the normal composer or active After Hours router; the cockpit reports unavailable or permission errors without pretending audio was processed.
- These are device speech features, not ChatGPT app controls. The documented ChatGPT Voice flow is started from ChatGPT itself; this separate WebView has no supported hook to press the app's private Voice or Read Aloud controls ([ChatGPT Voice](https://help.openai.com/en/articles/20001274-chatgpt-voice)). For a true AI speech-to-speech session, OpenAI documents the Realtime API as a separate integration; browser clients need a backend-minted short-lived client secret, and a standard API key must stay server-side ([Realtime API](https://platform.openai.com/docs/api-reference/realtime?lang=javascript), [API key safety](https://platform.openai.com/docs/api-reference/authentication)).
