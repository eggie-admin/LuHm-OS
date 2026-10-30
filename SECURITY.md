# LuHm-OS Security & Vulnerability Disclosure

LuHm-OS: Project Premonition is a public source repository, not a public permission grant for its production signing keys, private media, hosted apps, or provider accounts.

## Security channels

**Confidential vulnerability:** On the repository's GitHub **Security** tab, use **Security Advisories** or **Report a vulnerability** if private reporting is enabled. Do not submit exploit details, credentials, private artwork or personally identifying information through a public issue. Repository configuration for private vulnerability reporting is **not verified** by this document. If the private reporting button is unavailable, avoid putting sensitive details in a public issue; use an established private channel with the maintainer instead.

**Non-sensitive security improvements:** Open a standard GitHub issue or PR using a minimized, sanitized reproduction. Security patches affecting privileged workflows, Android signing, public package publication, input-to-tool boundaries or secret handling require independent code review.

**Supply chain:** Dependency alerts, code scanning, secret scanning, push protection and protected rulesets must be verified in GitHub repository settings. A source YAML file does not prove those switches are enabled. Dependabot PRs remain proposals, never automatic merges.

**Release or signature incident:** Halt public promotion, preserve exact source/artifact digests and signing certificate fingerprints, and use the existing release gate to record rollback and advisory outcomes. Do not rotate or paste a production key into a public issue.

## Fork safety

A public fork may include public source and public Git history. It must not include private Google Drive masters, OAuth credentials, `.env` files, tokens, API keys, device identifiers, signing keystores, private voice recordings, or nonredistributable vendor assets. Deleting a leaked secret from a branch is not sufficient: revoke/rotate it, assess exposure, and coordinate confidential disclosure.

Vendor forks are separate from LuHm-OS source forks. Review each upstream project's license, source provenance, notices, trademarks, patents, contribution policy and update strategy before making or publishing an official-looking derivative. Never claim that an optional model, ComfyUI custom node or external provider is installed or authorized solely from a manifest.

## Evidence boundary

The existing repository may have protected `main` and active rulesets; their current enforcement, dependency alerts and scanning settings require live API/settings verification. Source-only CI does not prove a Samsung install, ChatGPT widget mount, signed beta, F-Droid index, Cloudflare activation or public release.

**Authority law:** AI proposes. Policy authorizes. CI proves. Human promotes.
