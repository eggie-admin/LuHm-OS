# KAI 9000 Cathedral Skill

Use this skill when building or auditing the LuHm OS Cathedral lane that combines the native Godot shell, a caged local website/WebView cockpit, the optional Termux/Ollama companion, and the bounded Lum/Oni agent mesh.

## Source resolution

1. Current Professor instruction wins for requested candidate scope.
2. Resolve exact `eggie-admin/LuHm-OS` branch and SHA.
3. Preserve `main` unless separately authorized.
4. Reuse the current agent-mesh and WebView candidates by reference, not by copying legacy runtimes wholesale.
5. Treat `luhmos/api-spine-20260918` and older KAI/Termux material as selective donor/reference only.

## Cathedral boundaries

- Godot 4 remains the Android app/game lifecycle owner.
- WebView loads only bundled assets and receives no direct network/API privileges.
- `jquery.luhmSite` is UI-only and may not call shell, filesystem, remote fetch, WebSocket, or arbitrary URLs.
- Termux + Ollama is an optional headless companion. The base APK must still launch without it.
- The first implementation is a CLI adapter to loopback Ollama, not a public or privileged network listener.
- WebView never talks to Ollama directly. Native code or an explicitly trusted operator path mediates.
- No provider secrets in source, APK assets, screenshots, logs, or receipts.

## Agent workflow

`DOCTRINE -> AUDIT -> SANITY -> APPROACH -> READ/SHARD -> SINGLE PLAN -> SINGLE WRITE -> FOCUSED TEST -> EXACT-HEAD CI -> SEAL -> HUMAN PROMOTION`

- Lum is the only user-facing boss.
- Oni-Kumo = Context, Oni-Tetsu = Build, Oni-Sumi = Research.
- Oni-Ibara appears for audit/security/release/architecture conflict.
- Helpers are read-only, max parallelism 3, max delegation depth 1.
- Kanabo Gate is deterministic and performs only already-authorized side effects.
- Direct questions bypass the mesh.
- Evidence moves by reference.

## Background learning

Background learning means local **candidate-memory distillation**, not autonomous retraining.

A scheduled local job may summarize bounded event records into candidate memories with provenance. Candidate memories remain inactive until human promotion. The learner may not rewrite prompts, agent roles, source code, policies, or model weights.

## Proof ladder

1. Static contract audit.
2. Headless Ollama CLI unit tests and Termux shell syntax.
3. Website/plugin syntax and no-network checks.
4. Agent-mesh contract audit.
5. Exact-head GitHub Actions.
6. Android testing APK build receipt.
7. Native WebView/Termux mediation proof.
8. Physical Samsung launch/touch/chat smoke.
9. Only then may a later human action promote a proposed build.

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**
