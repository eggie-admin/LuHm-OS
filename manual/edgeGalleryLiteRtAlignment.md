# AI Edge Gallery / LiteRT-LM alignment proposal

**Status:** PROPOSED / NOT DEPLOYED  
**Checked:** 2026-11-20  
**Authority:** The Professor. AI proposes; policy authorizes; CI proves; human promotes.  
**Canonical repository:** `eggie-admin/LuHm-OS` (the former Hydra Android repository is historical/migration evidence, not current runtime authority).

## Stop the AI-to-AI chain

One task should not blindly bounce between OpenAI, Hugging Face, Google and GitHub. These are distinct roles:

| Role | Component | Contract |
| --- | --- | --- |
| Mobile user-facing local AI | Google AI Edge Gallery | Android Agent Chat client; no provider keys or shell authority |
| On-device model runtime | Google LiteRT-LM | Executes a compatible local LLM; it is **not** an API gateway |
| Model catalog/artifact source | Hugging Face | Supplies eligible, pinned and licensed `.litertlm` models; remote inference is a different optional adapter |
| Tool integration | MCP Streamable HTTP | Allows the mobile agent to discover **bounded** server-side tools |
| Policy and routing | Existing Python LuHm MCP + API spine | Enforces source scope, read-only vs write, budgets, receipts and execution boundaries |
| Source and proof | GitHub | Canonical code, review, CI and evidence; Copilot is a coding assistant, not a runtime connection requirement |
| Optional remote reasoning | OpenAI / Google AI / Hugging Face inference | Separate server-side adapters, never automatic uncontrolled delegation |

```text
[Android: Google AI Edge Gallery]
  [Gemma / local LLM via LiteRT-LM]
             |
       MCP Streamable HTTP
             |       (read-only first)
             v
[Existing Python LuHm MCP harness, Render HTTPS]
             |
    [LuHm capability-first API spine]
      |           |             |
   GitHub      OpenAI        Hugging Face
 source/CI     optional       model catalog/
               reasoning      remote optional

Hugging Face -- compatible .litertlm weights --> Edge Gallery local runtime
Google AI Edge Gallery != Google/Gemini Cloud API
```

## Reuse before building

- Existing server: `host/mcp/luhmMcpServer.py`
- Existing harness entrypoint: `host/mcp/luhmHarnessServer.py`
- Existing plugin MCP configuration: `plugins/luhm-os/mcp.json`
- Configured **candidate** read-only endpoint: `https://luhm-os-harness-green.onrender.com/mcp`
- Existing provider spine: `doctrine/apiSpineV1.json`
- Existing device authority contract: `doctrine/samsungAntennaV1.json`
- Existing MCP scope security: `doctrine/MCP_ENTERPRISE_SCOPE_V1.json`

The above are *source-configured*, not proof of a live endpoint or tested Samsung handset. The current source contract describes anonymous **read-only** public tools and records that private/write OAuth is **not implemented**. Do not add a privileged GitHub token to Edge Gallery, browser JavaScript, APK assets, logs, or a public repository.

## Phase A: verify the phone antenna (read-only)

1. Verify that the deployed harness responds correctly over HTTPS and that MCP discovery succeeds. A normal web GET alone does not prove MCP handshake/tool calls.
2. On the Android device, open **Google AI Edge Gallery -> Agent Chat -> MCP -> Add MCP Server**.
3. Enter `https://luhm-os-harness-green.onrender.com/mcp` **only after host and access checks pass**. Do not add a GitHub or Hugging Face token.
4. Prefer an appropriately supported Gemma model for MCP tool calling. Enable only 1-2 narrow tools at first to keep on-device prompt/context overhead manageable.
5. Ask: `Use the LuHm read-only MCP tools to report the current project status and tool list. Do not execute changes.`
6. Capture device version, app version, exact model ID and model artifact hash/revision, MCP URL, tool names, consent prompt, observed result/error and timestamp. This is an **evidence receipt**, not automatic GREEN.

## Phase B: model supply (Hugging Face + LiteRT-LM)

1. Choose a model explicitly marked compatible with LiteRT-LM / Google AI Edge Gallery.
2. Review license, provenance, revision, hardware compatibility and free/storage budget before download.
3. Import the compatible model into Gallery and test offline local text generation.
4. If no usable preconverted model exists, do the conversion/quantization in a **separate Python-capable development environment**, following the official LiteRT export instructions; do not require the Gallery app itself to run Python.
5. Record the result. Hugging Face remote inference credentials remain server-side when that optional adapter is used.

## Phase C: controlled service alignment

- Route external requests by **capability first**, not by repeating the user's entire prompt across AI providers.
- Keep the existing `apiSpineV1.json` and its typed receipt schema as the coordination contract.
- GitHub remains the single source of code/build truth; Google AI/Edge Gallery is a client/runtime, **not** a second GitHub master repository.
- Use GitHub/Copilot for reviewed proposals and GitHub Actions for tests. No model can silently merge, sign, deploy or publish.
- Add privileged GitHub write tools only after audited authorization and the repository's explicit scoped authority gates. The currently documented public LuHm MCP server is not permissioned for write operations.

## Acceptance gates (do not claim until independently demonstrated)

- [ ] Render service live and MCP Streamable HTTP handshake succeeds
- [ ] Actual Samsung Edge Gallery connection with discovered read-only tool
- [ ] One bounded, consented tool call with captured result
- [ ] Compatible LiteRT-LM model loaded and locally inferred successfully
- [ ] Model provenance, license and pin recorded
- [ ] No provider credentials leaked to mobile assets, Git, logs or debug output
- [ ] GitHub/CI evidence linked to specific source revision
- [ ] Human approval for any later elevated authority

## Official references

- Google AI Edge Gallery MCP: https://github.com/google-ai-edge/gallery/blob/main/mcp/README.md
- Google LiteRT: https://developers.google.com/edge/litert
- Google LiteRT-LM: https://developers.google.com/edge/litert-lm/overview
- Hugging Face LiteRT integration: https://huggingface.co/docs/transformers/community_integrations/litert
- Official Gallery repository: https://github.com/google-ai-edge/gallery

**This proposal changes documentation only. It does not deploy infrastructure, configure Android, grant tokens, authorize device actions, or alter the operational source of truth.**
