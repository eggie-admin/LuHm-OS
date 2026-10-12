# LuHm OS typed SQL lanes, source-only prototype

Four logical streams: **numeric**, **text**, **Boolean (tri-state)**, and **AI manifest**. The numeric stream stores signed int64, finite IEEE-754 floats, and scaled int64 exact decimals. One indexed `streamEvent` table binds taskId, sourceRef, scopeId, workerId, 8th note, and sequence. No binary files belong in SQLite.

Source compatibility: `doctrine/storageTopologyV1.json`, `doctrine/python3ControlPlaneLawV1.json`, `doctrine/aiTaskManifestV2.template.json`, and `doctrine/eighthNoteAgentScopeV1.json`.

Run offline with `python3 -m unittest discover -s tests -v` from this directory, then `python3 tools/typedSqlStub.py`. No additional dependencies or remote server needed. Tested with SQLite STRICT tables.

Storage: GitHub text/source receipts; ChatGPT Library optional **medium review copy**, not source authority; Google Drive durable binaries and larger artifacts. A `.sqlite` file is never committed to public GitHub. Never send secrets via manifests or source.

Admin: Datasette must use `--default-deny` and disallow arbitrary SQL unless separately authorized; pgAdmin 4 is Python/Flask server-side, not a static website. Both remain private, uninstalled candidates. Portal page is static reference only.

Cloudflare: no live Cloudflare DNS, routing, proxy, TLS, or publication mutation. Do not expose direct SQL ports. Target p95 <= 5000 ms remains unmeasured. Agent skills are contracts, not proof of running agent workers. All gates Crown STOP.

## Remote compact projection

For cellular latency, transmit only `{taskId, sourceRef, scopeId, sequenceId, evidenceRef}` plus the schema identifier when the receiving registry already knows the canonical manifest. Do not transport credentials, hidden chain-of-thought or complete audit histories. One stable HTTPS/MCP gateway is favored; Cloudflare DNS/TLS and remote SQL ports are independent gates. A sub-five-second p95 must be measured over cellular end-to-end, not inferred from CI.