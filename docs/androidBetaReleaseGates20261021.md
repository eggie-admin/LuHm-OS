# Android beta release gates (draft, fail closed)

Status: CROWN STOP. This document does not authorize signing, publishing, or merging.

## Canonical lanes
testing -> proposed -> beta -> betaLts. No promotion on CI green alone.

## Required before owner-signed private candidate
- Configure a GitHub protected environment for release signing with required human reviewer(s), no self-approval, and restricted deployment branches.
- Scope durable signing secrets to that environment, not repository-wide.
- Confirm an existing signing certificate is reused for upgrades. Never rotate a distributed beta signer automatically.
- Require an exact reviewed source commit and owner authorization.

## Required before public upgrade-safe beta
- Confirm fixed application ID `art.eggiebagelface.luhmos.beta` across releases.
- Verify versionCode strictly greater than the previously distributed versionCode, not merely derived from GITHUB_RUN_NUMBER.
- Verify signing certificate SHA-256 against the previous distributed release.
- Record signed APK SHA-256, source SHA, workflow run, signer fingerprint, versionCode, provenance, and package identity.
- Run actual device clean-install and in-place upgrade smoke tests from the prior distributed beta; retain evidence and results.
- Independently review privacy, rights, distribution destination and rollback plan.
- Keep F-Droid listing, public ChatGPT plugin access, and public prerelease publishing unclaimed until externally verified.

## Observed gap as of 2026-10-21
The inspected `.github/workflows/samsung-lite-signed-beta.yml` does not declare a protected `environment` on the build job. Its versionCode uses `200000 + GITHUB_RUN_NUMBER` without a previous-distributed-version comparison. The receipt explicitly sets `deviceProof=false` and `betaUpgradeProof=false`.

## Promotion rule
Any missing or unverifiable item above => STOP. No automatic merge, signing, production deploy, or public release.
