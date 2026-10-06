# Security

LuHm OS keeps production credentials, signing material, private media, and private reference assets out of Git.

Do not commit API keys, OAuth tokens, keystores, private keys, `.env` files, voice recordings, private model weights, or proprietary extracted runtime assets.

The playable Android lane is debug-only until separately Crown-authorized. Current builds use a disposable CI debug signer and a side-by-side package identity.

Security-sensitive reports should avoid posting secrets or private data in public issues.
