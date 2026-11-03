# LuHm-OS firmware-to-AI vendor automation hardening ladder
Status: PROPOSED_ONLY. Crown STOP. No firmware flashing, privilege escalation, production merge, signing or deployment.
Source law: AI proposes. Policy authorizes. CI proves. Human promotes.

## 0: exact source and inventory
Pin main and draft SHA. Enumerate supported Samsung Android and Linux hardware by actual device receipts, not inferred chipsets. Capture CPU architecture, ABI, kernel, firmware version, verified-boot status where exposed, drivers, memory budgets, GPU capabilities, network and device permissions. Redact serial numbers, unique identifiers and secrets.

## 2x2: four foundational trust boundaries
1. Firmware/boot: inventory OEM firmware, signed update provenance, Android verified boot or Linux UEFI Secure Boot where available; observe only, no firmware mutation.
2. Hardware/runtime: CPU instruction compatibility, GPU driver provenance, RAM/storage limits, endian and binary-format fixtures, reproducible SHA256.
3. AI vendors: capability matrix for local open-source models, optional hosted providers, licensing, privacy, latency, cost, model provenance and entitlement. Never auto-enable paid services.
4. Automation authority: separate observer, proposer, draft-branch mutator and human release approver. Agent outputs are untrusted proposals, not authority.

## 4x4 evidence matrix
Rows: boot/firmware, CPU/GPU/memory, OS/runtime, AI/vendor adapters.
Columns: provenance, compatibility, isolation, recovery.
Each of 16 cells must record exact source SHA, environment, test command, result PASS/FAIL/BLOCKED/NOT_RUN, logs and rollback or recovery.
No synthetic GREEN.

## 8x8 targeted hardening
- Validate firmware update and boot integrity only with official vendor evidence.
- Confirm Android sandbox/SELinux permissions and Linux user namespaces/seccomp where supported.
- Inventory model formats, tokenizer compatibility, quantization and accelerator fallbacks; compare CPU-only baseline.
- Use explicit allowlisted tool calls, scoped credentials, idempotency keys, rate limits, network egress policy, bounded retries and timeouts.
- Treat retrieved docs, plugin responses, model outputs and build logs as untrusted input; resist prompt injection.
- Verify SQL STRICT schema and rollback, JSON manifest authority=false, artifact hashes and immutable audit ledger.
- Keep PHP/phpBB separate from SQL authority and AI agent credentials.
- Verify backup/restore, dry-run, secret scanning, dependency/SBOM/licensing and emergency stop.

## 16x16 conditional escalation
Expand only failing or high-risk cells: real device, offline mode, adversarial inputs, compromised dependency simulation, permission denial, low memory, network outage, malformed binary, partial write, repeated execution, agent disagreement, recovery and signer mismatch.
No firmware or production changes in this phase.

## CAST Bridge gates
A. Hardware attestation/inventory supported by real receipts, not claimed universal firmware support.
B. Vendor-AI comparison with open-source default, optional paid-provider OFF and no private-artwork leakage.
C. Reproducible SQL/Python/npm/Android/creative smoke tests on exact candidate source.
D. Agent authority test: no self-approval, no blind merge, no automatic release.
E. CI logs, hashes, evidence ledger, explicit unresolved blockers.
F. Owner approves any promotion. Crown STOP until physical Samsung runtime and release proof.

## Immediate execution queue
1. Read-only inspect existing firmware, vendor reduction, agent and CAST workflows.
2. Add read-only CI audit for manifest authority, workflow permissions, action SHA pinning and vendor allowlist, after test design.
3. Run safe local schema and manifest tests, then extend to adversarial fixtures.
4. Stage narrow fixes on draft branch, re-test, report exact-source CAST readiness.
