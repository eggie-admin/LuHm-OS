# LuHm-OS machine CAST quick start (proposed)

## Goal
The Professor requests features in chat. GitHub source remains authoritative. Run reproducible testing (Build A) and proposed (Build B) checks automatically. Preserve exact-source evidence and require separate authorization for release.

## Start here
1. Read `AGENTS.md`, `doctrine/currentSourceTruthV3.json`, `doctrine/proposedWorkingLaneV1.json`, and `doctrine/storageTopologyV1.json`; capture current main SHA.
2. Reconcile PRs #482 (nightly), #485 (HTML machine 4x4), #486 (SQLite byte receipts), and #487 (thin-client contract), validating every branch against fresh main before proposing merge. Do not blindly merge.
3. Audit `plugins/luhm-os` and `plugins/luhm-android-beta`: configuration schema, localhost/remote endpoints, permissions, installation instructions, and MCP integration test. Never infer running server from manifest presence.
4. Run `npm ci --ignore-scripts` then `npm run stage:jquery` and `npm run check` from `frontEnd`. Avoid new vendor dependencies unless evidence proves need.
5. Test the HTML -> API request/response route and deny unapproved API capabilities. Prefer same-origin HTTPS when remotely deployed, and only add NGINX when it solves a verified deployment requirement.
6. Verify SQL milestone sorting and artifact pointer/digest checks. Store references and SHA-256, never binaries in SQLite. Preserve canonical schema and task/source/scope identity.
7. Run the machine layer 4x4: source boot/runtime assumptions; HTML smoke; API fail-closed responses; exact-source build/update receipts. Evidence is GREEN only for tests on the named commit.
8. Prepare Build A testing/debug artifact and Build B proposed candidate with distinct version identities and reproducible receipts; no promotion implied.
9. Request owner action only for real-device tests, signing credentials, protected merge, CAST promotion, Play Console access, and public release.
10. After approval, independently verify artifact signature, installation, update without save loss, rollback, and release status. Return to chat-only feature requests.

## Two-build state machine
For lane in [testing, proposed], iterate its required milestones:
- GREEN: all mandatory exact-source checks passed.
- AMBER: unknown/unverified.
- RED: verification failed.
- BLOCKED: external prerequisite.
On new sourceRef, restart; GREEN never authorizes deployment.
CAST is the owner-controlled bridge from tested candidate to the approved distribution stage.

## Human handoff: only when truly needed
- Real device: install candidate and provide actual launch/update proof.
- Signing/Play: configure owner-held keys and developer account using official interfaces.
- Protected merge and deployment: explicitly approve exact source SHA and target.
- Creative: select features, content, and product direction.

## Current limitations
This is a proposed quick start, not a claim of a live installed bot, completed backend, working Play release, or authorized merge. Existing agent quarantine and publication gates remain unchanged.
