# LuHm-OS public website: www.eggiebagelface.art

**Scope:** Prepare the existing **public** LuHm-OS studio website for a branded FQDN, while preserving Cloudflare Access on the **private** Worker. This document is an owner-executable plan. No live DNS, Render custom-domain, certificate, registrar, mail or private Worker settings are changed by this source update.

## Confirmed observations, 2026-11-18

- Canon domain spelling: `eggiebagelface.art` (not `iggybagelface.art`).
- Desired public website: **https://www.eggiebagelface.art/**.
- Root address: **https://eggiebagelface.art/**, ultimately directing to `www` without changing paths or query parameters.
- The **public** Render static service `luhm-os-publication-site` exists: https://luhm-os-publication-site.onrender.com/. Service ID: `srv-dauan1mgekts73dm91c0`. Publish path: `publicationSite`.
- Render dashboard service shows branch `publication/plugin-full-green-20260930`, auto-deploy **off**. Live page still says Project Hydra; the `main` website source says Project Premonition. Treat this as **deployment drift**, not DNS proof. Do not silently repoint or redeploy.
- External fetches of `https://www.eggiebagelface.art/` and `https://eggiebagelface.art/` did not return an inspectable page; actual DNS, redirect and TLS state are **unverified**.
- Existing Cloudflare Worker `https://luhm-os.eggiebagelface.workers.dev/` currently shows Cloudflare Access email-code authentication. **Do not** attach the public hostname to the protected Worker, turn off its Access policy, or carry access-login redirects into the public site.
- Existing `doctrine/staticPublicEdgeV1.json` lists apex as prior primary and `www` as alternate. This scoped desired-host configuration expresses the Professor's new preference; do not silently rewrite prior provenance until the actual FQDN works.

## Actual owner-account steps

1. In the **existing** Render public static service, open <https://dashboard.render.com/static/srv-dauan1mgekts73dm91c0> and navigate to **Settings → Custom Domains**. Review any existing hostnames first. Add `www.eggiebagelface.art` only if absent. Render's documented behavior is to add the root hostname as well and redirect it to `www`. Retain the current `onrender.com` fallback while testing.
2. In Cloudflare → `eggiebagelface.art` zone → **DNS → Records**, inspect current `www` and apex records and preserve all MX, SPF, DKIM, DMARC, DNSSEC/DS, NS, CAA and other subdomains. **Create only if nonconflicting**:
   
   | Type | Name | Target | Proxy initially |
   | --- | --- | --- | --- |
   | CNAME | `www` | `luhm-os-publication-site.onrender.com` | DNS only (grey cloud) |
   
   Do not assume a missing record from an unsuccessful public fetch. Do not replace an existing `www` CNAME/A/AAAA without reviewing its owner and use.
3. Check what Render asks for at the apex. If it requests an apex CNAME to the same verified Render hostname, review existing apex A/AAAA/CNAME first and use Cloudflare apex CNAME flattening *only where compatible with the existing zone and mail setup*. **No blanket deletion**. Cloudflare redirects require a proxied hostname; do not mix Cloudflare redirect rules into a DNS-only Render redirect without checking the actual route.
4. Wait for Render to confirm custom-domain ownership and issue a valid hostname-specific certificate. Render-managed TLS is the default. No self-signed origin certificate, phone Certbot, or private key in GitHub. The stricter Canon Let's Encrypt-only issuer goal needs an **actual serving-certificate issuer receipt**; a successful HTTPS page does not prove it.
5. Verify `www` serves the intended branded public site over HTTPS. Then verify the apex is reachable, redirects **once** to `www`, preserves `/privacy.html`, `/terms.html`, `/support.html` and query strings, and does not loop. Render should handle the apex-to-www redirect if both hostnames resolve correctly. Only add one Cloudflare redirect rule if needed after verifying Cloudflare proxy eligibility.
6. Review the branch mismatch separately: if the owner chooses current GitHub `main` site instead of the historic live branch, change the Render publication service's build branch through a scoped service configuration review, deploy an exact audited source, and verify title and policies before declaring Canon alignment. Do not deploy unreleased private artwork/agent functionality by changing this setting casually.
7. Recheck the **private Worker** still requires Cloudflare Access and that `mcp.eggiebagelface.art`, `system.eggiebagelface.art`, `art.eggiebagelface.art`, `assets.eggiebagelface.art` are unchanged. Recheck mail reachability if public DNS was touched.

## Non-destructive independent verification

Run from a terminal with network and DNS working:

```bash
dig +short CNAME www.eggiebagelface.art
dig +short NS eggiebagelface.art
curl -sS -I --max-time 15 https://www.eggiebagelface.art/
curl -sS -I --max-time 15 https://eggiebagelface.art/privacy.html?ref=canon
openssl s_client -connect www.eggiebagelface.art:443 \
  -servername www.eggiebagelface.art </dev/null 2>/dev/null | \
  openssl x509 -noout -issuer -subject -dates -ext subjectAltName
```

For apex: expect a permanent redirect status (301/308) with `Location: https://www.eggiebagelface.art/privacy.html?ref=canon`. Do not enable HSTS preload or `includeSubDomains` without separately verifying all active subdomains.

## DNS and other domain names

`www.eggiebagelface.art` is the fully qualified public website hostname. `eggiebagelface.art` is the zone apex, not a different purchase. The `art.eggiebagelface.luhmos.beta` string is a package-ID namespace, not DNS routing, and changing the web domain does **not** fix APK signing. Keep the ChatGPT MCP Render endpoint unchanged until its independent streaming/host checks pass.

## References
- Render: https://render.com/docs/custom-domains
- Render + Cloudflare: https://render.com/docs/configure-cloudflare-dns
- Cloudflare redirect documentation: https://developers.cloudflare.com/rules/url-forwarding/examples/redirect-root-to-www/
- Existing source contract: `doctrine/staticPublicEdgeV1.json`
- New stage receipt: `doctrine/wwwPublicFqdnActivationV1.json`

**Current result:** public-FQDN plan preserved in GitHub only. **Crown:** STOP pending authenticated provider changes and real DNS + TLS + redirect evidence.
