# Lum + Goddess GitHub-gated deployment

**Existing Render services only.** GitHub main remains canonical source; Render remains a preview/runtime sidecar. Its native `autoDeployTrigger` stays `off` on both existing services. This is a separate GitHub Actions runner that deploys only after its **exact merged commit** passes source and quarantine tests.

## Activate once

Add `RENDER_API_KEY` as an encrypted **GitHub Actions repository secret** in `eggie-admin/LuHm-OS`. It must be a Render API key authorized for the existing workspace, not an API key pasted in a chat. This tool cannot configure GitHub secrets for you. No other Google AI key is requested or allowed in this workflow.

After the key exists, a relevant merge to `main` automatically runs source CI and triggers **the two existing free Render web services**, pinned to `github.sha`. The run polls and records provider commit/status evidence. Missing key produces **AMBER, no deploy**, rather than an imaginary green. A manual workflow dispatch additionally requires `cast` and exact full main SHA.

Do not enable native Render auto-deploy concurrently. It would allow bypassing GitHub's guarded gate. Leave `render.yaml` as-is. Static publication branch and public art publication remain separate manual approvals.

## Google AI proxy

The proposed Big Brother/Google AI proxy is **not billable or active**. MCP exposes only `luhm_google_ai_proxy_status` to show the blocked readiness state. No Gemini Developer API/Vertex token is embedded in source, no secret is read by that tool, and no Google requests occur. See `doctrine/googleAiProxyDeploymentV1.json`.

## Lum and Goddesses

Lum is the single conversational coordinator; Urd reviews evidence, Belldandy records continuity, Skuld researches, Yume directs art. All 15 worker routes stay quarantined until the separate audited human authorization process. Publishing a new MCP build means **deploying their supervised source contracts**, not starting independent background agent workers.

## Evidence

- GitHub workflow green == exact-head source tests passed.
- Render `LIVE_EXACT_SHA` == provider returned live status and the exact source SHA.
- Google AI status == fail-closed, no provider calls.
- End-user ChatGPT iframe/3D or native Samsung installation == must be tested separately.

No new service, DNS, billing, private art, signing or app permission is changed by this workflow.
