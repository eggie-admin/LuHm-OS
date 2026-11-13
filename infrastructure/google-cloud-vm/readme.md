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
- `snapshot.sh --dry-run` plans a disk snapshot with zero API calls. An actual disk\n  snapshot is a separately billable GCE operation, gated behind VM boot and\n  exact-source verification, approved account identity and snapshot-cost authority.\n- **Google Cloud DNS is NOT activated**: canonical Cloudflare zone/NS, existing
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

## Final proposed Crown Cathedral closeout

The single SQL/JSON proof envelope at `doctrine/crown-single-proof-v1.json`
now contains the **whole creative company's closeout catalog**, not only VM
infrastructure: publisher/product identity, business records and operations,
illustrated field manuals, original comics (Rebel, Into the Warp, Crown Cathedral
scene plates), character artwork/Blender masters, campaign and partner assets.
These are **logical references** to private Drive content; source discovery is
not export/rights or public release permission. Originals, credits and original
dictation are preserved. Read `doctrine/organizationBrandRegistryV1.json`,
`doctrine/yumeCreativePipelineV1.json`, `manual/README.md`, and
`doctrine/continuityReleaseLifecycleV1.json` before promoting any content.

Existing two **product delivery lanes** (APP and PLUGIN) remain independent
of the existing four **company operating tiers**. They are not competing
classification schemes. Machine identifiers are camelHump, transport slugs
lowercase kebab-case, status tokens DRAGONTAIL, SQL keywords UPPERCASE.

### Google AI Big Brother executor

`host/api/google-ai-candidate-proxy.py` implements an explicitly gated,
server-side **Gemini Developer API** candidate-review request through the
existing `bigBrother` provider identity. It supports a source-only plan with
no Google key, network, cloud VM, or credits:

```bash
python3 host/api/google-ai-candidate-proxy.py --check
python3 host/api/google-ai-candidate-proxy.py --input /path/to/sanitized-task.json
```

For a real single `--execute` request, an operator-controlled trusted host
must inject `GEMINI_API_KEY`, an explicitly verified `GOOGLE_AI_MODEL`, and
all six current `GOOGLE_AI_*` gate values documented in `readiness()` as
`YES` (plus `GOOGLE_AI_MAX_REQUESTS=1`). These values represent checks
performed outside this repository; setting them is not evidence they were
truthfully verified. The executor is **not automatically deployed** or
reachable via public HTTP. It does not accept raw Drive files, private art,
email addresses, bearer tokens, account identifiers or tool-execution requests.
Its output remains advisory. The minimal signed-off provider smoke receipt is
needed before enabling persistent use.

Google Gemini API generation is distinct from Google Cloud DNS or Google
Cloud Compute Engine. An AI subscription, Drive storage, or code in GitHub
cannot create a Google Developer API key/role or prove that it is valid.
The authorized key belongs in an approved host secret manager, never in
GitHub files, ChatGPT chats, client JS, screenshots, or public issues.
Google Gemini API documentation: https://ai.google.dev/api/generate-content .
Current authentication guidance: https://ai.google.dev/gemini-api/docs/api-key .

### Network, proxy and publication freeze

Continue using existing Cloudflare-managed DNS and optional approved edge
policy; maintain current Render-managed HTTPS service and existing private
Project Hydra Site. Cloudflare should act as a **thin proxy when compatible**,
but its CURRENT authoritative DNS role cannot disappear without a separate
nameserver migration. Keep Google Cloud DNS and Hurricane Electric on hold.
The private NGINX VM is an optional test origin, not a replacement for Site
MCP registration. No auto-beta, app-identity replacement or external invite
until an actual Samsung ChatGPT inline touch+Undo receipt, privacy/rights
checks and supported external install path exist.

**Proposed → Canon → Doctrine** uses the existing everlasting covenant and
exact-source approvals. Passing source/CI may close the *proposed candidate*
only; it never grants public release, independent AI agent activation or Crown.
