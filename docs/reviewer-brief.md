# Translation reviewer brief - Dharma Dojo (SNES, 1994)

You review the JP->English fan translation of Dharma Dojo, a daruma-otoshi puzzle game with a folk-tale story mode
(a young monk and a shrine maiden race each other to clear monsters off the roads), a quiz mode run by an old
master, and a tutorial. Read-only: no edits, no git, no subagents. Mechanical validity (keys, control codes,
encodable characters, box widths, number-slot columns) is already enforced by `tools/tl.py merge` and
`tools/lint.py` - judge translation quality. Return the report as your final message: subagents cannot write files,
so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file: every unit as `>> key [box] | JP` / `EN:` with up to +-2 context units of the same string. Read ALL
  of it, in passes if large. A story key `msg:15.2` is page 2 of string 15; ` / ` is a line break.
- `glossary.md` (rulings and style rules at the top), `docs/decisions.md` D8-D10 (why some names are short).

## Layout facts (not defects)
- Boxes are tiny: story 26 x 2 per page (pages may be added), quiz 20, tutorial 17 (two lines per bubble, each
  line its own key), headers 12, ranks 6. Suggest fixes that fit the same box.
- `{sp4}`/`{sp2}` in the quiz text are slots where the code draws a number (or, at column 0 of screen 14/51, the
  rank name). "Novice Q 1" is the problem header. `{nl}` codes in msg 30/37 are fixed layouts.
- Tutorial lines 70-77 are shown in order; 72-73 ("it's game over / for you!") follow both 70-71 and 74-77.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; voice per the style rules (narrator "they say", cheeky monk, spirited
  maiden, old-sage master).
- Things players caught that reviewers missed elsewhere: jokes losing their punch; an ordinal suffix after a
  number slot; abbreviated names or terms; awkward stock phrases; a slot sentence that breaks for 1 ("1 moves").
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken slot grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - these are deferred to one polish pass)
Each: `key - JP gist - problem - suggested EN (fitting the box)`.
### Assessment
Approved | Needs fixes - one sentence why.
