# LuHm OS Virgin Install

This package is built for a clean manual upload.

Uninstall the older LuHm OS plugin first. The new package does not migrate or depend on old plugin state.

The archive root contains `plugin.json`. Upload the archive exactly as built.

After installation, start a new chat and ask LuHm OS to inspect current source truth. Normal ChatGPT is the default mode. Coding roleplay starts only when explicitly requested or when continuing an active scene.

The package connects to the live Godot-hosting read-only MCP endpoint declared in `mcp.json`, including `luhm_open_godot_player`. The ChatGPT host must still accept the connection and in-chat iframe. The package does not contain local MCP configuration, private MCP configuration, tokens, private keys, or secrets.

A successful manual upload proves installation only. It does not prove directory publication, production signing, live DNS/TLS mutation, certificate issuance, or Crown.
