# CAST Bridge storage alignment: one Canon, two storage tiers

**Status:** candidate source; private host NOT provisioned; schedule NOT installed;
Google credentials NOT configured; no real Drive data transferred; Crown STOP.

## What happens automatically after private-host setup

1. Use the connected Google Drive folder in ChatGPT Library where available. This
   references Drive files **without reuploading** them to ChatGPT storage.
2. Files created only inside ChatGPT Library **do not have a supported general
   consumer Library filesystem/rsync endpoint** in this workflow. Download or
   export those files into the private host's `LuHmInbox/` when they need archiving.
3. The authorized private Linux host runs `rsync` from its inbox or a pinned
   SSH-readable remote source into private staging. It never deletes source files.
4. `canonTransferIndex.py` computes a SHA-256 ledger and finds exact duplicates.
   That ledger contains PRIVATE filenames. It never goes to public GitHub.
5. `rclone copy --checksum --immutable` uploads the raw files to a deliberately
   scoped **private** Drive destination. Repeated uploads skip unchanged files,
   and modified existing remote paths fail closed rather than overwriting.
6. `rclone check --one-way --checksum` independently checks what was uploaded.
   A versioned private manifest is then uploaded to Drive's `_control` directory.
7. GitHub retains code, policy and privacy-safe verification metadata, **never
   media archives, raw paths, OAuth tokens, service-account JSON, or private IDs**.

**Not a bidirectional mirroring system.** There is no automatic deletion,
reverse synchronization, or automated Canon promotion. Directory/path collisions
with changed contents are errors requiring versioned filenames and review.

## Why a private systemd timer instead of a public GitHub self-hosted runner

The canonical repository `eggie-admin/LuHm-OS` is public. GitHub explicitly
discourages self-hosted runners attached to public repositories because untrusted
workflow code can compromise long-lived hosts. The new GitHub Actions workflow
uses GitHub-hosted ephemeral runners for **source-only tests**, with no secrets.
The actual file copier runs under the private user's OS account. It requires no
publicly exposed SSH or database ports and can work with a local inbox.

## Once-only installation on an approved Ubuntu host (not yet performed)

The operator must first verify a source commit that has been approved and merged
into `main`; do not run arbitrary PR branches with private credentials. Existing
source is retained and inspected before any local upgrade.

- Install `rsync`, `rclone` and Python 3 from approved distribution packages.
- In `rclone config`, create **your own Google OAuth client ID**, authenticate
  the intended Drive account, and scope the remote with a `root_folder_id` for a
  private `LuHm-OS-Private` directory. Confirm that the root is owner-only and
  not inherited from a broadly shared folder. If approved, a correctly scoped
  service-account setup is an alternative. Keep `~/.config/rclone/rclone.conf`
  permission 0600 and NEVER commit it. Provider account quota is not yet verified.
- Clone the verified source at `~/LuHm-OS` or point the service to the
  actual approved local checkout.
- Create `~/LuHmInbox` for locally downloaded/exported ChatGPT files. If using
  `LUHM_RSYNC_SOURCE`, configure key-based SSH separately, pin the host key,
  use read-only permissions for the source account, and do not open inbound
  access to the private storage server.
- Copy `ops/canon-sync/canon-sync.env.example` to
  `~/.config/luhm/canon-sync.env`, replace `YOUR_USER`, set the existing private
  rclone remote and scoped folder. Do not copy credentials into the env file.

### Private host commands (operator-run AFTER approval)

```bash
mkdir -p ~/.config/luhm ~/LuHmInbox ~/LuHmState/staging ~/LuHmState/state
chmod 700 ~/.config/luhm ~/LuHmInbox ~/LuHmState
cp ~/LuHm-OS/ops/canon-sync/canon-sync.env.example ~/.config/luhm/canon-sync.env
chmod 600 ~/.config/luhm/canon-sync.env
# Edit the private config to replace YOUR_USER and choose the correct remote.
# Ensure it is still LUHM_SYNC_ARMED=NO.
set -a; source ~/.config/luhm/canon-sync.env; set +a
bash ~/LuHm-OS/tools/luhmCanonSync.sh --dry-run
rclone about luhm-drive: --json
```

**Activation is a separate host action.** After successful dry-run, identity
check, private-folder permissions check, quota check and an initial backup,
set `LUHM_SYNC_ARMED=YES` in the private configuration, then perform one
manually supervised `--apply`, inspect the full private checksum proof and
perform a recovery pull into a different local directory.

Only after that proof:

```bash
mkdir -p ~/.config/systemd/user
cp ~/LuHm-OS/ops/canon-sync/luhm-canon-sync.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now luhm-canon-sync.timer
systemctl --user list-timers luhm-canon-sync.timer
```

The timer runs every six hours, with an anti-overlap lock, bounded retries,
and local-only evidence logs. The private host may need a user login session
or an approved lingering configuration for the user timer to work unattended.
**The timer and host have not been configured from this chat.**

## Guardrails and failure modes

- Default is dry-run; live transfer requires the exact local `YES` arm.
- Remote is restricted to `remote:LuHm-OS-Private/... `. No whole-Drive sync.
- No `--delete`, no `rclone sync`, no `move`, no `purge`.
- Known credentials and partial-download file patterns are excluded. This is
  defense in depth, **not** automatic sensitive-data classification. Operators
  must still vet the incoming folder and keep private artwork private.
- Source symlinks are skipped. Directories must not overlap.
- Private local paths and Drive credentials never enter public CI logs.
- Quota exhausted, rate-limited, missing hash support, unknown Drive permissions,
  or missing authenticated host are **AMBER/RED**, not GREEN.
- Google Docs/Sheets/Slides native files are NOT equivalent to raw binary files:
  use official Docs/Drive export workflows separately, with format/provenance.
- GitHub can only call the code/manifests reviewed at an exact source ref. Any
  independent device, deploy, promotion or signature gates remain unchanged.
- Rclone `copy --immutable` prevents overwrites; `check --one-way` verifies
  source items but intentionally permits additional older destination files.
- Restore is required: pull a hash-pinned private file into a new directory and
  verify its SHA-256 before treating the durable backup as proven.

## Current evidence

Source-only implementation staged on the library cleanup candidate branch.
No credentials used, no Google Drive sync executed, no ChatGPT Library API used,
and no production host or systemd timer changed.
