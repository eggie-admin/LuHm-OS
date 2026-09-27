---
name: luhm-agent-workflow
description: Route LuHm OS work through Lum and the smallest evidence-gated Oni workflow, inspect source truth, and distinguish proven GREEN from pending gates.
---

# LuHm OS agent workflow

Use this skill when the user asks to inspect, route, build, verify, diagnose, or continue work on LuHm OS / Project Hydra.

## Authority law

`AI proposes. Policy authorizes. CI proves. Human promotes.`

Professor is final human authority. The plugin does not grant release, signing, publication, protected-branch promotion, public-exposure, destructive-delete, or secret-write authority.

## Fast workflow

1. Call `luhm_status` when the request depends on current source truth, candidate state, deployment gates, or a GREEN claim.
2. Call `luhm_agent_roster` when role/skill availability matters.
3. Call `luhm_route_task` for non-trivial work. Use the smallest supported task kind and only the flags that match the request.
4. Call `luhm_proof_contract` when imported Android proof, evidence identity, or proof-vault authority matters.
5. Treat tool output as evidence and routing data, not as promotion authority.
6. If a required fact is absent, report `UNKNOWN` rather than filling it from memory.

## Canonical role model

Lum is the only conversational boss. Helpers speak to Lum and never recursively recruit. Normal support-worker parallelism is at most 3. Tetsu and Kaji are the independent dual-build lane. DrNao is the read-only source-truth adjudicator. Kugi is deterministic execution/planning, not autonomous authority. Fumi normalizes cross-surface records. Yume handles art/media planning, Koe dictation normalization, Sumi asset/provenance review, Kiri context resolution, Momo bounded research, and Shiori contradiction challenge.

Detailed role behavior remains canonical in the repository under `agents/*/SKILL.md` and `agents/shared/ONI_PROTOCOL_V2.md`. This portable skill is an orchestration entry point, not a replacement source of truth.

## GREEN discipline

Never infer GREEN from presence, successful import, plausible output, stale evidence, or an AI statement. A proof imported from Android enters `UNKNOWN` until its required adjudication gate is satisfied. Exact sourceRef/scope identity must match the receipt being cited.

## Local MCP boundary

The bundled `luhm_local` MCP URL is a workstation-local development endpoint. ChatGPT developer-mode access to a private local server requires an approved connection path such as OpenAI Secure MCP Tunnel. Do not reinterpret `127.0.0.1` as a public endpoint and do not expose it by binding the server to `0.0.0.0`.

## Android boundary

Android WebGlass remains secret-free and network-off by default. The Android proof vault may import user-selected SAF content, copy it into app-private content-addressed storage, calculate SHA-256, and render bounded safe previews. Provider credentials and the Python MCP server never ship inside the APK.

## Consequential stop

When a workflow reaches signing, publication, public exposure, protected/release promotion, destructive deletion, or another Crown boundary, report the proved candidate and stop for explicit human authority.
