# LuHm OS ChatGPT Plugin

LuHm OS packages reusable agent skills plus a hardened MCP server for source-truth inspection, bounded Lum/Oni routing, and proof-aware status.

## Current endpoint layout

- Canonical MCP endpoint: `https://luhm-os-harness-green.onrender.com/mcp`
- Health/readiness: `https://luhm-os-harness-green.onrender.com/healthz`
- Standalone cockpit: `https://luhm-os-harness-green.onrender.com/harness/`
- Local workstation MCP: `http://127.0.0.1:8788/mcp`

`plugins/luhm-os/mcp.json` is the current connection source. A custom FQDN, DNS cutover, Cloudflare proxy, or public directory publication is not implied by this README and remains separately evidence-gated and Professor-controlled.

## Portable plugin root

- `plugin.json` - Agent Plugins manifest.
- `mcp.json` - current remote HTTPS MCP connection.
- `mcp.local.json` - explicit loopback-only development connection.
- `mcp.remote.example.json` - non-routable deployment example.
- `skills/` - reusable LuHm workflow skills.
- `PRIVACY.md` and `TERMS.md` - publication-policy candidates.

## OpenAI developer-mode evaluation lane

Test capabilities before the complete installed plugin and retain evaluation prompts/results across releases.

1. Confirm public HTTPS Streamable HTTP at `/mcp` and inspect tool names, descriptions, schemas, annotations, authentication behavior, and model-readable results with MCP Inspector.
2. Enable ChatGPT Developer mode when available under the account/workspace policy.
3. Add the canonical MCP endpoint as a developer connection and inspect discovered tools and metadata.
4. Run direct, indirect, follow-up, authorization/confirmation, unsupported, and empty/error evaluation cases. Record selected tool, arguments, result, errors, and confirmation behavior.
5. Test optional UI both as a component and model-readable result. For LuHm, exercise `luhm_open_cockpit`, commandCapsule controls, networkTruth presentation, state restoration, and console-error behavior.
6. Optionally use the OpenAI API Playground MCP Server tool for raw request/response inspection.
7. After tool/schema/annotation/auth/UI-resource changes, deploy/restart, Refresh the developer connection, confirm metadata, start a new conversation, and rerun affected evaluations.
8. Package and test the complete plugin only after the MCP capability lane works. Verify skills, manifest, MCP connection, starter prompts, bundled references, negative cases, and end-to-end combined workflows.
9. Public submission remains a separate Professor Crown decision.

## Current authority boundary

The candidate exposes read-oriented status, roster, deterministic routing, proof-contract tools, and a read-only cockpit. It does not gain production signing, release promotion, publication, remote shell, secret-write authority, DNS/Cloudflare mutation authority, or GREEN authority.

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**
