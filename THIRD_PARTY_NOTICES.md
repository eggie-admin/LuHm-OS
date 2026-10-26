# Third-party notices and asset-rights status

**Scope:** LuHm OS public-source inventory; candidate documentation, not a legal clearance or release authorization.

## Repository source license

The root [LICENSE](LICENSE) contains the GNU General Public License, version 3. The ChatGPT plugin manifest declares `GPL-3.0-only`. Do **not** replace this existing source license during first-install setup. A source-code license does not establish that every contributed photograph, character, sound, font, model, sample, or donated asset is owned by the publisher.

## Vendored browser libraries

| Component | Version recorded in repo | Notice retained | Release rule |
| --- | --- | --- | --- |
| jQuery | 3.7.1 | [jquery-LICENSE.txt](host/harness/jquery-LICENSE.txt), OpenJS MIT terms | Ship its copyright/license with distributions that include it; keep version pinned. |
| jQuery UI | 1.14.2 | [jquery-ui-LICENSE.txt](host/harness/jquery-ui-LICENSE.txt), OpenJS MIT terms plus demo/third-party exceptions | Keep the existing notice, including exceptions, and review bundled third-party components. |
| Vue | Optional, **not bundled by default** in the current cockpit policy | [libraryPolicy.json](host/harness/libraryPolicy.json) | Do not add to production before separate lockfile/notice review. |
| Godot Engine | Project uses Godot 4.7.2 tools/export lanes in source | Upstream Godot MIT license and third-party engine notices | If distributing Godot engine binaries/templates, include the exact version's notices/required attribution in the release package. |

The existing [frontEnd/package-lock.json](frontEnd/package-lock.json) and [frontEnd/package.json](frontEnd/package.json) are the dependency inputs. Run the existing pinned build checks; do not pull unreviewed third-party CDNs at runtime. Approved self-hosted Cloudflare delivery through a branded `/assets/` path does not eliminate attribution obligations.

## Art, characters, models, music and assets

Authoritative **identity** is [organizationBrandRegistryV1.json](doctrine/organizationBrandRegistryV1.json) and [CHARACTER_CANON_V1.json](game/canon/CHARACTER_CANON_V1.json). Authorized **release eligibility** is per asset, not implied by a manifest entry, contributor name, public Git hosting, or the repo GPL license. The [assetCatalog.json](plugins/luhm-os/assets/assetCatalog.json) includes original draft candidates marked `publicApproved:false`. Retain that restriction.

Private Drive references, extracted donor art, celebrity likenesses, game or anime references, song recordings and protected character source art **must not** be copied into public packages without a verified, asset-specific license, chain of permission and Professor's publication approval. Drawn inspiration does not grant reuse rights.

The separate `scripts/adventures/ghostsOfAramoor/PROVENANCE.md` documents a CC BY-SA 4.0 source case. Preserve its required attribution and ShareAlike obligations on qualifying derivatives. Do not imply the repo's blanket GPL license replaces this source-specific license.

## Before each public package

1. Generate an exact list of files actually contained in the release, and their hashes.
2. Attach notices for **all shipped** vendored dependencies, engines and assets, with their actual versions.
3. Mark rights for each shipped visual/audio/model asset `approved` or `held`; fail the public gate on `unknown`, `referenceOnly` or `publicApproved:false`.
4. Verify README, privacy, terms, security reporting, license and accessibility links in the **built** package, not just source.
5. Confirm the package contains no private media, secrets, identifiers, API credentials or unauthorized generated art.

**Status: INVENTORY PRESENT, RELEASE-WIDE THIRD-PARTY AND ART CLEARANCE NOT YET PROVED.** This document does not relicense third-party files or claim ownership.
