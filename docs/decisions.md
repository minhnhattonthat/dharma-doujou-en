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
