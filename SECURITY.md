# Security

LuHm OS keeps production credentials, signing material, private media, and private reference assets out of Git.

Do not commit API keys, OAuth access or refresh tokens, browser cookies, keystores, private keys, `.env` files, voice recordings, private model weights, VPN client secrets, `tls-crypt` keys, or proprietary extracted runtime assets.

The playable Android lane is debug-only until separately Crown-authorized. Current candidate builds use a disposable CI debug signer and side-by-side package identity. A release/update lane requires a persistent signing trust anchor with private custody outside pull-request code and public fingerprints recorded as receipts.

## Google identity and authorization

A live Google login is an identity/session source, not a bag of tokens to scrape. Connector/browser session credentials remain opaque. The Android app must not copy cookies or export tokens from an existing Chrome/Google session.

When Google sign-in is activated, prefer Android Credential Manager / Sign in with Google. When Google account data such as Drive requires authorization, use the supported Google authorization client or an installed-app authorization-code flow with PKCE as appropriate. Native public clients do not embed a client secret. Validate issuer, audience, expiry, nonce/state, and requested scopes at the appropriate relying party before trusting credentials.

Bearer tokens must never be logged, placed in WebView DOM/localStorage, committed to source, or uploaded with build artifacts. Avoid persistent refresh tokens where possible. If persistent credential material becomes necessary, protect it with the Android Keystore and provide revocation/sign-out behavior.

## TLS, certificates, and OpenSSL

Non-loopback network traffic is HTTPS-only. Prefer TLS 1.3 and require at least TLS 1.2 for any future remote lane. Keep hostname verification and normal certificate validation enabled. Do not add trust-all managers, hostname-verifier bypasses, mixed-content overrides, or certificate-warning click-through code.

OpenSSL is a build/operator verification tool for certificate inspection, CSR generation, fingerprints, and crypto receipts. Private keys generated with OpenSSL must be created outside the repository, kept out of logs and artifacts, and never uploaded to the ordinary Google Drive build-artifact folder. Public certificates and SHA-256 fingerprints may be recorded when their owner, purpose, algorithm, and rotation metadata are clear.

## VPN and remote administration

KAI 9000 loopback services do not need a VPN. If remote administration is activated later, route it through an explicitly approved private overlay such as a managed OpenVPN profile rather than exposing Ollama, VNC, or an administrative API directly to the Internet.

OpenVPN profiles containing passwords, client private keys, or `tls-crypt`/`tls-crypt-v2` secret material are not repository artifacts. Prefer per-client material and managed device/profile storage. A public CA certificate may be distributed; private client keys may not.

## Shizuku

Shizuku is an optional scoped privilege lane, not an Android root login. The base APK must work without it. Permission is requested only from an explicit native user action. A Shizuku instance started through ADB has shell identity (UID 2000), which is distinct from root UID 0. The first-pass integration is capability detection only: no generic shell, no `newProcess`, no UserService, no WebView privilege request, and no Secure Folder/profile-boundary bypass.

## CI and source control

GitHub Actions should use minimum permissions, pinned action commit SHAs, exact-source checkout, and `persist-credentials: false` unless a write is explicitly Crown-authorized. Pull-request code must never receive release signing material.

Main-branch protection/rulesets, persistent signing custody, OAuth client configuration, and any live remote TLS/VPN endpoint remain separate enterprise gates. Static source GREEN does not imply those external gates are complete.

Security-sensitive reports should avoid posting secrets or private data in public issues.
