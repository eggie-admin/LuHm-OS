# Security

LuHm OS keeps production credentials, signing material, private media, and private reference assets out of Git.

Do not commit API keys, OAuth tokens, keystores, private keys, `.env` files, voice recordings, private model weights, proprietary extracted runtime assets, certificate private keys, or recovery secrets.

## Public transport

The production LuHm MCP endpoint is `https://mcp.eggiebagelface.art/mcp` behind Render-managed TLS. Public cleartext transport is forbidden. Local development may use HTTP only on loopback (`127.0.0.1` / `localhost`). Development or self-signed certificate authorities are not production trust anchors.

Render-managed TLS can issue custom-domain certificates through **Let's Encrypt** or **Google Trust Services**. LuHm prefers Let's Encrypt, but does not falsely require Let's Encrypt exclusively because Render can rotate between its supported public CAs during managed issuance or renewal. When CAA records are present, they must permit both `letsencrypt.org` and `pki.goog` for the Render-managed domain.

Do not pin the public MCP leaf certificate or intermediate certificate. Managed certificates rotate. Production trust is the platform TLS chain plus hostname verification and live certificate evidence.

## Secrets

Provider credentials and OpenAI secrets remain host-only and must not enter Git, the Android APK, browser JavaScript, plugin packages, proof packets, CI artifacts, or public logs. Render secret values use runtime environment configuration or provider secret storage, with Blueprint `sync: false` for externally supplied secrets. **Do not log secrets**, authorization headers, bearer tokens, keystore passwords, private keys, or full credential-bearing environment dumps.

Enterprise operator accounts should use MFA. Production environments should restrict secret visibility and destructive infrastructure changes to explicitly authorized operators.

## Encryption versus integrity

SHA-256, SBOM hashes, Git object IDs, and APK signatures provide identity, integrity, or authenticity. They are **not encryption** and do not provide confidentiality.

The security candidate implements ProofVault at-rest encryption using **AES-256-GCM** with a non-exportable **Android Keystore** key. StrongBox is requested when the device supports it, with Android Keystore fallback when StrongBox is unavailable. Proof blobs and proof metadata are encrypted before being sealed to app-private storage, and WebGlass receives decrypted bytes through an in-process streaming path instead of a decrypted disk copy.

This source implementation is not yet a physical-device cryptographic proof. Sensitive enterprise proofs remain blocked until exact-head Android CI passes and a real device demonstrates import, reopen/decrypt, and tamper-failure behavior. The WebView origin `https://appassets.androidplatform.net` remains a local virtual origin and must never be represented as evidence of public network TLS or public certificate trust.

## Authentication and signing

Current public MCP tools remain anonymous and read-only. Private or write-capable MCP tools stay blocked until OAuth 2.1 is implemented with an established identity provider and validated server-side.

The playable Android lane is not production-signed until separately Crown-authorized. Production signing must use a persistent Crown-owned signing identity generated and stored outside Git. Signing secrets must never be included in SBOM or provenance receipts.

Security-sensitive reports should avoid posting secrets or private data in public issues.
