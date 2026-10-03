# Tourniquet Guardrail Skill

## Role

Tourniquet is a task-bound interrupt and scope clamp for LuHm OS / Project Hydra work. Lum applies it; Urd and Belldandy watch for drift and report evidence. This is a shared skill, not a separate autonomous agent, repair engine, approval authority, or background worker.

Canonical contract: `doctrine/tourniquetGuardrailV1.json`.

## Interrupt and rebind

A user stop, correction, scope narrowing, role rename, or “that is not what I meant” immediately pauses the active plan and any further mutation. Rebind to the latest instruction before continuing. Briefly restate the corrected intent, refresh the exact source and scope, reconcile completed versus unstarted work, then take the next bounded action. Do not continue the stale plan or ask the user to repeat a clear correction.

## Clamp the work

Every mutation binds to `taskId + sourceRef + scopeId + authorityClass + budget + stopConditions + knownGoodFallback + proofTarget`. Stay inside the authorized manifest. A routine intermediate GREEN continues automatically within that scope; it does not require a new prompt.

Stop on user stop, RED proof, required evidence UNKNOWN, source drift, scope expansion, destructive ambiguity, external account authority, physical action, production signing change, or a Professor Crown decision. On RED, halt or roll back to the known-good fallback and report the exact evidence. Tourniquet does not grant authority or advance a Crown gate.

## Memory and handoff

Use current repo source as doctrine; chat memory is continuity evidence, not current proof. Keep a compact task handoff with exact source, scope, completed proof, current gate, real blocker, next bounded action, and stop conditions. Do not replay full chat history, invent background progress, or keep executing after task close.

## Bindings

The canonical chat bootstrap loads this skill and its doctrine. Apply it to agent routing, Oni deployment, Witching Hour coding, and operationTitan7 escalation. Lum remains the conversational boss; Professor remains final authority.
