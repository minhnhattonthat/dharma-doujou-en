# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (recon) mostly done; next 2 (debug tool). Last build: none yet (2026-10-26).
- **Done:**
  - Step 0: template, MesenCE 2.2.1 in tools/mesen, guard hook (plugin) blocks the canary, pre-commit runs
    tools/check.py and rejects a failing test, rom.sha1 pinned, smoke boots the original.
  - Recon: both text engines decoded with roundtrip tests (docs/re/text.md): engine 1 = 91 strings at $82:A724
    (BG3 2bpp font), engine 2 = 98 strings at $84:DA42 (BG1 4bpp font). RLE graphics codec (tools/rle.py,
    docs/re/graphics.md). Free space listed. Font sheets: tools/fontsheet.py.
- **Next:**
  1. Phase 2 debug tool: tools/debug/warp.lua + scenes list (main menu, each mode, story stages 1-8 with their
     intro/outro text, quiz, tutorial, 2P battle, continue/game-over, rank certificate, ending, credits, options).
     Find RAM for game mode / stage id with ramsearch.
  2. While touring: finish the graphics survey rows G1, G3, G4, G5, G7, G9 in docs/re/graphics.md (sources unknown:
     difficulty menu, continue menu, quiz counter label, title logo).
  3. Phase 3 identity build (tools/build.py writing nothing must equal the original), phase 4 extract to script/*.json.
  - Engine plan (tentative): English 8x16 narrow font (mode 2000) in both fonts, 26 chars per story line, more pages
    instead of cuts; 24x24 picture tiles redrawn as English for G2/G3.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (D8 "Dharma Dojo" as English title is a default I chose; change it if you prefer.)
