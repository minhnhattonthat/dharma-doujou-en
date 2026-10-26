# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator) done: `qa_gate.py check` exits 0 (130 sheets, 3 review rounds). Next: phase 9.
  Last build 2026-10-26: build/dharma_en.sfc sha1 b075a46baf04...
- **Done:**
  - English font, build, width gate, full script (reviewed), phase 7 checks: see git log and docs/re/text.md.
  - Graphics text (docs/re/graphics.md G-rows; edits in tools/gfx_edits.py, applied by `tools/gfx.py gen`, written by
    the build): G1 title DOJO, G2, G4-G7 (HUD, pause plates, training crow countdown), G9, G12, G13, G16-G21 English;
    G22 千両 piece art kept (D11).
    G3/G10/G15 are text. G11 (place-name plates) and G14 (release date, res 67) unused: never shown/decoded in any
    warp (`tools/debug/reslog.lua` hooks both resource loaders).
  - Quiz pause plate is a BG1 map stream at 0xB050 naming engine-2 kana tiles: `font.PLATES` points it at the
    English glyphs.
  - QA tour: `tools/tour.py` (all scenes in tools/debug/scenes.lua) -> work/qa/tour (130 sheets); manifest
    work/qa/manifest.tsv; chunks work/qa/chunks; brief docs/visual-qa-brief.md; verdicts work/qa/verdicts.
- **Next:**
  1. Visual-QA gate passed. Any later rebuild: re-tour, `qa_gate.py init`, review changed sheets, `check` again.
  2. G12 stack warning: done (STACK TOO HIGH!!, seen in training_crow). G21 story road sign and the credits
     EXECUTIVE PRODUCER (original credit glyphs, build.py `pack`) fixed in QA round 2.
  3. Res 37 also holds ちょっとたんま and a small おぷしょん with no screen found (likely unused).
  4. Still guessed boxes (lint warns): password msg 11-13, record msg 37, end msg 20, qchoice screen 38/39.
  5. Minor review items for one polish pass: msg:49.1, msg:36.2, msg:19, screen:15-17, msg:12 (see git history of
     this file for detail).
  6. Phase 9: release script runs `qa_gate.py check`; jp_left; patch + verify; README hashes.
- **Open bugs:** none known beyond the QA gate.
- **Waiting on the user:** nothing. Defaults I chose, change if you prefer: D8 "Dharma Dojo", D9 fixed-width font,
  D10 names that fit fixed layouts. Title logo: the original's gold DHARMA stays, the big だるま道場 became DOJO.
