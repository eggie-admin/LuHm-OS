# Eggie Bagelface · Studio public front door

This is an intentionally **static, public, under-construction** site for `eggiebagelface.art`. Source-only staging is not proof of deployment.

## Public identity

- **Pirate Daddy Studios**: creative house / umbrella label (no assertion of legal registration)
- **Pirate Daddy Film**: film imprint / public working name. Existing historical `Pirate Daddy's Film` and `PIRATE DADDIES FILM` nomenclature retained in private/source metadata.
- **Eggie Bagelface Art**: independent artist and public publisher, @eggiebagelface on Instagram.
- **LuHm-OS** remains the software product, not another public brand title for the whole studio site.
- Contact for launch: `eggiebagelface@gmail.com` until Cloudflare forwards the proposed `admin@`, `support@`, `web@` aliases and each has a verified inbound test.

## Private/Public line

Public = `studioPortal/index.html`, hand-written CSS and copy only. It contains no unpublished media, passwords, Drive links, third-party tracking scripts, user analytics, embedded Meta token or outgoing automation.

Private = **owner-only Google Drive Studio Release Desk** (separately verified not shared), with one branch per brand, Drafts / In Review / Approved / Published Receipts, plus a native Google Sheets approval board. The existing Pirate Daddy's Film social-media folder and its 2026-10-20 ratified law remain the source production workflow; the new desk is only the outbound publishing gate, not a replacement for originals.

### Approval invariant

A post may be prepared as a **Draft** by AI or collaborator. The user must approve the exact caption, destination platform, source media version, ownership/license, and any disclosure; only Professor may set **Approved** in the private board. Publishing is a separate explicit action, never inferred from moving a file or a passing CI check. Record release URL and version. Drafts or media without actual approval stay private.

## Deployment path

Use one **existing** provider account, not a second unnecessary stack:

1. Ask the owner to confirm the active Render workspace. Create a free static service on that confirmed workspace with repository `https://github.com/eggie-admin/LuHm-OS`, branch `main`, `buildCommand: echo "Static studio portal"`, and publish path `studioPortal`.
2. Confirm HTTPS and content at Render's assigned URL; don't guess or claim it is live before an HTTP proof.
3. Inspect actual Cloudflare zone `eggiebagelface.art` and current apex/WWW records before editing. Preserve all existing mail records and other services. Attach custom domain to the already-verified Render static site, follow the provider-recommended CNAME/A record, then verify HTTPS certificates and `https://eggiebagelface.art/` externally.
4. Certificate issuer policy in the separate Crown Cathedral milestone is strict Let's Encrypt. Render and Cloudflare choose issuers differently; do not assume provider-managed certificate implies the required issuer, and don't buy certificate management without a new explicit pricing decision.
5. Only after DNS/TLS success and the owner's preview acceptance, mark the site LIVE in a nonsecret operational receipt.

Do not create a fake private route on a public static site. If a browser-accessible private portal is later wanted, use Cloudflare Access or authenticated provider identity with origin enforcement rather than a public HTML page hiding content in CSS or JavaScript.

## Social connectors

- Windsor.ai has authenticated read access to Instagram `eggiebagelface` and exposes supported write action names; **no social account actions were executed for this milestone**.
- vidIQ does not currently show an Instagram publishing connection, so its draft/publish flow cannot be applied to that account until an actual social connection is established.
- If the owner connects Meta Business Suite or a review-capable scheduler, map approved board rows to native drafts. Never auto-post, and preserve the exact platform publication receipt.

**Crown:** public placeholder source can be approved/merged, but real site release, Meta publish, credentials, art rights, account changes and network records each require their own observed receipts.
