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

## Graphics-text survey (tile-drawn Japanese)
Method: every resource 0-79 rendered with `tools/ressheet.py` (4bpp; fonts 1-4 as 2bpp) and read, plus VRAM dumps of
the screens below. "seen" = seen in game; "res" = found in the resource sheets only, screen to confirm with the debug tool.
| # | Screen | Element | Source | State |
|---|---|---|---|---|
| G1 | Title | だるま道場 logo (letters fly in); PRESS START / ©METRO/ITC already English | res 27 (BG tiles) + its tilemap | seen |
| G2 | Mode select (story/training) | 時間制限 / 手数制限 big 24x24 words | font1 picture tiles (res 4) via strings 9, 10 | seen |
| G3 | Stage cards | STAGE n + two 24x24 kanji (place names) | font1 picture tiles (res 4) via strings 22-29 | res |
| G4 | Difficulty menu | やさしい / ふつう / むずかしい | res 36, BG1 tiles 0x220-0x253 (pre-drawn map) | seen |
| G5 | Continue screen after game over | 再度挑戦 / 出直す | res 36, BG1 tiles 0x202-0x21F | seen |
| G6 | Options | おぷしょん header plate | res 37 | seen |
| G7 | Quiz (問答) HUD | あと・N手 / 秒 labels; 五四三二一 秒前 countdown; ちょっとたんま (pause); こうさん / つづける | res 37, res 64 | seen (あと・手) / res |
| G8 | In-game HUD | NEXT, LEVEL, GAME OVER, CLEAR, CLEAR BONUS | graphics, already English | keep |
| G9 | Rank certificate / mastery | 免許 皆伝 plates | res 78 | res |
| G10 | Bottom-right rank plate | 入門 1 | engine-2 strings 52-56 + big digits 0-9 | seen |
| G11 | Stage names (story) | 鎌倉 箱根 浜松 伊勢 滋賀 奈良 大阪 京都, STAGE FINAL | res 36 (big plates) | res |
| G12 | Stack warning | 積み上がり注意!! banner | res 8 | res |
| G13 | 2P battle | 一 三 本 勝 負 (best of 1/3), 勝利 (victory) | res 63, res 77 | res |
| G14 | Attract / demo | 1995年2月発売予定 ("on sale Feb 1995") | res 67 | res |
| G15 | Credits | romaji names (English already) | engine-1 strings 57-90 | text |
Also in ROM: res 31 holds a full Latin 8x8 font (A-Z, a-z), and res 25/59 small English HUD letters.
