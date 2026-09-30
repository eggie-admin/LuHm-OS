# LuHm OS MCP Enterprise Deployment Runbook

Status: staged production candidate. This runbook does not authorize public release.

Canonical production MCP origin: `https://mcp.eggiebagelface.art`

## Architecture

`ChatGPT / Codex -> HTTPS -> Render edge -> LuHm MCP process`

Cloudflare is authoritative DNS for the public name. During initial certificate issuance the `mcp` record stays **DNS only**, so Render receives the TLS connection directly. The workstation is never an origin for the public endpoint.

The local development endpoint remains `http://127.0.0.1:8788/mcp` and is not published.

## Phase 1: Render bootstrap

1. Deploy the `luhm-mcp` web service from the repository Blueprint.
2. Keep `renderSubdomainPolicy: enabled` during bootstrap so the generated Render hostname remains available for service-health diagnosis.
3. The build must run both `python host/mcp/luhmMcpServer.py --check` and `python tools/luhmPluginPackageAudit.py` before the service can start.
4. Confirm `/healthz` returns only service/version health metadata and never source truth or secrets.
5. Confirm the process binds Render's `PORT` and that production Host filtering accepts only the canonical FQDN.

## Phase 2: FQDN and TLS

In Render, attach `mcp.eggiebagelface.art` as the custom domain.

In Cloudflare DNS:

- create CNAME `mcp` -> the Render-generated `*.onrender.com` hostname;
- use **DNS only** while Render verifies the domain and issues its certificate;
- remove any `AAAA` record for `mcp` because this Render custom-domain path is IPv4;
- do not point the FQDN to a LAN address and do not expose workstation ports.

If the `eggiebagelface.art` zone uses restrictive CAA records, allow both Render certificate authorities:

- `CAA 0 issue "letsencrypt.org"`
- `CAA 0 issue "pki.goog"`

Render terminates TLS, automatically redirects HTTP to HTTPS, and manages certificate renewal. Do not add a second origin certificate inside the Python service.

For this MCP endpoint, keep Cloudflare in DNS-only mode unless proxy behavior is separately tested against MCP streaming and OpenAI connectivity. If Cloudflare proxying is later approved, use SSL/TLS mode **Full** and re-run the complete MCP transport test suite.

## Phase 3: TLS proof

Required evidence before cutover:

1. DNS resolves `mcp.eggiebagelface.art` through the intended Render target.
2. `http://mcp.eggiebagelface.art/healthz` redirects to HTTPS.
3. the HTTPS certificate is valid for `mcp.eggiebagelface.art` with no browser/client trust error;
4. `https://mcp.eggiebagelface.art/healthz` returns HTTP 200 and minimal health JSON;
5. MCP Inspector initializes `https://mcp.eggiebagelface.art/mcp` and discovers only the expected read-only tools;
6. invalid Host values and unsupported task kinds fail closed;
7. no secret-like material appears in deployment logs.

Do not add HSTS preload or `includeSubDomains` at first cutover. Those settings affect the whole domain hierarchy and require a separate deliberate review.

## Phase 4: OpenAI domain verification

The OpenAI submission portal provides a domain-verification token.

Store that token only in Render as the secret environment value `OPENAI_APPS_CHALLENGE`. Never commit it.

The server exposes:

`https://mcp.eggiebagelface.art/.well-known/openai-apps-challenge`

That endpoint must return exactly the configured token as plain text and nothing else.

After verification, run **Scan Tools** and inspect every discovered tool and annotation before any submission decision.

## Authentication boundary

The current candidate is intentionally anonymous and read-only. It exposes bounded project-status/routing contracts and no user-specific account data or write action.

Before any tool can read user-specific/private account data or mutate state, add **OAuth 2.1** using the MCP authorization contract. That upgrade requires protected-resource metadata, authorization-server discovery, PKCE S256, issuer/audience/expiry/scope validation, and per-tool security metadata. Do not substitute a hard-coded API key in the plugin package.

OpenAI-managed mTLS can strengthen ChatGPT client authentication only when the public TLS edge can validate or safely forward the client certificate. Do not claim mTLS enforcement behind Render unless that path is explicitly proven.

## Observability and operations

Production operations require:

- Render health checks on `/healthz`;
- deployment only after GitHub checks pass;
- logs that exclude secrets, raw credentials, and unnecessary personal data;
- alerting for repeated initialization failures, 5xx responses, and abnormal request volume;
- dependency patch review and pinned build inputs;
- rollback to the previous known-good Render deploy instead of live source editing;
- no database or persistent disk until a tool actually needs state.

If scale requires multiple instances, keep MCP runtime stateless or move required state into an explicitly managed backing service before scaling horizontally.

## CROWN CUTOVER

Only after DNS, TLS, MCP initialization, OpenAI domain verification, and exact-head CI receipts are GREEN:

1. change the Blueprint to `renderSubdomainPolicy: disabled`;
2. redeploy and confirm the generated `onrender.com` hostname returns 404;
3. re-run FQDN health and MCP initialization tests;
4. preserve the exact source SHA and deployment receipt;
5. request the separate human Crown decision for public submission/promotion.

No CI or hosting success grants publication authority by itself.
