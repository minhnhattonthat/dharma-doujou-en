# Dharma Doujou English translation

Unofficial English fan translation of **Dharma Doujou** (だるま道場, *Dharma Dojo*; SNES, Metro, 1994): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story scenes | Translated |
| Menus and tutorial | Translated |
| Quiz questions | Translated |
| Title logo, banners, HUD, pause plates, certificates | Translated (small 千両 label on the treasure-chest piece kept, part of its picture) |
| Credits | Translated |

Known issues: none known; [report one](../../issues/new/choose).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/dharma-doujou-en
cd dharma-doujou-en
# copy your dump to: "rom/Dharma Doujou (Japan).sfc"
#   (1,048,576 bytes, SHA-1 506231c0b1fa34b3ac47880363c7cd4656ea4c42; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/dharma_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
python -X utf8 tools/release.py                        # gates + BPS patch + zip -> release/
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Metro's and is included only so
the translation can be checked against it. Dharma Doujou is (c) Metro; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
