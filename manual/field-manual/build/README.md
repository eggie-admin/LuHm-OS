# Manual Forge build lane

`build_manual.py` is the first deterministic build edge for the editable manual source project.

## Validate

```bash
python build/build_manual.py --validate-only
```

Checks chapter, scene, generated-block, and asset references. It verifies sealed image hashes and dimensions and checks that generated doctrine metadata agrees with `book.yaml`.

## Preview

```bash
python build/build_manual.py
```

Writes `dist/preview/index.html` with local copied artwork. Preview generation does not grant print, release, publication, or runtime authority.

## Press rule

A press build stays blocked while the sealed scene plates remain below the requested 300 ppi at 17×11 and until bleed/crop-mark output is separately implemented and inspected.
