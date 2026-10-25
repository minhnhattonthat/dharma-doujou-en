import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import font  # noqa: E402
import rle  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ORIG_ROM.is_file(), reason="no ROM dump in rom/")
PRINTABLE = "".join(font.glyphs())


def test_glyphs_fit_the_cell():
    for ch, rows in font.glyphs().items():
        assert len(rows) == 16 and all(len(r) == 8 for r in rows), ch
        assert not any(rows[y][x] == 1 for y in (0, 1, 15) for x in range(8)), ch  # ink only in rows 2-14
        assert not any(r[7] == 1 for r in rows), ch  # column 7 is for the shadow / letter gap


@pytest.mark.parametrize("engine", font.ENGINES)
def test_english_table_roundtrip(engine):
    c = font.codec(engine)
    s = "The quick brown fox, " + PRINTABLE + "{end}"
    assert c.decode_words(c.encode_words(s)) == s
    assert c.encode_words(" ") != [0xFF01]  # engine 2: a drawn blank, not a tile skip


@pytest.mark.parametrize("engine", font.ENGINES)
def test_slots_spare_every_other_glyph(engine):
    """No English glyph tile is a tile of a Latin, digit, sign or small-kana entry of the jp table."""
    tbl, _, _, step = font.ENGINES[engine]
    c = build.Codec.load(ROOT / "tbl" / tbl)
    used = set()
    for w, v in c.dec.items():
        if w < 0x2000 and v.isascii():
            used |= font.tiles_of(engine, w)
        elif w < 0x6000 and w >= 0x2000:
            used |= {w & 0x1FFF} | ({(w & 0x1FFF) + step} if w < 0x4000 else set())
    for code in font.assign(engine).values():
        assert not {code & 0x1FFF, (code & 0x1FFF) + step} & used, hex(code)


@needs_rom
def test_english_build_draws_the_font(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    texts = {b[0]: build.unpack(orig, b) for b in build.BLOCKS}
    texts["msg"][14] = ("en", "Long, long ago...{end}")
    out = build.build(orig, tmp_path / "en.sfc", texts)
    data = rle.decode(out, 1)[0]
    n = font.assign("msg")["A"] & 0x1FFF
    assert data[n * 16:n * 16 + 16] == font.tile_bytes("msg", font.glyphs()["A"][:8])
    assert font.codec("msg").decode_at(out, build.ptr_offsets(out, build.BLOCKS[0])[14]) == texts["msg"][14][1]


@needs_rom
def test_long_text_spills_into_free_space(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    texts = {b[0]: build.unpack(orig, b) for b in build.BLOCKS}
    texts["msg"][14] = ("en", "x" * 2700 + "{end}")  # 5.4 KB: more than the block has left, less than free space
    out = build.build(orig, tmp_path / "spill.sfc", texts)
    offs = build.ptr_offsets(out, build.BLOCKS[0])
    lo, hi = build.BLOCKS[0][7]
    assert lo <= offs[14] < hi
    assert font.codec("msg").decode_at(out, offs[14]) == texts["msg"][14][1]


@needs_rom
def test_marker_build(tmp_path):
    texts = build.marker_texts()
    assert texts["msg"][14][1].startswith("14")
    assert texts["msg"][57] == ("jp", "EXECTIVE PRODUCER{end}")  # credits kept
    build.build(build.ORIG_ROM.read_bytes(), tmp_path / "m.sfc", texts)
