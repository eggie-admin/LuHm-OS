# LuHm Shared Escalation Kernel v1

Canonical contract: `doctrine/escalationKernelV1.json`.

This is a shared reasoning contract, not a new agent stack.

## Universal rhythm

Every supported domain uses the same zero-based escalation grammar:

`0 default -> 1 coordinated -> 2 specialist -> 3 closure`

Tier changes operational maturity, staffing, evidence depth, and closure discipline. It does **not** increase project authority.

## Mandatory state

Before escalating a truth-sensitive task, preserve:

`taskId + sourceRef + scopeId + domain + tier + evidenceRefs + blocker + authorityBoundary`

A source or scope change invalidates prior proof for the changed scope.

## Escalation logic

- Start at tier 0 unless exact evidence already proves a higher tier is necessary.
- Use the smallest staff set capable of closing the current tier.
- Reuse current receipts before making provider calls.
- Escalate only when the current tier cannot responsibly close the blocker.
- `UNKNOWN` and `CONFLICT` remain explicit; do not promote through them.
- A deterministic RED blocks promotion, but may justify escalation for deeper diagnosis.
- Tier 3 is domain closure, not automatic GREEN.
- Consequential promotion still stops at Professor Crown.
- After closure, park unnecessary helpers and return to the lowest useful operating tier.

## Domain profiles

- `default` -> `doctrine/founderEscalationLadderV1.json`
- `corporate` -> `doctrine/corporateEscalationProfileV1.json`
- `magic` -> `doctrine/magicEscalationProfileV1.json`
- `art` -> `doctrine/yumeCreativeEscalationV1.json`
- `technology` -> `doctrine/operationTitan7ChatTriggerV2.json`

Titan is the technology hard-audit implementation. Yume owns creative escalation. Magic is presentation plus ritual sequencing. Corporate escalation is organizational maturity. The default profile is the Professor garage-to-closure path.

## Agent behavior

Lum resolves the active domain and chairs escalation after the Professor garage tier.

Urd diagnoses health, evidence, security, contradiction, rollback and sanity. Urd may recommend escalation but may not promote or deploy.

Belldandy preserves tier/state continuity, names, receipts, handoffs and the reason an escalation occurred.

Skuld owns deep technical/research compatibility questions when the active profile requires specialist technology work.

Yume owns creative fitness and art-direction decisions in the art profile.

Support workers remain bounded by `doctrine/staffIntentTeamsV1.json`. Team membership never changes authority.

## FAST_PATH

FAST_PATH means machine-resolvable gates continue without asking Professor to babysit them.

FAST_PATH stops at:
- real user action
- missing authority
- missing external receipt
- unresolved RED/UNKNOWN/CONFLICT that automation cannot close
- physical-device proof
- Professor Crown

No repeated evidence request is allowed while a valid current receipt already proves the same source and scope.


## Urd + Belldandy tier-transition sync

Canonical contract: `doctrine/fourTierEscalationSyncV1.json`.

Every 0-3 tier transition keeps one shared `taskId + sourceRef + scopeId` identity. Urd supplies evidence-health, risk, proof-boundary, and stay/escalate/de-escalate/close/hold recommendation. Belldandy supplies previous-tier receipt, continuity state, decision record, and smallest next action.

This is a task-bound synchronization contract, not hidden background execution and not a new agent stack. The pair does not vote project state into GREEN and cannot grant Crown. If their packets conflict, identity mismatches, or deterministic RED exists, hold the current tier and return the conflict to Lum. Professor remains final authority.
