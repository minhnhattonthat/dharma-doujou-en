"""build.py: build build/dharma_en.sfc from the original dump (docs/re/text.md).

Each text block is unpacked to strings and repacked: strings laid out in id order from the block start, identical
strings stored once, the pointer table rewritten. Every write goes through put() and is logged to build/writes.txt
with the original bytes it replaces, then romdiff checks the result. With no edits the output equals the original
(tests/test_build.py, the identity build).
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402
import check_rom  # noqa: E402
import romdiff  # noqa: E402
from text import Codec  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Dharma Doujou (Japan).sfc"
OUT = ROOT / "build" / "dharma_en.sfc"

# name, table, pointer table (file offset), entries, file offset of the bank's $8000, text start, text end (exclusive)
BLOCKS = [
    ("msg", "jp.tbl", 0x12724, 91, 0x10000, 0x127E4, 0x13DD2),
    ("screen", "jp2.tbl", 0x25A42, 98, 0x20000, 0x25B06, 0x2609C),
]


class Rom:
    def __init__(self, orig):
        self.orig, self.data, self.writes = orig, bytearray(orig), []

    def put(self, off, data, by):
        self.writes.append("%X %s %s %s" % (off, self.orig[off:off + len(data)].ljust(len(data), b"\xff").hex(),
                                            data.hex(), by))
        self.data[off:off + len(data)] = data


def ptr_offsets(rom, block):
    _, _, table, count, base, _, _ = block
    return [base + struct.unpack_from("<H", rom, table + 2 * i)[0] - 0x8000 for i in range(count)]


def unpack(rom, block):
    """Strings of one block, by id, in the table's text form."""
    c = Codec.load(ROOT / "tbl" / block[1])
    return [c.decode_at(rom, off) for off in ptr_offsets(rom, block)]


def pack(rom, block, strings):
    name, tbl, table, count, base, start, end = block
    c = Codec.load(ROOT / "tbl" / tbl)
    # ids that shared an address in the original share one copy (the first id's text); equal texts elsewhere don't
    first = {}
    alias = [first.setdefault(off, i) for i, off in enumerate(ptr_offsets(rom.orig, block))]
    blob, ptrs = bytearray(), []
    for i, s in enumerate(strings):
        if alias[i] != i:
            ptrs.append(ptrs[alias[i]])
            continue
        ptrs.append(start + len(blob) - base + 0x8000)
        blob += c.encode(s)
    if start + len(blob) > end:
        sys.exit(f"{name}: text is {start + len(blob) - end} bytes over its block ({len(blob)} > {end - start})")
    rom.put(table, struct.pack(f"<{count}H", *ptrs), f"{name}-ptrs")
    rom.put(start, bytes(blob), f"{name}-text")


def build(orig, out=OUT, texts=None):
    """texts: {block name: strings by id}; a block not given is repacked from the original."""
    rom = Rom(orig)
    for block in BLOCKS:
        pack(rom, block, (texts or {}).get(block[0]) or unpack(orig, block))
    data, _ = bps.snes_checksum(rom.data)
    rom.put(0x7FDC, data[0x7FDC:0x7FE0], "checksum")
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom.data)
    log = out.with_name("writes.txt")
    log.write_text("\n".join(rom.writes) + "\n", encoding="utf-8")
    errs, _ = romdiff.check(orig, bytes(rom.data), set(), romdiff.load_writes(log))
    if errs:
        sys.exit("romdiff:\n" + "\n".join(errs))
    return bytes(rom.data)


if __name__ == "__main__":
    check_rom.check()
    import hashlib
    data = build(ORIG_ROM.read_bytes())
    print(f"{OUT.relative_to(ROOT)}: sha1 {hashlib.sha1(data).hexdigest()}")
