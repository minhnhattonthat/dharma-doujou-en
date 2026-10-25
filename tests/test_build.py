import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ORIG_ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_identity_build(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    assert build.build(orig, tmp_path / "id.sfc") == orig


@needs_rom
def test_edited_string_moves_the_rest(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    texts = {b[0]: build.unpack(orig, b) for b in build.BLOCKS}
    texts["msg"][0] = "ア{end}"  # shorter: every later string and pointer shifts
    out = build.build(orig, tmp_path / "ed.sfc", texts)
    for block in build.BLOCKS:
        assert build.unpack(out, block) == texts[block[0]]
    assert len(set(build.ptr_offsets(out, build.BLOCKS[0])[57:65])) == 1  # aliases still share


def test_outside_allowed_ranges():
    ok = (0x127E4, b"", b"\0" * (0x13DD2 - 0x127E4), "msg-text")
    over = (0x13DD1, b"", b"\0\0", "spill")
    stray = (0x40000, b"", b"\0", "stray")
    assert build.outside([ok]) == []
    assert [e.split("(")[1] for e in build.outside([ok, over, stray])] == ["spill)", "stray)"]


@needs_rom
def test_pack_rejects_overflow(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    block = build.BLOCKS[0]
    strings = build.unpack(orig, block)
    strings[0] = strings[0][:-5] + "ア" * 4000 + "{end}"
    with pytest.raises(SystemExit, match="over its block"):
        build.pack(build.Rom(orig), block, strings)
