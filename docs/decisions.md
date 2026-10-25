# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-26 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (owner's standing answer for one-shot runs). |
| D2 | 2026-10-26 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. No earlier patch found. |
| D3 | 2026-10-26 | Credits | stay Japanese, translate | English (the credits are already romaji; keep them, fix only Japanese parts). |
| D4 | 2026-10-26 | Abbreviations | engine work first (default), abbreviate | Engine work first: full terms, extra pages instead of cuts. |
| D5 | 2026-10-26 | Graphics text left in Japanese | none (default), list | Translate all graphics text; keep the Japanese logo only if no official English version exists. |
| D6 | 2026-10-26 | Specs and plans | need approval, pre-approved | Pre-approved: run through checkpoints, report at the end. Never `gh release create`, never change repo visibility. |
| D7 | 2026-10-26 | Existing saves / states | user files, none | None provided: build the debug tool (phase 2). |
| D8 | 2026-10-26 | Game title in English | Dharma Doujou, Dharma Dojo, Daruma Dojo | "Dharma Dojo": Metro's own romanization (ROM header and credits say DHARMA; the arcade title is "Dharma Doujou"), with the common Western spelling of dojo. Revisit if an official English logo turns up. |
| D9 | 2026-10-26 | English font (my default, pre-approved run) | fixed 8 px narrow glyphs in the engine's own 8x16 mode; VWF hook; tiny 2-per-tile font | Fixed 8 px narrow glyphs, new 1 px font for caps and lower case (fonts/en8x16.txt). Both engines already draw 8x16 narrow glyphs, so no code change; the story box gives 26 x 2 per page, about twice the Japanese characters, and pages can be added (D4). Revisit with a VWF only if a box can't fit its meaning. |
| D10 | 2026-10-26 | Names that hit fixed layouts (my default, pre-approved run) | widen plates / patch draw code; rename to fit; abbreviate | Rename to fit, no abbreviations: the mode headers sit in a 12-column framed plate, so Daruma Trek / Daruma Drill / Daruma Quiz / 2P Battle / How to Play / Options (was Daruma Journey, Daruma Training, Daruma Basics). The quiz header draws the course name at column 0 and the problem number at column 8 (probed with a qa build), so ranks are 6 letters: Novice / Sensei / Expert / Master / Legend, written "Novice Q 1". The versus record draws each count right before a 2-column label: W / L (the one abbreviation; widening needs the draw code moved). Change any of these if you prefer the longer names; they'd need engine work. |
