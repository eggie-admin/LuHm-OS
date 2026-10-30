# LuHm-OS Free-First Studio | GitHub workhorse, four streams, conditional Drive, local and remote proxies

**Status:** Proposed source-only. Authority: Professor. Public Crown: STOP. Google AI and remote VM account entitlements are UNVERIFIED. No proxy, VM, API key, billing or network settings changed.

## Four evidence streams, not four competing code repositories

1. **OpenAI:** agent conversation, semantic decisions, orchestration and pointers. Neither OpenAI consumer subscription nor ChatGPT conversation creates a developer API entitlement or build service.
2. **GitHub:** exclusive authoritative source, protected main, PRs, deterministic CI, exact SHA, source receipts and reproducible package builds. GitHub has no private Google Drive content by default.
3. **Google AI:** optional, free-tier-model-only advisory review of sanitized **public** source diffs after specific authenticated API/project/quota verification. Never allow developer review to become source mutation, production secret access or release authority. Free-tier inputs may be used by the provider to improve products.
4. **Runtime sidecars:** existing Render managed-TLS MCP/Godot runtime provides independent network and UI evidence. Cloudflare candidate, approved local host, and optional Google free-VM are separately verified deployments, never source authorities.

**Additional custody boundaries:** Google Drive is durable binary/file-vault storage only after a *fresh owner-only ACL check for the exact source and destination*. Samsung devices give physical runtime proof, never source authority. Both are independent of the four reasoning/control streams.

## CRITICAL: Drive ACL exposure

On October 30, 2026, connected Google Drive metadata reported **anyone:writer** on the previously designated **PRIVATE CONTROL PLANE** and the known **PUBLIC-WRITE WORKSPACE**. A separate October 25 owner-only Forge Candidate folder reported owner-only ACL. The September 22 recovery note said the private control plane had been owner-only; **that historical assertion is now contradicted by live metadata**. We do not put Drive folder IDs or signing-file identities in public source.

Treat the formerly private control plane as compromised for trust routing until authenticated ACL repair, membership verification, and child-folder permission inspection. Do not read, move, back up, copy, upload, delete, or publish secrets or protected masters through it. A label or parent ACL alone is not proof a child is safe. Use Google Drive settings or an owner-authorized permission-management integration to remove broad public writer grants, then read back permissions; user confirmation does not substitute for actual ACL proof. If secrets were ever exposed, separately assess and rotate affected credentials. The current connected Drive tools have **no delete permission** action.

## Four execution tiers

| Tier | Work | Proxy boundary |
| --- | --- | --- |
| 0. Thin client | Samsung WebView/DeX, touchscreen/S Pen cockpit, read-only status and local caching | Only normal authenticated TLS and OS permissions; no Python/Node/Blender daemon on Android |
| 1. Owner local studio | Blender, Godot 4, FFmpeg, hardware ingest, static export | Bind to 127.0.0.1 first. Any LAN/VPN/tunnel requires deliberate scoped authorization. No raw SQL or local machine admin from UI. |
| 2. GitHub workhorse | Source checks, npm/python builds, PR reviews, snapshots | Public repository free-hosted Actions, exact HEAD, minimal permissions, no Drive credentials, paid inference or signing keys |
| 3. Existing remote sidecar | Render managed TLS MCP previews; Cloudflare optional after failed Workers logs resolved; tiny VM only if approved | Reuse existing Render direct TLS. Separate auth for private methods, zero open proxy, no new public port, no unverified forwarding headers |

Daily snapshots are GitHub **ephemeral artifacts**, not durable Drive archives. They contain sanitized policy and bundle hashes, source SHA, test results and blockers. After secure Drive repair, an independently authorized owner-local job can upload accepted hashed binaries and then add sanitized GitHub pointers. Do not give public PR CI Drive OAuth access. Daily cadence is `14:37 UTC` and GitHub scheduling is best-effort. Schedules activate only once merged into the default branch.

## 4 sources × 4 tiers × 6 safety gates

96 documented routing cells: inventory, normalize, sandbox, zero-cost eligibility, independent proof, human approval. An inventory PASS does not prove remote running or free quota. The owner approval gate stays **BLOCKED** while external permission, model, signer and distribution receipts are absent. Use `python3 tools/freeFirstWorkspaceAudit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/free-first.json` to create a deterministic snapshot.

## Free-tier admission

- **Public GitHub Actions standard runner:** published no-charge eligibility, subject to usage-policy and Actions limits, **not** an always-on server. Use existing workflows rather than creating 129 additional agents. New daily workflow is source-build-only.
- **Personal Codespaces:** limited monthly quota. User account balance is unverified; idle shutdown, no unlimited studio claim.
- **Gemini Developer API:** certain models support limited free calls with provider free-tier processing terms. No key, API project, quota or billing status verified by source. Do not send private art, chat, protected models, customer data or signing material. Unknown model means no call.
- **Google Compute Engine e2-micro always-free:** eligible only under exact published regions/configuration and project billing rules. Not a GPU/media transcoding/rendering workstation. No instance provisioned.
- **Render:** existing services may be on a free plan; reuse them. Do not assume all new services, managed DB, Cron Jobs, storage, or sidecars are free.
- **Copilot:** developer assistance is not proof of included Copilot subscription or model quota. Prefer review on existing GitHub source and standard free CI until entitlements verified.

No billing entitlement system is needed **for zero-cost offline source builds**. A small explicit approval receipt *is* necessary before any billable sidecar/model/VM action. Default request budget $0; unknown or exceeded quota degrades to deterministic local/offline processing.

## Antenna, resolution and studio

Samsung S24 FE is the unrooted antenna/mobile test device; Tab S10 Lite is touch and art QA; Linux workstation owns heavy interactive Blender/Godot/FFmpeg. Video candidate quality is adaptive 540p → 720p → 1080p → physical native-measured. These are design profiles, not verified GPU FPS or webcam performance. Six simultaneous cameras, Bluetooth/microphone mux, USB access, Shizuku, Secure Folder and hardware permission paths must each be proven with owner-driven device receipts.

**Next evidence:** revoke/verify exposed ACL; GitHub exact-head daily workflow green; resolve Workers build log; verify Render and local proxy auth; demonstrate one rights-cleared Blender → FFmpeg → Godot → WebView mobile round-trip; prove signing and same-signer update; only then publish Beta.
