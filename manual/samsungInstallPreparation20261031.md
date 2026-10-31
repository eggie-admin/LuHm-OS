# Samsung install preparation 2026-10-31

The ChatGPT mobile cockpit responds, but a signed Android beta and an installable F-Droid repository have not been verified. These are separate install surfaces.

## Observed evidence

- Canonical main inspected: `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`.
- Project Hydra mobile tool responded with `ui://luhm-os/mobile-cockpit-v1.html`; upstream reported `ca369e6925406e9a00008bbc629bb5db67a7d02c`. Device rendering remains unverified.
- Latest owner-signed beta run returned in the main workflow-dispatch history: [39907957047](https://github.com/eggie-admin/LuHm-OS/actions/runs/39907957047), source `bad92d3187f1ab197609a6860b3258d823d38962`. Job `120299363670` failed at Owner-held beta keystore. Logs show four empty signing inputs. This is evidence about that run, not inspection of today's stored secrets.
- [PR 378](https://github.com/eggie-admin/LuHm-OS/pull/378) remains open at `3bbe1c8ee13ed1b2e0bd461e6c2192e7e9609414`; GitHub reported mergeable=false. Its protected-environment and release-baseline changes are not on inspected main.
- Source audit, staging negative controls, offline F-Droid candidate negative controls and signed-beta source audit passed locally on inspected main. No actual APK was built by these tests.
- Private Project Hydra plugin updated from 1.0.15 to 1.0.16, release `pluginrel_6ae6786e227c81918e72c9f7e9906038`. Read-back verified mobile guidance, unchanged App binding and preservation of original file paths. This updates assistant guidance, not Site UI or native Android code.

## Bounded changes

`checkSamsungSigningInputs.py` checks input presence and fingerprint format before Java/Android/Gradle/Godot setup. It neither decodes keys nor attests signer validity, environment policy or release readiness. Diagnostics contain field names only. Existing actual key and APK verification remains required.

`plugins/project-hydra-site-mobile/` is an update overlay for the existing Site-backed plugin. Omitted skills and assets are retained by Plugin Creator; this directory is not a replacement full plugin or Android package. The private plugin identity and audience remain unchanged; the Site's separately observed public audience was not changed.

## Shortest remaining route

1. Reconcile and review protected signing changes in PR 378 with current main and verify the owner-controlled release baseline and signing setup. Do not provision repository-wide secrets as a workaround.
2. Obtain one verified owner-signed `.beta` artifact and receipt, preserving the stable signer. The historical failed run must not be rerun with an obsolete pinned source.
3. Sign the independent F-Droid repository index with its own durable key and verify the chosen HTTPS host, fingerprint and exact APK. No repository URL or QR is ready from this receipt.
4. Confirm device model/Android version and physically test installation, launch and same-signer upgrade. Current source targets SM-X400; an informal device name is not compatibility proof.

No merge, release signing, public F-Droid publication, native install, device acceptance or Crown promotion was performed. The source repair is a proposed candidate; the private plugin guidance update is saved.
