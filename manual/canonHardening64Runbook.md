# LuHm-OS Canon hardening 0x00–0x3F

**Status:** draft source-only 64-cell independent hardening. Main and historical receipts are never changed by this source gate.

## Geometry and scope

Four domains (`governance`, `security`, `integration`, `delivery`) × four document lanes per domain × four audit beats (`inventory`, `scope`, `verify`, `propose`) = **64 individual source-value checks**, hexadecimal `0x00..0x3f`. They are logical labels, **not hardware operations** or 64 live deployment tests. Each check pins a named JSON selector in an approved canonical file. 16 documents receive SHA-256 digests in the receipt.

Run the additional existing 200-pass hard system audit, 16-cell machine 4×4, escalation policy, source API spine, company quarantine, and storage law checks at the same PR-head SHA. A fresh 64/64 plus 200/200 plus machine 16/16 is still **AMBER for real-world external proof**. Tests cannot prove live Google AI IAM, Cloudflare DNS and Workers, Render deployment, Android install, operating-system kernel boot, app signing, or art rights.

## Sanest escalation

All 16 document lanes start at tier 0. On an actual source check failure, escalate only that lane to tier 1 for focused diagnosis, then tier 2 for specialist repair and tier 3 for explicit human HOLD after three consecutive same-SHA failures. No retry expands authority. Each tick re-evaluates all 64 checks; stale receipts cannot certify a new source. A changed commit or document fingerprint resets prior retry history. Passing checks de-escalate one tier. Unknown live evidence stays AMBER, never silently GREEN.

The source gate is intentionally non-destructive and does not activate workers or use external AI. The broader `sanityCheck → audit → ingest → mutation → test → apply → continue → deploy` Covenant continues to govern consequential actions. A proposed-source `deploy` stage does not mean production deployment.

## Independent reconciliation boundaries

- Existing PR #512: HEX-64 Insanus 2,048-scenario source model (separate candidate), not 2,048 real devices or runtime tests.
- Existing PR #520: OpenAI 200-pass/automatic audit candidate, with a CI failure awaiting diagnosis.
- Existing PR #522: Google AI sixteen-cell source readiness candidate, with runtime API entitlement unverified.
- Existing PRs #516–#519 and #521: distinct SQL, naming, network, art, device candidates. Do **not** cherry-pick or merge blindly.
- Cloudflare Workers build failures seen on main and several PRs are a separate production/builder integration issue, not cleared by source checks.

## Execution

```bash
export LUHM_SOURCE_REF="$(git rev-parse HEAD)"
python3 -m unittest discover -s tests -p testCanonHardening64Audit.py -v
python3 tools/canonHardening64Audit.py --source-ref "$LUHM_SOURCE_REF" --output /tmp/canon-hardening-64.json
python3 tools/hardSystemAudit200.py
python3 tools/machineCanonFourLoop.py --source-ref "$LUHM_SOURCE_REF"
```

GitHub Actions performs exact-head execution with `contents: read`, no `id-token`, no cloud secrets, and no automatic deploy. External test receipts remain scoped to each independently verified environment.

**CROWN STOP**: no main merge, user-data mutation, production SQL migration, provider charges, Cloudflare changes, live signing, publication, or agent release.
