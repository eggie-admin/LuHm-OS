# CAST Bridge bounded continuation

Run `python3 tools/castBridgeLoop.py` on a clean committed checkout.
The four independent source ladders are machine, humanMachine, humanHuman and
automatedStudio. Each uses the existing technology escalation kernel tiers 0..3.
These axes do not replace Canon or create four new release systems.

Each tick rechecks Canon JSON, records its SHA-256 digests and runs existing audits.
A failed check increments the ladder retry count, escalates diagnosis and continues
to the next independent ladder. Three failures on the same source exhaust the
budget; subsequent ticks hold that ladder until a bounded repair creates a new
commit. A source change resets verification; prior GREEN is always retested.
There is no sleep loop, shell command supplied by user input, automatic patching,
merge, signing or release action. The scheduler/reviewer must persist the state
JSON between ticks; fresh CI runs start a fresh budget and do not count as a
persistent unattended repair worker.

The existing escalation-kernel workflow runs the controller and preserves evidence;
no additional nightly workflow is introduced. PRs #482 and #485 remain separate
proposals and should be reconciled before enabling their overlapping schedules.

Testing source GREEN only qualifies source checks. Build A must additionally
produce a tested artifact. Build B must be reproducible and satisfy owner signing,
Samsung launch/save/resume/upgrade and approved Play internal-track evidence.
The loop deliberately cannot accept a boolean CAST flag as release authority.
A supervised exact-candidate CAST operation remains separate. Google Play install
is incomplete until an actual tester installation and runtime receipt exists.

Automation may prepare bounded draft repairs with tests on the active candidate.
Notify only on a material verified milestone or a new necessary owner action.
When CAST is requested, pause preparation and verify exact candidate and destination;
never convert missing credentials, device proof or Play account setup into GREEN.
