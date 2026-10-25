# Text engine

All verified 2026-10-26 on the original ROM (Mesen watch on the BG3 map buffer, disassembly, full decode + roundtrip).

## Format (verified: decoded every string; `encode(decode())` is byte-exact for all 91)
- Strings are **16-bit little-endian words**. Table `tbl/jp.tbl` keys are the word value in hex.
- Word < 0x8000 = draw tile code N = `w & 0x1FFF` with mode bits 13-14 (handler $80:963E):
  - `0000`: 16x16 glyph, tiles N, N+1 (top) / N+2, N+3 (bottom). Advance 2 tiles. Kana/kanji (codes step 4).
  - `2000`: 8x16 narrow glyph, tile N over N+1. Advance 1 tile. Latin capitals, digits, `!?`, `「`.
  - `4000`: 8x8 tile N in the bottom row, top blank. Advance 1 tile. Small kana, `、。」`; `4000` alone = 8 px space.
  - `6000`: 24x24 picture, 9 tiles N..N+8 (3x3). Advance 3 tiles. Used for big stage art / rank graphics in strings 9, 10, 22-29.
  - Palette override: `$1A27` bit 15 set -> palette `$1A27 & 7` (routine $80:96FA).
- Word >= 0x8000 = control, high byte = code, low byte = argument (handler $80:94C0):
  - `80xx` {end}; `81xx` {nl} (one 8 px tile row down; the story uses three = 24 px line pitch);
  - `82nn` {down:nn} (2*nn rows); `83nn` {wait:nn} (frames); `84xx` {key} (wait for a button);
  - `85xx` {page} (cursor back to the box origin; does NOT clear: the script clears with `{rep:1A} ` spaces);
  - `86nn` {rep:nn} (draw the next word nn times); `87nn` {mode:nn} (stores `$1A46`; seen 01/02 in the story, meaning unknown).
- Drawing goes to a WRAM copy of the BG3 map at `$7E6000` (row*64 + col*2), DMA'd to VRAM word $7400.

## Pointers (verified)
- One table at **$82:A724** (file 0x12724), 16-bit pointers into bank $82, indexed by message id `$1A25`
  (`$80:9604: LDA $82A724,x`). 91 real entries (0-90); entries 91-95 point at 0x13DD2 (past the text, not strings).
- Text block: file 0x127E4 - 0x13DD1 (bank $82, $A7E4-$BDD1), 5,614 bytes. Strings 57-64 share one address.
- Message ids are set by the callers of $80:9604 (search `STA $1A25`).

## Box geometry (from the script, to be measured in game)
- Story box: 26 tiles wide (the clear runs are `{rep:1A}` = 26 spaces), 2 lines of 16 px, line pitch 24 px.
- A narrow glyph is 8 px, so 26 narrow characters per line.

## Engine 2: BG1/BG2 screens (tutorial, quiz mode, ranks; verified: decoded all 98, roundtrip exact)
- Table **$84:DA42** (file 0x25A42), 98 16-bit pointers into bank $84; strings 0x25B06 - 0x26097. Table `tbl/jp2.tbl`.
- Draw routines: `$84:D94C` (to the BG1 map buffer $7E4000) and `$84:D982` (BG2 map buffer $7E5000); string id `$0238`,
  column `$023A`, row `$023C`; palette/priority `$1800` (BG1 via `#$2000|$1800`). Draws the whole string at once.
- Words: `0000|N` 16x16 glyph tiles N, N+1 / N+16, N+17 (4bpp font laid out 16 tiles wide); `2000|N` narrow 8x16
  (N over N+16); `4000|N` 8x8 tile N in the bottom row only (top row untouched); `FFnn` skip nn tiles; `FFFF` end.
- Strings 0-9 are big digits; 57-64 share one address. Font: BG1 tiles 0x200-0x3FF (4bpp).

## Font
- BG3 2bpp, chr base VRAM word $5000, 1,024 tiles, from compressed resources 1-4 (`tools/rle.py`, docs/re/graphics.md).
- Kana and kanji at tiles 0x000-0x2EB (16x16), Latin capitals/digits as 8x16 narrow glyphs at 0x148-0x156, 0x1F8-0x1FE,
  0x2EC-0x2F4, 0x300-0x32B, 0x3F1-0x3FE. 0x330-0x3EF = 24x24 picture tiles.
