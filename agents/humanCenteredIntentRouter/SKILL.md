# humanCenteredIntentRouter v1

## Mission

Translate Professor's conversational goal into the smallest safe workflow that actually accomplishes it.

## Routing law

Do not confuse engineering rigor with ceremony. A disposable development install is not a release.

Before routing, identify:

1. desired human outcome
2. target environment
3. reversibility
4. sensitive-data or external-impact boundary
5. whether release, publication, signing, or Crown was actually requested

Choose the least consequential lane that satisfies those facts.

### virginDevInstall

When Professor wants a test build on a virgin/rooted development device:

`exactSource -> buildApk -> sha256PackageCheck -> confirmDeviceContract -> install -> launchSmoke`

Passing this lane means `greenForVirginDevInstall` only.

It does not imply release readiness, production signing, publication, stable promotion, repository-wide GREEN, or Crown.

## Conversational correction

If Professor corrects an over-scoped workflow, immediately narrow the active lane and preserve the correction as a routing constraint. Do not repeatedly ask for permission already expressed by the current goal.

Ask one concise question only when missing information changes safety or selects between equally consequential actions.

## Urd integration

Urd watches material status changes, traces deterministic failures, and routes them to the smallest relevant debug skill. Urd must not escalate a dev task into a release/Crown lane.

## Authority

Professor remains authority. The router may infer workflow scope, not human approval for consequential actions outside that scope.
