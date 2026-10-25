# Graphics, compression, free space

## Compression (verified: `tools/rle.py` decodes resources that match VRAM dumps byte for byte)
- Decoder `$80:9D53` / stream decoder `$80:9D97`. Resource table **$87:8000** (file 0x38000): 3-byte entries
  (addr16, bank), ~96 entries, data from 0x38120.
- Resource = header word (address of the even-byte stream, same bank) + odd-byte stream, then the even stream.
  Stream: control c; 00 = end; 01-7F = literal run of 0x80-c bytes; 80-FF = 0x100-c copies of the next byte.
- Known resources: 1-4 = BG3 dialogue font (tiles 0x000-0x3FF, 4 KB each, VRAM words $5000-$6FFF);
  27 = BG1 tiles 0x200-0x3FF on the menu screen (BG1 4bpp font, guess: also the tutorial font); 50 = BG1 tiles 0-0x1FF there.

## Free space (candidates: zero runs at bank ends, not yet trap-tested)
| Bank | File range | Bytes |
|---|---|---|
| $82 (main text bank) | 0x16900-0x17FFF | 5,888 |
| $84 (engine-2 text bank) | 0x2709E-0x27FFF | 3,938 |
| $94 | 0x0A5980-0x0A7FFF | 9,856 |
| $9C | 0x0E2E8D-0x0E7FFF | 20,851 |
| $9E | 0x0F5121-0x0F7FFF | 11,999 |
Others listed by the recon scan (most banks have 300-4,000 bytes). The ROM can also grow to 2 MB (header $FFD7 0A -> 0B).

## Graphics-text survey (tile-drawn Japanese; status per row)
| # | Screen | Element | Source | State |
|---|---|---|---|---|
| G1 | Title | だるま道場 logo, letters fly in | BG graphics (resource TBD) | seen, untranslated |
| G2 | Mode select (story/training) | 時間制限 / 手数制限 big 24x24 words | font1 picture tiles 0x330-0x35F via strings 9, 10 | seen |
| G3 | Stage cards | STAGE n + two 24x24 pictures (stage name kanji?) | font1 picture tiles 0x366-0x3EC via strings 22-29 | not yet seen |
| G4 | Difficulty menu | やさしい / ふつう / むずかしい | unknown (not in either text table) | seen |
| G5 | Continue screen after game over | 再挑戦 / やめる-like menu | unknown (kanji not in fonts) | seen, unread |
| G6 | Options | おぷしょん header plate | BG graphics | seen |
| G7 | Quiz (問答) HUD | あと・N手 / N秒 counter label (yellow) | unknown (sprites?) | seen |
| G8 | In-game HUD | NEXT, LEVEL, GAME OVER | graphics, already English | keep |
| G9 | Rank certificate | 段位認定状 frame text | string 30 (text) + frame graphics TBD | not yet seen |
| G10 | Bottom-right rank plate | 入門 1 | engine-2 strings 52-56 + big digits 0-9 | seen |
| G11 | Story intro pictures | none seen yet | - | - |
| G12 | Credits | romaji names (English already) | engine-1 strings 57-90 | text |
Rows marked TBD are completed in phase 2, when the debug tool reaches every screen.
