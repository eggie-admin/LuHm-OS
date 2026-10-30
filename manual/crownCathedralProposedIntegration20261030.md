# Crown Cathedral Proposed Integration | 2026-10-30

Status: SOURCE-ONLY STAGED ON PR #460. No protected-main mutation, live build,
runtime deployment, agent activation or release. Crown STOP.

## One spine, not five overlapping platforms

Private owner-controlled Blender masters / original art in Drive
  -> rights/provenance and SHA-256 at a logical assetId
  -> isolated headless Blender conversion with scripting disabled
  -> content-addressed glTF 2.0 GLB
  -> Godot 4 headless scene import and runtime tests
  -> private playable candidate.

Independent frontend route: pinned npm manifests/lockfiles
  -> exact npm ci with install scripts disabled
  -> Vite/Babylon/Vue **only in the isolated glassWorld prototype**
  -> reviewed static JS/CSS for browser/WebView; canonical frontend separately pins jQuery.
  -> no Node, Python, Blender or dpkg interpreter required inside Android APK.

Headless control route: Python standard library + SQLite STRICT, parameterized
typed JSON API, local job and SHA receipts; SQLite stores metadata and logical
pointers, NEVER binary 3D/MP4 or private Drive IDs. No SQL server on Android.
Versioned migrations must have transaction, backup, rollback and restore proof.

Package boundary: npm produces browser assets. dpkg-deb optionally packages
approved **first-party headless Linux** service and static output. It does not
install npm dependencies on Android, and does not make npm a Debian package
manager. Godot/Gradle owns Android packaging. No privileged dpkg maintainer
scripts or auto host package upgrades.

## Hardest-first 4 x 4

Risk       | 3D scenes / rigs | custom resources | npm / JS | SQLite / Linux
Identity   | editable .blend, GLB SHA | assetId/rights/parent | exact lockfile | migration/version/ref
Security   | no donor script execution | archive bounds/quarantine | no CDN/hooks | least privilege/no secret
Runtime    | skeleton/IK/physics/import | Godot .tres/.res owned by Godot | WebView input/FPS | offline API/rollback
Proof      | Blender+Godot actual run | hash/license/review receipt | bundle + browser run | SQL + deb smoke

Blender is the editable asset authority, not the game executor. Unsupported
Geometry Nodes, materials and procedural rig effects must be baked or recreated
before glTF export; Godot-specific resources/scripts remain Godot-side.
Tetsu and Kaji are existing source/compile role labels, not independently proven
running agents. Lum, Urd, Belldandy, Skuld and Yume provide supervised review
roles; corporate roleplay or Witching Hour does not supply an approval token.

## Source selection and vendor mutation

Prefer browser/engine/OS APIs before copying vendor implementations. Fork only
from explicitly identified official upstream release and source tag, after
license, NOTICE, SPDX, redistribution, integrity, maintenance and exact-SHA
review. MIT/BSD/ISC/Apache-2.0 can be good candidates; GPL/LGPL/MPL code is
also modifiable, but its obligations do not vanish. The root LuHm-OS GPL-3.0
cannot be relabeled wholesale Apache. Unknown, proprietary, unlicensed and
private-reference art stays quarantined.

## Actual automation, without another workflow

The existing Unified Goddess Orchestra workflow covers packages/unified-ops/**
and runs npm test. This candidate adds a read-only, fail-closed source preflight
and negative tests, not a new Actions workflow.

On the candidate branch, with an exact candidate commit SHA:
  cd packages/unified-ops
  npm ci --ignore-scripts --no-audit --no-fund
  npm test
  npm run plan:cathedral -- EXACT_40_CHARACTER_SHA

Plan source PASS means required manifests, private npm packages, exact direct
versions/lockfile integrity and no-auto-promotion flags were observed. It is
NEVER Blender/Godot runtime, rights clearance, device proof or release GREEN.

## Promotion path

1. Do not bulk-import Drive or merge unrelated historical luhmos/testing,
   proposed, beta and stable branches. Reconcile by reviewed source/files.
2. Choose one original, rights-cleared Cathedral environment and one original
   character. Preserve private .blend; stage only validated GLB and manifest.
3. Run sandboxed Blender, headless Godot import and real playable/input tests
   on the same exact source/asset hashes. Benchmark scene size and frame pacing.
4. Build reviewed static npm assets separately. Run isolated SQLite schema and
   backup/rollback tests; optional dpkg package on an ephemeral Linux worker.
5. Review the actual #448 through #460 stack, parallel #447 diff and current
   main changes. Integrate small reviewed units; never blind-merge 146 files.
6. Proposed means source checks, isolated artifacts and review, not public
   deployment. A future current-main owner-authored /cast command needs its
   own milestone and exact main SHA.
7. Private beta needs signer custody, same-artifact install and launch,
   Godot/device acceptance and privacy/rights receipts. Public Crown is a
   separate explicit Professor decision.

Existing blockers: private asset permissions need live verification; no
universal 3D import proof; no current signed physical acceptance; host and
ChatGPT mount cannot be inferred from source CI. CROWN STOP.
