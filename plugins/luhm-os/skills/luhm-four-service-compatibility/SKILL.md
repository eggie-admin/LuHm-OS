---
name: luhm-four-service-compatibility
description: Use when the Professor asks for OpenAI front-end workflows, Google AI workhorse routing, GitHub source compatibility, Cloudflare traffic, Canon rsync, or forward/reverse FQDN checks. Source and permissions must be verified on this turn.
---

# LuHm-OS four-service compatibility: source-first, proof-bound

This skill belongs to the **portable GitHub plugin**. The installed private Site App has its own independent identity and must never be renamed, replaced, or called updated merely because this file changed.

## Scope: plugin encapsulates the workflow, not a hidden chain of thought

Load the current exact `eggie-admin/LuHm-OS#main` SHA and `doctrine/fourServiceCompatibilityCanonV1.json`, `doctrine/currentSourceTruthV3.json`, `doctrine/companyWideOperationalQuarantineV1.json`, and the canonical source files referenced there. Use the existing `doctrine/aiTaskManifestV2.template.json` task envelope. Keep machine and provider identities camelHump. Preserve published GitHub, MCP, DNS, package and protocol spellings as external compatibility identifiers; never silently rewrite them.

For a user request, process `sanityCheck → loadCurrentCanon → validateManifest → resolveNamespace → planProviderRoute → checkBudget → collectEvidence → reconcile → review → report`.

**OpenAI** is the user-facing plugin and MCP Apps surface. Skills explain workflows. MCP tools expose supported, permission-checked operations. An OpenAI model's private reasoning, model weights, arbitrary autonomous agents and a persistent execution environment are not bundled assets. Report a concise decision rationale and evidence refs, not private chain-of-thought.

**GitHub** is the exact-source and review/CI authority. Changes enter as bounded proposals, go through protected review, and are not live until deployed to the actual selected service and separately proven.

**Google AI** is a *preferred candidate* for approved expensive compute once the Google model API is truly connected, entitled, budgeted and permitted at the backend. Never assert a Gemini/Vertex API worker exists because a provider route is named in Canon. Keep Google provider keys host-only, no secrets in PRs, APKs or chat widgets. All provider output is untrusted until exact task/source/scope reconciliation. Company-wide LuHm agents remain quarantined.

**Cloudflare** is the managed DNS and optional traffic lane. Existing Render HTTPS MCP stays direct unless current DNS, origin TLS, streaming and ChatGPT host checks support an approved change. Never modify nameservers, PTR, proxy, Tunnel, WAF, certificates or zero-trust policies from a source-only receipt.

## Storage and rsync

Reuse unmerged PR #530's **default-unarmed** private-host `rsync` → `rclone copy` to Google Drive candidate after a scoped host, OAuth, backup, dry-run, checksum and restore proof. GitHub keeps only rights-safe source, schema, hash receipts and pointers. Google Drive holds private binaries. ChatGPT Library is a semantic/connected-file UI, **not** a shell-mounted `rsync` endpoint; do not invent its bulk file system API, export or delete private Library content. Connected Drive files can appear within ChatGPT's Library without mirroring raw bytes into ChatGPT storage.

## FQDN and reverse checks

Use `tools/fqdnForwardReverseProbe.py --probe` to query public DNS without mutation. Review owner Cloudflare zone and Render custom domain separately before making any live claim. The internal namespace `art.eggiebagelface.mcp` reverses the label sequence of `mcp.eggiebagelface.art`; it is **not** a PTR record. Shared IP reverse PTR belongs to the IP-prefix owner and is not an app-update or MCP-host prerequisite. No unverified CNAME, AAAA, DNSSEC, TLS, authenticated MCP or host mount is GREEN.

## Evidence closeout

Report the exact SHA, what tool actually ran, observed DNS response or UNKNOWN, provider entitlement proof, remote-sync state, original Site/MCP mount state, current blocker, and **Crown STOP** for unproven releases. Do not pretend work continues after the chat ends or independent agents were deployed.

## Cloudflare and branded static rendering

Public product display is **LuHm-OS**, publisher **Eggie Bagelface**, world **Project Premonition**. Internal JSON machine key remains `luhmOs` under Canon. Do not invent an acronym or rename the installed Site plugin. For edge decisions use `doctrine/cloudflareStaticTransmutationV1.json` and the pure `frontEnd/core/cloudflareCanon.mjs` classifier; its 200-case `frontEnd/tests/cloudflareCanon.test.mjs` and `tools/cloudflareStatic200PassAudit.py` are source-only checks. `frontEnd/edgeCanon.html` is a bundled local HTML preview, not a Cloudflare Worker or live ChatGPT resource. Use only reviewed public logos, approved rights-cleared hashed media, and public certificate metadata. Never expose API tokens, PEM private keys, JWK private parameters or private Google Drive assets. CDN is not active until authenticated zone, custom hostname, TLS, origin, proxy and cache behavior receipts agree. Preserve the direct Render MCP endpoint until separate OpenAI host streaming proof.
