# Project Premonition · LuHmOS.fn.cast

**Status:** source-side voice CAST + real SQL-backed JSON system-variable tuning + independent FINAL_FORM evidence preflight. SQL means **parameterized SQLite JSON1 `json_set`, `json_extract` and `json_valid`**, not merely casting the word CAST to a Boolean. It is not a microphone driver, a production MariaDB connector, a workflow dispatcher, an APK release, or a Crown ceremony.

## Professor's shorthand

Within an explicitly armed `fnCast` context, the aliases `cast`, `cst`, and `c` all resolve to one Boolean CAST intent. Surrounding punctuation such as `!`, `?`, `/`, `;`, `:`, quotes, and `*` is permitted. Whole-command matching rejects substrings, narratives, and appended SQL. The input text is never run as SQL or shell code.

The global `cst` alias still means **currentSourceTruth**, and global `c` still means **continue**. The one-letter `c` inside `fnCast` requires an additional confirmation.

```bash
python3 tools/fnCast.py --voice "CAST!" --context fnCast --armed --source-ref "$(git rev-parse HEAD)"
python3 tools/fnCast.py --voice "cst" --context fnCast --armed --source-ref "$(git rev-parse HEAD)"
python3 tools/fnCast.py --voice "c" --context fnCast --armed --confirm-single-letter --source-ref "$(git rev-parse HEAD)"
```

## SQL: JSON data tuning is the primary action

The voice alias becomes a Boolean **authorization-to-enter-the-tuner** signal. The actual work is typed SQL JSON tuning in `tools/fnCastSqlJson.py`. A SQLite table holds a JSON document, and parameter-bound `json_set` modifies whitelisted JSON paths inside `systemVariables`. `json_extract` confirms the values and `json_valid` verifies the document, in one transaction.

```bash
# SQL JSON1 dry-run: shows exactly what would change, no database written.
python3 tools/fnCast.py --voice "cast" --context fnCast --armed \
  --set 'ui.glassOpacity=0.84' --set 'render.frameCap=90'

# Actual persistent candidate SQL tuning, with explicit apply.
python3 tools/fnCast.py --voice "cast!" --context fnCast --armed \
  --set 'audio.voiceGain=1.35' --set 'gameplay.dialogueSpeed=1.2' --apply-tuning
```

The live parameters are `ui.glassOpacity`, `audio.voiceGain`, `audio.musicVolume`, `gameplay.dialogueSpeed`, and `render.frameCap`. Each uses numeric range and type constraints in `doctrine/fnCastV1.yaml`; unknown paths, SQL fragments, nulls, and malformed JSON stop the transaction. A preview uses memory only. `--apply-tuning` persists a real SQLite database under `build/fnCastTuning/systemVariables.sqlite3`, never to production MariaDB or canonical doctrine. This is a working local-data tuning backend, **not yet connected to the running cockpit's settings UI**.

The resulting receipt contains the before/after JSON SHA-256, changed paths, revision, tuned JSON document and independent Crown state. JSON tuning cannot modify release/Crown guards or escalate Build authority.

## Hard-bound meaning

- **Function:** `LuHmOS.fn.cast`, source `doctrine/fnCastV1.yaml`
- **SQL JSON1 tuning:** actual parameterized SQLite JSON mutations with typed bounds, preview/commit, receipts and rollback. Boolean CAST is only the voice gate.
- **Tier:** `FFS!` resolves to `forFuckSake` hard-audit intensity from the existing Titan trigger contract, not execution privilege
- **Milestone:** `FINAL_FORM`, tied to `doctrine/finalFormPublicReleaseGateV1.json`
- **CROWN_CONDITION:** every required proof must be `PROVEN` and non-null, exact source identities must agree, stable signing and human review must exist, and the independent release audit must pass; logical OR or a numerical shortcut is never enough
- **FINAL_CAST:** the parser returns an evidence receipt. Actual builds still require a separately approved, single-use, exact-source GitHub CAST. Public distribution, installed ChatGPT host state, and Crown are separately authorized.

Current release evidence is incomplete, so an armed voice CAST is valid **intent** but produces `HOLD_FINAL_FORM_EVIDENCE`, not a published binary or approval. Test with `python3 -m unittest discover -s tests -p 'testFnCast*.py' -v`.

Human-facing historical label: `LuHm-OS.fn.cast.yaml`. Canonical repository path: `doctrine/fnCastV1.yaml`, using the current camelHump machine namespace. JSON syntax is deliberately used as a valid YAML 1.2 subset so only Python's standard library is needed and custom YAML tags cannot execute.

## CAST matrix candidate: four by four by four

The case-sensitive product identity is **LuHm-OS: Project Premonition**. An explicit 4×4×4 coordination contract now records 64 *source-only candidate coordinates* without adding 64 workers.

| Axis | Four entries |
| --- | --- |
| CAST stage | `castTesting`, `castProposed`, `castBridge`, `cast` |
| Interaction beat | `hear`, `resolve`, `act`, `verify` |
| Titan audit tier | `technologyFastPath`, `forFuckSake`, `scorchedEarth`, `finalForm` |

The earlier `devCast` and `castDev` spellings are compatibility aliases for `castTesting`. Movement is initial `castTesting`, then same-stage or one-stage forward only. A stage never grants signing or release authority. The `cst` global alias still resolves to currentSourceTruth.

Python `tools/fnCastMatrix.py` validates stage/beat/tier, exact checked-out source SHA, task/scope identity and explicit armed CAST intent. `frontEnd/jquery/luhm.cockpit.js` exposes `$(root).luhmCockpit("castIntent", request)`, which emits only `luhm:cast:intent` for separately validated Python processing. No network or release mutation is performed by that jQuery method.

Example **candidate-only** read:

```bash
python3 tools/fnCast.py --voice "cast" --armed --context fnCast \
  --source-ref "$(git rev-parse HEAD)" \
  --cast-stage castTesting --cast-beat hear --cast-tier technologyFastPath \
  --task-id premonitionCastMatrix --scope-id samsungStudio
```

The returned `castMatrix` is not a runnable action or deployment approval. Python negative tests enumerate all 64 coordinates and illegal stage jumps; the existing SQL JSON1 tuner remains isolated.
