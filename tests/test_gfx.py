"""tools/gfx.py (graphics-text redraws) and the font ligatures."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import gfx  # noqa: E402


def test_png_roundtrip(tmp_path):
    data = bytes(range(256)) * 32  # 8 KB, every index pattern
    for bpp in (2, 4):
        gfx.to_png(data, bpp, tmp_path / "x.png")
        assert gfx.from_png(tmp_path / "x.png", bytes(len(data)), bpp) == data


def test_tile_put_get():
    buf = bytearray(32)
    px = [[(x + y) % 16 for x in range(8)] for y in range(8)]
    gfx.tile_put(buf, 0, 4, px)
    assert gfx.tile_get(buf, 0, 4) == px


def test_draw_erases_and_inks_inside_the_rect():
    canvas = [[7] * 40 for _ in range(16)]
    gfx.draw(canvas, dict(text="Hi", erase=[7], fill=0, ink=3, bitmap=True))
    flat = {p for row in canvas for p in row}
    assert flat == {0, 3}


def test_pick_follows_the_majority_source():
    # two cells unique to raw ROM tiles at addr+0x1000; one solid cell also matching a resource elsewhere
    c = {(0x800, "a"): [("rom", 0x1800)], (0x820, "b"): [("rom", 0x1820)],
         (0x840, "c"): [(46, 0x40), ("rom", 0x1840)]}
    assert gfx.pick(c)[(0x840, "c")] == ("rom", 0x1840)


def test_candidates_prefer_the_resource_loaded_there(monkeypatch):
    # the quiz 手 tiles: res 64 is loaded at that VRAM spot, res 37 holds an identical copy
    tile = bytes(range(1, 33))
    res = {37: bytes(64) + tile, 64: tile}
    monkeypatch.setattr(gfx, "resource", lambda orig, r: res.get(r, b""))
    vram = bytearray(0x10000)
    vram[0x9000:0x9020] = tile
    assert gfx.candidates({64: 0x9000}, b"", 0x9000, 4, vram) == [(64, 0)]


def test_rank_ligature_fills_six_columns():
    s = font.ligate("screen", "Novice{end}")
    assert s.endswith("  {end}") and len(s) == 6 + len("{end}")
    assert font.ligate("screen", "Master every{end}") == "Master every{end}"  # whole strings only
    assert font.ligate("msg", "Novice{end}") == "Novice{end}"
