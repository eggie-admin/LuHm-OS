# LuHm OS | Cloudflare air-traffic + Lum OpenAI orchestration field card

Canonical policy: `doctrine/cloudflareLumOrchestrationV1.json`  
Canonical source: `doctrine/currentSourceTruthV3.json`  
Source-only gate: `tools/cloudflareLumOrchestrationAudit.py`  
Current runtime authority: **no agent worker activation and no Cloudflare mutation**.

## Four independent planes

1. **Network and DNS:** Cloudflare is the authoritative-DNS candidate, optional edge proxy/CDN and optional private Tunnel. It never becomes an LLM, agent, provider credential manager or owner of source truth.
2. **Host and transport:** Existing Render Managed TLS serves the public MCP origin and Godot harness. Keep the present MCP route direct until an alternative path passes Streamable HTTP, SSE, hostname/certificate, and ChatGPT-host compatibility checks.
3. **AI and capability selection:** Lum is the sole manager. Python3 deterministic policy checks precede any SDK or external-provider action. Urd adjudicates; Skuld researches; Belldandy keeps only nonsecret receipt references; Kugi is the bounded executor when separately authorized. All fifteen agents remain **registered but quarantined**.
4. **Human governance:** GitHub holds versioned source and CI. Google Drive holds durable binaries. OpenAI provides semantic/model capability only when entitlement and scoped access are proven. Professor grants promotion.

## DNS identity sequence and checkpoints

`forwardFqdn → reverseFqdnNamespace → authoritativeNameservers → reverseDnsPtrWhenApplicable → proxyLane → canonicalRepository`

For `mcp.eggiebagelface.art`, the current custom hostname is a candidate, **not** observed DNS. The internal reverse namespace `art.eggiebagelface.mcp` is an identifier, **not** PTR or DNS. Verify registrar delegation and Cloudflare NS/SOA and DNSSEC if enabled; only inspect PTR when the project controls the relevant IP prefix. Prefer DNS-only CNAME to existing Render Managed TLS for this MCP lane; avoid guessing a shared Render IP. Preserve both existing live `onrender.com` services during any proposed hostname migration.

`system.eggiebagelface.art`: private portal candidate, optional outbound-only Tunnel, Zero Trust login/policy, verified origin certificate and bounded origin. No open SQL/phpMyAdmin, router forwarding, SSH shell or implicit public admin.

`assets.eggiebagelface.art`: optional public CDN **after** asset/public-rights approval. Never cache authenticated MCP or user-private data.

For an approved proxied service, require Full (strict) origin certificate validation and separately review the Tunnel-to-origin hop. `noTLSVerify` remains **false**.

## Model orchestration selection

`Task envelope → deterministic validation → capability classification → budget/security guard → read-only plan → receipt → Urd review → Professor decision`.

Default selection: deterministic local checks, existing exact receipts, then Google AI or OpenAI only if user intent, provider availability, task budget, privacy rules and tool authorization independently allow it. API/model/provider availability is **not** implied by source. No model may originate irreversible shell, DNS, app publication, payment, key handling or self-Crown actions.

OpenAI Agents SDK is a **future optional Python adapter**. Prefer a manager pattern with specialists exposed as tools only after quarantine clears. Validate each tool invocation at the application boundary, not solely with model input/output guardrails. Keep provider traces redacted or disabled until explicitly reviewed. Never collect private hidden reasoning or sensitive raw payloads as telemetry. Expose brief decision summaries and proof references rather than internal reasoning.

## Developer preflight

```bash
python3 tools/cloudflareLumOrchestrationAudit.py
python3 tools/cloudflareLumRoute.py --self-test
python3 tools/openAiAgentTopology.py --self-test
```

For a bounded task JSON, run `python3 tools/cloudflareLumRoute.py --task path/to/task.json`. This prints a **non-executing** routing decision; it does not contact Cloudflare, issue OpenAI tokens, modify DNS, create agents or publish assets.

## Actual release gates

A source GREEN means only the policy / route contract is coherent. Separate receipts are required for DNS + certificates, private identity policies, MCP streaming and host invocation, live provider entitlements, agent activation, public asset rights and any publication. Record actual GitHub SHA, Render deployment IDs and Urd review. Professor keeps Crown.

Upstream references:

- Cloudflare private networking: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/
- Cloudflare origin TLS: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- OpenAI tool guardrails: https://openai.github.io/openai-agents-python/guardrails/
