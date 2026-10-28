# LuHm OS Virgin Install

This package is built for a clean manual upload.

**Do not uninstall an existing Project Hydra Site plugin.** The private Project Hydra Site/App plugin is a separate installed identity and its App binding must be preserved. This standalone GitHub-managed `luhm-os` portable package has its own identity and MCP configuration. For a true first install, install the approved package through the supported ChatGPT plugin flow. For an upgrade of the *same* standalone package, use that existing plugin's supported update/reconnect process, not a duplicate installation.

A successful plugin package upload is not a live MCP Apps HTML mount. See [remote ChatGPT debug lane](../../manual/chatGptRemoteCompatibilityDebugLane.md) and inspect host tools/resources, CSP, and mobile acceptance before claiming completion.

The archive root contains `plugin.json`. Upload the archive exactly as built.

After installation, start a new chat and ask LuHm OS to inspect current source truth. Normal ChatGPT is the default mode. Coding roleplay starts only when explicitly requested or when continuing an active scene.

The package connects to the updated read-only MCP endpoint declared in `mcp.json`. Its `luhm_open_godot_player` offers a candidate viewer for the existing separate Godot HTTPS service, with explicit host verification pending. The ChatGPT host must still accept the connection and in-chat iframe. The package does not contain local MCP configuration, private MCP configuration, tokens, private keys, or secrets.

A successful manual upload proves installation only. It does not prove directory publication, production signing, live DNS/TLS mutation, certificate issuance, or Crown.
