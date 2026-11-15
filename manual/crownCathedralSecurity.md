# Crown Cathedral · one-time signing, certificate and email foundation

**Owner/authority:** Professor · **Project:** LuHm-OS · **Zone:** `eggiebagelface.art`  
**Professor's scoped CAST:** APPROVED for staged source/tooling, Cloudflare mail-route provisioning, GPG owner setup and public Let's Encrypt proof. **Provider proof:** NOT YET GREEN. **Product Crown:** STOP.

This guide applies alongside `doctrine/currentSourceTruthV3.json`, `doctrine/securityTrustFoundationV1.json`, `doctrine/crownCathedralMailRoutingV1.json`, and `SECURITY.md`.

## One rule: no self-signed certificates

- Public-facing TLS is accepted only when a **publicly trusted Let's Encrypt** certificate is confirmed for the actual hostname. Never generate self-signed website, origin, proxy, or LAN TLS for this milestone.
- A private `*.lan` name cannot receive a publicly trusted Let's Encrypt certificate. Use a genuine hostname under the owned `eggiebagelface.art` zone with DNS-01 validation and internal split-horizon resolution if local HTTPS is required.
- Cloudflare **Universal SSL is publicly trusted** but **does not guarantee Let's Encrypt**: Cloudflare selects the CA and may change it. To deliberately select Let's Encrypt for a proxied Cloudflare edge certificate, review the **paid** Advanced Certificate Manager option. Do **not** purchase it, replace a live certificate, or disable Universal SSL without checking cost and providing a working replacement.
- Cloudflare Origin CA certificates are not publicly trusted and are **not allowed by this strict Let's Encrypt policy**. Even though they are not technically self-signed, they do not meet this milestone's requirement.
- Render's managed TLS is safe to leave in place pending issuer proof. The actual issuer **must be verified**, not assumed. If Render uses a different publicly trusted issuer, record AMBER against this **strict LE-only** acceptance rule rather than replacing a working endpoint blindly.
- Let's Encrypt uses ACME **HTTP-01 or DNS-01**, not inbox verification. Let's Encrypt stopped certificate expiration notification emails in **June 2025**, so add an independent certificate monitor.

## Cloudflare incoming email

Use existing Cloudflare DNS. **First inspect existing MX, SPF, DKIM, DMARC and existing inboxes.** Cloudflare Email Routing normally needs exclusive root MX ownership. Never remove existing live mail provider MX without a migration plan.

Create one verified destination: the project's **owner-controlled Gmail**, held only in local operator configuration and not committed in public source. The owner must click the verification email sent by Cloudflare.

Create the following addresses, all forwarded to that verified Gmail destination:

| Address | Purpose | Suggested Gmail label |
| --- | --- | --- |
| admin@eggiebagelface.art | corporate admin / account verification | LuHm/Admin |
| web@eggiebagelface.art | website operations | LuHm/Web |
| webmaster@eggiebagelface.art | conventional webmaster contact | LuHm/Web |
| postmaster@eggiebagelface.art | mail system contact | LuHm/Mail |
| hostmaster@eggiebagelface.art | DNS and hostname contacts | LuHm/Infrastructure |
| security@eggiebagelface.art | security disclosures | LuHm/Security |
| abuse@eggiebagelface.art | abuse notices | LuHm/Security |
| support@eggiebagelface.art | public support | LuHm/Support |
| certs@eggiebagelface.art | our own TLS monitoring alerts | LuHm/Certificates |
| errors@eggiebagelface.art | sanitized website/app error reports | LuHm/Errors |
| dmarc@eggiebagelface.art | domain mail-authentication reports | LuHm/Mail |

**Do not enable catch-all** until mail-abuse/privacy implications are assessed. `noreply@` is not needed for inbound contact and should not pretend to be a support address.

### Account provisioning sequence

