---
name: luhm-oni-summoner-ui
description: Render the LuHm Oni roster, bounded summon requests, and observed task/process activity in the jQuery cockpit and ChatGPT MCP Apps surface without inventing hidden reasoning or authority.
---

# LuHm Oni Summoner UI

Use this skill for the Oni summon/activity GUI only.

## Canonical authority

`AI proposes. Policy authorizes. CI proves. Human promotes.`

Lum is the only conversational boss. The GUI never promotes a worker, process, tool call, or animation into authority.

## UI contract

Display every canonical role from `doctrine/ONI_MESH_CONTROL_PLANE_V2.json` with:
- name;
- role/kind;
- canonical skill path;
- default authority;
- current observed activity state;
- concise observed summary;
- task/source identity when present;
- receipt reference when present.

A summon button emits a bounded request to the host/router. It never invokes Kugi or another executor directly.

## Background process law

Render only observed task/process events. Valid presentation states are `PARKED`, `QUEUED`, `ACTIVE`, `WAITING`, `VERIFYING`, `SUCCESS`, and `ERROR`.

Do not fabricate background work to keep the UI lively. Fun animation may decorate a real state, but cannot create one.

## Thinking echo law

The chat bubble may show a short activity/status summary that is safe to expose. Do not expose hidden chain-of-thought, private scratchpad text, raw prompts, tool arguments, secrets, or private evidence blobs.

## Surface split

- **In-app:** `$.fn.luhmOniSummoner` on existing jQuery 3.7.1.
- **In-chat:** MCP Apps widget adapter with the same roster/activity schema. The widget may call `luhm_request_oni` through the standard `tools/call` bridge; the result is a bounded request packet, not worker execution.

The in-chat adapter is dependency-free to keep the ChatGPT frame self-contained; this does not replace the canonical jQuery implementation.

## Consequential stop

The UI may request routing. Merge, signing, publication, destructive delete, public exposure, persistent secret writes, and protected/release promotion remain Crown-gated.
