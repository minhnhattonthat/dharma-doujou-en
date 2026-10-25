# Glossary - Dharma Dojo (だるま道場)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
The English lives in `script/en.tsv` (`tools/tl.py merge` writes it into script/*.json).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept where the Japanese has them (-sama, -san). Name order: Western.
- Romanisation source: official English names where they exist, else Hepburn without macrons.
- Credits: English (already romaji in the ROM; keep the staff names exactly as the ROM spells them; EXECTIVE ->
  EXECUTIVE is the only fix).
- Register / flavour: folk-tale narrator (the story ends sentences with そうな/じゃ: "they say", "or so the story
  goes"); light Japanese flavour.
- Abbreviations: none. Use more pages instead of shortening. Known exception: the versus record's W / L labels
  (2 columns between code-drawn counts; D10).

## Style rules
- Punctuation map: 「」 -> "...", ・・・ / … -> ..., ！！ -> !!, ？ -> ?.
- The narrator tells an old tale; the young monk is cheeky, the shrine maiden is spirited, the old master (tutorial
  and quiz) speaks like an old sage ("...ja" -> plain old-man English, no fake dialect).
- Number slots: a `{sp4}` in the quiz text is a number or rank the code draws at a fixed column. Keep it at the JP
  column (tools/tl.py checks) and write around it so it reads for 1 as well as for 12 ("{sp4}-move limit!").

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 小坊主 | the young monk | | player 1 (story) | acolyte |
| 巫女 | the shrine maiden | | player 2 (story) | miko, priestess |
| おしょうさま | the head priest | | the monk's master | osho-sama |
| 神主さま | the shrine master | | the maiden's master ("my shrine master" in her mouth) | Kannushi, head priest |
| ねこまた | nekomata | | two-tailed cat spirit; きょうだい = "the nekomata siblings" | cat demon |
| かっぱ | kappa | | river imp; plural "kappa" | kappas |
| あかおに / あおおに | the red oni / the blue oni | | | ogre |
| からくりだるま | the clockwork daruma | | | |
| ゆうれい | ghost | | | |
| 化物 | monsters | | | |
| 村人 | the villagers | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 鎌倉 | Kamakura | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| だるま | daruma | | the dolls (pieces); こま = pieces | dharma (except in the title) |
| だるま道場 | Dharma Dojo | | game title | |
| だるま道 / 達磨道 | the Daruma Way | | | Way of the Daruma |
| だるま道中記 | Daruma Trek | 12 | story mode (header plate, D10) | Daruma Journey |
| だるま修行編 | Daruma Drill | 12 | training mode | Daruma Training |
| だるま問答 | Daruma Quiz | 12 | puzzle-problem mode | |
| ふたりで対決 | 2P Battle | 12 | versus mode | |
| だるま入門編 | How to Play | 12 | tutorial mode | Daruma Basics |
| おぷしょん | Options | | | |
| 入門 / 師範 / 名人 / 達人 / 道主 | Novice / Sensei / Expert / Master / Legend | 6 | ranks and quiz courses (D10: the quiz header draws the rank at column 0 and the problem number at column 8) | Instructor, Grandmaster |
| 悪霊 | evil spirits | | | demons |
| 悪霊の置物 | haunted idols | | what the monsters pile on the roads | |
| おにぎり | rice balls | | | onigiri |
| 免許皆伝 | full mastery | | | |
| そうこ | the storehouse | | the bin below the stack (tutorial) | |
| 時間制限 / 手数制限 | Time Limit / Move Limit | | | |

## Decisions from earlier batches
- Story pages: one English page per JP page where it fits; tools/tl.py adds a page (with the script's own key-wait
  and clear) when it doesn't. A `{mode}` switch stays at the start of its JP page.
- screen 21-23 (あと N 手/秒/分): "Only {sp4} left!" without the unit, on purpose: the slot is fixed at column 5,
  so the unit can only follow the number and breaks at 1 ("1 moves"); the unit is in the problem line
  ("{sp4}-move limit!") and the HUD under the bubble. Reviewer flagged it Important; kept with this reason.
- Certificate (msg 30): "Exam:" = the course passed (row 11), "Rank:" = the rank conferred (row 14).
