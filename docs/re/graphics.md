# Graphics, compression, free space

## Compression (verified: `tools/rle.py` decodes resources that match VRAM dumps byte for byte)
- Decoder `$80:9D53` / stream decoder `$80:9D97`. Resource table **$87:8000** (file 0x38000): 3-byte entries
  (addr16, bank), ~96 entries, data from 0x38120.
- Resource = header word (address of the even-byte stream, same bank) + odd-byte stream, then the even stream.
  Stream: control c; 00 = end; 01-7F = literal run of 0x80-c bytes; 80-FF = 0x100-c copies of the next byte.
- Two loaders take A = resource index: `$80:9D4E` (to WRAM `$5F:$5D`, also via 4-byte lists `res, bank, addr16`
  ending FFFF, e.g. 0x1C57B) and `$80:8941` (to the NMI DMA buffer). `tools/debug/reslog.lua` logs both.
- Known resources: 1-4 = BG3 dialogue font (tiles 0x000-0x3FF, 4 KB each, VRAM words $5000-$6FFF);
  27 = BG1 tiles 0x200-0x3FF on the menu screen (BG1 4bpp font, guess: also the tutorial font); 50 = BG1 tiles 0-0x1FF there.

## Free space (zero runs at bank ends; trap-tested 2026-10-26: `tools/debug/freetrap.lua` over all 43 warps on
the original logged no reads of the ranges used, except bank $94)
| Bank | File range used | Bytes | State |
|---|---|---|---|
| $82 (main text bank) | 0x16910-0x17FFF | 5,872 | free (no reads); build.py text spill |
| $84 (engine-2 text bank) | 0x270A0-0x27FFF | 3,936 | free (no reads); build.py text spill |
| $94 | 0x0A5980-0x0A7FFF | 9,856 | NOT free: `$80:98BC` reads the whole tail at boot (f130) |
| $9C | 0x0E2E90-0x0E7FFF | 20,848 | free (no reads); font.py resource moves |
| $9E | 0x0F5130-0x0F7FFF | 11,984 | free (no reads); font.py resource moves |
Others listed by the recon scan (most banks have 300-4,000 bytes). The ROM can also grow to 2 MB (header $FFD7 0A -> 0B).

## Graphics-text survey (tile-drawn Japanese)
Method: every resource 0-79 rendered with `tools/ressheet.py` (4bpp; fonts 1-4 as 2bpp) and read, plus VRAM dumps of
the screens below. "seen" = seen in game; "res" = found in the resource sheets only. Warp = `tools/warp.py` scene
that shows it (add `--hold N --mash 60 --shot-every 60` for scenes that come after arrival).
| # | Screen | Element | Source | State | Warp |
|---|---|---|---|---|---|
| G1 | Title | だるま道場 logo (letters fly in) under the gold DHARMA -> DOJO; PRESS START / ©METRO/ITC already English | res 27 (BG1, pal 3) | EN | title |
| G2 | Mode select (story/training) | 時間制限 / 手数制限 big 24x24 words | font1 picture tiles (res 4) via strings 9, 10 | seen | story_limit |
| G3 | Stage cards | STAGE n + two 24x24 kanji (place names) | font1 picture tiles (res 4) via strings 22-29 | seen (STAGE 2 箱根, on the map) | stage2-8 + hold |
| G4 | Difficulty menu | やさしい / ふつう / むずかしい | res 36, BG1 tiles 0x220-0x253 (pre-drawn map) | seen | training_diff |
| G5 | Continue screen after game over | 再度挑戦 / 出直す | res 36, BG1 tiles 0x202-0x21F | seen | gameover, quiz_gameover |
| G6 | Options | おぷしょん header plate | res 37 | seen | options |
| G7 | HUD, pause, crow | あと・N手 (story res 37, quiz res 64 at VRAM $8000: the quiz loads its own copy); pause plate つづける / こうさん (story/training: res 37 tiles; quiz: a BG1 map stream at 0xB050 naming engine-2 kana tiles, font.py PLATES); training crow bubble 五秒前 四 三 二 一 それっ! (res 37 glyphs). ちょっとたんま and a small おぷしょん in res 37: no screen found | res 37, res 64, 0xB050 | EN | stage1_moves, quiz_play, stage1_pause, quiz_pause, training_crow |
| G8 | In-game HUD | NEXT, LEVEL, GAME OVER, CLEAR, CLEAR BONUS | graphics, already English | keep | stage1 |
| G9 | Rank certificate / mastery | 免許 皆伝 plates | res 78 | seen | quiz_master |
| G10 | Bottom-right rank plate | 入門 1 | engine-2 strings 52-56 (rank ligatures, font.py) | EN | quiz_play, quiz_lv2-5 |
| G11 | Stage names (story) | 鎌倉 箱根 浜松 伊勢 滋賀 奈良 大阪 京都 24x24 wood-plate kanji | res 36 | unused: every stage card and plate in the warps (STAGE n-1, FINAL-STAGE) is text or English already | stage2-8 + hold |
| G12 | Stack warning | 積み上がり注意!! banner, BG1 at the top, blinks while the stack is high (training) | res 8 tiles 50-7D (decoded to WRAM $7F:0000 at boot; DMA table $83:C663 entries 1 / 2A copy $7F:0A00 at play start) | EN | training_crow (EN build, A mashed: the run is input-timed) |
| G13 | 2P battle | 一 三 本 勝 負 (best of 1/3), 勝利 (victory) | res 63, res 77 | seen (三本勝負, 1P 勝利) | versus_play, versus_win |
| G14 | Attract / demo | 1995年2月発売予定 ("on sale Feb 1995") | res 67 | unused: never decoded by either loader in any of the warps, title + attract held 12,000 frames (reslog.lua) | - |
| G15 | Credits | romaji names (English already) | engine-1 strings 57-90 | text | credits |
| G16 | Password screen | ぱすわーど header plate | res 81 (the options plate's twin) | EN | password |
| G17 | 2P match record | 対戦成績 header; つづける / やめる = msg 56 (text) and win counts = msg 37 (text) | res 80 | EN | versus_win + hold |
| G18 | Quiz certificate | body = msg 30 + rank names msg 31-35 (text); たいへん よくできました seal stamp | res 66 (OBJ) | EN | quiz_break |
| G19 | Round start | よーい / どん call | raw OBJ tiles 0xCA000 / 0xCA800 | EN | stage1_moves |
| G21 | Story opening picture | slanted road sign かまくら | res 21 (BG1 pal 2) | EN (sheared text) | story_intro |
| G22 | Puzzle piece | 千両 on the treasure-chest piece | piece graphics | kept (D11) | stage2 |
| G20 | Time running low | HURRY UP 急げ HURRY UP banner with crows | res 13 (OBJ) | EN | stage1_hurry |
Also in ROM: res 31 holds a full Latin 8x8 font (A-Z, a-z), and res 25/59 small English HUD letters.
