# LuHm OS first-install foundation · Professor's Basement

**Status: source checklist / draft PR only. Not a CAST, merge, install, DNS mutation, certificate issuance, deployment or classroom graduation.**

This is the **one-page gate** before starting development debugging. Check the existing parts and only revisit items that failed, changed source identity or are newly required. Avoid giant context reloads or building new plugins that already exist.

## Four foundations

| Foundation | Source already present | Verification required | Do not redo |
| --- | --- | --- | --- |
| **1 · Identity / Branding** | [organizationBrandRegistryV1](../doctrine/organizationBrandRegistryV1.json), [character canon](../game/canon/CHARACTER_CANON_V1.json), [pet presentation](../doctrine/characterPetPresentationV1.json), [loading sprites](../host/harness/agent-loading-sprites.json), [brand-session candidate](../doctrine/defaultBrandSessionTrustCandidateV1.json) | First paint on installed host, Godot boot, original-art provenance and rights; visually review final character approvals. | Do not regenerate approved masters, replace the pet dock or treat an emoji as a final character portrait. |
| **2 · Plugin / Skills** | [LuHm plugin](../plugins/luhm-os/plugin.json) v0.5.2, [MCP URL](../plugins/luhm-os/mcp.json), five [bundled skills](../plugins/luhm-os/skills), `luhm_open_cockpit` and `luhm_open_mobile_cockpit` source, glass module dock | Independently confirm current ChatGPT host install, exact tool discovery, resource URI and mobile mount; owner-managed Site/Project Hydra plugin is a **separate product/update path**. | Do not duplicate the personal Site app, overwrite plugin ID or assume GitHub repo commits update Plugin Creator-owned releases. |
| **3 · Architecture / Pipelines** | Python3 MCP, [frontEnd package lock](../frontEnd/package-lock.json), self-hosted jQuery/jQuery UI, Godot 4, GitHub Actions, existing Render MCP, [network spine](../doctrine/networkSpineV1.json), [CDN candidate](../doctrine/oneServiceCdnCandidateV1.json) | Exact-head source tests; check **deployed** SHA separately; Verify Cloudflare custom DNS/TLS, /mcp streaming and branded /assets/ only when actually activated. | Do not create new paid services, expose .lan publicly or replace the healthy direct Render route to make a staged hostname appear live. |
| **4 · Documentation / Rights** | [README](../README.md), [GPL-3.0 license](../LICENSE), [contributing](../CONTRIBUTING.md), [security](../SECURITY.md), [third-party notices](../THIRD_PARTY_NOTICES.md), [plugin privacy](../plugins/luhm-os/PRIVACY.md), [plugin terms](../plugins/luhm-os/TERMS.md), [virgin-install runbook](../plugins/luhm-os/VIRGIN_INSTALL.md) | Ship matching privacy/terms/license links and actual dependency notices; use per-asset copyright and release approval checks. | Do not change GPL terms from a setup task, imply public approval for unapproved art or add private chat/email content to public Git. |

## Actual tools and update responsibilities

**Installed/available in chat:** GitHub (canonical repository and Actions proof), Project Hydra (separate Site read-only MCP interface), Plugin Creator (owned-plugin source/update only for eligible plugin identities), Plugin Management (discovery and permissions), Gmail and Google Drive (only when a specified communication, approved private record or private binary is needed). Specialized installed skills include `github-first-seven-plane`, `project-hydra-continuity`, `goddess-cabinet-live-chat`, and `luhm-glass-module-dock`. Those are workflow tools, not additional autonomous workers.

**GitHub package skills:** `belldandy-housekeeping`, `luhm-agent-workflow`, `luhm-coding-roleplay`, `luhm-glass-module-dock`, `solo-studio-default`. The owner-managed Project Hydra Site plugin has its **own** skills and versioned release. Do not copy its private IDs, archives or owner account secrets into the public repository.

**Storage:** GitHub = public-safe code, manifests, CI, release hash receipts. Owner-controlled Drive = durable approved private binaries. Cloudflare = DNS/TLS/edge delivery proposal. Render = currently running host subject to observed source/deploy receipt. Gmail = private communications only with user-appropriate recipient and explicit purpose, not a bulk dependency in virgin-install.

## Default quick path

`inspect exact ref → run firstInstallFoundationAudit.py → targeted CI → source receipt → install/render/device proof if needed`.

No reinstall for a presentation-only change if the existing hosted MCP resource can be safely updated, but check the tool contract and host state before claiming a mobile UI fix. First-install is quick because most artifacts are **already source-present**; no source audit can claim actual host, mobile, Cloudflare or copyright clearance.

`python3 tools/firstInstallFoundationAudit.py` (offline, read-only) and
`python3 -m unittest tests/testFirstInstallFoundationAudit.py -v` (negative controls).

## Current open issues

- Shared **LuHm OS GitHub plugin package** and **personal Project Hydra Site plugin** remain independently versioned/updated.
- GitHub `ui://luhm-os/cockpit-v2.html` source and connected Site `cockpit-site-v3.html` response require reconciliation.
- Current network doctrine uses `mcp.eggiebagelface.art` → direct Render; proposed public apex `/mcp` is **not live**.
- Copyright release audit must validate every shipped asset and dependency version. Having asset slot names does not supply final approved character masters.
- Public beta, Android signing, Cloudflare Worker, custom domain, login policies, and host-rendered corrected GUI still require independent proofs/owner decisions.

**Crown STOP; Class 1 remains open; no irreversible mutation.**
