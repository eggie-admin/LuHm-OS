# LuHm OS: Cloudflare DNS, CDN, PKI and Zero Trust edge

**Canonical source:** `eggie-admin/LuHm-OS` • **Owner:** Professor • **Network change state:** STOP pending owner-account proof. This is an executable *read-only audit plan* plus reviewed source law, **not** live Cloudflare application.

Read first: `doctrine/cloudflareEdgeHardeningV1.json`, `doctrine/cloudflareAirTrafficControllerV1.json`, `doctrine/networkSpineV1.json` and `doctrine/belldandyPkiCorporateSecretaryV1.json`.

## Existing architecture. Do not re-onboard the zone.

Cloudflare remains the established operator/provider in source doctrine. Do **not** invent assigned nameservers, run nameservers, transfer registrars, overwrite apex records or set new public A/AAAA records toward the private workstation.

The currently linked MCP endpoint is `https://luhm-os-harness-green.onrender.com/mcp` with **Render-managed TLS**. Keep it direct and stable while the in-chat cockpit contract is being debugged. A Cloudflare-proxied domain or a Tunnel is **not** a prerequisite for that MCP connection.

The local `eggiebagelface.lan` namespace belongs to LAN-only `dnsmasq` and is never published in public Cloudflare DNS. No router port forwarding, public IP exposure of workstation, externally open MariaDB/SSH, or public mic/camera routes.

## Hostname / transport registry

| Canonical identity | Current vs candidate | DNS / traffic | Certificates & cache | Action |
| --- | --- | --- | --- | --- |
| `eggiebagelface.art` | Established zone, exact current apex unresolved | Preserve provider delegation, current apex records; inspect NS/SOA/DS/CAA | Do not force redirect or HSTS until apex and subdomains are proved | Inspect only |
| `ai.eggiebagelface.art` | Legacy host, verify current use | Do not change existing tunnel or records without live owner receipt | Access and cert status unknown | Inspect only |
| `mcp.eggiebagelface.art` | Candidate alias | When requested and verified: **DNS-only CNAME** to actual Render hostname, without AAAA conflict. Live plugin remains on `.onrender.com`. | Render-managed TLS; no CDN cache, no Cloudflare Access HTML redirects | Do not apply without Render custom-domain and ChatGPT streaming proof |
| `system.eggiebagelface.art` | Candidate private portal | Outbound-only cloudflared Tunnel -> bounded private Nginx; protected by Access. No port forward | Verify browser-edge TLS **and** Tunnel-to-origin TLS independently; never `noTLSVerify` | No live activation before identity, hostname and connector receipts |
| `assets.eggiebagelface.art` | Candidate public CDN | Existing safe baseline: Render same-origin `/harness/assets/`. Cloudflare CDN is optional, after origin/cert/rights proof. | Cache only rights-approved, hashed immutable public media | Private Rebel masters never enter CDN |
| `art.eggiebagelface.art` | F-Droid repo candidate | Preserve current DNS until signed APK repo origin and index metadata exist | Immutable signed APK by digest; signed indexes revalidate | Do not publish unsigned/debug packages |
| `eggiebagelface.lan` | Internal namespace | Local resolver only; never public wildcard / CNAME / A / AAAA | LAN local trust independent of Cloudflare | KEEP PRIVATE |

The reversed semantic code namespace `art.eggiebagelface.*` is not reverse DNS/PTR. PTR records on third-party shared Render/Cloudflare IPs are not LuHm-owned. Nameserver delegation needs no replacement merely for certificate or Android beta work.

## Zone / authoritative NS / DNSSEC

Read assigned Cloudflare zone NS from the actual account; compare the registrar's parent-zone delegation, public recursive resolution, and authoritative SOA. Preserve the known setup if there is no incident. If DNSSEC is on, confirm the registrar DS matches Cloudflare's DNSKEY and validation succeeds; do not remove or reconfigure DS in a blind rebuild. CAA, if configured, must authorize the actual issuers that will renew current edge and origin certs; do not assume a hardcoded issuer list. Never disclose scoped API tokens, keys, or hidden DNS verification challenge secrets in repo or receipts.

For a manual read-only host check in a normal network-enabled Linux shell:

```bash
python3 tools/cloudflareEdgeHardeningAudit.py
python3 tools/cloudflareEdgeHardeningAudit.py --live
# Optional: network tools provide raw DNS observations, not Cloudflare account access.
dig +short NS eggiebagelface.art @1.1.1.1
dig +short SOA eggiebagelface.art @1.1.1.1
dig +short DS eggiebagelface.art @1.1.1.1
dig +short CAA eggiebagelface.art @1.1.1.1
```