1. In Cloudflare, select the correct account/zone under **Compute > Email Service > Email Routing**. Check whether Email Routing is already active. Back up existing DNS mail configuration without secrets.
2. Add owner Gmail to **Destination Addresses** and complete the Gmail verification link. Until then, forward rules will be disabled.
3. If the zone has no competing mail provider, onboard Email Routing so Cloudflare manages the required MX/DKIM/SPF. If it does, preserve mail delivery and plan a deliberate migration.
4. On the owner workstation, use a **zone-scoped Cloudflare API token** with Email Routing Rules Read/Write, Addresses Read/Write and DNS Records Read. Do not use the global Cloudflare API key. Put values in the owner secret manager only:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_ZONE_ID`
   - `LUHM_MAIL_DESTINATION`
5. Once environment variables exist, run `python3 tools/cloudflareEmailRoutingApply.py --audit`. If the destination does not yet exist, use `--request-verification` once. After Gmail verification and Cloudflare MX readiness, run `--apply-rules`. This idempotent tool adds missing rules only and refuses to overwrite conflicting ones. **It does not change DNS.**
6. Send a test message from an unrelated email provider to each alias and confirm delivery to Gmail, preserved headers, labels and reply routing. Gmail labels currently exist in the connected account, but **automatic Gmail filters were not created** by this source change.
7. For replying *as* `support@` or another brand address, configure an actual authenticated **outbound SMTP provider** with DKIM/SPF/DMARC alignment, then use Gmail's verified **Send mail as** feature if supported. **Cloudflare Email Routing alone is inbound forwarding**, not outbound mailbox hosting. Replies sent directly as ordinary Gmail do not automatically appear as the branded alias.

## Separate signing identities

- **Git owner:** use `bash tools/ownerGpgBootstrap.sh --configure` on an owner-controlled interactive workstation. It generates an Ed25519 **GPG signing** key if none exists, registers only the armored **public** key with GitHub, and enables signed commits/tags. Inspect fingerprint and create two encrypted offline recovery copies of private key + revocation material.
- **Do not** generate a GitHub signing private key in CI or in chat. This repository's GitHub App-generated API commits may not be Verified by the owner's GPG key. Test the GitHub **require signed commits** rule with actual bot contributors before applying to `main`, otherwise the integration could be locked out.
- **GitHub Actions:** use built-in `GITHUB_TOKEN` with narrow workflow permissions; use OIDC to federated clouds when the receiving provider supports it; use short-lived GitHub App installation tokens for managed repo access. Do not create evergreen personal access tokens or impersonate an owner's GPG key.
- **OAuth / MCP:** separate public anonymous read-only endpoints from private scoped OAuth 2.1 + PKCE S256 operations. Validate resource indicator, audience, issuer, scopes, expiry and redirect URI. Tokens reside only in server-side secret storage.
- **Android:** release keystore and F-Droid index key are distinct from TLS and Git commit keys. Store offline/owner controlled. Their creation and public use remain separately gated.

## Certificate check (read-only)

Run from an internet-connected trusted operator machine:

```bash
python3 tools/securityTrustCertAudit.py --host eggiebagelface.art --json
python3 tools/securityTrustCertAudit.py --host luhm-os-harness-green.onrender.com --json
# Add only deployed hostnames, such as mcp.eggiebagelface.art AFTER domain readiness.
```

This script uses OS-trusted CA validation, hostname verification, Let's Encrypt issuer matching and >=14 days remaining by default. It **cannot prove renewal automation**, and a failed probe is not authority to replace an active certificate.

Actual success requires receipts for: serving certificate SAN/issuer/fingerprint/expiry; Cloudflare edge vs origin TLS; owner-held key fingerprint and a GitHub **Verified** commit; correct GitHub protection rules; verified email destination; Cloudflare active routes; independently received test emails; approved outgoing mail identity and SPF/DKIM/DMARC; automatic certificate renewal checks; and recovery rehearsal.

**Milestone logic:** Professor approval = GREEN authority to prepare and carry out this scoped setup. Source candidate = review pending. Mail forwarding, TLS issuer, source signing and provider rulesets = AMBER/UNVERIFIED until actual readbacks pass. No agent or CI automatically declares global Crown.
