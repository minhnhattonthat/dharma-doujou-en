"""English redraws of graphics text, applied by tools/gfx.py gen (docs/re/graphics.md, the G-rows).

Each edit: name ("G<row> what"), then either
  dump (work/gfx/dumps/ prefix, from `gfx.py dump SCENE`), layer (bg1 bg2 bg3 obj), rect (screen x, y, w, h)
  or pics (engine-1 24x24 picture codes, drawn side by side as one canvas);
and the drawing: text ("\n" between lines), ink (index, or a list of indices top to bottom), edge (1 px ring) /
shadow (1 px down-right) indices, erase (indices of the Japanese to paint over), fill (paint index; default: the
nearest kept pixel, for textured plates), font (sans / serif; bitmap=True: fonts/en8x16.txt), cap (cap height px),
gap (px between letters), lead (px between lines), bold (px of extra width), align (c l r), dx, dy, pad, shear (px up per px right: a slanted sign).
"""

# wood plates: the text tiles hold text + wood only; repaint them whole from a clean 16x16 patch of the wood
PLATE = dict(layer="bg1", erase=list(range(16)), ink=1, shadow=5, bitmap=True, align="l", pad=0)
GO = dict(PLATE, dump="gameover/ppu_008550", tex=(72, 56, 16, 16))  # story continue screen (res 36 on res 79)
TD = dict(PLATE, dump="training_diff/ppu_001470", tex=(72, 40, 16, 16))  # training difficulty (res 36 on res 6)
HUD = dict(dump="stage1_moves/ppu_006300", layer="bg1", erase=list(range(1, 16)), fill=0, bitmap=True, pad=0,
           ink=[4, 3, 2, 1, 1, 2, 3, 4], edge=14)
VS = dict(dump="versus_play/ppu_001410", layer="bg1", erase=list(range(1, 16)), fill=0, ink=[1, 1, 2, 2], edge=13,
          font="sans", gap=1)
WIN = dict(dump="versus_win/ppu_001560", layer="bg1", erase=list(range(1, 16)), fill=0, ink=2,
           edge=4, edge2=14, font="serif", cap=30, gap=1)

# training-mode crow's bubble (BG1, res 37 glyphs; dark brown 12 / 11 / 10 on cream 15). Tile 0x42 (top-left of
# っ!) is the bubble's blank padding, so それっ! keeps it blank and the English sits in そ れ.
CROW = dict(layer="bg1", erase=[10, 11, 12], fill=15, ink=12, bitmap=True, pad=0)

