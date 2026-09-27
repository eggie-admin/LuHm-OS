# LuHm Agent Mesh — Crown-Gated Host Runtime

This directory defines the host-side OpenAI agent mesh for LuHm OS / Project Hydra.

## Authority

`AI proposes. Policy authorizes. CI proves. Human promotes.`

Lum is the only user-facing manager. Oni specialists are invoked as bounded agent tools so they return to Lum rather than taking over the conversation. No Oni may recursively recruit another agent. The runtime intentionally keeps parallel tool calls disabled; serial delegation is below the doctrine maximum of three concurrent helpers and fails closed until an audited scheduler exists.

## Agents

- **Lum** — manager/orchestrator; integrates evidence and speaks to Professor.
- **Kiri / Context** — resolves source authority, dependencies, receipts and blockers.
- **Tetsu / Build** — proposes the smallest reversible patch and tests; never executes mutations.
- **Momo / Research** — read-only external research using OpenAI hosted web search when invoked.
- **Shiori / Critic** — attacks unsupported GREEN, stale evidence and scope drift.
- **Kugi / Tool Executor** — remains outside the LLM mesh. Consequential mutations are executed only by a deterministic external tool path after Crown authorization and matching policy checks.

## Provider boundary

The Android APK does **not** contain `OPENAI_API_KEY`, provider credentials, a Python interpreter, Termux bridge, remote shell, or loopback control plane. OpenAI calls belong on the trusted host side. The APK carries only the non-secret agent/doctrine contract used to identify the active architecture.

Runtime secrets are expected from an environment file outside the repository, for example `/home/eggie/.secrets/luhm-agent.env` with mode `0600` and a parent directory with mode `0700`.

## Pinned SDK

The candidate pins `openai-agents==0.22.3`. CI installs the exact top-level SDK version and performs construction/self-tests without making an OpenAI request. A live provider smoke requires a separately authorized key and is intentionally not CI-green evidence.

## Privacy defaults

- Responses use `store=False`.
- OpenAI Agents tracing is disabled by the supplied service example unless the Professor explicitly opts in.
- No prompt, key, approval state or full RunState is shipped in the APK.
- The mobile client receives no provider secret.

## Local validation

```bash
python3 -m pip install -r agents/requirements.txt
python3 agents/luhm_mesh.py --self-test
python3 tools/agentMeshAudit.py
```

A live run is separate:

```bash
OPENAI_API_KEY=... python3 agents/luhm_mesh.py "audit the current candidate"
```

Live execution does not itself grant repository mutation, release, signing, publication or promotion authority.
