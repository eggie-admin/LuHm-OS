# LuHm-OS Final Mutation Ingestion Snapshot | 30 October 2026

One integration branch, source-only. Four layers with four ownership threads each:

1. **Canon** GitHub SHA/source law, one immutable typed envelope, 4×4+8×8+16×16 source evidence, SQLite STRICT receipt store.
2. **Adapters** npm for web, Python MCP for remote host, Android Gradle/Godot for app. Do not force every package through npm or embed Node/Python in Samsung.
3. **Studio** Blender approved originals → audited GLB → Godot; FFmpeg for cinema/media; lightweight static HTML/WebView for control. Heavy work belongs local/approved remote, not Android.
4. **Distribution** fork/security policy, Drive durable vault after safe ACLs, GitHub reproducible CI and snapshot, separate official signing and human acceptance.

The shared `packages/cathedral-kernel/contract.v1.json` drives JavaScript `CathedralEnvelope` class and Python `CathedralEnvelope` dataclass. Both consume matching golden vectors, normalize hash arrays and reject mutating operation, untrusted origins, arbitrary file identifiers, nonzero cost, false approval and fake GREEN. SQLite STRICT receipt has zero-spend/zero-authority constraints. No network execution or file ingestion occurs merely through import.

**Donor provenance:** PR #462 security and matrices are source-copied into PR #463, which retains its free-first daily snapshot workflow. PR #460 is donor quarantine only, not silently merged. Preserve original code and vendor attribution. SPDX metadata alone does not establish distribution rights; CycloneDX/SLSA are future optional output formats, neither attestation nor SBOM is yet generated.

**Source commands:** `python3 -m unittest tests.testCathedralKernel -v`; `node --test packages/cathedral-kernel/tests/envelope.test.mjs`; `python3 tools/cathedralUnificationAudit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/unification.json`.

**Security HOLD:** Live Drive metadata found public-write access on formerly private control-plane root and seven immediate children. No protected Drive read/write until every relevant ACL is repaired and reverified. Cloudflare Workers builds have failed and exact logs remain outstanding. Device/runtime, signer custody, vendor redistribution, private proxy and beta publication are NOT proved by source CI.

**One law:** AI proposes. Policy authorizes. CI proves. Human promotes. Crown STOP.
