# Project Premonition: ROM-era hex/IPS → text-emote → SQL (source-only)

**Scope:** synthetic 32-byte `LTXT` fixture, not a game ROM or Android firmware image. Study only. No bootloader unlock, device I/O, signing, ROM distribution, filesystem binary mutation, or publication.

Old Famicom translation workflow: inspect a legal source image's hex bytes; build a `.tbl` glyph/control-code map; identify fixed strings, bank-relative/little- or big-endian pointers and terminators; repoint if lengths change; build IPS patch; validate in an emulator. Here the fixed layout has pointers `10 00` and `18 00` at offsets 8 and 10 (16-bit little-endian, absolute file offsets), two eight-byte slots at 0x10/0x18, and synthetic codes `F0=happy`, `F1=angry`, `FE=newline`, `FF=end`.

```text
0000: 4c 54 58 54 01 02 00 00 10 00 18 00 00 00 00 00
0010: 41 42 f0 fe 43 ff 00 00 43 20 f1 ff 00 00 00 00
IPS : 50 41 54 43 48 00 00 12 00 01 f1 45 4f 46
```

Classic IPS holds `PATCH`, 3-byte big-endian offset, 2-byte big-endian length, payload (or zero-length RLE) and `EOF`. It does **not** bind a source ROM checksum; this exercise adds an exact SHA-256 guard. No extension/truncate, pointer writes, overlapping records or external bytes accepted. BPS is a modern alternative with source, target and patch CRC32 receipts.

`tools/legacyIpsTextBridge.py` turns a byte change at 0x12 into a typed token change `<EMOTE_HAPPY>` → `<EMOTE_ANGRY>` and projects only text/hash/event metadata into existing local-only `tools/typedSqlStub.py`. SQL **indexes meaning**, rather than becoming a source binary. The future Godot event adapter can map those semantic tokens into animation, dialogue and UI events, subject to separate runtime tests.

Run: `python3 -m unittest discover -s tests -p 'testLegacyIpsTextBridge.py' -v`. Existing typed-four-lane-sql CI is reused, no new workflow. Android AVB/Knox/vendor firmware stays untouched and authoritative, per `doctrine/machineToHumanWizardV1.json`.

**Status:** SOURCE_ONLY / Crown STOP. This does not assert actual Nintendo/Netcom byte maps, real firmware parsing, game engine integration or physical Samsung proof.
