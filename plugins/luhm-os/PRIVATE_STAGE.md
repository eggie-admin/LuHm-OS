# LuHm OS Private Plugin Stage

Status: PRIVATE STAGING ONLY. This file does not authorize public publication.

## Goal
Use LuHm OS privately through ChatGPT with the existing read-only MCP surface while keeping a clean path toward later public review.

## Private connection target
Preferred canonical URL: `https://mcp.eggiebagelface.art/mcp` once custom-domain DNS/TLS is independently proven.

Private fallback URL: `https://luhm-os-mcp.onrender.com/mcp`.

The fallback exists only so private testing does not depend on the unfinished custom-domain gate. It does not replace the canonical production FQDN.

## Current private tool surface
- `luhm_status`
- `luhm_agent_roster`
- `luhm_validate_scope`
- `luhm_route_task`
- `luhm_proof_contract`
- transport/source-contract inspection tools exposed by the current read-only MCP server

All current plugin capabilities remain read-only. No merge, publish, production signing, destructive delete, secret write, infrastructure mutation, or Crown promotion tool is exposed.

## ChatGPT private-use flow
1. Open ChatGPT on a surface that exposes Plugins/developer mode.
2. Enable Developer mode under Settings -> Security and login if available for the account.
3. Open Plugins -> Personal -> add MCP server.
4. Try the canonical URL first only after TLS/DNS evidence is GREEN; otherwise use the private Render fallback URL above.
5. Install the resulting personal plugin.
6. In ChatGPT Work, invoke it with `@LuHm OS` and run the staged positive/negative tests in `review-tests.json`.

If the account does not expose personal MCP creation, that is an external product-access gate, not a LuHm source failure.

## Public-release staging
The repository keeps public submission separate from private use. A future public submission requires explicit Professor Crown authority plus verified publisher identity, public website/support/privacy/terms URLs, custom-domain TLS evidence, review test receipts, and a final OpenAI policy review.

## Monetization boundary
Monetization is disabled in this stage. Do not add checkout, subscription purchase, digital-service upsells, or upgrade promotion to the plugin without a fresh OpenAI commerce-policy review. Existing external paid-account entitlements may be recognized later only if the then-current rules permit it.

## Source law
AI proposes. Policy authorizes. CI proves. Human promotes.
