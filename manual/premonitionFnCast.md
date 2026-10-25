# Project Premonition · LuHmOS.fn.cast

**Status:** functioning source-side voice-transcript intent parser and read-only FINAL_FORM Crown evidence preflight. This is not a microphone driver, an SQL execution engine, a GitHub Actions build dispatcher, an APK release, or a Crown ceremony.

## Professor's shorthand

Within an explicitly armed `fnCast` context, the aliases `cast`, `cst`, and `c` all resolve to one Boolean CAST intent. Surrounding punctuation such as `!`, `?`, `/`, `;`, `:`, quotes, and `*` is permitted. Whole-command matching rejects substrings, narratives, and appended SQL. The input text is never run as SQL or shell code.

The global `cst` alias still means **currentSourceTruth**, and global `c` still means **continue**. The one-letter `c` inside `fnCast` requires an additional confirmation.

```bash
python3 tools/fnCast.py --voice "CAST!" --context fnCast --armed --source-ref "$(git rev-parse HEAD)"
python3 tools/fnCast.py --voice "cst" --context fnCast --armed --source-ref "$(git rev-parse HEAD)"
python3 tools/fnCast.py --voice "c" --context fnCast --armed --confirm-single-letter --source-ref "$(git rev-parse HEAD)"
```

## Hard-bound meaning

- **Function:** `LuHmOS.fn.cast`, source `doctrine/fnCastV1.yaml`
- **SQL:CAST(boolean):** type/intent conversion only, not an actual SQL query
- **Tier:** `FFS!` resolves to `forFuckSake` hard-audit intensity from the existing Titan trigger contract, not execution privilege
- **Milestone:** `FINAL_FORM`, tied to `doctrine/finalFormPublicReleaseGateV1.json`
- **CROWN_CONDITION:** every required proof must be `PROVEN` and non-null, exact source identities must agree, stable signing and human review must exist, and the independent release audit must pass; logical OR or a numerical shortcut is never enough
- **FINAL_CAST:** the parser returns an evidence receipt. Actual builds still require a separately approved, single-use, exact-source GitHub CAST. Public distribution, installed ChatGPT host state, and Crown are separately authorized.

Current release evidence is incomplete, so an armed voice CAST is valid **intent** but produces `HOLD_FINAL_FORM_EVIDENCE`, not a published binary or approval. Test with `python3 -m unittest discover -s tests -p testFnCast.py -v`.

Human-facing historical label: `LuHm-OS.fn.cast.yaml`. Canonical repository path: `doctrine/fnCastV1.yaml`, using the current camelHump machine namespace. JSON syntax is deliberately used as a valid YAML 1.2 subset so only Python's standard library is needed and custom YAML tags cannot execute.
