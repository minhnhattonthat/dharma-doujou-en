# Visual-QA reviewer brief - Dharma Dojo (だるま道場, SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's sheets: `work/qa/tour_jp/`, same ids (not every scene has one; frames can be offset).
- `glossary.md` for names and terms.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" SHEET.png --crop x,y,w,h --zoom 3 --out work/qa/vq/<name>.png`
  and read that (write scratch images only under `work/qa/vq/`).
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png --out ...`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (text or graphics: plates, banners, bubbles, HUD labels);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp; black or faded frames between scenes;
- anything identical in the original's sheet;
- the font is a fixed 8 px width by design (docs/decisions.md D9): tight letter spacing is not a bug;
- the HUD number is drawn by the game right before the label, so "2left" / "5left" under "Moves" has no space;
- the credits and the title's PRESS START / (c) METRO line were already English in the original;
- the gold "DHARMA" above the big "DOJO" title logo is the original's own lettering (title = "Dharma Dojo");
- "Novice Q 1" style quiz headers (rank, then the problem number at a fixed column; D10);
- the versus record's W / L labels (D10).

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
