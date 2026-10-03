# LuHm OS ChatGPT Plugin

LuHm OS packages reusable agent skills plus a hardened MCP server for source-truth inspection, bounded Lum/Oni routing, and proof-aware status.

## Endpoint layout

- Production MCP FQDN: `https://mcp.eggiebagelface.art/mcp`
- Render bootstrap origin: `https://luhm-os-mcp.onrender.com`
- Health/readiness: `https://mcp.eggiebagelface.art/healthz`
- OpenAI domain challenge: `https://mcp.eggiebagelface.art/.well-known/openai-apps-challenge`
- Local workstation MCP: `http://127.0.0.1:8788/mcp`

The production endpoint is intentionally separate from the workstation. Render is the public application edge; the workstation remains local-first.

## Portable plugin root

Required portable files live here:

- `plugin.json` - Agent Plugins manifest.
- `mcp.json` - production remote HTTPS MCP connection.
- `mcp.local.json` - explicit loopback-only development connection.
- `mcp.remote.example.json` - non-routable deployment example.
- `skills/` - reusable LuHm workflow skills.
- `PRIVACY.md` and `TERMS.md` - publication-policy candidates.

## Render production lane

The repository root `render.yaml` is the deployment contract for the `luhm-os-mcp` web service.

It requires:

- Python 3.12.11.
- MCP SDK 2.2.0.
- CI checks passing before automatic deploy.
- app-level `/healthz` readiness.
- production profile binding to Render's `PORT` on `0.0.0.0`.
- DNS-rebinding protection with the canonical `mcp.eggiebagelface.art` Host allowlisted.
- the Render-provided `RENDER_EXTERNAL_HOSTNAME` accepted only when it is a bare `*.onrender.com` hostname, so bootstrap diagnostics work before FQDN cutover.
- 1 MiB maximum MCP request bodies.
- stateless HTTP compatibility.
- Render's default `onrender.com` hostname disabled only after the custom domain is proven healthy.
- `OPENAI_APPS_CHALLENGE` supplied through Render secret configuration, never committed.

Render terminates public TLS and redirects HTTP to HTTPS. The Python MCP process receives proxied HTTP only inside Render's service boundary.

## Cloudflare DNS

For the custom FQDN, create a Cloudflare CNAME named `mcp` that points to `luhm-os-mcp.onrender.com`.

During Render domain verification and certificate issuance, use **DNS only**. Remove any `AAAA` record for `mcp`, because Render's custom-domain path currently uses IPv4. After Render reports the certificate valid, Cloudflare proxying is optional. Keep Cloudflare SSL/TLS mode at **Full** if proxying is enabled.

Do not expose workstation ports and do not point the public FQDN at a LAN address.

## OpenAI plugin review lane

Before public submission:

1. exact source SHA and package CI are GREEN;
2. Render deploy is healthy on the production FQDN;
3. `https://mcp.eggiebagelface.art/mcp` initializes successfully with MCP Inspector;
4. every tool advertises `readOnlyHint=true`, `openWorldHint=false`, and `destructiveHint=false` accurately;
5. the OpenAI portal challenge token is placed in Render as `OPENAI_APPS_CHALLENGE` and the well-known endpoint returns only that token;
6. privacy and terms URLs resolve publicly;
7. ChatGPT developer-mode tool scan succeeds against the production FQDN;
8. golden prompts call each expected tool and reject unsupported inputs cleanly;
9. logs contain no secrets or unnecessary personal data;
10. public submission remains a separate Crown decision.

## Current authority boundary

The candidate exposes read-oriented status, roster, deterministic routing, and proof-contract tools. It does not gain production signing, release promotion, publication, remote shell, secret-write authority, or GREEN authority.

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**


Candidate transport rules and verified current boundaries: `doctrine/luhmNetworkTransportV1.json`.
