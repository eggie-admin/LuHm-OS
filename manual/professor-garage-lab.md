# Professor Garage Lab: remote-first AI-FFmpeg

## Mission

No Professor desktop is required. GitHub owns code and tests, GitHub Actions supplies short-lived rendering compute, and GitHub Codespaces provides an interactive *remote* production workstation. Render's existing LuHm sidecars remain unchanged; no new public endpoint was created. Drive remains durable binary storage. Professor retains release and publication authority.

## Workshop startup

The existing `.devcontainer/devcontainer.json` now prepares FFmpeg on Codespace creation and starts the private AI-FFmpeg worker when the Codespace starts. It uses `scripts/ai-ffmpeg-codespaces.sh`, a private token stored only in the Codespace home directory, and the workstation's **remote** `127.0.0.1:8797` loopback interface. A forwarded port in Codespaces is private by default. Do not change its visibility to public.

Open this PR branch in a new browser Codespace after choosing to spend any applicable Codespaces usage. The Codespace must actually be started; source configuration does not prove an active runtime, and Codespaces may stop automatically. From its terminal, the optional sanity check is:

```bash
bash scripts/ai-ffmpeg-codespaces.sh status
```

This does not require a personal Ubuntu installation. Remote file staging defaults to `~/hydra/media`, with private candidate renders at `~/hydra/media/candidates`. Do not place private art or raw videos in the public repository. Copy finished files to Drive before the Codespace is discarded.

## Remote render proof in GitHub Actions

The PR workflow `.github/workflows/ai-ffmpeg-audit.yml` builds seven synthetic still-frame shots into a real silent portrait H.264 MP4. It tests invalid input rejection and publishes **temporary** MP4 plus SHA-256 receipt as an Actions artifact, with a three-day retention period.

The proof is generated on a GitHub-hosted Linux runner. This does not mean the Codespace service is live or that production footage has been rendered. The sample is colored dummy footage, not finished Pirate Daddy art.

## Film manifest

`media/pirate-daddy-film/episode-template.json` describes seven shots across five story sections: 100 brand, 200 transmission, 300 world, 401 old guard, 402 berserker, 403 witching hour, and 500 DADDY Codex. Audio is deliberately deferred. Only the Professor may approve real assets and publication.

## Persistent cloud runtime boundary

A GitHub Actions runner lasts only for its job; Codespaces may stop when idle. The existing Render services have not been modified. A truly always-on authenticated media queue requires explicit runtime, storage, provider and cost decisions, plus a new proof of access. It must not quietly reuse or expose the public MCP harness as an arbitrary video rendering endpoint.

## Verified and unverified

- Verified by CI on the exact candidate: FFmpeg discovery, security controls, real silent seven-shot render and artifact upload once the run passes.
- Code-configured only: Codespace FFmpeg installation and automatic start when a Codespace is created/rebuilt and started.
- Not verified: an actual running Codespace, persistent cloud runtime, private Drive art inputs, NVIDIA GPU acceleration, public publication, or Facebook account automation.

Crown remains with the Professor.
