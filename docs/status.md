# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done 2026-10-26: `tools/release.py` built and verified release/Dharma_Doujou_EN_v1.0.zip
  (BPS patch 87,870 bytes + README.txt; patched crc32 2224E204, sha1 b075a46baf04...). Not published: that is the
  user's call (`gh release create` with the zip; see the skill's references/pipeline.md §Publish).
- **Done:**
  - English font, build, width gate, full script (reviewed), phase 7 checks: see git log and docs/re/text.md.
  - Graphics text (docs/re/graphics.md G-rows; edits in tools/gfx_edits.py, applied by `tools/gfx.py gen`, written by
    the build): G1 title DOJO, G2, G4-G7 (HUD, pause plates, training crow countdown), G9, G12, G13, G16-G21 English;
    G22 千両 piece art kept (D11). G3/G10/G15 are text. G11 (place-name plates) and G14 (release date, res 67)
    unused: never shown/decoded in any warp (`tools/debug/reslog.lua` hooks both resource loaders).
  - Quiz pause plate is a BG1 map stream at 0xB050 naming engine-2 kana tiles: `font.PLATES` points it at the
    English glyphs. Credits: Latin-only original strings keep the game's credit glyphs (build.py `pack`).
  - QA tour: `tools/tour.py` -> work/qa/tour (130 sheets); visual-QA gate passed (3 rounds). Any later rebuild:
    re-tour, `qa_gate.py init`, review changed sheets, `check` again (release.py runs `check`).
  - Release: tools/release.py (build, tests, smoke, jp_left on the text banks with --orig, qa gate, checksum, BPS,
    re-apply, zip check); player README template docs/release-readme.txt; repo README filled in.
- **Next (optional polish, for a v1.1):**
  1. Res 37 also holds ちょっとたんま and a small おぷしょん with no screen found (likely unused).
  2. Still guessed boxes (lint warns): password msg 11-13, record msg 37, end msg 20, qchoice screen 38/39.
  3. Minor review items: msg:49.1, msg:36.2, msg:19, screen:15-17, msg:12 (see git history of this file).
- **Open bugs:** none known.
- **Waiting on the user:** publishing v1.0 (zip ready in release/). Defaults I chose, change if you prefer:
  D8 "Dharma Dojo", D9 fixed-width font, D10 names that fit fixed layouts, D11 千両 piece art kept. Title logo: the
  original's gold DHARMA stays, the big だるま道場 became DOJO.
