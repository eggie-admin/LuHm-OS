# LuHm-OS · strict Google Cloud VM candidate

**Source only.** This is a GitHub-pinned **VM configuration snapshot**, not an actual
Google Compute Engine disk snapshot, running VM, Google API connection, Cloud DNS
delegation, authenticated Site fix, or released beta.

## Why this shape

- Existing canonical `eggie-admin/LuHm-OS` remains the ONLY source of truth.
- Snapshot: `vm-profile.json` with one private Debian 12 `e2-micro` in an eligible
  US zone and 30 GB `pd-standard` disk. Not a Blender/AI inference server.
- `install-web.sh`: idempotent NGINX installation, static HTML on
  `127.0.0.1:8080`, no frontend framework, secrets, or public exposure.
- `provision.sh --dry-run`: generates exact CLI plan, **never contacts Google**.
- `provision.sh --apply`: requires matching account/project, verified billing,
  IAM, quota, explicit cost flag and a preexisting private outbound package path.
  No NAT, firewall, IAM, DNS or VM added automatically by the source-only workflow.
- A private no-external-IP VM needs a pre-existing approved Cloud NAT or package
  mirror to `apt-get install nginx`; without it, the startup script fails closed.
  An existing IAP-only SSH path (scoped `35.235.240.0/20` to port 22, OS Login)
  is also required to access the VM; this candidate creates neither.
- The private NGINX test intentionally does not expose a ChatGPT MCP endpoint.
  Existing Render and the owner-private ChatGPT Site remain the current services.
- **Google Cloud DNS is NOT activated**: canonical Cloudflare zone/NS, existing
  `mcp.`, `system.`, `assets.`, and `art.eggiebagelface.art` routes remain intact.
  A Google Cloud DNS migration is a separate paid, verified and reversible plan.
- Network routing order: client → current Cloudflare DNS/optional reviewed edge
  → existing Render HTTPS → bounded MCP. The private Google VM is an isolated
  alternative web origin, **not a drop-in replacement** for the Site MCP editor.

## SQL/JSON proof consolidation

`doctrine/crown-single-proof-v1.json` is ONE logical evidence envelope
with `proofId`, `sourceRef`, `taskId`, `scopeId` and nested evidence
pointers, mapped to canon's exact four tiers. A SQL implementation can upsert
JSON1 using **INSERT**, **SELECT**, **UPDATE**, **JSON_VALID**, **JSON_EXTRACT**
and `sourceRef`; the database stores indexes/pointers, not private media,
credentials or multiple contradictory sources of truth. Historic receipts
remain immutable, not erased. No source-only test flips host, phone or Crown GREEN.

## Safe gates

The founder's current ChatGPT Site inline mount is RED, Google Cloud API
identity/billing/quota are unverified through this connector, and plugin outside
account sharing is unverified. **Do not auto-release a public beta or invite
Alex to install**. The prior private reviewer update is not a plugin install link.

First verify account-owned Google Compute Engine in the matching Google
project, then private VM boot/NGINX through authorized IAP, then Site owner
editor and real Android touch + Undo, then review paid DNS alternative and
private beta distribution separately. No need to recreate the existing app.
