# Crown Cathedral | 4x4 → 8x8 → 16x16 escalation (2026-10-30)

**Scope:** exact-source escalation on a fork-and-security candidate. This audit **does not** test Android hardware, deploy Cloudflare/Render, run an interactive Blender/Godot session, sign binaries or clear vendor licenses.

## 4×4: sixteen hard source assertions
Cross four domains (identity, vendor, security, release) with four rules (source, lock, boundary, proof). All 16 must validate checked-in policy and artifact declarations. Source assertions that the release is NOT green are valid source checks; they are not release approval.

## 8×8: sixty-four cross-component observations
Eight components: HTML frontend, npm shell, isolated glass-world renderer, MCP host, typed SQLite, Godot, Android WebView and release contract. Eight contracts: existence, source bound, manifest, dependency pin, license review, sandbox, runtime and rollback. The script observes source paths and exact manifests. A test not backed by independent evidence is explicitly `UNVERIFIED`.

## 16×16: two hundred fifty-six integration evidence slots
Sixteen targets (source, governance, vendor, web, glassWorld, MCP, SQLite, Godot, Blender, FFmpeg, APK, update, F-Droid, ChatGPT, Cloudflare and Render) × sixteen controls (source anchor, digest, license, provenance, dependency, syntax, negative tests, input sandbox, secrets, network, build artifact, runtime acceptance, exercised rollback, signer custody, distribution acceptance, Crown).

A file digest is only source-integrity evidence. A checked-in JSON file is not a real deployed service or signed installer. Thus `UNVERIFIED` is a valid **assessed** slot and `BLOCKED` is the only valid public Crown status until independent external acceptance.

## Exact-head execution

```bash
python3 -m unittest tests.testCrownEscalationMatrix -v
python3 tools/crownEscalationMatrix.py --source-ref "$(git rev-parse HEAD)" --output /tmp/crown-escalation.json
```

The existing GitHub Source Governance Audit workflow runs these commands and checks the 16 + 64 + 256 cardinality, accurate blocking, and source status at the precise PR SHA. No workflow duplication.

**Live external observations**, tracked separately in PR #462: GitHub source CI passing; Cloudflare Workers external check failing; current Render deployment lagging GitHub main. The matrix cannot certify or repair those services through a source-only workflow. Repair must follow actual logs, separate IAM/entitlement, narrow source/config mutation, exact rebuild, rollback, and reviewer approval.

## Escalation policy
4×4 failure → restrict to offending domain. 4×4 pass → assess 8×8 per component. Missing source component → RED, no promotion. 8×8 unresolved interface → 16×16 evidence slots for exact targets; do not multiply identical tests. 16×16 runtime gaps → request independent host/device evidence instead of automatically deploying or rewriting code. Vendor forks are only created after each upstream license/provenance and maintenance review.

**No auto-merge. No secret retrieval. No remote deployment. No self-awarded GREEN Crown.**
