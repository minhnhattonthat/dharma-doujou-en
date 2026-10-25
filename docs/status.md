# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done; next 5 (engine spike + marker build). Last build: build/dharma_en.sfc 2026-10-26,
  sha1 506231c0... (= original, script untranslated), smoke ok.
- **Done:**
  - Extract: `tools/dump.py` -> script/msg.json (91) and script/screen.json (98): id, ptr, jp, en ("" = untranslated),
    alias (57-64 share id 57's copy; translate 57 only), note (picture tiles, digits, credits, empty). build.py reads
    `en` (LANG constant), falling back to `jp`. tests/test_script.py: jp re-encodes to the ROM bytes at ptr, strings
    cover both text ranges with no gap, untranslated script builds the original, dump --force keeps en.
  - Identity build: `tools/build.py` repacks both text blocks (id order, aliases kept, pointer tables rewritten,
    checksum), logs writes to build/writes.txt, runs romdiff. tests/test_build.py.
  - Step 0, recon (docs/re/text.md, graphics.md), debug tool (`tools/warp.py`, 43 scenes, docs/re/debug.md).
- **Next:**
  1. Phase 5: English font. Both engines already have 8x16 narrow glyph mode (2000|N): draw A-Z a-z punctuation
     into free narrow-tile slots of font 1 (BG3 2bpp, res 1-4, tools/rle.py) and font 2 (BG1 4bpp), add an en
     table per engine (tbl/en.tbl, en2.tbl), make build encode `en` with it. Text blocks are full: find free space
     in banks $82/$84 (or move a block; pointers are 16-bit per bank) before English grows.
  2. Marker build: every string -> `[id]`-style marker; tour all 43 warps; confirm which survey rows are text:
     likely G16 ぱすわーど = msg 7/11, G17 つづける/やめる = msg 56, G18 免状 body = msg 30 (title maybe graphics).
     Also STAGE FINAL / G11 / G14 confirmation (`warp.py stage8 --hold 3000 --mash 60 --shot-every 60`).
  3. Width gate: measure story box (26 tiles), menu, screen-2 lines in game before any translator dispatch.
  - Credits typo "EXECTIVE PRODUCER" (msg 57): fix to EXECUTIVE when translating.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (D8 "Dharma Dojo" as English title is a default I chose; change it if you prefer.)
