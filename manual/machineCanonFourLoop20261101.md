# Machine Canon: bounded four-loop escalation

**Draft source-only implementation**, integrated with the existing machine PR #487 and
`tools/unifiedMachineBaseAudit.py`. This does not activate a new autonomous agent,
cron job, production service, kernel, disk action, build or public release.

## The literal for-loop / continue rule

```python
for lane in (machine, service, studio, interface):
    if same_source_retries_for_lane >= 3:
        record(BLOCKED, "prepare an exact-source bounded repair")
        continue                         # Another lane may still be checked.
    for beat in (inventory, scope, verify, propose):
        if current_source != pinned_source:
            stop_tick("source changed")
        result = run_exact_allowlisted_read_only_check(lane, beat)
        if result is not PASS:
            record_unchecked_remaining_beats(lane)
            escalate_one_tier_only_if_blocked()
            break                        # Never check off failed beat or successors.
    else:
        tick_off_four_source_only_checks()
        deescalate_one_tier_if_needed()
    continue
```

A **tick** is one finite pass of 16 *logical* `0x00..0x0f` slots. These are
**not hardware addresses or BIOS registers**. All passes begin at technology
Tier 0; Tier 1 coordinates a bounded diagnosis, Tier 2 calls for specialist
review/fallback, and Tier 3 is closure/hold rather than permission to bypass
the release gates. Tier increases only following a real blocked check.
An UNKNOWN receipt holds without claiming success.

The `sanityCheck → audit → ingest → mutation → test → apply → continue → deploy`
Canonical guardRail still applies to consequential operations. In this tool
`propose` is a source-only check, **not** permission to deploy. The four
beats are audit organization and not a replacement for the eight-stage law.

## Checklist: four lanes × four beats

| Lane | 0 inventory | 1 scope | 2 verify | 3 propose |
|---|---|---|---|---|
| machine | read-only machine wizard | minimal headless contract | overall architecture + negative tests | escalation kernel |
| service | network and proxy boundaries | Certbot path metadata only | PKI/secret policy | storage law |
| studio | headless Codespaces contract | Linux studio profile | Python/JS desktop safety | machine-base regression tests |
| interface | local HTML/JS audit | Pi desktop profile | Android WebView boundary | thin Android client profile |

Each beat runs **only literal pre-registered local commands** in
`tools/machineCanonFourLoop.py`. No user-provided command, network model
prompt, shell interpolation, sudo, package install or privileged mutation.
Outputs are hashed; raw CLI output is not stored in the receipt. A failed
beat stops only its own lane; other independent lanes continue.

**Check marks mean SOURCE AUDIT PASS ONLY.** They do not mean physical Pi
kiosk boot, userland service active, disk or firmware integration, model
execution, Android install, live database migration, browser interaction,
signing, Google Play distribution or CAST.

## Exact-source entry point

On a clean committed checkout (CI uses the exact PR head):

```bash
python3 -m unittest discover -s tests -p testMachineCanonFourLoop.py -v
SHA=$(git rev-parse HEAD)
python3 tools/machineCanonFourLoop.py --source-ref "$SHA" \
  --output /tmp/luhm-machine-canon-receipt.json
```

To recheck **one previously failing same-SHA tick** without losing the bounded
retry count, pass the previous `--state` receipt and choose `--output`.
This is explicit, not an unbounded local `while true` loop. A new exact
SHA or changed Canon fingerprint resets retry counts and forces fresh tests.
Prior GREEN receipts are *never* reused as proof. CI each new PR commit
checks fresh; recurring scheduling must persist retry receipts separately
if desired. A held lane after three failures needs a reviewed repair on a
new SHA, not a blind retry.

The existing `.github/workflows/premonition-machine-wizard-audit.yml`
runs deterministic regression tests and the four-lane source tick on its
exact head, uploads a 14-day receipt, and preserves all prior machine checks.
Keep protected main and overlapping CAST PR #490 distinct; combine by
reviewed exact-source reconciliation, not automatic cherry-picks/merges.

## Authority and escalation

Professor approves **source-scope 4×4 escalation and reversible draft
proposals**. This does not authorize live package installation, GParted,
firmware writes, production SQL/Apache migration, Certbot issuance,
agent unquarantine, Android release signing, branch protection bypass,
public deployment or final CAST. When a boundary needs the Professor,
record the smallest actionable blocker and stop that lane.

Source truth: `doctrine/currentSourceTruthV3.json`,
`doctrine/projectChatCanonV1.json`,
`doctrine/everlastingCovenantV1.json`,
`doctrine/escalationKernelV1.json`,
`doctrine/unifiedMachineBaseV1.json` and the existing machine wizard.
