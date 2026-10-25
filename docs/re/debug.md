# Scene state machine and debug-tool RAM

Verified 2026-10-26 on the original ROM (disassembly + `tools/debug/modelog.lua` logs + warps in `tools/warp.py`).

## Main loop (verified)
- `$80:80C4` loop calls `$80:A0EA` each frame: `$17` = mode, `$19` = sub-state; table `$80:A129` (15 x 3-byte
  pointers) -> per-mode tables of 3-byte handler pointers indexed by `$19`. `$021C == $3000` = soft reset.

| Mode | Table | What (seen) |
|---|---|---|
| 0 | $80:A156 | boot logos, title (sub 4 = title idle, waits for Start) |
| 1 | $80:B21D | main menu; sub 1 = menu and its submenus (new/password, time/move limit, character) |
| 2 | $80:C257 | staff credits (after the ending) |
| 3 | $80:CA25 | story opening (picture scenes + text) |
| 4 | $80:D937 | after "出直す" on the continue screen (guess: back to menu) |
| 5 | $80:DE01 | options |
| 6 | $80:E3DB | tutorial (入門編) |
| 7 | $85:8000 | story map; shows the STAGE n card before play |
| 8 | $80:E5CD | 2P vs (ふたりで対決): sub 1 三本勝負 banner, sub 2 play, sub 3 after a round; also the attract demo |
| 9 | $80:E8A8 | story play; sub 1 = playing, sub 3/4 = continue screen (再度挑戦 / 出直す) |
| 10 | $80:EDC3 | training (修行編): sub 1 = difficulty menu, then play |
| 11 | $80:EF41 | quiz (問答) play |
| 12 | $84:A2EF | guess: 2P battle (set from bank $84 code) |
| 13 | $85:86CA | scenes, 3 subs each: $15 story outro of stage `$04B8`-1 (ending when `$04B8`=8); quiz $00/$03/$06/$09/$0C after problems 5/15/25/35/45 (scenery interlude), $0F after 10/20/30/40 (免状 certificate), $12 after 50 (免許皆伝); $1B 2P victory (勝利), then $18 対戦成績 record + つづける/やめる |
| 14 | $85:85DE | not seen |

## Variables (verified unless marked)
| RAM | Meaning |
|---|---|
| `$781C` | main-menu cursor 0-5 (story, training, quiz, 2P, tutorial, options); copied to `$04C6` on A. Reset to 0 when the menu opens: poke it 20 frames later. |
| `$04C6` | chosen menu item -> mode via `$80:B3ED` (3,10,11,8,6,5) |
| `$04B4` | 0 time limit, 1 move limit (quiz forces 1) |
| `$04B8` | story stage 0-7 (8 = all cleared -> ending) |
| `$04B6` | round within the stage 0-2 |
| `$04C4` | puzzle index: story `$04B8*9 + $04B6*3 + random`; quiz problem 0-49 (table `$82:C002`) |
| `$024E` | round result, polled by play sub 1: 2 = cleared, other non-zero = lost; also menu results |
| `$1CF8` | attract demo running |
| `$1A62` | started from a password (skips the random pick) |
| `$0238` | last menu/BG string id drawn; inside mode 1 it tells the submenus apart: $A1 main menu, $A5 new game / password, $A3 character pick (どっちでプレイするの?), $A4 time / move limit |
| `$0218`/`$021A` | pad 1/2 new presses, `$021C`/`$021E` held (read from $4218/$421A at `$80:85EB`) |
| `$190A`/`$190C` | 2P wins of P1/P2; 2 wins ends the match |

## Warps (tools/debug/scenes.lua)
- Story stage N: play stage 1 from "new game", then poke `$04B8`=N-2, `$04B6`=2, `$024E`=2: the game itself
  plays the stage N-1 outro, map, STAGE N card and stage N.
- Ending: same with `$04B8`=7: map, ending scene, credits (mode 2).
- Quiz: in quiz play poke `$04C4`=N-1, `$024E`=2 = "problem N cleared": the game goes to table `$80:F123`
  entry N (next problem, or a mode 13 scene).
- 2P win: in play poke `$190A`=2, `$024E`=1.
- Pad 2: under MesenCE `--testRunner` there is no port-2 device (`emu.setInput(.., 1)` lands on pad 1), so
  warp.lua returns pad-2 bits from a read callback on `$421A/B`. Mesen read callbacks may return a value to
  override the read.
- Game over: hold no useful input (story: mash Down) until the stack tops out; the continue screen is sub 4.