An absent answer, recursive answer, or successful certificate probe **alone** is not an authoritative zone-change approval.

## Certificates: edge -> proxy -> origin

- **DNS-only Render alias or active `.onrender.com`**: Render issues/renews origin certificate on its managed service. Do not install duplicate Certbot or Cloudflare Origin CA inside the Python MCP app. Confirm the alias is actually verified at Render before altering DNS.
- **Cloudflare-proxied public assets/private portal**: Cloudflare's edge certificate is managed by Cloudflare; configure SSL/TLS to **Full (strict)** only with a matching, unexpired origin certificate already installed. Cloudflare Origin CA or normal publicly trusted CA can validate a suitable origin.
- **Cloudflare Tunnel to Nginx**: check `cloudflared` verification of its origin's CA/name separately. No `noTLSVerify: true`. For private local CA, install trusted CA on the connector, not into GitHub.
- **PKI ledger (Belldandy)**: record SANs, issuer, validity, SHA-256 fingerprint, renewal and revocation receipts, and secret custodian **reference only**. Never PEM private keys or API tokens.
- **HTTP redirects/HSTS**: HTTPS only after matching cert is observed; use one redirect owner. No automatic `includeSubDomains` or HSTS preload that could break pending F-Droid or MCP names. Prefer TLS 1.3 where supported; maintain appropriate client compatibility.

## Reverse proxy, security and Zero Trust

**MCP / ChatGPT:** retain direct HTTPS Render ingress and Streamable HTTP response semantics. Do not insert Cloudflare proxy/WAF challenge, Access login redirects, cache rules, URL rewrites or Tunnel in front of the currently working transport before testing real `initialize`, tool list, SSE/streaming, headers, and ChatGPT UI mounts. Static 200 is **not** protocol proof.

**Private system:** create Access application with owner-only allow and MFA **before** tunnel hostname publication; machine-to-machine consumers need scoped service tokens, not public bypass policies. Verify Access JWT at `cloudflared`/origin as configured. Tunnel connector egresses outbound only to Cloudflare. Keep origin loopback/LAN-bound and Nginx allowlisted. Do not expose database admin, raw shell, SSH, or private `.lan` resolution.

**CDN:** Cloudflare Cache Rules apply only to **proxied** hostnames. Set explicit bypass for `/mcp`, private routes and authorization/cookies; do not cache `Set-Cookie`, user-specific HTML, metadata, signed-in or Rebel-private assets. Public hashed images/JS/CSS can use long immutable caching only after rights/release proof. F-Droid signed index metadata requires revalidation and must not be treated as forever immutable. Review WAF and rate limits against real permitted clients before enforcing global challenges.

**Recovery:** do not edit working Render endpoints while chasing Cloudflare hostname changes. Snapshot DNS/proxy/Access settings **outside public Git** before any account mutation; change one hostname/rule at a time, verify TLS and exact route, and restore the previous DNS-only or direct Render route on failure. Never raise an origin's privilege to make a CDN check pass.

## What would make it actually GREEN

1. A real Cloudflare account snapshot: zone ID held privately, assigned NS and registrar delegation, active record types, DNSSEC status, SSL mode, certificate hostnames/validity, caching/WAF rules, tunnel status and Access application policy.
2. Validate each **in-scope hostname** from an external network, with timestamped NS/SOA/DS/CAA plus SNI-correct TLS and HTTPS response, and record the actual expected origin/service.
3. If the MCP alias is required: Render verified custom domain first; DNS-only alias next; test MCP protocol, ChatGPT tool discovery and resource UI mount **before** flipping the plugin manifest or attempting proxy mode.
4. If a private portal is required: verified owner MFA, Access policy and token validation, local Nginx verified TLS, tunnel healthy, end-to-end denial tests, no ports forwarded.
5. For CDN: publish **approved** static assets only; check cache hit/miss and no private or authenticated response retention, plus a purge/rollback dry-run.
6. Belldandy records only nonsecret receipts. Urd evaluates current evidence. Professor approves each externally visible mutation.

**Current honest status:** source hardening can pass CI. Account NS/DNSSEC/cert/proxy/WAF/cache/tunnel/Access remain unverified until a Cloudflare-scoped connection or actual read-only account proof is available. No new paid Cloudflare, DNS, registrar or remote origin required to keep Rebel production moving.

Vendor references: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/ ; https://developers.cloudflare.com/cache/how-to/cache-rules/ ; https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/ ; https://developers.cloudflare.com/tunnel/concepts/routing/
