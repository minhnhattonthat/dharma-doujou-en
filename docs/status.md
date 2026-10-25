# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check) done; next 8 (QA in the emulator). Last builds 2026-10-26:
  build/dharma_en.sfc sha1 34049c83... (full English script), build/dharma_marker.sfc sha1 444d4d5b...; smoke ok.
- **Done:**
  - English font: `fonts/en8x16.txt` (drawn, MIT) -> `tools/font.py` draws it into kana slots of both engines' fonts
    (res 1-4 BG3 2bpp; res 34-35 BG1 4bpp) and builds the English tables in code. Engine 2 space = a drawn blank
    glyph (its `{spN}` skips leave stale tiles). D9: fixed 8 px glyphs, no VWF. docs/re/text.md "English font".
  - build.py: `en` strings encode with the English table (fallback `jp`), text spills into bank free space,
    `--marker`, `--qa block:id=Text` overrides. Free space trap-tested.
  - Width gate: docs/re/windows.md + tools/lint.py BOXES.
  - Translation: `script/en.tsv` is the only source of `en` (119 strings / 164 units); `tools/tl.py merge`.
    Reviewer: Approved after fixes.
  - Phase 7 checks (all in build/check): every write logged and romdiff-checked, and must sit inside
    `tools/ranges.txt` (build fails otherwise); lint: control codes JP == EN except layout ({nl} {page} {key} {rep}
    {sp} {down}; {key}/{page} may grow), Japanese with no English is an error (aliased ids count once). Stale-reader
    scan: strings reached only via the pointer tables (docs/re/text.md). `jp_left.py` on the text ranges: 0 runs
    (cmd: `jp_left.py build/dharma_en.sfc --tbl tbl/jp.tbl --le16 --range 127E4-13DD1 --range 16910-17FFF`, and
    jp2.tbl with 25B06-2609B, 270A0-27FFF). In game: msg 36 master (3 pages) and msg 30 certificate ok
    (warp quiz_master / quiz_break).
- **Next:**
  1. Phase 8: QA tour of changed scenes via `tools/warp.py` (scene list in tools/debug/scenes.lua), contact sheets,
     `qa_gate.py` manifest + visual-qa subagents until `qa_gate.py check` exits 0. Graphics text rows (G1-G18 in
     docs/re/graphics.md) are phase 8's done-when too: they are still Japanese, so phase 8 includes redrawing them.
  2. Still guessed boxes (lint warns 7): password msg 11-13 (find the confirm input for `password_end`), record
     msg 37, end msg 20, qchoice screen 38/39. Measure in phase 8 QA.
  3. Minor review items deferred to one polish pass: msg:49.1 "Return our rice balls!!" stiff (28-col fix
     doesn't fit); msg:36.2 "Well done." vs Congratulations (16 > 15 cols); msg:19 loses the mountains/valleys
     image (kept the idiom "ups and downs"); screen:15-17 drop そろえよ; msg:12 "Play again soon!" (16 > 14).
  4. Graphics text: G1-G18 in docs/re/graphics.md; 24x24 picture strings 9, 10, 22-29 (tails kept as JP
     pictures); yellow HUD "あと・N手" under the quiz bubble; 免許皆伝 plate in the master scene.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Defaults I chose, change if you prefer: D8 "Dharma Dojo", D9 fixed-width font,
  D10 names that fit fixed layouts (Daruma Trek/Drill, How to Play, ranks Novice/Sensei/Expert/Master/Legend,
  versus record W/L).
