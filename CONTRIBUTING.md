# Contributing to LuHm OS

Thanks for helping build LuHm OS. This is an open-source GitHub project under the repository's existing [GNU GPLv3 license](LICENSE). You can fork the repository, propose changes, and distribute modified code under the applicable license terms. Assets and third-party content may have separate rights: do not assume that a public file is cleared for reuse.

## Safe fork workflow

1. Fork `eggie-admin/LuHm-OS`. Branch in **your own fork** under `candidate/<purpose>` or `audit/<purpose>`; do not push into the Professor's protected `main`.
2. Keep source-only changes separate from build, deployment, publication, agent activation and production signing. Write a focused test and reference exact source SHA.
3. Submit a reviewable pull request with intent, affected files, security boundary, test results and rollback. Existing Canon and host receipts stay independent.
4. Don't include private Google Drive media, chat messages, medical/personal information, credentials, app binding IDs, signing certificates or Site owner authorizations. An independent fork needs its own approved host and provider configuration.
5. Preserve agent role identities as *contracts*, not claims that independent models/servers are running. A green mock or roleplay is not proof of a worker.

## Mobile/ChatGPT contributions

Test `host/harness/mobileCockpitWidget.html` using `python3 -m unittest tests/testMobileCockpitEvidenceContract.py -v` and follow `manual/mobileChatGptReleaseTrain.md`. Check both the legacy full studio and the lightweight mobile resource. A successful HTML source test is **not** evidence that ChatGPT mounted the plugin on a tester's iPhone.

## Release responsibilities

The project's official Beta and Stable brands and published plugin identities are controlled by the Professor. Forks can create their own legally compliant distributions under distinct identities, but must not impersonate the official project or copy private plugin credentials. Stable publication requires a separate exact-artifact human-approved review, security/rights acceptance, device-level evidence and rollback.

No secret donations or external developer tokens are requested in public issues. Bug reports should provide non-sensitive reproduction steps, sanitized logs and device/client versions.
