---
name: luhm-agent-workflow
description: Route LuHm OS work through Lum and the smallest evidence-gated Oni workflow, inspect source truth, and distinguish proven GREEN from pending gates.
---

# LuHm OS agent workflow

## Project chat bootstrap

For any LuHm OS / Project Hydra related request, first resolve and follow `agents/projectChatBootstrap/SKILL.md` plus `doctrine/projectChatCanonV1.json`. This portable skill does not replace that bootstrap contract.

The core chat environment is `lum` plus read-only monitoring mini-agents `urd`, `skuld`, and `belldandy`. Load other specialists only when the active task actually needs them.


Use this skill when the user asks to inspect, route, build, verify, diagnose, or continue work on LuHm OS / Project Hydra.

## Authority law

`AI proposes. Policy authorizes. CI proves. Human promotes.`

Professor is final human authority. The plugin does not grant release, signing, publication, protected-branch promotion, public-exposure, destructive-delete, or secret-write authority.

## Fast workflow

1. Call `luhm_status` when the request depends on current source truth, candidate state, deployment gates, or a GREEN claim.
2. Call `luhm_agent_roster` when role/skill availability matters.
3. Call `luhm_route_task` for non-trivial work. Use the smallest supported task kind and only the flags that match the request.
4. For truth-sensitive patch/build/release routing, pass explicit `taskId`, `sourceRef`, and `scopeId`. Do not rely on transport-session memory to identify the target source or authority.
5. Call `luhm_proof_contract` when imported Android proof, evidence identity, or proof-vault authority matters.
6. Call `luhm_transport_contract` when connection, FQDN, statelessness, authentication readiness, or session-authority questions matter.
7. Treat tool output as evidence and routing data, not as promotion authority.
8. If a required fact is absent, report `UNKNOWN` rather than filling it from memory.

## Explicit request scope

Transport state is not source truth. An MCP reconnect, HTTP session, or selected UI context must never silently change the candidate or grant authority.

For truth-sensitive routing, carry these values in the tool call:

- `taskId`: stable identity for the current task packet;
- `sourceRef`: the exact branch/SHA or other source identity being discussed;
- `scopeId`: the bounded workflow scope;
- `candidateSha`: optional exact candidate SHA when separately known;
- `proofContext`: optional receipt/proof identity.

`UNKNOWN` source identity cannot become GREEN, promotion, signing, publication, or mutation authority.

## Canonical role model

Lum is the only conversational boss. Helpers speak to Lum and never recursively recruit. Normal support-worker parallelism is at most 3. Tetsu and Kaji are the independent dual-build lane. DrNao is the read-only source-truth adjudicator. Kugi is deterministic execution/planning, not autonomous authority. Fumi normalizes cross-surface records. Yume handles art/media planning, Koe dictation normalization, Sumi asset/provenance review, Kiri context resolution, Momo bounded research, and Shiori contradiction challenge.

Detailed role behavior remains canonical in the repository under `agents/*/SKILL.md` and `agents/shared/ONI_PROTOCOL_V2.md`. This portable skill is an orchestration entry point, not a replacement source of truth.

## GREEN discipline

Never infer GREEN from presence, successful import, plausible output, stale evidence, or an AI statement. A proof imported from Android enters `UNKNOWN` until its required adjudication gate is satisfied. Exact sourceRef/scope identity must match the receipt being cited.

## MCP transport and authentication boundary

The bundled `luhm_local` MCP URL is a workstation-local development endpoint. Private local access may use OpenAI Secure MCP Tunnel rather than exposing the workstation publicly.

The production profile is HTTPS Streamable HTTP at the canonical LuHm MCP FQDN and remains stateless with respect to authority. Public beta tools are anonymous and read-only. Before any tool reads user-specific/private account data or writes state, add OAuth 2.1 using an established identity provider, protected-resource metadata, per-tool security schemes, PKCE S256, and server-side issuer/audience/expiry/scope validation. Do not substitute session selection, a committed API key, or model judgment for authorization.

## Android boundary

Android WebGlass remains secret-free and network-off by default. The Android proof vault may import user-selected SAF content, copy it into app-private content-addressed storage, calculate SHA-256, and render bounded safe previews. Provider credentials and the Python MCP server never ship inside the APK.

## Consequential stop

When a workflow reaches signing, publication, public exposure, protected/release promotion, destructive deletion, or another Crown boundary, report the proved candidate and stop for explicit human authority.

## Storage topology

Google Drive is the durable binary file server. GitHub is canonical source plus receipts/hashes/pointers and may use release/CI assets only as transient transport or cache. OpenAI is semantic state/context, not binary storage or source authority. Android/Termux is runtime and physical-proof space.

Prime law: `databases point to files; databases do not become the file server`.
