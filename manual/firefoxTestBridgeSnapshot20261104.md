# LuHm-OS TestBridge · Static HTML → Python 3 → SQLite

**November 4, 2026 · proposed source-only.** This is not phpMyAdmin, phpBB,
a signed Firefox extension, a public forum, or a ChatGPT-hosted application.

## What "collect personal data" means at this stage

The existing Firefox **Antenna extension** only requests local status from
`127.0.0.1:8765` and receives no forum content or user identification.
Its Mozilla `data_collection_permissions.required=["none"]` remains accurate
**only for the extension's current implemented behavior**.

A separate static TestBridge page on `127.0.0.1:8766` can receive an
**explicitly consented display name and note**, using Python 3's standard
HTTP server and in-memory SQLite. The fields can contain personal information,
so the page has an in-product disclosure and delete control. They are never
sent to Mozilla, OpenAI, GitHub, the hosted MCP plugin, or any external site.
Session state and notes disappear when the process exits and expire after
one hour if the process stays up. Max 32 records; no emails, login passwords,
financial/health data, user registration, or browsing data.

Neither extension nor local admin is a public personal-data service.
Do not run real client/customer information through this demonstration:
there is no per-user identity, encrypted durable database, backup/recovery,
production access control, at-rest encryption, legal retention policy, or
deployed TLS proof. Local hostile OS users and processes remain out of scope.

## Single static HTML surface

`host/testBridge/index.html` loads `testBridge.js` and
`testBridge.css` from the **same loopback origin**. It has a read-only
status board plus one manual opt-in save/delete form.

```text
Firefox ESR kiosk                       Normal Firefox toolbar popup
 http://127.0.0.1:8766/                 Antenna at 127.0.0.1:8765
          |                                        |
 static HTML + textContent                        |
          |                                      status
 GET /api/testbridge/v1/session
 GET /api/testbridge/v1/status
 GET /api/testbridge/v1/notes
 POST /api/testbridge/v1/notes     (consent + same origin + CSRF)
 POST /api/testbridge/v1/delete    (same origin + CSRF)
          |
      SQLite :memory: (one-hour maximum records)
          |
     NO DATA TO GITHUB; snapshots contain source-policy *counts only*
```

### Run on disposable local Debian test user

```sh
python3 -m unittest discover -s tests -p testFirefoxTestBridge.py -v
python3 tools/firefoxTestBridge2048Audit.py --output-dir build/testBridge2048
python3 host/testBridge/luhmTestBridge.py
# Then open in local Firefox ESR:
# http://127.0.0.1:8766/
```

No sudo/root, no systemd service installation, no network listener other
than loopback, no self-signed cert. Host HTTPS CA certificates are a
**separate production deployment proof**, not used for local-only HTTP.

## 2048 audit geometry and TestBridge snapshot

- 16 different policy families x 128 decision combinations = 2048
  deterministic assertions; **not 2048 independent integration tests**.
- Eight evidence states, four network scopes and four authority classes
  tested per family. Invalid, stale, remote, absent-consent, agent-unlock,
  personal-data-to-GitHub and Crown transitions must HOLD.
- Fixed 64-byte binary record, 128 KiB total. Per-record hash is for
  reproducible source comparison, not public-key authentication.
- Direct tests exercise opt-in, revocation via delete, TTL expiry, bind,
  host/origin/CSRF enforcement, SQL placeholders, and HTML text rendering.
- The JSON snapshot explicitly declares unsupported claims false:
  public HTTPS, Mozilla signing, multiuser auth, public production, current
  ChatGPT MCP host mount, and final Crown.

Artifacts saved by existing CI workflow at the **exact PR head**:

```text
build/testBridge2048/snapshot.json
build/testBridge2048/testBridge2048.bin
```

Do not commit real note contents, cookies, bearer secrets, server logs,
database files, browser profiles, AMO API tokens or TLS private keys.
GitHub stores source, hashes and aggregated candidate receipts.

## phpMyAdmin / phpBB architecture analogy

- phpMyAdmin-like **admin diagnostics**: machine data and SQL state overview,
  never an unrestricted SQL execution textarea.
- phpBB-like **user entries**: explicit consent, bounded records, list and
  delete. Not a real authenticated community website yet.
- Python performs typed validation and parameterized SQL operations.
- GitHub records source revisions and test receipts, not personal records.
- The existing Mozilla signing preflight continues on the underlying
  Firefox antenna branch; signed XPI distribution still requires AMO.
- Do not call an app *official ChatGPT Firefox extension*. It is an
  independent LuHm-OS WebExtension beside the existing ChatGPT MCP adapter.

## Next security gates before a real live service

1. A real user identity model and secure session/CSRF rotation.
2. Per-user authorization (owner/admin/forum role), retention & export/delete.
3. HTTPS with verified certificate chain at approved host, safe headers.
4. Durable encrypted storage and reliable backup/rollback proof.
5. Review Mozilla data-collection declaration when the **extension**
   actually starts collecting/transmitting forum records or identifiers.
6. Separate explicit publish/merge/release gates. Professor retains Crown.

**Status:** proposed local source/CI only. Actual X11, Firefox add-on
installation, public Internet, CA TLS, live storage and signing UNKNOWN.
