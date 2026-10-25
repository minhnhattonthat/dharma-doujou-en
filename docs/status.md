# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done; next 6 (translate). Last builds 2026-10-26:
  build/dharma_en.sfc sha1 506231c0... (= original, script untranslated), build/dharma_marker.sfc sha1 444d4d5b...;
  both smoke ok. All 43 warps reach their scene on the marker build.
- **Done:**
  - English font: `fonts/en8x16.txt` (drawn, MIT) -> `tools/font.py` draws it into kana slots of both engines' fonts
    (res 1-4 BG3 2bpp; res 34-35 BG1 4bpp) and builds the English tables in code. Engine 2 space = a drawn blank
    glyph (its `{spN}` skips leave stale tiles). D9: fixed 8 px glyphs, no VWF. docs/re/text.md "English font".
  - build.py: `en` strings encode with the English table (fallback `jp` with jp.tbl; identity build still exact),
    text spills into bank free space (msg 0x16910-, screen 0x270A0-), block tail zeroed. `--marker` (id + column
    ruler per text run), `--qa block:id=Text` overrides. Free space trap-tested (tools/debug/freetrap.lua over all
    warps): $82/$84/$9C/$9E tails unread; bank $94 tail is read at boot (not free).
  - Width gate: docs/re/windows.md + tools/lint.py BOXES (lint runs in check). Measured: story 26x2, intro 25,
    subtitle 19, stage 19, master 15x2, choice 8, quiz 20, tutorial 17, header 12, menu 24, prompt 21, certificate 26.
    Fixed-position layouts (msg 30 rank slots at column 11 rows 11/14; msg 37 digits) in windows.md.
  - Marker findings: G16 ぱすわーど plate, G17 対戦成績 header, G18 seal stamp and the G10 quiz rank plate are
    graphics (stay Japanese in the marker build). jp.tbl 013C = ピ fixed.
- **Next:**
  1. Phase 6 translate (~190 strings, small): docs/translator-brief.md and reviewer brief don't exist yet: copy from
     the skill assets and fill in (boxes = docs/re/windows.md, lint = tools/lint.py). Glossary first (place names
     鎌倉 箱根 浜松 伊勢 滋賀 奈良 大阪 京都; ranks 入門 師範 名人 達人 道主; だるま道 = "Way of the Daruma"?).
     Story pages: keep `{key}{page}{rep:1A} {nl}{nl}{nl}{rep:1A} {page}` structure, 26x2 per page, add pages
     rather than cut (D4). Credits typo "EXECTIVE PRODUCER" (msg 57) -> EXECUTIVE.
  2. msg 0-5 must fit the 12-column header plate (story menu) or the plate gets widened; msg 30/37 layouts.
  3. Still guessed boxes (lint warns): password msg 11-13 (find the confirm input for a `password_end` warp:
     Start didn't confirm), rank msg 31-35 / screen 52-56 (where 52-56 show is unknown), record msg 37,
     end msg 20, qchoice screen 38/39. Measure in phase 7/8 QA.
  4. Graphics text (later): G1-G18 in docs/re/graphics.md; 24x24 picture strings 9, 10, 22-29.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (D8 "Dharma Dojo" and D9 fixed-width font are defaults I chose; change them if
  you prefer.)
