# Text boxes and their budgets (the width gate)

One column = one 8 px narrow English glyph. The budgets live in `tools/lint.py` (BOXES, box_of); this file says how
each was found. Measured 2026-10-26 on `build/dharma_marker.sfc` (every text run = `<id>` + a column ruler, digits
= column mod 10) and `build/dharma_qa.sfc` (exact-fill torture lines via `build.py --marker --qa ...`), warped with
`tools/warp.py <scene> --hold 1500 --mash 60 --shot-every 60`. "measured" = the last column still inside the frame
in a 3x zoom; "guess" = not yet seen with a full-width line: measure before release (lint warns).

| Box | Strings | Cols x lines | How |
|---|---|---|---|
| story | msg 15-19, 48-55 | 26 x 2 per page | measured: 26-char torture lines fit exactly (story_intro, qa build). The script clears with `{rep:1A} ` = 26: anything past 26 is never cleared (stale "78" seen) |
| intro | msg 14 | 25 x 1 | measured: 25 chars fit with ~1 column to spare (story_intro) |
| subtitle | msg 9, 10 | 19 x 1 | measured: starts at column 13, wraps to the left edge after column 31 (story_limit) |
| stage | msg 22-29 line 1 | 19 x 1 | measured: column 20 sits on the card's frame (stage2) |
| master | msg 36 | 15 x 2 (16 px pitch) | measured: column 16 is on the border; its clears are `{rep:0F}` = 15 (quiz_master) |
| choice | msg 56 | 8 x 2 | measured: box from column 13, border at 21 (versus_win, 対戦成績 screen) |
| quiz | screen 10-37, 40-51 | 20 x 1 | measured from the marker shot: border at column 21 (quiz_play). Confirm with a 20-char line in QA |
| tutorial | screen 57-97 | 17 x 1 | measured: an 18th character overwrites the bubble's right border (tutorial, qa build). screen 96/97 also show in the quiz bubble; the smaller box wins |
| header | msg 0-5 | 12 x 1 | measured: msg 0 heads the story menu in a framed plate, text from column 10, a 13th character touches the frame (story_menu). In the main menu the same items have 26. Widening the plate is engine/graphics work if names don't fit |
| menu | msg 6, 7 | 24 x 1 | measured: column 8 to the screen edge, no frame (story_menu) |
| prompt | msg 8 | 21 x 1 | measured: plate from column 6, 22nd character on the frame (training_char) |
| password | msg 11-13 | 14 x 1 | guess: not reached with text yet (password_end warp's Start doesn't confirm; find the confirm input) |
| certificate | msg 30 | 26 x 6 | measured: lines from column 5 to the border at column 31 (quiz_break); see below |
| rank | msg 31-35, screen 52-56 | 6 x 1 | screen 52-56: the course name drawn at column 0 of the quiz header, with the problem number at column 8 (measured, see below). Certificate slot (msg 31-35) has ~19; same names for consistency. The bottom-right quiz rank plate (G10) is graphics |
| record | msg 37 | layout | code draws the win counts at fixed columns; keep every space and `{rep}` count, 勝/負 -> 2-column labels |
| end | msg 20 | 26 x 1 | guess |
| qchoice | screen 38, 39 | 8 x 1 | guess |

## Fixed-position layouts
- **msg 30 (quiz certificate 段位認定状):** text origin column 5. The game draws one rank name (msg 31-35) at
  column 11 on row 11 (the course passed) and another at column 11 on row 14 (the rank awarded), over whatever the
  text left there. So in English each of those two rows must have exactly 6 columns of text (label + space) before
  the slot and nothing after it; other rows are free. Check in the quiz_break warp.
- **msg 37 (versus record 対戦成績):** measured 2026-10-26 (qa build with AB/CD/EF/GH for 勝/負, versus_win warp,
  `--hold 1200 --mash 400`): the code draws each count (one big digit) in the column just left of each label, i.e.
  string columns 4, 9, 21, 26; labels at 5-6, 10-11, 22-23, 27-28. English uses W / L there (D10).
- **Quiz header (screen 51, and 14 with a 2-digit slot):** measured (qa build, quiz_play / quiz_lv5): the code
  draws the course name (screen 52-56) at column 0, in full, before the string (a 10-letter name showed whole
  where the string skips), then the problem number at columns 8-9 (8-11 for 14). So rank names are at most 6
  letters and the English is `{sp4}{sp2} Q{sp4}` -> "Novice Q 1".
- **Quiz number slots (screen 15-17, 21-23):** the number is drawn right-aligned in the JP `{sp4}` slot (columns
  0-3 for 15-17; 5-8 for 21-23); tools/tl.py keeps every `{sp4}` at its JP column.
- **Tutorial order (seen in the tutorial warp):** 74-75, 72-73, 76-77, 72-73: "game over" follows each condition.
- **Engine 2 (screen block):** `{spN}` skips N tiles without clearing them: a skipped tile shows the previous line's
  glyph. English spaces use a drawn blank glyph (tools/font.py), and `{sp4}` slots (screen 14-17, 21-23, 51) are
  where the game draws a number: keep them.
- Clears: story pages clear 26 columns, msg 36 clears 15; a longer line leaves stale glyphs on the next page.
