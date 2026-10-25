"""build.py: build build/dharma_en.sfc from the original dump (docs/re/text.md).

    python -X utf8 tools/build.py [--marker] [--qa msg:14="Text{end}" ..]

Each text block is unpacked to strings and repacked: strings laid out in id order from the block start (spilling
into the bank's free space when the block is full), strings that shared an address in the original stored once, the
pointer table rewritten. English strings are encoded with the English font's table (tools/font.py), and the font is
drawn in when any string is English. Every write goes through put() and is logged to build/writes.txt with the
original bytes it replaces, then romdiff checks the result. With no edits the output equals the original
(tests/test_build.py, the identity build). Text comes from script/<block>.json (tools/dump.py writes it).

--marker: every string's text runs become "<id>" labels with a column ruler (build/dharma_marker.sfc), to find each
string in game and measure its box. --qa overrides single strings (English) on top of either build.
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402
import check_rom  # noqa: E402
import font  # noqa: E402
import gfx  # noqa: E402
import romdiff  # noqa: E402
from text import Codec  # noqa: E402

LANG = "en"  # target language: the script field read and the output name
ORIG_ROM = ROOT / "rom" / "Dharma Doujou (Japan).sfc"
OUT = ROOT / "build" / f"dharma_{LANG}.sfc"

# name, table, pointer table (file offset), entries, file offset of the bank's $8000, text start, text end
# (exclusive), free space in the same bank for text that doesn't fit (start, end; docs/re/graphics.md)
BLOCKS = [
    ("msg", "jp.tbl", 0x12724, 91, 0x10000, 0x127E4, 0x13DD2, (0x16910, 0x18000)),
    ("screen", "jp2.tbl", 0x25A42, 98, 0x20000, 0x25B06, 0x2609C, (0x270A0, 0x28000)),
]


class Rom:
    def __init__(self, orig):
        self.orig, self.data, self.writes = orig, bytearray(orig), []

    def put(self, off, data, by):
        self.writes.append("%X %s %s %s" % (off, self.orig[off:off + len(data)].ljust(len(data), b"\xff").hex(),
                                            data.hex(), by))
        self.data[off:off + len(data)] = data


def ptr_offsets(rom, block):
    table, count, base = block[2:5]
    return [base + struct.unpack_from("<H", rom, table + 2 * i)[0] - 0x8000 for i in range(count)]


def unpack(rom, block):
    """Strings of one block, by id, in the table's text form."""
    c = Codec.load(ROOT / "tbl" / block[1])
    return [c.decode_at(rom, off) for off in ptr_offsets(rom, block)]


def pack(rom, block, strings):
    """strings: by id, each text in the jp table's form or a (lang, text) pair; lang other than jp = English."""
    name, tbl, table, count, base, start, end, extra = block
    codecs = {"jp": Codec.load(ROOT / "tbl" / tbl)}
    # ids that shared an address in the original share one copy (the first id's text); equal texts elsewhere don't
    first = {}
    alias = [first.setdefault(off, i) for i, off in enumerate(ptr_offsets(rom.orig, block))]
    regions = [(start, end, bytearray()), (*extra, bytearray())]
    ptrs = []
    for i, s in enumerate(strings):
        if alias[i] != i:
            ptrs.append(ptrs[alias[i]])
            continue
        lang, s = s if isinstance(s, tuple) else ("jp", s)
        if lang not in codecs:
            codecs[lang] = font.codec(name)
        enc = codecs[lang].encode(font.ligate(name, s) if lang != "jp" else s)
        for lo, hi, blob in regions:
            if lo + len(blob) + len(enc) <= hi:
                ptrs.append(lo + len(blob) - base + 0x8000)
                blob += enc
                break
        else:
            sys.exit(f"{name}: text is over its block: string {i} ({len(enc)} bytes) fits in no free region "
                     f"({', '.join('%d bytes left' % (hi - lo - len(b)) for lo, hi, b in regions)})")
    rom.put(table, struct.pack(f"<{count}H", *ptrs), f"{name}-ptrs")
    rom.put(start, bytes(regions[0][2]).ljust(end - start, b"\0"), f"{name}-text")  # no stale Japanese tail
    lo, hi, blob = regions[1]
    if blob:
        assert len(set(rom.orig[lo:hi])) == 1, f"{name}: free space 0x{lo:X} is not blank"
        rom.put(lo, bytes(blob), f"{name}-text2")


