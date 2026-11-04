# LuHmOS Samsung Field Forge (Termux + Edge Gallery + Ollama)

**Status: PROPOSED SOURCE-ONLY, Crown STOP.** This is an operator-invoked, read-only field kit, not a model installer, Android bridge, launched agent, signed APK, or automatic remote service.

## Safe Tarmac path, once parked

Use Termux from one reputable distribution source, never mix Termux add-ons from different signing sources. Do not run the historical rooted virgin installer: it can uninstall and clear the testing app.

On a new Termux installation:

```sh
pkg install -y python git
git clone --depth 1 --branch main https://github.com/eggie-admin/LuHm-OS.git ~/LuHm-OS
cd ~/LuHm-OS
python3 tools/luhm.py --help
python3 tools/samsungFieldKit.py help
python3 tools/samsungFieldKit.py status
python3 tools/samsungFieldKit.py git
python3 tools/samsungFieldKit.py edge
```

For an existing checkout, first run:

```sh
cd ~/LuHm-OS
python3 tools/samsungFieldKit.py git
```

Only when that prints `git pull --ff-only origin main` is an ordinary fast-forward update appropriate. Review status/branch first; the field kit **never executes** the pull. New experimental code stays in [a draft PR](https://github.com/eggie-admin/LuHm-OS/pulls) until separately approved and merged, so a `main` clone won't contain this candidate yet.

Run the full read-only source audit when desired:

```sh
python3 tools/samsungFieldKit.py doctor --passes 1
```

The audit requires the exact checked-out Git SHA and tests the existing `tools/hardSystemAudit200.py`, not a mocked 200-pass count. Passing does **not** certify the Android device, physical GPU, WebView, local LLM, local network, installed plugin, or signing.

## Local model boundaries

- `python3 tools/samsungFieldKit.py edge`: **Canon status only** from `doctrine/apiSpineV1.json`. App installation, downloaded models, Secure Folder access, and actual model execution remain `UNVERIFIED`. Google AI Edge Gallery is a separate on-device app, not a normal Termux port or a presumed callable service. Do not attempt private inter-app access.
- `python3 tools/samsungFieldKit.py ollama`: explicit, read-only GET requests to **only** `127.0.0.1:11434/api/version` and `/api/tags`. If the service is absent, the result is `NOT_REACHABLE_OR_UNVERIFIED`; nothing is installed, pulled, or started. A reachable local Ollama is **not** proof that LuHm's application bridge exists. Model names/counts are bounded; no prompts, logs, model digests, cookies, keys, or private files are transmitted.

Ollama official API: https://github.com/ollama/ollama/blob/main/docs/openapi.yaml

Google AI Edge Gallery source: https://github.com/google-ai-edge/gallery

Termux installation/signature precautions: https://github.com/termux/termux-app

## Remote Tetsu source forge: bounded 4×4

The `.github/workflows/samsung-field-forge-audit.yml` GitHub PR workflow runs **four independent shards**. Each shard executes:

1. Exact-head checkout and `git diff --check`.
2. Ten no-mutation field-kit self-tests.
3. **Four** serial full `hardSystemAudit200.py` source passes on the same exact checked-out candidate.

This is at most **16 actual 200-check runs (3,200 individual check evaluations)** per completed workflow matrix. Shards are CI workers, **not AI agents**, and repeat count does not imply independent device tests. It uses stock Ubuntu Python and no model downloads, GPU, paid vendors, secrets, or Android install. It does not trigger a release or a deployment.

Use only this bounded four-shard proof, not unbounded CI self-dispatch. A failed check stops the affected shard, preserves its red verdict and requires targeted repair. Source CI succeeds only with observed exact-head output.

## Stop lines

No root, Shizuku, Secure Folder bridge, model installation, APK install/uninstall, `pm clear`, public server binding, production merge, publish, signing, or Crown promotion. No GitHub CI run can operate the Professor's physical Samsung without an independently configured and explicitly authorized device bridge.

No driver interaction in a moving vehicle. Save keyboard steps for when parked.
