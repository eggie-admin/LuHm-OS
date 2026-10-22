# OpenAI developer entitlements | LuHm OS source-only candidate

**Studio:** Pirate Daddy's Film (independent, private, non-Enterprise)
**Source:** `doctrine/openAiDeveloperEntitlementsV1.json`
**Canonical repository:** `eggie-admin/LuHm-OS`
**State:** source-only candidate. Does **not** activate a product benefit or change account settings.

## What is separate
- **ChatGPT personal plan:** the user-reported Plus plan must be checked in ChatGPT Settings; Plus is not API credit.
- **ChatGPT Work:** eligible individual plans can use Work on web/mobile when available on the account. Work and Codex share an allowance, but Codex is optional, and this task forbids its use. Check **Settings → Usage** for what remains; model availability and rollout vary.
- **Sign in with ChatGPT:** identity sign-in and sharing included allowance with a participating external tool are separate user authorizations. The eligible tool draws from the shared Work/Codex allowance, not API billing. Set a per-app weekly usage limit in Settings → Usage; never turn on optional credit sharing or automatic purchases implicitly.
- **OpenAI Platform API:** separate organization/project, billing, usage tier, model limits, and credits. Paid API execution is disabled here until an authenticated receipt and an explicit cost approval.
- **Developer community:** published learning/support resources are not a paid-plan upgrade or automatic API credit.
- **OpenAI for Startups:** certain VC-partner-backed startups may qualify for credits/support. No eligibility, referral, credit, or rate-limit benefit has been proven for this studio.
- **Verification:** identity/business verification is not an entitlement grant and must be requested only when OpenAI actually requires it.

## Chat session fast lane
1. Work mode is selected by the account holder, not by LuHm JSON or an MCP tool.
2. Reuse current GitHub source, chat context, and evidence references. Do not re-upload private media or full repo state per turn.
3. Use native Chat/Work tools only when available in the actual session, and never require Codex.
4. Never echo secrets or full private account identity in source, logs, bug reports, or tickets.
5. Preserve existing 15-role registry and company worker quarantine. In-chat character presentation is not live agent runtime.
6. Emit evidence state per product and per access path: public-policy / user-reported / provider-observed / host-invoked / unknown.
7. If Work is missing or exhausted, check the account mode selector and Settings → Usage; schema changes cannot refresh plan limits. Contact OpenAI Support for account-grant problems.

## Local audit

`python3 tools/openAiDeveloperEntitlementsAudit.py`

GREEN_STATIC_ONLY means the JSON safety constraints and eight negative controls passed. It is **not** proof of a Work-mode grant, API credits, or developer-program eligibility.

Official references:
- https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex
- https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
- https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform
- https://developers.openai.com/community
- https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites
- https://openai.com/startups

**CROWN STOP:** no branch merge, deployment, plugin install, entitlement change, API key, billing mutation, or publication by this candidate.
