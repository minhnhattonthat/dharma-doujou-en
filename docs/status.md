# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translate) done; next 7 (insert, fit, check). Last builds 2026-10-26:
  build/dharma_en.sfc sha1 34049c83... (full English script), build/dharma_marker.sfc sha1 444d4d5b...; smoke ok.
- **Done:**
  - English font: `fonts/en8x16.txt` (drawn, MIT) -> `tools/font.py` draws it into kana slots of both engines' fonts
    (res 1-4 BG3 2bpp; res 34-35 BG1 4bpp) and builds the English tables in code. Engine 2 space = a drawn blank
    glyph (its `{spN}` skips leave stale tiles). D9: fixed 8 px glyphs, no VWF. docs/re/text.md "English font".
  - build.py: `en` strings encode with the English table (fallback `jp`), text spills into bank free space,
    `--marker`, `--qa block:id=Text` overrides. Free space trap-tested.
  - Width gate: docs/re/windows.md + tools/lint.py BOXES. Quiz header, number slots, versus record and tutorial
    order measured this session (windows.md "Fixed-position layouts").
  - Translation: `script/en.tsv` is the only source of `en` (119 strings / 164 units); `tools/tl.py merge` wraps
    story pages (adds pages, D4), keeps `{mode}` at page starts, checks `{sp4}` slot columns, lints. Glossary
    updated; D10 (short mode/rank names, W/L). Reviewer (docs/reviewer-brief.md): Approved after fixes, no
    Critical/Important left. Spot-checked in game: quiz (Novice Q 1, -move limit, Only 1 left), certificate,
    story intro, tutorial.
- **Next:**
  1. Phase 7: romdiff with allowed ranges (`romdiff.py` + build write log), control-code match JP vs EN, lint
     clean (it is). Check msg 36.2 (master, now 2 pages) and msg 30 rows in game.
  2. Still guessed boxes (lint warns 7): password msg 11-13 (find the confirm input for `password_end`), record
     msg 37, end msg 20, qchoice screen 38/39. Measure in phase 7/8 QA.
  3. Minor review items deferred to one polish pass: msg:49.1 "Return our rice balls!!" stiff (28-col fix
     doesn't fit); msg:36.2 "Well done." vs Congratulations (16 > 15 cols); msg:19 loses the mountains/valleys
     image (kept the idiom "ups and downs"); screen:15-17 drop そろえよ; msg:12 "Play again soon!" (16 > 14).
  4. Graphics text (later): G1-G18 in docs/re/graphics.md; 24x24 picture strings 9, 10, 22-29 (tails kept as JP
     pictures); yellow HUD "あと・N手" under the quiz bubble.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Defaults I chose, change if you prefer: D8 "Dharma Dojo", D9 fixed-width font,
  D10 names that fit fixed layouts (Daruma Trek/Drill, How to Play, ranks Novice/Sensei/Expert/Master/Legend,
  versus record W/L).
