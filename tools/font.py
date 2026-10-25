"""font.py: the English 8x16 font (fonts/en8x16.txt) drawn into both text engines' fonts, and their tables.

    python -X utf8 tools/font.py [--sheet OUT.png]    # print the slot map; --sheet renders the source glyphs

The glyphs go into tile slots of kana/kanji glyphs, which no English string uses (docs/re/text.md, Font):
- engine 1 (BG3 2bpp, resources 1-4): narrow glyph 2000|N = tile N over N+1; a 16x16 kana slot N (tiles N..N+3)
  holds two narrow glyphs, N and N+2. Ink colour 3, shadow colour 1 (right and down), like the kana.
- engine 2 (BG1 4bpp, resources 34-35 = tiles 0x200-0x3FF): narrow glyph 2000|N = tile N over N+16; a kana slot N
  (N, N+1 / N+16, N+17) holds narrow glyphs N and N+1. Ink colour C on background F, no shadow.
Patched resources are re-encoded (tools/rle.py) in place when they fit, else moved to free space and the resource
table entry repointed.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rle  # noqa: E402
from text import Codec  # noqa: E402

SRC = ROOT / "fonts" / "en8x16.txt"
# free space for moved resources (file ranges, each inside one bank; docs/re/graphics.md)
FREE = [(0x0E2E90, 0x0E8000), (0x0F5130, 0x0F8000), (0x0A5990, 0x0A8000)]
# engine: (jp table, resources with the tile index of their first tile, bytes per tile, narrow bottom-tile step)
ENGINES = {
    "msg": ("jp.tbl", [(1, 0x000), (2, 0x100), (3, 0x200), (4, 0x300)], 16, 1),
    "screen": ("jp2.tbl", [(34, 0x200), (35, 0x300)], 32, 16),
}


def glyphs():
    """{char: 16 rows of 8 pixels, 0 blank / 1 ink / 2 shadow} from the source file."""
    out, name, rows = {}, None, []
    lines = SRC.read_text(encoding="utf-8").splitlines() + ["== "]
    for n, line in enumerate(lines, 1):
        if line.startswith("== "):
            if name is not None:
                assert len(rows) == 13, f"{SRC.name}: glyph {name!r} has {len(rows)} rows, want 13"
                out[name] = shade([[0] * 8] * 2 + rows + [[0] * 8])
            name, rows = line[3:], []
            assert name not in out, f"{SRC.name}:{n}: duplicate glyph {name!r}"
        elif line and not line.startswith("# "):  # glyph rows start with '#' too, comments with '# '
            assert len(line) == 7 and set(line) <= set(".#"), f"{SRC.name}:{n}: want 7 of '.#', got {line!r}"
            rows.append([int(c == "#") for c in line] + [0])
    return out


def shade(rows):
    """Add the shadow: each blank pixel right of or below an ink pixel becomes 2."""
    out = [r[:] for r in rows]
    for y in range(16):
        for x in range(8):
            if rows[y][x] == 1:
                for yy, xx in ((y, x + 1), (y + 1, x)):
                    if yy < 16 and xx < 8 and out[yy][xx] == 0:
                        out[yy][xx] = 2
    return out


def slots(engine):
    """Narrow glyph codes free for English, in order: from the jp table's kana/kanji glyphs (mode 0000), skipping
    any slot whose tiles another table entry (Latin, digits, signs, small kana) also uses."""
    tbl, _, _, step = ENGINES[engine]
    c = Codec.load(ROOT / "tbl" / tbl)
    big = sorted(w for w, v in c.dec.items() if w < 0x2000 and not v.isascii())
    keep = set()
    for w, v in c.dec.items():
        if w < 0x2000 and v.isascii():
            keep |= tiles_of(engine, w)
        elif 0x2000 <= w < 0x4000:
            keep |= {w & 0x1FFF, (w & 0x1FFF) + step}
        elif 0x4000 <= w < 0x6000:
            keep.add(w & 0x1FFF)
    out = []
    for w in big:
        for n in ((w, w + 2) if engine == "msg" else (w, w + 1)):
            if not {n, n + step} & keep:
                out.append(n)
    return out


def tiles_of(engine, w):
    n = w & 0x1FFF
    return {n, n + 1, n + 2, n + 3} if engine == "msg" else {n, n + 1, n + 16, n + 17}


def tile_bytes(engine, rows):
    """One 8x8 tile from 8 rows of 0/1/2 pixels."""
    if engine == "msg":  # 2bpp: ink 3, shadow 1
        out = bytearray(16)
        for y, r in enumerate(rows):
            for x, p in enumerate(r):
                col = (0, 3, 1)[p]
                out[2 * y] |= (col & 1) << (7 - x)
                out[2 * y + 1] |= (col >> 1 & 1) << (7 - x)
        return bytes(out)
    out = bytearray(32)  # 4bpp: background F, ink C, shadow left as background
    for y, r in enumerate(rows):
        for x, p in enumerate(r):
            col = 0xC if p == 1 else 0xF
            for plane in range(4):
                out[(plane >> 1) * 16 + 2 * y + (plane & 1)] |= (col >> plane & 1) << (7 - x)
    return bytes(out)


def assign(engine):
    """{char: narrow code (2000|N)} for every source glyph."""
    gl, sl = glyphs(), slots(engine)
    if len(gl) > len(sl):
        sys.exit(f"font: {len(gl)} glyphs, only {len(sl)} {engine} slots")
    return {ch: 0x2000 | n for ch, n in zip(gl, sl)}


def table_lines(engine):
    """Lines of the English text table: the jp table's controls, a space, and the English glyphs."""
    tbl = ENGINES[engine][0]
    lines = [ln for ln in (ROOT / "tbl" / tbl).read_text(encoding="utf-8-sig").splitlines()
             if ln.startswith("#!") or ("={" in ln and ln.endswith("}"))]
    if engine == "msg":
        lines.append("4000=\\s")
    lines += ["%04X=%s" % (code, ch) for ch, code in assign(engine).items()]
    return lines