def load_script(lang=LANG):
    """{block name: (lang, text) by id} from script/<block>.json: the lang field, else ("jp", jp)."""
    texts = {}
    for block in BLOCKS:
        items = json.loads((ROOT / "script" / f"{block[0]}.json").read_text(encoding="utf-8"))
        if [e["id"] for e in items] != list(range(block[3])):
            sys.exit(f"script/{block[0]}.json: ids must be 0..{block[3] - 1} in order")
        texts[block[0]] = [(lang, e[lang]) if e.get(lang) else ("jp", e["jp"]) for e in items]
    return texts


TOKEN = re.compile(r"\{rep:[0-9A-Fa-f]{2}\}.|\{[^}]*\}|\[[0-9A-Fa-f]{4}\]")  # {rep} takes the next character
RULER = {"msg": 28, "screen": 18}


def marker_texts():
    """Every string's text runs replaced by a label "<id>" (+ a, b.. when a string has several runs); the first
    two runs carry a ruler of digits (column numbers mod 10) out to RULER columns. Strings whose dump.py note marks
    them as kept (credits, digits) stay as they are. Controls, picture codes and blank runs are kept."""
    texts = {}
    for block in BLOCKS:
        name = block[0]
        out = []
        for e in json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8")):
            if e.get("note", "").startswith(("digit", "big digit", "credits", "already English", "empty")):
                out.append(("jp", e["jp"]))
                continue
            parts, pos = [], 0
            for m in TOKEN.finditer(e["jp"]):
                parts += [e["jp"][pos:m.start()], m[0]]
                pos = m.end()
            runs = [k for k in range(0, len(parts), 2) if parts[k].strip()]
            for n, k in enumerate(runs):
                label = str(e["id"]) + (chr(97 + n) if len(runs) > 1 else "")
                width = RULER[name] if n < 2 else len(label)
                parts[k] = label + "".join(str(c % 10) for c in range(len(label) + 1, width + 1))
            out.append(("en", "".join(parts)))
        texts[name] = out
    return texts


def outside(writes, path=ROOT / "tools" / "ranges.txt"):
    """Errors for writes (romdiff.load_writes form) not inside one allowed range of tools/ranges.txt."""
    ranges = [[int(x, 16) for x in line.split()[0].split("-")]
              for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and line[0] != "#"]
    return [f"write outside tools/ranges.txt: 0x{off:X}+{len(new)} ({by})" for off, _, new, by in writes
            if not any(lo <= off and off + len(new) - 1 <= hi for lo, hi in ranges)]


def build(orig, out=OUT, texts=None):
    """texts: {block name: strings by id}; a block not given is repacked from the original."""
    rom = Rom(orig)
    english = False
    for block in BLOCKS:
        strings = (texts or {}).get(block[0]) or unpack(orig, block)
        english |= any(isinstance(s, tuple) and s[0] != "jp" for s in strings)
        pack(rom, block, strings)
    if english:
        free = list(font.FREE)
        font.patch(rom, rom.put, free)
        gfx.patch(rom, rom.put, free)
    data, _ = bps.snes_checksum(rom.data)
    rom.put(0x7FDC, data[0x7FDC:0x7FE0], "checksum")
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom.data)
    log = out.with_name(out.stem + "_writes.txt") if out != OUT else out.with_name("writes.txt")
    log.write_text("\n".join(rom.writes) + "\n", encoding="utf-8")
    writes = romdiff.load_writes(log)
    errs, _ = romdiff.check(orig, bytes(rom.data), set(), writes)
    errs += outside(writes)
    if errs:
        sys.exit("romdiff:\n" + "\n".join(errs))
    return bytes(rom.data)


def main():
    import argparse
    import hashlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker", action="store_true", help="marker build -> build/dharma_marker.sfc")
    ap.add_argument("--qa", action="append", default=[], metavar='BLOCK:ID=TEXT', help="override one string")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    check_rom.check()
    texts = marker_texts() if a.marker else load_script()
    for q in a.qa:
        key, _, text = q.partition("=")
        name, _, i = key.partition(":")
        texts[name][int(i)] = ("en", text if text.endswith("{end}") else text + "{end}")
    out = a.out or (OUT.with_name("dharma_marker.sfc") if a.marker else OUT)
    data = build(ORIG_ROM.read_bytes(), out, texts)
    print(f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}: sha1 {hashlib.sha1(data).hexdigest()}")


if __name__ == "__main__":
    main()
