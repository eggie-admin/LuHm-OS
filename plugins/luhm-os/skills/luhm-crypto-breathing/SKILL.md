---
name: luhm-crypto-breathing
description: Inspect, plan and audit LuHm R1-R4 hexadecimal integrity, encrypted snapshots, SQLite/MariaDB receipt routing and two-lane Lum orchestration without inventing live proof or revealing keys.
---

# LuHm R1-R4 cryptographic breathing and SQL escalation

Operate through the existing private Project Hydra / LuHm MCP cockpit. Resolve the current source SHA and Canon before touching a machine or update. The read-only tools `luhm_crypto_breathing_status`, `luhm_mariadb_receipt_status` and `luhm_orchestration_status` are **source candidates** until verified as installed in the actual host.

## Four gates
1. **R1** (Canon tier zero): hash exact bounded bytes with SHA-256 and compare to an independently supplied expected digest. A digest is not proof of origin.
2. **R2** (tier one): compare SHA-512 and SHA3-256 digests and bind an immutable snapshot reference to the same task/source/scope/artifact.
3. **R3** (tier two): verify a constant-time HMAC-SHA256 over the canonical identity and digest using a host-only secret. This is shared-key authenticity, **not** an externally verifiable software publisher signature.
4. **R4** (tier three): verify a privately encrypted AES-256-GCM snapshot using authenticated additional data bound to the same identity. A host-only helper can produce random-nonce encrypted bytes in memory; it cannot authorize storage, publication, update, or release. Final state: `HOLD_FOR_PROFESSOR`.

When a gate is missing evidence, **HOLD**. On mismatch, **STOP**. Continue only after **PASS** at that exact gate. Maximum four passes; never loop until convergence, reuse a receipt after source changes or self-promote from candidate-green to release-green.

## SQL and transport
- Python stdlib `hashlib` and `hmac` plus optional `cryptography` on an approved private host.
- `host/api/luhmCryptoSqlite.py` uses the existing SQLite STRICT four-lane typed schema, storing only digests, metadata and source-identity references. No keys or raw assets.
- `host/api/luhmMariaDbReceipt.py` is an optional parameterized receipt sink with no direct connection or schema creation. Operator must separately establish private-network access, verified TLS, least-privilege credentials and backup/rollback before any write.
- Base64 and hex are encodings, not secrecy or authorization. JSON feeds/RSS can carry **signed public metadata only** after provenance review; no automatic update based on RSS. 7z is an optional compression format, not evidence of integrity, authenticity or encryption without separately verified controls.
- GDM is only a presentation analogy for the ChatGPT cockpit, not a privileged display manager. Do not expose SSH, VM ports, SQL admin or FastAPI host tokens to the client.
- RetroArch, ROMs, firmware files, JIT emulators and Perl legacy tools are not installed or activated by this skill. Study licensing, firmware rights, unsafe dynamic code/JIT and network transport before admitting any adapter.

## Proof and reporting
Separate code staged, CI passing, private host running, in-chat tool mounted, actual VM connected, physical Samsung proof, and owner-approved release. The 15 named agent contracts remain registered but their independent worker execution is still quarantined. Two lanes are **logical task/evidence checkpoints**, not autonomous async processes. No paid API calls are authorized here.

Do not include private keys, tokens, source media, raw chat contents, device addresses or private Drive identifiers in public PRs.
