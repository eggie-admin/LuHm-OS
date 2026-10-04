# LuHm Embedded Proof Viewer Contract v1

## Purpose
The proof viewer renders evidence inside the LuHm chat workbench without granting that evidence execution or promotion authority.

A proof is a display packet. It never upgrades the source verdict. `GREEN`, `AMBER`, `RED`, and `UNKNOWN` come from the producing evidence gate.

## Supported proof types
- `pdf` — browser/WebView PDF object from a safe local/blob/HTTPS URL.
- `docx` — backend-extracted structured blocks only. Raw DOCX/Office HTML is never injected.
- `website` — captured screenshot first. Optional live URL must be explicitly `allowLive: true` and renders in a fully sandboxed iframe without script/origin privileges.
- `image` — safe local/blob/HTTPS image proof.
- `asset` — visual preview plus structured asset/provenance fields.
- `json` — structured object rendered as escaped JSON text.
- `text` — escaped plain text.

## Common packet
```json
{
  "id": "proof:device:52cdb6e:001",
  "type": "image",
  "title": "Samsung Cathedral launch",
  "status": "GREEN",
  "sourceRef": "52cdb6e948be91dd0939264cdd09ff8284292d85",
  "sha256": "...",
  "provenance": "physical Samsung capture",
  "capturedAt": "2026-09-27T21:00:00Z",
  "url": "blob:..."
}
```

`id` and a supported `type` are mandatory. Missing status becomes `UNKNOWN`. Missing source/hash/provenance remain visibly `UNKNOWN` rather than inferred.

## DOCX structured blocks
The backend may convert an Office document into these bounded display blocks:
- `heading` with `level` 1–3 and `text`
- `paragraph` with `text`
- `quote` with `text`
- `code` with `text`
- `list` with `ordered` and `items[]`
- `table` with `rows[][]`
- `image` with a safe preview `url` and optional `alt`

The front end creates DOM nodes with `.text()` and never accepts raw HTML from DOCX.

## Website proof
Preferred packet fields:
```json
{
  "type": "website",
  "url": "https://example.org/report",
  "snapshotUrl": "blob:captured-screenshot",
  "capturedAt": "...",
  "status": "AMBER",
  "sha256": "sha256-of-capture-or-receipt"
}
```

Live frames are optional and secondary. A backend may add `liveUrl` plus `allowLive: true`. The front end still applies an empty `sandbox` attribute and `no-referrer`; sites may refuse to frame themselves and that refusal is not a proof failure.

## Chat integration
A normal chat receipt may include a `proof` object. The workbench then renders an **Open proof** button.

```js
LuHmFrontEnd.appendReceipt({
  title: "Device proof",
  status: "GREEN",
  fields: { sourceRef: "...", sha256: "..." },
  proof: { id: "...", type: "image", url: "blob:..." }
});
```

Direct host/native integration may call `LuHmFrontEnd.openProof(packet)`.

## Authority and security rules
- No proof packet executes tools.
- No proof packet can merge, sign, publish, promote, or self-approve.
- Raw HTML from websites, DOCX, receipts, JSON, or text is not injected.
- `javascript:` and `data:` URLs are not accepted by the safe URL gate.
- Remote `http:` is rejected; same-origin HTTP is accepted for the local-first development shell.
- External links open with `noopener noreferrer`.
- Website live mode is sandboxed and opt-in.
- Pinning a proof emits a request boundary only; it does not persist anything by itself.
- Evidence identity must remain attached to exact `sourceRef`, hash, provenance, and capture time when known.

## Native/backend expectation
The native Android/Godot or host bridge owns file picking, DOCX extraction, website capture, cryptographic hashing, provenance collection, persistence, and authenticated retrieval. The HTML workbench is a renderer and request surface only.
