# LuHm OS ChatGPT Plugin

LuHm OS packages reusable agent skills plus an MCP server for source-truth inspection, bounded Lum/Oni routing, and proof-aware status.

## Portable plugin root

Required portable files live here:

- `plugin.json` - Agent Plugins manifest.
- `mcp.json` - local-development MCP connection.
- `skills/` - reusable LuHm workflow skills.
- `PRIVACY.md` and `TERMS.md` - publication-policy candidates.

`mcp.remote.example.json` is a deployment template only. It deliberately uses the reserved `.invalid` domain so it cannot be mistaken for a live backend.

## Development connection

The repository MCP server is `host/mcp/luhmMcpServer.py` and defaults to `http://127.0.0.1:8788/mcp` for workstation-local development.

ChatGPT does not directly reach workstation loopback. Use an approved secure tunnel for development, or deploy the MCP server behind a stable HTTPS endpoint. Do not make the workstation server public merely by changing it to `0.0.0.0`.

## Production connection

A publishable ChatGPT app/plugin requires a tested remote HTTPS MCP endpoint. Before replacing `mcp.json` with that endpoint, verify:

1. exact source SHA and package audit are GREEN;
2. endpoint is HTTPS and exposes only `/mcp` plus explicitly documented health metadata;
3. authentication/authorization match the data and actions exposed;
4. provider secrets remain server-side;
5. MCP DNS-rebinding/host/origin protections are configured for the deployed hostname;
6. tool schemas and read/write annotations match actual behavior;
7. privacy and terms URLs resolve publicly;
8. ChatGPT developer-mode tool scan succeeds;
9. a real ChatGPT conversation calls each expected tool;
10. publication remains a separate Crown decision.

## Current authority boundary

The candidate exposes read-oriented status, roster, routing, and proof-contract tools. It does not gain production signing, release promotion, publication, remote shell, or secret-write authority.

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**
