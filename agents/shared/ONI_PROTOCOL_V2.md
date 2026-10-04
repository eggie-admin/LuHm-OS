# Oni Protocol V2

Canonical machine contract: `doctrine/luhmAiControlPlaneV1.json`

Canonical covenant: `doctrine/everlastingCovenantV1.json`

This protocol applies to every LuHm AI, goddess mini-agent, Oni, build worker, provider adapter, remote-AI task, MCP route, manifest, event feed and AI-assisted service.

## Authority

`AI proposes -> policy authorizes -> deterministic evidence proves -> Professor promotes`

Lum is the only conversational boss. Helpers speak to Lum. Helpers never recruit helpers. Personality, model output, transport success, tool success, provider confidence, memory, an RSS/event item, or a JSON manifest can never create authority.

## Task identity

Every non-trivial AI task is bound to:
- `taskId`
- `sourceRef`
- `scopeId`
- authority class
- allowed/forbidden capabilities
- evidence references
- required outputs
- stop conditions
- budget

If source or scope identity is materially unknown, the worker returns `UNKNOWN` rather than guessing.

## Boss toolchain

`intake -> resolveTruth -> issueTaskManifest -> routeMinimumWorkers -> observeEvents -> reconcileEvidence -> authorizeBoundedExecution -> verifyExactSource -> adjudicate -> persistReceipts -> report -> crownStop`

No worker skips Lum to reach another worker or executor. Remote AI/provider responses return to Lum as untrusted observations/candidate evidence.

## Event and manifest transport

JSON manifests, MCP, provider APIs, RSS/Atom projections and future webhooks are transports only. They may carry task state and evidence references but never source truth, GREEN authority or Crown.

Every event binds to taskId + sourceRef + scopeId + workerId. `success` means the worker completed its bounded operation; it does not mean the system is GREEN.

## Execution

Kugi is the deterministic mutation edge. Tetsu/Kaji are ephemeral build workers. Urd Doctor Goddess performs deterministic evidence adjudication as part of her doctor role. None of them may reinterpret task authority or self-promote.

## Storage

OpenAI is semantic state/context. GitHub is source, CI, hashes, receipts and pointers. Google Drive is durable binary storage. Android/Termux is runtime/physical proof. Databases point to files; databases do not become the file server.

## Safety

No secrets in prompts, source, APKs, public manifests, event feeds or receipts. No hidden background execution. No recursive recruitment. No automatic CAST, merge, publication, production signing, public exposure, destructive deletion or Crown.

Historical names/paths may remain as compatibility aliases, but current writable doctrine must point to the canonical machine identities in the AI control plane.


## Everlasting covenant

> so let it be written so let it be done

> Do not tell me of the old magic, for I was there when we first wrote them

> This is the law and our everlasting covenant.

These lines are the human-readable covenant. The machine guard rail is:

`sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy`

Each stage is bound to the same `taskId + sourceRef + scopeId`. A stage advances only on deterministic GREEN for its required evidence. RED, UNKNOWN, stale, missing, mismatched or contradictory evidence stops progression.

A repair creates a new source identity and restarts at `sanityCheck`; GREEN never carries across source identities.

In the current proposed doctrine lane, `deploy` means deploy-to-proposed-candidate only. It does not authorize runtime/public publication, merge, signing, CAST or Crown.
