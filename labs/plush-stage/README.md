# Plush Stage | Offline 4×4 game-studio prototype

A standalone, dependency-free **creative game and shot planner**, designed to open on iPhone Safari or Samsung Chrome. The toy includes four editable plush names, four acts, sixteen scenes, and four theatrical actions. It can import and export a local JSON storyboard, preview a user-selected video clip, and attempt browser microphone recording when the page runs in a secure context.

## Privacy and boundaries

- Source-only placeholder cast. No child's name, account, videos, voices, photographs, transcripts, or other private media belongs in this public repository.
- No network calls, CDN, trackers, external dependencies, persistent local storage, ads, registration, or auto-posting.
- Uploaded media is never transmitted: file picker uses a browser-local object URL and is not included in the exported JSON.
- The recorded audio is downloaded through a browser-provided file action; compatibility varies with Safari/iOS, HTTPS permissions and active mic input. It is never sent to a server.
- Game choices, saved notes and project title only persist in RAM until explicitly exported. A tab reload resets the current project.
- This prototype cannot open/edit CapCut-native project files or export a finished video. CapCut's exported MP4/MOV is a *preview* input; game shot plans are separate JSON files.
- No ChatGPT account, unmoderated local LLM, public sharing, music ripping, biometric analysis or child profile.
- Standard YouTube embedding/linking can be added later for approved references. Never automatically download other creators' videos/audio.

## Running it

From a clone of the feature branch:

```sh
cd labs/plush-stage
python3 -m http.server 8766 --bind 127.0.0.1
```

Open **http://127.0.0.1:8766** on the **same device**. The microphone recorder needs HTTPS or secure localhost support. A public HTTPS demo requires a separately reviewed static host with no personal media; avoid exposing a Termux HTTP server directly to a child phone on the network. If loading `index.html` from Files, some iOS browser features may be unavailable.

On iPhone: eventually serve over HTTPS and use **Safari → Share → Add to Home Screen**. A Mac `.dmg` is not an iPhone app.

## Source-to-game pipeline

1. iPhone Camera captures original footage and voice. Keep the originals.
2. USB Yeti may be tested using an appropriate iPhone adapter and, when necessary, a powered USB hub. Verify input using Voice Memos or a supported recording app before blaming the game.
3. CapCut handles editing. Export MP4/MOV. Its native project format is not interoperable with this tool.
4. Plush Stage previews the exported video locally and exports JSON storyboards. Later adapters may accept separate recordings/captions and produce a Godot scene or video-edit decision list, without modifying CapCut files.

## Firmware and Odin

Samsung Odin protocol / open-source Heimdall applies to **certain Samsung Galaxy devices**, not iPhones, Yeti microphones, Logitech UVC webcams or unidentified camcorders. The first version performs **no flashing**. Do not attempt firmware writes until exact make/model, chip and firmware provenance are independently confirmed, the original state is backed up, and a responsible adult authorizes the update.

## Device and release gates

- Evidence needed: iPhone model/port, USB Yeti model/connector, browser version, secure-origin behavior, mic input path, CapCut exported video format, and actual on-device response.
- Playable source ≠ installed iOS PWA ≠ signed native iOS IPA ≠ App Store distribution.
- Keep the existing LuHm-OS agent quarantine and release/signing boundary intact.
- No merge to `main` or hosting of family material without separate review.
