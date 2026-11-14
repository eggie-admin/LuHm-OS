# LuHm-OS Firefox Antenna · Mozilla signing handoff
Status: PROPOSED_SOURCE_ONLY. The signing preflight is NOT an AMO signature or installation proof.

## Separate trust boundaries

| Trust chain | What it verifies | Authority |
| --- | --- | --- |
| TLS certificate on approved HTTPS origin | Browser↔server connection, hostname and transport | Public CA |
| SHA-256 reproducible source ZIP | Bytes match a named SHA-256 recorded for an exact Git source ref | GitHub CI receipt |
| Mozilla signed XPI | Firefox add-on package accepted/signed by Mozilla | addons.mozilla.org (AMO) |
| Local backend release policy | Read-only localhost API, no web→shell bridge | Existing LuHm-OS Canon and Professor |

Do not extract, upload, repurpose or reuse the live TLS **private key** to sign a browser extension. Certificate validity does **not** satisfy Mozilla's AMO add-on signing requirement.

## Already implemented

1. A stable Gecko extension ID, `luhm-antenna@eggiebagelface.art`.
2. Firefox Manifest V3 with `browser_specific_settings.gecko.data_collection_permissions.required = ["none"]`. This extension only reads a local status response, does not store or transmit it to a third party.
3. Local-only host permission `http://127.0.0.1:8765/*`, no content scripts, native messaging, remote JS, auto-update endpoint or admin privileges.
4. Reproducible **unsigned ZIP** using `tools/firefoxAntennaSigningPreflight.py`. The same four files are included in stable order and timestamps, with receipt bound to exact `git rev-parse HEAD`.
5. Existing `.github/workflows/self-hosted-remote-updates.yml` runs negative tests and uploads the preflight ZIP as a CI artifact.

## Safest first signing lane: unlisted AMO (private distribution)

No need to submit the add-on for a publicly listed page. Mozilla signs unlisted
extensions for self-distribution. Choose one of these **manual, owner-authorized**
handoffs after reviewing exact-head CI:

**Browser upload, no AMO API keys in scripts:**
- Sign in to the Mozilla Add-ons Developer Hub with the owner's Mozilla account.
- Select **Submit a New Add-on** and **On your own (self-distribution)**.
- Upload the CI-produced `luhm-firefox-antenna-0.1.0-unsigned.zip`.
- Complete any required policy/review information. Download the **Mozilla-signed XPI** when approved.

**CLI alternative, using a recent supported `web-ext` with Node 22+:**

```sh
# Local operator machine, in a trusted checkout at the exact approved head:
web-ext lint --source-dir plugins/luhm-firefox-antenna
# Store AMO developer API credentials in a protected operator secret store.
# Do not paste secrets into chat or commit them. The following shell
# variables are read by web-ext, not by the LuHm packaging script.
web-ext sign --source-dir plugins/luhm-firefox-antenna \
  --channel=unlisted \
  --api-key="$WEB_EXT_API_KEY" \
  --api-secret="$WEB_EXT_API_SECRET" \
  --artifacts-dir build/firefoxAntennaSigned
```

Mozilla AMO Developer Hub: https://addons.mozilla.org/developers/
Mozilla instructions: https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/
Firefox distribution: https://extensionworkshop.com/documentation/publish/self-distribution/

### Signed release receipt gate

Before calling the add-on signed, verify and record all of:
- Exact Git source SHA and CI package SHA-256.
- AMO signed build for the **same stable extension ID and version**.
- Signed `.xpi` file SHA-256 and trusted storage destination.
- Install proof in real Firefox ESR without disabling signature enforcement.
- Local antenna handshake and Firefox toolbar UI smoke test.
- No unexpected permissions, secrets, remote scripts, private-media exposure or auto-installer.
- Separate Professor release permission and rollback route.

An XPI is not `SIGNED_GREEN` merely because it contains signature-looking ZIP entries.
The definitive installation/signature check requires Firefox verifying Mozilla's signature.

## Future update channels

Firefox signed XPI updates stay inside the Firefox/Mozilla add-on trust model.
LuHm UI/art packs use a separately authenticated asset manifest. The existing
ChatGPT MCP plugin host contract remains independent. No in-chat browser
extension automatically changes the installed ChatGPT app.

## Remaining stops

No connected Mozilla AMO developer account/API signing credentials were available
to the source packaging job. It does not submit, sign, list, install, publish,
touch TLS certificates, or grant production deployment. The clean preflight
does not prove Firefox runtime or Debian kiosk installation.

CROWN STOP until independent signing and target-runtime proof.
