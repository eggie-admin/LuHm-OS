# Firefox / FQDN / NGINX / SQL candidate

Current source: `69e8d2fc7df1288aaa1665efaea2bf2674056a1b`. Scope: source-only private candidate. **Not deployed. Crown STOP.**

## Target
- Firefox opens `https://eggiebagelface.art`, optionally `www` redirecting to apex.
- Browser logs in with a REAL OIDC authorization-code + PKCE implementation (no generated passwords or fake auth).
- Browser uses the same-origin `/api/v1/` path to avoid credentialed cross-origin CORS.
- `api.eggiebagelface.art/v1/` is reserved for separately verified bearer-auth API consumers.
- The current `https://luhm-os-harness-green.onrender.com/mcp` **does not move** during this work.
- For the current Render MCP custom domain, follow `plugins/luhm-os/DEPLOYMENT.md` (DNS-only CNAME, Render-managed TLS, streamable HTTP proof).
- NGINX runs only on an approved origin with private loopback web (`8789`), API (`8787`) and OIDC/session verifier (`8790`). **These services are NOT verified deployed.** No internet-to-workstation port-forwarding.

## Mandatory sequence
1. Snapshot current Cloudflare zone records/delegation/DNSSEC/CAA, Render routing and existing ingress. No NS or apex overwrite without evidence.
2. Select the actual managed/approved HTTPS origin and verify its ownership, domain, public identity and TLS certificate. Existing Render Python services do **not** become an NGINX server by changing this template.
3. Install a real OIDC verifier with pinned issuer/client settings in approved private environment storage: redirect URI exact match, state, nonce, PKCE S256, issuer/audience/expiry checks, short session TTL, `__Host-` Secure HttpOnly SameSite cookies, CSRF protections, MFA at provider where supported. On auth service error all private endpoints must return deny.
4. Run `nginx -t` with valid certificate paths before any reload. Enable the NGINX candidate only after local upstream checks and a restore point.
5. **Only then**, configure the approved zone records and Render custom-domain verification as appropriate. Root/apex cutover and API subdomain are separate changes with separate rollback.
6. Test Firefox desktop and Android HTTPS-Only mode; mixed content, login/logout/expiry, redirect loop, CSRF, unauthorized `/api/v1/` and `api.` access, mobile touch, session cookie scope and CORS.
7. Prove private SQL location/engine and least-privilege account. Prepared statements only, no runtime DDL, no raw SQL endpoint, no public port 3306/5432, backup+restore proof before schema changes. SQLite private metadata and MariaDB are alternative approved deployments, NOT both assumed live.
8. Re-check direct MCP `initialize`, tools/list, read-only routing and ChatGPT UI mount. Then human Crown review.

## Test and evidence
Run `python3 tools/firefoxFqdnSqlGatewayAudit.py` for source controls. These are **not** TLS, browser, identity, SQL or NGINX runtime tests. Collect exact DNS, TLS hostname/chain, NGINX `-t`, OIDC login, API deny/allow, DB role and restore receipts separately.

## Rollback
Preserve current Cloudflare and Render state first. Revert only the last changed record or NGINX service, restore last-known-good config, and keep existing `.onrender.com/mcp` path running. Never alter `main` by an unreviewed deployment.