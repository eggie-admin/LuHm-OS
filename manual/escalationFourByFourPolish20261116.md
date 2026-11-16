# LuHm-OS 4×4 Escalation · Polished proposed lane

This proposal refines **the existing** source-bound 0–3 escalation grammar. It does **not** replace the unrelated 1–4 operating/presentation layers, activate 16 workers, or override the Everlasting Covenant.

| Depth | Hear | Resolve | Act | Verify |
|---|---|---|---|---|
| 0 · FAST PATH | Current request | Minimal task/source/scope | Bounded authorized fix | Same-gate proof or named blocker |
| 1 · FFS! | Failing test/receipt | Narrow root cause | Reversible repair | Rerun the failing test |
| 2 · SCORCHED EARTH | Contradictory evidence | Cross-layer diagnosis | Rollback-safe patch | Cross-layer regression |
| 3 · FINAL FORM | Exact final target | Authority + rollback | Only approved candidate action | Independent runtime/device/release gate |

**Four beats** are `hear → resolve → act → verify`. The transition is decided **only** at Verify: GREEN with a receipt closes or de-escalates; BLOCKED requires a named, evidenced blocker and rises at most one tier; RED stops; UNKNOWN/CONFLICT hold; WORKING repeats the tier. A source or scope change invalidates the previous handoff. Each turn yields one concrete next action.

**Proof class matters.** The helper `tools/escalationFourByFourPolish.py` accepts reported receipt references but does not authenticate the references or claim the work occurred. A successful decision is not device proof, beta signing, F-Droid index signing, Play Store trust, or authorized publication.

For the Nov 16 private Android beta, the known good proof is the debug-signed ARM64 GitHub artifact from run `43899856693`. PR #572 is a separate scoped owner-signing-source candidate; it is not an installed trusted signer or an automatic high-fidelity asset importer. The EVE, Destiny Child, Resident Evil and Fallout references remain off the public repository and must be lawfully validated and locally import-tested before packaging.

Example CLI input (save as `/tmp/escalation-measure.json`):

```json
{
  "taskId": "privateBetaPolish",
  "sourceRef": "5dede4ce5a38722bd089c4d0b36ad7b067354096",
  "scopeId": "samsungBeta",
  "domain": "technology",
  "tier": 0,
  "beat": "verify",
  "outcome": "blocked",
  "evidenceRefs": ["GitHub:PR572"],
  "blocker": "owner-signed beta environment not independently attested"
}
```

```bash
python3 tools/escalationFourByFourPolish.py --measure /tmp/escalation-measure.json
python3 -m unittest tests.testEscalationFourByFourPolish -v
python3 tools/escalationKernelAudit.py
```

**Crown: STOP.** No automatic sign, merge, deploy, publication, model-agent release or firmware changes.
