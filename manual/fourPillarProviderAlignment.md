# LuHm OS · Four-Pillar Provider Alignment

**Canon source policy candidate, not a live system installation.**  
**Before-state:** `f2e4be2224dd706d93d2dc660f536431a7d04f34`  
**Recovery:** [`snapshot/pre-four-pillar-canon-20261120-f2e4be22`](https://github.com/eggie-admin/LuHm-OS/tree/snapshot/pre-four-pillar-canon-20261120-f2e4be22)

This is a **human-friendly vendor assignment**, not four independent AI operators. **Lum** remains the boss/router and **the Professor** keeps final decisions. We preserve the existing capability-first Python API spine; calls only happen after permission, model, billing and receipt checks. There is no compulsory AI-to-AI hop.

| Character | Preferred home | What it actually means |
| --- | --- | --- |
| **Urd** | Google AI | Technical doctor for system diagnosis, security and compatibility; Google answers are advisory and Urd still independently checks evidence |
| **Skuld** | GitHub (Copilot optional) | Engineering and code research: repository context, PRs, compatibility, CI; GitHub is code and evidence, not an AI model |
| **Yume** | OpenAI image and creative capability | Original concept art, storyboards and writing; “DALL-E” is a legacy shortcut, actual model must be current and verified |
| **Lum** | Cloudflare edge, optional Workers AI / AI Gateway | Traffic coordination and possible lightweight inference; Cloudflare is **not** Lum herself and does not gain authority |

**Support staff and services:** Belldandy maintains Canon/evidence continuity. Hugging Face is a specialist model catalog. Render continues hosting the *existing* Python/MCP service. Edge Gallery and LiteRT-LM remain optional, physically unverified Samsung/local-inference components. Other plugins are convenient adapters, not new source authorities.

## Workflow rules

1. Identify the task and exact source before choosing a vendor.
2. Prefer deterministic local/GitHub evidence when sufficient.
3. Select a verified provider by needed capability, minimum scope and spend budget.
4. Send only the minimum relevant inputs; do not pass all chats between vendors.
5. Treat outputs as proposals; Urd cross-checks evidence when relevant, Skuld verifies code/source, Lum reconciles, Belldandy tracks the receipt.
6. No self-approval, automatic merge, signing, deployment, publication, agent activation or Crown.

## Explicit boundaries

- `doctrine/cloudflareAirTrafficControllerV1.json` currently declares Cloudflare to be the **network** controller, *not* an active AI provider. Optional Workers AI or AI Gateway is a **future, separate runtime candidate**, not a replacement for the existing Render MCP address.
- `doctrine/googleAiProxyDeploymentV1.json` presently blocks Google developer API calls pending authenticated entitlement/billing proof. Google consumer subscription does not prove developer API access.
- OpenAI creative-image execution is *not* asserted merely because ChatGPT can converse or generate images in a different surface.
- GitHub remains the canonical source authority. Copilot can advise; its execution is not assumed.
- `doctrine/companyWideOperationalQuarantineV1.json` remains `QUARANTINED`. This source-only mapping does not release the 15 roles.
- `doctrine/currentCanonSnapshot20261022.json` is preserved as a dated historical snapshot and not rewritten to suggest current runtime proofs.
- The separate Edge Gallery/LiteRT draft remains independently reviewable at [PR #593](https://github.com/eggie-admin/LuHm-OS/pull/593).

**Runtime status:** `UNVERIFIED`. **Source status:** reviewed/CI-tested only if exact-head checks are actually observed. **Crown:** `STOP`.

Machine-readable contract: [`doctrine/fourPillarProviderAlignmentV1.json`](https://github.com/eggie-admin/LuHm-OS/blob/main/doctrine/fourPillarProviderAlignmentV1.json) when merged.
