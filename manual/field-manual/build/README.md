# Manual Forge build lane

Two validators have different jobs.

## Source structure

```bash
python build/validate_source.py
```

This validates chapter Markdown, scene YAML, doctrine metadata, and the Drive/SHA bindings for sealed art without requiring the image bytes in Git. It writes `build/source-validation-report.json`.

## Full materialized validation

Materialize the sealed Drive art into `assets/scenes/`, then run:

```bash
python build/build_manual.py --validate-only
```

This verifies the actual image bytes, SHA-256 hashes, and dimensions. It is the stronger artifact check.

## Preview

With art materialized:

```bash
python build/build_manual.py
```

The preview does not grant print, runtime, release, signing, or publication authority.

## Press rule

Press remains AMBER while the sealed plates are below the requested 300 ppi at 17×11 and until bleed/crop-mark output is implemented and visually inspected.
