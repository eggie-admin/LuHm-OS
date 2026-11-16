---
name: luhm-openai-chat-bridge
description: Plan and inspect LuHm OS OpenAI Responses API tasks through Lum's canonical spine without activating paid calls, secrets, or quarantined workers.
---

# LuHm OpenAI Chat Bridge

Use this skill for the Professor's requests to develop, inspect, or prepare ChatGPT/OpenAI API automation in the LuHm studio. Prefer the existing LuHm OS MCP app and source, not a duplicate Site plugin.

## Safe current workflow

1. Resolve exact Git source SHA, `doctrine/currentSourceTruthV3.json`, `doctrine/apiSpineV1.json`, `doctrine/openAiDeploymentV3.json`, and `doctrine/companyWideOperationalQuarantineV1.json`.
2. Use `luhm_openai_bridge_status` to inspect the host-only gate, or `luhm_openai_bridge_plan` with explicit `taskId`, 40-character exact `sourceRef`, `scopeId`, allowed `capabilityId`, and small prompt.
3. Report BLOCKED and its concrete conditions. Planning makes **zero model/network calls** and incurs **zero OpenAI API usage**.
4. Keep Lum as the single conversational coordinator. A plan is not worker execution, GREEN, beta, publication or Crown.
5. For actual API calls, the separate host-only `execute_request` function must pass a released company quarantine, an explicitly enabled live flag, explicit API billing approval, an approved server-held key and selected available model. There is **no** live MCP tool in this candidate.
6. Never paste or solicit raw API keys in chat, GitHub, APK, browser code, CI logs or public files. ChatGPT subscriptions and OpenAI API billing are separate.
7. Do not auto-merge, deploy, spend, activate workers, or publish. Leave code as reviewable candidate with deterministic tests and source SHA receipts.

## Safe test prompts

- "What is the LuHm OpenAI bridge status, without an API call?"
- "Plan a read-only semanticSynthesis task for this exact SHA, without making a paid call."
- "Explain which gate is blocking live model execution and give the minimum next owner action."

This portable skill informs ChatGPT behavior. The GitHub MCP code must be separately reviewed, deployed, discovered and invoked before claiming an in-chat tool is live.
