import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from text import Codec  # noqa: E402
import rle  # noqa: E402

ROM = ROOT / "rom" / "Dharma Doujou (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")

# (table, file offset of the pointer table, entries, bank file base)
TABLES = [("jp.tbl", 0x12724, 91, 0x10000), ("jp2.tbl", 0x25A42, 98, 0x20000)]


@needs_rom
@pytest.mark.parametrize("tbl,table,count,base", TABLES)
def test_text_roundtrip(tbl, table, count, base):
    rom = ROM.read_bytes()
    c = Codec.load(ROOT / "tbl" / tbl)
    for i in range(count):
        off = base + struct.unpack_from("<H", rom, table + 2 * i)[0] - 0x8000
        s = c.decode_at(rom, off)
        enc = c.encode(s)
        assert enc == rom[off:off + len(enc)], (i, s)


@needs_rom
def test_rle_roundtrip():
    rom = ROM.read_bytes()
    for i in range(1, 5):
        data, off, size = rle.decode(rom, i)
        blob = rle.encode(data, 0x8000)
        tmp = bytearray(blob)
        # decode our own encoding from a scratch "ROM" placed at file 0 / CPU $80:8000
        even = struct.unpack_from("<H", tmp)[0] - 0x8000
        e, _ = rle.decode_stream(tmp, even)
        o, _ = rle.decode_stream(tmp, 2)
        assert bytes(e) == data[0::2] and bytes(o) == data[1::2]
