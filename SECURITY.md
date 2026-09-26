# Security

LuHm OS keeps production credentials, signing material, private media, and private reference assets out of Git.

Do not commit API keys, OAuth tokens, keystores, private keys, `.env` files, voice recordings, private model weights, or proprietary extracted runtime assets.

## Android lanes

Development candidates may use disposable CI signers and side-by-side package identities.

The public beta lane uses package `art.eggiebagelface.luhmos.beta`. A published beta must use one persistent signing certificate for the life of that update channel. The keystore and passwords must remain outside the repository and outside build logs. A beta signed with a different certificate is not an update and must not be published as if it were one.

The compact local-install APK must remain non-debuggable, ARM64-only, target Android API 36, 16 KB ZIP aligned, and without the Android `INTERNET` permission unless a separately reviewed release contract changes that boundary.

## Remote assets

Remote assets may be fetched during CI only through a pinned manifest. CI must verify the remote archive SHA-256 and each selected member SHA-256 before staging. Archive traversal, symlinks, unexpected output paths, and configured byte-ceiling violations are rejected. The runtime APK does not fetch those build assets from the network after installation.

## Updates

LuHm OS does not implement an in-app self-updater in the compact beta lane. Updates are distributed by an external package manager or a human-promoted signed release channel. Every promoted APK must publish its SHA-256 and must preserve package identity and signing-certificate continuity.

Security-sensitive reports should avoid posting secrets or private data in public issues.
