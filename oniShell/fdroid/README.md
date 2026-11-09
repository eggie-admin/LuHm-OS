# Independent F-Droid repository handoff for ONI SHELL

**Candidate instructions only.** These steps do not create a live repository or issue keys from ChatGPT. A private signing key must never be stored in public Git history, chat prompts, APK assets, CI artifacts or an unencrypted public file server.

The LuHm repository has an existing, independent signed beta pipeline (see `manual/samsung-lite-signed-beta.md`). ONI SHELL is a separate package. Its proposed manually gated workflow reuses the owner's pre-existing **APK** signer secrets, if already correctly provisioned. Those are NOT the F-Droid **index** signing secrets.

## One-time setup on owner-controlled workstation

1. Download the candidate `oni-shell.apk` and `receipt.json` from the private GitHub Actions run. Independently inspect package `art.eggiebagelface.luhmos.onishell`, versionCode, SHA-256 and APK signing certificate with `aapt`, `sha256sum` and `apksigner verify --print-certs`. Compare fingerprints to an independently trusted certificate, **not only** the downloaded receipt. Confirm rights, provenance, privacy and actual device behavior before public distribution.
2. Install trusted `fdroidserver` tools on an owner-controlled Linux machine. Make an F-Droid repository working directory OUTSIDE the checked-out public GitHub project and run `fdroid init` there. This creates the **separate, long-lived repository INDEX signing identity**. Back up its keystore offline and retain the exact public fingerprint for client trust.
3. Edit the PRIVATE `config.yml`: name, description, and `repo_url` must reflect the **real** intended HTTPS URL. Do not publish private config, passwords or keystores.
4. Place the already-signed ONI APK under `repo/art.eggiebagelface.luhmos.onishell_1.apk`. Create/update `metadata/art.eggiebagelface.luhmos.onishell.yml` using the reviewed metadata in this directory. Run `fdroid update --create-metadata`, inspect generated files, then `fdroid update`. This signs the repository index using your separate index signer.
5. With explicit owner publication approval, host **only public** files generated under `repo/` on approved HTTPS hosting (such as a controlled static-site service). Confirm a real signed index, valid TLS, correct repository public fingerprint and APK digest before issuing an F-Droid add-repository link/QR.
6. On the tablet open F-Droid → Settings → Repositories → add the verified HTTPS URL (and compare the fingerprint) → install ONI SHELL. Approve the normal Android Home selector. Test an update signed with **the same APK signer** and a higher versionCode, without uninstalling.

**Do not** run `fdroid publish` on an already signed APK to re-sign it. This candidate is a binary repository: `fdroid update` indexes it, and the existing owner app signature stays intact. Avoid publishing private reference assets.

Until an actual HTTPS URL and signed index are proven, there is **no functioning one-tap F-Droid install**. A placeholder repo URL would be misleading.

Official documentation:
- https://f-droid.org/en/docs/Setup_an_F-Droid_App_Repo/
- https://f-droid.org/docs/Signing_Process/
- https://f-droid.org/en/tutorials/add-repo/

Owner-authorized future host/CI work is a separate release task. Nothing in this source automatically deploys.
