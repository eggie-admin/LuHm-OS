# LuHm OS Pet Runtime Hardening

Status: **CROWN AMBER CANDIDATE**  
Authority: **Professor**  
Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**

This checkpoint hardens the path Professor asked for:

`FULLSCREEN -> MINI PLAYER -> PET INSPECT -> CHAT HEAD -> BACKGROUND -> EXIT`

It does **not** claim physical-device, Termux:X11, Ollama, Android bubble, release, or production proof.

## 1. Fullscreen Cathedral

Godot owns the visible LuHm OS game/cockpit. This remains the clean playable spine.

The fullscreen lane is intentionally boring at the process boundary: no arbitrary shell, no secrets, no embedded remote admin, no Termux execution bridge.

## 2. MINI PLAYER

The visual target is an **original Winamp-inspired compact strip**, not a Winamp skin clone.

Desktop/X11 implementation may use a borderless, always-on-top window with compact controls. Android native Godot must not pretend those desktop window flags create a system overlay.

Suggested controls:

`Lum | chat | pet | inspect | audio | expand | background | X`

Touch targets stay large even when the visual chrome is tiny.

## 3. PET INSPECT

The sitter is a cute, sexy, adult pixel-anime wifey presentation while remaining non-explicit and original.

Required animation states:

`idle / blink / talk / inspect / sleep / alert / drag / dismiss`

Recommended production format:

- 128x128 logical sprite canvas
- integer nearest-neighbor scaling
- transparent PNG/APNG or sprite sheets
- provenance manifest beside every imported community asset
- no automatic donor download or execution

## 4. CHAT HEAD / BUBBLE

There are two separate implementations.

### Desktop or Termux:X11

A small Godot/X11 window can be borderless and always-on-top when the display server supports it. This is the cleanest real window-sitter lane.

### Android native

A real Android system bubble is a native notification/conversation feature controlled by the user. Godot desktop flags are not evidence of Android bubble support. Until a native adapter exists and CI/device evidence is produced, this lane remains AMBER.

## 5. BACKGROUND

Do not equate "background" with "immortal process."

- Godot Android UI may be paused or killed by Android.
- Persistent Android work must obey current background and foreground-service rules.
- Termux/Ollama/X11 remain separate companion processes under operator control.
- No hidden restart loop.
- No kill-all command that catches unrelated Termux processes.

## 6. EXIT

Exit means exit.

LuHm-owned state must distinguish:

- close visible Godot window/app
- stop LuHm-owned X11 sitter client
- stop X server only when Professor explicitly chooses that scope
- stop Ollama only when Professor explicitly chooses that scope
- leave unrelated Termux sessions alone

## 7. Ollama hardening

Ollama is a local companion lane, not the Android app control plane.

Rules:

- local-only by default
- never treat an unauthenticated local API as safe for LAN/public exposure
- probe daemon/model state before GREEN
- use bounded keep-alive and request concurrency on mobile hardware
- use strictly local settings when the session is intended to remain offline
- no API keys in source, logs, screenshots, app assets, or doctrine

## 8. Termux hardening

Termux stays operator-owned.

- no root requirement
- scoped Android permissions only
- runtime packages and virtual environments stay in Termux private home unless separately proven
- no Android-app execution bridge in the clean LuHm runtime
- shell commands remain explicit operator actions

## 9. Termux:X11 hardening

Use the official Termux:X11 application and companion package as a matched pair.

Our doctrine deliberately rejects upstream root/SELinux-bypass instructions for LuHm OS. We do not need them for the supported lane.

Process ownership must remain visible:

- X11 Android activity
- X server process
- desktop/session process
- LuHm sitter client

Each has a separate stop action. That prevents the classic haunted-toaster problem where the UI is gone but three invisible processes are still chewing battery.

## 10. Copilot lane

Current spellbook doctrine defines Copilot as a bounded reviewer: scaffold, lint, test, refactor, and review proposed code only. It may not change doctrine, push/publish, deploy APKs, ingest donor code, print secrets, or silently alter deterministic state.

This environment does not expose a direct GitHub Copilot review action, so this checkpoint preserves a clean handoff target for Copilot rather than pretending a review occurred.

Recommended Copilot prompt for the branch:

> Review `luhm/pet-runtime-hardening-20260926` for Godot 4.7 syntax, Android lifecycle mistakes, process ownership leaks, false capability claims, and any path that could expose Termux/Ollama as an Android control plane. Do not mutate doctrine or publish.

## Ten-pass gate

1. Source-of-truth alignment.
2. Process lifecycle ownership.
3. Android lifecycle honesty.
4. Ollama locality and resource bounds.
5. Termux:X11 separation.
6. Window-capability feature gates.
7. Sprite provenance and licensing.
8. Secrets/shell/root/public-control-plane denial.
9. Deterministic CI contract proof.
10. Crown reporting and separate promotion.

A GREEN repository contract means the files agree with each other. It does **not** mean the phone, Ollama daemon, X11 session, bubble adapter, or production release is GREEN.