EDITS = [
    # G12 stack warning 積み上がり注意!! (BG1, res 8 tiles 50-7D, DMA'd from WRAM $7F:0A00): white 15 shadow 9 on red 12.
    # Blinks at the top in training once the stack is high (training_crow, EN build dump: the run is input-timed).
    dict(name="G12 stack", dump="training_crow/ppu_005760", layer="bg1", rect=(40, 0, 184, 16),
         text="STACK TOO HIGH!!", erase=[9, 15], fill=12, ink=15, shadow=9, font="sans", cap=10, gap=1, pad=0),
    # G21 story opening picture: the slanted wooden road sign かまくら (BG1 res 21, pal 2): ink 15 on wood 8 9 10
    dict(name="G21 sign", dump="story_intro/ppu_002640", layer="bg1", rect=(59, 94, 37, 34), text="Kamakura",
         erase=[10, 15], ink=15, font="sans", cap=7, gap=0, shear=0.45, pad=0),
    # G7 crow countdown 五秒前 / 四 / 三 / 二 / 一 / それっ!
    dict(CROW, name="G7 crow 5", dump="training_play/ppu_005280", rect=(176, 120, 48, 16), text="5 sec"),
    dict(CROW, name="G7 crow 4", dump="training_play/ppu_005340", rect=(192, 120, 16, 16), text="4"),
    dict(CROW, name="G7 crow 3", dump="training_play/ppu_005400", rect=(192, 120, 16, 16), text="3"),
    dict(CROW, name="G7 crow 2", dump="training_play/ppu_005460", rect=(192, 120, 16, 16), text="2"),
    dict(CROW, name="G7 crow 1", dump="training_play/ppu_005520", rect=(192, 120, 16, 16), text="1"),
    dict(CROW, name="G7 crow now", dump="training_play/ppu_005610", rect=(176, 120, 32, 16), text="Now!"),
    dict(CROW, name="G7 crow now end", dump="training_play/ppu_005610", rect=(208, 120, 16, 16), text=""),
    # G1 title logo だるま道場 (BG1, res 27, pal 3) under the game's own gold DHARMA -> DOJO.
    # Dark purple 8 with purple rims 6 / 5 on transparent 0; the kana fly in one 48 px block at a time.
    dict(name="G1 logo", dump="title/ppu_001740", layer="bg1", rect=(8, 32, 240, 48), text="DOJO",
         erase=[5, 6, 7, 8], fill=0, ink=8, edge=6, edge2=5, font="serif", cap=38, gap=10, bold=4),
    # G5 continue screen: 再度挑戦 / 出直す
    dict(GO, name="G5 retry", rect=(104, 64, 64, 16), text="Try Again"),
    dict(GO, name="G5 quit", rect=(104, 88, 48, 16), text="Quit"),
    # G4 training difficulty: やさしい / ふつう / むずかしい; しい is one set of tiles in both rows, so the words go
    # in やさ / ふつう / むずか and しい is blanked (shared=True: the むずかしい row shows the same blank)
    dict(TD, name="G4 easy", rect=(96, 48, 32, 16), text="Easy"),
    dict(TD, name="G4 shii", rect=(128, 48, 32, 16), text="", shared=True),
    dict(TD, name="G4 normal", rect=(96, 72, 48, 16), text="Normal"),
    dict(TD, name="G4 hard", rect=(96, 96, 48, 16), text="Hard"),
    # G6 options header plate おぷしょん (BG2, res 81; dark brown 1 with a mid-brown rim 14 on gold 2-4)
    dict(name="G6 options", dump="options/ppu_001260", layer="bg2", rect=(64, 16, 120, 32), text="Options",
         erase=[1, 6, 14], ink=1, shadow=14, shadow_full=True, font="serif", cap=21, gap=1),
    # G7 story move-limit HUD (BG1, res 37): あと・ / N手 -> Moves / N left (the code draws N left of 手).
    # Yellow rows dark-light-dark (4 3 2 1 2 3 4), dark grey outline 14.
    dict(HUD, name="G7 moves", rect=(208, 64, 40, 16), text="Moves"),
    dict(HUD, name="G7 left", rect=(232, 88, 16, 16), text="left", bitmap="cond", align="r"),
    # the same under the quiz master's bubble (res 64)
    dict(HUD, name="G7 quiz moves", dump="quiz_play/ppu_002460", rect=(112, 40, 40, 16), text="Moves"),
    dict(HUD, name="G7 quiz left", dump="quiz_play/ppu_002460", rect=(136, 64, 16, 16), text="left",
         bitmap="cond", align="r"),
    # G9 quiz master scene: 免許皆伝 plate (BG1, res 78): black 11 with a dark brown glow 5 on wood
    dict(name="G9 mastery", dump="quiz_master/ppu_001650", layer="bg1", rect=(36, 80, 184, 48), text="Full Mastery",
         erase=[11], halo=3, grain="h", ink=11, edge=5, edge_w=2, font="serif", cap=18, gap=1, dy=3),
    # G19 round start call よーい / どん (OBJ, raw tiles at ROM 0xCA000 / 0xCA800, shared by every mode)
    dict(name="G19 ready", dump="stage1_moves/ppu_006300", layer="obj", rect=(80, 88, 112, 32), text="Ready...",
         erase=list(range(1, 16)), fill=0, ink=[4, 5, 5, 6, 6, 7, 7, 8], edge=14, font="sans", cap=21, gap=1),
    dict(name="G19 go", dump="stage1_moves/ppu_006510", layer="obj", rect=(100, 86, 72, 38), text="GO!",
         erase=[9, 10, 11], halo=2, fill=15, ink=[9, 9, 10, 10, 11], edge=14, font="sans", cap=24, gap=2),
    # G13 2P banner 三本勝負 / 一本勝負 (BG1, res 63): the number kanji is its own 32x32 block, 本勝負 is shared
    # -> "3-Round Match" / "1-Round Match". Pink 1 2 with a grey rim 13.
    dict(VS, name="G13 three", rect=(64, 64, 32, 32), text="3", cap=22, align="r", pad=0),
    dict(VS, name="G13 one", grid=(63, [[0x80 + 16 * y + x for x in range(4)] for y in range(4)]), pal=5,
         text="1", cap=22, align="r", pad=0),
    dict(VS, name="G13 match", rect=(96, 64, 96, 32), text="-Round Match", cap=15, align="l", pad=0, dy=3),
    # G13 2P victory 勝利 (BG1, res 77): two 56x56 blocks with a gap the map leaves empty -> "YOU" "WIN!"
    # under the 1P / 2P tag. Black 2 with grey highlights, white rim 4, dark ring 14.
    dict(WIN, name="G13 you", rect=(64, 56, 56, 56), text="YOU"),
    dict(WIN, name="G13 win", rect=(144, 56, 56, 56), text="WIN!"),
    # G17 2P record header 対戦成績 scroll (BG1, res 80): black 7 / grey 8 9 on paper 3-6
    dict(name="G17 results", dump="versus_win/ppu_001830", layer="bg1", rect=(80, 24, 104, 32), text="Results",
         erase=[7, 8, 9], halo=1, grain="h", ink=7, shadow=8, font="serif", cap=18, gap=1),
    # G16 password header plate ぱすわーど (BG1, res 81 tiles 70-AE: the options plate's twin)
    dict(name="G16 password", dump="password/ppu_001680", layer="bg1", rect=(64, 24, 120, 32), text="Password",
         erase=[1, 6, 14], ink=1, shadow=14, shadow_full=True, font="serif", cap=19, gap=1),
    # G18 quiz certificate seal たいへん / よくできました (OBJ, res 66): pale pink 15 outlined magenta 4 on the flower
    dict(name="G18 stamp", dump="quiz_break/ppu_002490", layer="obj", rect=(12, 148, 58, 42), text="Well\nDone!",
         erase=[4, 15], ink=15, edge=4, font="sans", cap=12, lead=3, gap=1),
    # the stamp's lower Japanese strokes are in the outline colours 2/3: clear them inside the outline only
    dict(name="G18 stamp low", dump="quiz_break/ppu_002490", layer="obj", rect=(16, 184, 52, 4), text="",
         erase=[2, 3, 4], tex=(20, 165, 2, 2)),
    dict(name="G18 stamp mid", dump="quiz_break/ppu_002490", layer="obj", rect=(16, 172, 52, 12), text="",
         erase=[2, 3], tex=(20, 165, 2, 2)),
    # G7 pause menu (all modes): つづける / こうさん, res 37
    dict(name="G7 pause", dump="stage1_pause/ppu_007380", layer="bg1", rect=(104, 88, 62, 32),
         text="Continue\nGive Up", erase=[11, 12], fill=15, ink=12, bitmap=True, align="l", pad=0),
    # G20 time running low: HURRY UP 急げ HURRY UP banner (OBJ, crows)
    dict(name="G20 hurry", dump="stage1_hurry/ppu_007740", layer="obj", rect=(112, 58, 32, 22), text="NOW!",
         erase=list(range(15)), fill=15, ink=[6, 7, 2, 2, 3], edge=14, font="sans", cap=14, gap=1, dy=-1),
    # G2 mode select: 時間制限 / 手数制限 (msg 9, 10) -> TIME LIMIT / MOVE LIMIT; 制限 is shared by both
    # (en.tsv msg 9/10 set the pictures side by side as two words)
    dict(name="G2 time", pics=[0x6330, 0x6339], text="TIME", erase=[1, 2, 3], fill=0, ink=3, shadow=2, cap=16,
         gap=2),
    dict(name="G2 move", pics=[0x6354, 0x635D], text="MOVE", erase=[1, 2, 3], fill=0, ink=3, shadow=2, cap=16,
         gap=1),
    dict(name="G2 limit", pics=[0x6342, 0x634B], text="LIMIT", erase=[1, 2, 3], fill=0, ink=3, shadow=2, cap=16,
         gap=2),
]
