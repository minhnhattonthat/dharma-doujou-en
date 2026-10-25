# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise. Header: LoROM, FastROM ($FFD5 = $30), 1 MB.

| File | Covers | State |
|---|---|---|
| text.md | both text engines: encoding, control codes, pointer tables, box size, fonts | verified (roundtrip) |
| graphics.md | RLE compression, resource table, free space, graphics-text survey | compression verified; survey partial |

Gotchas:
- Text is 16-bit tile codes, not bytes: `relsearch.py` finds nothing. Trace the BG map buffer writer instead.
- Mesen run timing drifts between runs (random SRAM / RNG): wait on screens, not frame counts.
