# Translator brief - Dharma Dojo (SNES, 1994)

You translate or fix part of the Japanese script of Dharma Dojo, a daruma-otoshi puzzle game: a folk-tale story
(a cheeky young monk and a spirited shrine maiden race to clear monsters off the roads), a quiz mode run by an old
master, and a tutorial. The whole script is ~120 units, so the English lives in one file, `script/en.tsv`.
Work only on the keys named in your dispatch. Do all translation yourself; do not dispatch subagents.

## Read first
1. `glossary.md` - binding names, terms and style rules.
2. `python -X utf8 tools/tl.py units` - every unit: key, box, columns, JP (display form).
3. `docs/re/windows.md` - what each box is and where the code draws numbers or ranks.

## Format: `script/en.tsv`, edited with your file-edit tool (never sed, heredoc or a replace script)
`key<TAB>English`. Plain ASCII: straight quotes, `...`; no tabs inside the English, no Japanese.
- Story/master keys (`msg:15.2` = page 2 of msg 15) wrap automatically to 26 (master: 15) columns, 2 lines a page.
  ` / ` forces a line break, ` // ` a page break. A page that overflows becomes an extra page (allowed, D4), but
  keep one English page per JP page where the meaning fits.
- Other keys are the raw string without `{end}`, control codes as in the JP. Quiz `{sp4}` slots are numbers or
  ranks the code draws at a fixed column: keep each at its JP column (the check enforces it).

## Validate
`python -X utf8 tools/tl.py merge` (writes script/*.json and runs the lint), until it prints `lint 0 errors`;
it lists `note: key takes N pages` for pages that grew. Then `python -X utf8 tools/check.py`.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Adapt wordplay so the joke lands.
- Names and terms exactly as in the glossary; never abbreviate to fit (D4) - report `LONG: key` instead.
- Punctuation: 「」 -> "...", ・・・ -> `...`, ！？ -> `!?`.
- A sentence around a number slot must read for 1 and for 12 ("{sp4}-move limit!", not "{sp4} moves").

## Report (reply with only this)
Keys changed; then any lines: `NEW TERM: jp -> en`, `UNSURE: key - note`, `LONG: key - note`.
