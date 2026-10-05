# LuHm System Portal Candidate

Status: CANDIDATE / CROWN=STOP

Purpose: provide a tiny read-only HTTPS landing layer for LuHm services. The portal is designed to sit behind Cloudflare DNS/Tunnel or another HTTPS reverse proxy without becoming an execution or authority surface.

Rules:
- static/read-only by default
- no credentials, bearer tokens, private keys, cookies, or provider secrets in source
- no Kugi execution, merge, signing, publication, deployment, or Crown authority
- DNS TXT/SRV are metadata/discovery only; HTML is served by HTTPS
- DNS-01/ACME material is never stored here as live secret state
- unknown or stale service state renders AMBER/UNKNOWN, never GREEN

Files:
- `index.html` static portal shell
- `services.json` bounded service registry
- `dns.example.yaml` Cloudflare/DNS design example only
- `portalPolicy.json` fail-closed portal contract

Promotion requires exact-head CI plus Professor review. This candidate does not configure Cloudflare, certificates, tunnels, DNS, or public exposure by itself.

## Air-traffic split

Canonical controller: `doctrine/cloudflareAirTrafficControllerV1.json`.

- ChatGPT plugin MCP currently flies directly to the canonical Render harness over Render-managed TLS.
- A future `mcp.eggiebagelface.art` custom domain uses Cloudflare as authoritative DNS, initially DNS-only to the Render hostname.
- The System Portal may use a separate Cloudflare Tunnel lane.
- Do not silently substitute the Tunnel lane for the MCP lane.
- Cloudflare is network traffic control only. It is not an AI provider, agent, source-truth authority, GREEN authority, or Crown authority.
