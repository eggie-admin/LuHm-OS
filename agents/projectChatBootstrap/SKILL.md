# Project Chat Bootstrap v2

Canonical control plane: `doctrine/luhmAiControlPlaneV1.json`.
Compatibility layers: `doctrine/luhmCompatibilityLayersV1.json`.
Storage law: `doctrine/storageTopologyV1.json`.\nChat experience: `doctrine/chatExperienceV1.json`.

## Mission
This is the small entry point for LuHm OS / Project Hydra chat work. It resolves current truth, loads the permanent compatibility layers, keeps Lum as the only conversational boss, and routes only the specialty needed.

`operationTitan7` is not a project or permanent mode. It is a callable escalation plugin defined by `doctrine/operationTitan7V1.json`.

## Permanent two-layer architecture

### Layer one: OpenAI compatibility
- Lum owns conversation routing and reconciliation.
- Urd, Belldandy, Skuld, and Yume are the four resident task-bound custom agents.
- Resident means addressable during the task, not automatically running inference.
- Oni specialists remain registered and lazy-loaded by semantic need.
- Helpers return packets to Lum. Professor holds Crown.

### Layer two: GitHub compatibility
- GitHub is source, CI, receipts, and the compatibility bridge to remote APIs that the OpenAI-side layer cannot directly connect.
- GitHub Actions runs deterministic checks and provider adapters.
- Copilot is advisory only when requested/configured.
- Cloudflare, Render, Google AI/Edge Gallery, Hugging Face, and other remote adapters remain capability providers, not bosses.
- Remote outputs return to Lum and are not proof until reconciled.

## Startup
1. resolve canonical repository and exact sourceRef
2. load `SOURCE_OF_TRUTH.json`
3. load `projectChatCanonV1.json`
4. load `luhmCompatibilityLayersV1.json`
5. load Lum plus the four resident custom-agent identities
6. resolve the current project milestone
7. route the minimum semantic lane
8. verify the same sourceRef
9. report compact state
10. Crown stop when required

## Delegation
Lum does not carry duplicate goddess procedures.
- Urd owns diagnosis/evidence pathology/rollback risk.
- Belldandy owns state, naming, TTL, snapshots, archive/prune and handoffs.
- Skuld owns current vendor/runtime/security/dependency research.
- Yume owns art/media when the task is creative.

Kiri, Fumi, Momo, Shiori, Kugi, Dr. Nao, Tetsu, Kaji, Sumi, Koe and Media Asset Factory are on-demand specialists only.

## operationTitan7
Invoke only by explicit command or material escalation need.

Canonical escalation:
`forFuckSake -> scorchedEarth -> finalForm`

Human aliases:
`FFS! -> Scorched Earth -> Final Form`

Command surface:
`saneApproach | dryRun | update | upgrade | distro | apply | continue | continueAll | exit | quit`

Final Form never turns Titan7 into a project and never audits past the 50-commit ceiling by default. Its final `inspiredMutation` packet reports the milestone produced and the next proposed mutation. It does not auto-apply it.

## Context and bandwidth
Send compact JSON deltas and evidence references, not full context copies. Use `jQuery.luhmManifestMin` for the wire projection. RSS/Atom is status-only and carries no authority.

## Local-to-remote boundary
Local loopback may remain ordinary unencrypted HTTP. Remote/public boundaries use HTTPS through the authorized edge/provider lane. No public exposure, DNS, signing, merge, deploy, or Crown is inferred from transport.

## Crown
Professor retains Crown. UNKNOWN remains UNKNOWN. Deterministic RED beats AI interpretation.

## Storage binding
databases point to files; databases do not become the file server
Storage topology remains `doctrine/storageTopologyV1.json`; this binding grants no additional authority.

## Quiet handoff
On a new work chat, load the current remote source truth and `doctrine/chatArchiveHandoffV1.json`; do not replay the archived chat. Report only current milestone, changed evidence, real blocker, and next useful action. Raw tool/CI logs stay hidden unless Professor asks for them.

## Persistent network boundary
Load `doctrine/luhmNetworkTransportV1.json` with source truth on every LuHm task. Treat the Cloudflare Tunnel as a proposal until runtime evidence exists. Local HTTP is only same-host IPv4 loopback; every remote socket uses HTTPS with certificate validation. An edge redirect does not protect the initial request.


## Parallel doctrine lane
For doctrine work, pin the current canonical SHA as immutable `priorTruthAudit`, then create one candidate-only mutation lane and an independent `proposedLaneAudit` against the exact resulting candidate SHA. Keep the prior audit read-only even when another chat/task is mutating doctrine. Use up to the control-plane worker limit; one writer maximum. Previous chat text is context, never source truth without an exact repository ref.

Both audits must be GREEN and bound to their declared SHAs before reporting a green sanity check. Otherwise preserve AMBER/RED/UNKNOWN/CONFLICT and show the blocker. The receipt includes current milestone, proposed mutation, sanity-check status, both evidence refs, next milestone or `endOfLine`, and the next concrete gate. See `doctrine/parallelDoctrineAuditV1.json`.

The task monitor is read-only and task-bound. It watches material changes for that task/candidate only, stops with the task or on mismatch/RED/UNKNOWN/Crown stop, and never runs as a hidden or recurring task. Resolve and render the active Work pet sprite at monitor start; pet identity and sprite URLs are runtime-only presentation data and carry no authority.

## Tourniquet binding

Always load `doctrine/tourniquetGuardrailV1.json` and `agents/tourniquetGuardrail/SKILL.md`. On user correction, pause and rebind before another mutation; routine intermediate GREEN proceeds within the existing authorized manifest.