def codec(engine):
    c = Codec(table_lines(engine))
    if engine == "screen":
        c.enc[" "] = c.cenc["sp1"]  # engine 2 has no space glyph: a space skips one tile (decodes as {sp1})
    return c


def patch(rom, put):
    """Draw the English glyphs into both engines' font resources in rom (a Rom from build.py)."""
    free = list(FREE)
    gl = glyphs()
    for engine, (_, resources, size, step) in ENGINES.items():
        data = {r: bytearray(rle.decode(rom.orig, r)[0]) for r, _ in resources}
        for ch, code in assign(engine).items():
            n = code & 0x1FFF
            for t, rows in ((n, gl[ch][:8]), (n + step, gl[ch][8:])):
                r, first = max((r, f) for r, f in resources if f <= t)
                data[r][(t - first) * size:(t - first + 1) * size] = tile_bytes(engine, rows)
        for r, _ in resources:
            off, size_was = rle.decode(rom.orig, r)[1:]
            if bytes(data[r]) == rle.decode(rom.orig, r)[0]:
                continue
            bank = rom.orig[rle.TABLE + 3 * r + 2]
            blob = rle.encode(bytes(data[r]), bank << 16 | 0x8000 | (off & 0x7FFF))
            if len(blob) > size_was:
                off = alloc(rom.orig, free, len(blob))
                bank = 0x80 | (off >> 15)
                blob = rle.encode(bytes(data[r]), bank << 16 | 0x8000 | (off & 0x7FFF))
                put(rle.TABLE + 3 * r, struct.pack("<HB", 0x8000 | (off & 0x7FFF), bank), f"font-res{r}-ptr")
            put(off, blob, f"font-res{r}")


def alloc(orig, free, n):
    for i, (lo, hi) in enumerate(free):
        if hi - lo >= n:
            assert len(set(orig[lo:lo + n])) == 1, f"free space 0x{lo:X} is not blank"
            free[i] = (lo + n, hi)
            return lo
    sys.exit(f"font: no free space for {n} bytes")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="render the source glyphs (ink, shadow) to a PNG")
    a = ap.parse_args()
    for engine in ENGINES:
        m = assign(engine)
        print(engine, f"{len(m)} glyphs in {len(slots(engine))} slots:", " ".join(f"{c}={w:04X}" for c, w in m.items()))
    if a.sheet:
        from PIL import Image
        gl = glyphs()
        img = Image.new("RGB", (len(gl) * 9, 17), (40, 40, 60))
        for i, rows in enumerate(gl.values()):
            for y, r in enumerate(rows):
                for x, p in enumerate(r):
                    img.putpixel((i * 9 + x, y), [(240, 230, 200), (90, 60, 30), (200, 180, 150)][p])
        img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(a.sheet)


if __name__ == "__main__":
    main()
