# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en8x16.txt | drawn for this project (2026-10-26) | MIT, same as repo | yes | English 8x16 glyphs in both text engines (tools/font.py); small graphics labels (tools/gfx.py, bitmap=True) | - |
| fonts/en_cond.txt | drawn for this project (2026-10-26) | MIT, same as repo | yes | condensed glyphs: quiz rank plate (font.py LIGATURES), HUD "left" (gfx.py) | - |
| fonts/LiberationSans-Bold.ttf, fonts/LiberationSerif-Bold.ttf | https://github.com/liberationfonts/liberation-fonts 2.1.5 | SIL OFL 1.1 (fonts/LICENSE-Liberation.txt) | yes (rendered pixels ship, not the font file) | graphics-text redraws (tools/gfx.py, gfx_edits.py) | rendered without antialiasing, squeezed to fit |
