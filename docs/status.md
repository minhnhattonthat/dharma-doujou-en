# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done; next 4 (extract). Last build: build/dharma_en.sfc 2026-10-26, sha1 506231c0...
  (= original), smoke ok.
- **Done:**
  - Identity build: `tools/build.py` unpacks both text blocks and repacks them (id order, original aliases kept as
    one copy, pointer tables rewritten, checksum), logs every write to build/writes.txt and runs romdiff on it.
    tests/test_build.py: identical to the original; an edited string shifts the rest and reads back; overflow fails.
    Equal strings at distinct addresses exist, so packing dedupes by the original's shared pointers, not by text.
  - Step 0: template, MesenCE 2.2.1 in tools/mesen, guard hook (plugin) blocks the canary, pre-commit runs
    tools/check.py and rejects a failing test, rom.sha1 pinned, smoke boots the original.
  - Recon: both text engines decoded with roundtrip tests (docs/re/text.md): engine 1 = 91 strings at $82:A724
    (BG3 2bpp font), engine 2 = 98 strings at $84:DA42 (BG1 4bpp font). RLE graphics codec (tools/rle.py,
    docs/re/graphics.md). Free space listed. Font sheets: tools/fontsheet.py.
  - Debug tool: `tools/warp.py` + `tools/debug/{scenes,warp,modelog}.lua`; 43 scenes from a cold boot (title,
    menu, attract, every menu/submenu, story intro, map, stages 1-8 via outro+map+card, game over/continue,
    ending, credits, training, quiz problems/rank scenes/certificate/免許皆伝, 2P play/victory/record, tutorial,
    options, password). RAM and state machine: docs/re/debug.md. Graphics survey rows now name their warp.
- **Next:**
  1. Phase 4 extract: dump script/{msg,screen}.json (id, jp, en, ptr; dump never clobbers en), build.py reads
     `en` (fallback jp) into `build(texts=...)`; roundtrip test from JSON; text ranges fully covered
     (msg 0x127E4-0x13DD1, screen 0x25B06-0x2609B). Text growth will need free space: blocks are full.
  2. Graphics survey: locate sources of G16 (ぱすわーど plate), G17 (対戦成績, つづける/やめる), G18 (免状
     certificate: text or graphics?); confirm G11 stage-name plates, G14 attract release date, STAGE FINAL with
     `warp.py stage8 --hold 3000 --mash 60 --shot-every 60` / `attract --hold 3000`.
  - Engine plan (tentative): English 8x16 narrow font (mode 2000) in both fonts, 26 chars per story line, more pages
    instead of cuts; 24x24 picture tiles redrawn as English for G2/G3.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (D8 "Dharma Dojo" as English title is a default I chose; change it if you prefer.)
