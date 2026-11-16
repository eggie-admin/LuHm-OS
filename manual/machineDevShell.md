# LuHm-OS default attested development shell

Portable testing launcher, not a new Linux login shell or an Android firmware flasher. Uses the exact canonical checkout and existing tools/canonHexLedger.py to create 1,792 HEX assessments in 28 SHA-256-chained 64-slot checkpoints.

## Verify before execution

Download the successful main-branch LuHm Signed Machine Development Shell workflow artifact. Before extraction, verify its tar.gz file with:

    gh attestation verify luhm-machine-dev-shell-SHA12.tar.gz --repo eggie-admin/LuHm-OS --signer-workflow eggie-admin/LuHm-OS/.github/workflows/machine-signed-shell.yml --source-digest EXACT_MAIN_COMMIT_SHA

Then unpack into an unprivileged folder and from the exact matching Git checkout run: bash /extracted/shell/luhm-dev-shell.sh help.

Commands: help, status (read-only hardware), tests, sql-snapshot /tmp/NEW_DIR (private SQLite and JSON), container-check (Docker Compose config only). Root, source mismatch, existing SQL output path and unknown commands all fail closed.

Main workflow keylessly attests with GitHub OIDC/Sigstore short-lived certificate, then verifies its own provenance and uploads a seven-day artifact. PRs run unsigned tests only. A SHA checksum is not a signature. This is not an owner GPG signature, Android APK signing or physical Pi/Android proof.

Owner GPG remains separate via tools/ownerGpgBootstrap.sh on trusted owner hardware. No self-signed TLS certificate, remote database, paid service, device flashing, signing key or agent activation is created. Root license remains GPLv3. Crown STOP.
