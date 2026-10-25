"""fontsheet.py: render a 16x16 text font from a VRAM dump as labelled glyphs, for reading tile codes.

    python -X utf8 tools/fontsheet.py VRAM.bin OUT.png [--chr 0xA000] [--first 0] [--count 0x400] [--mode ...] [--bpp 2|4]

full:   BG3 dialogue font: glyph N = tiles N,N+1 (top) N+2,N+3 (bottom), step 4 (the text engine's code N).
narrow: BG3 8x16 glyph = tile N over N+1 (code N|0x2000), step 2.
grid:   BG1 font (4bpp): glyph N = tiles N,N+1 / N+16,N+17 (16-tile-wide sheet), codes step 2 within a row pair.
"""
import argparse

from PIL import Image, ImageDraw


def tile(vram, chr_base, n, bpp):
    size = 8 * bpp
    b = vram[chr_base + n * size: chr_base + n * size + size]
    return [[sum(((b[16 * (p // 2) + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(bpp)) for x in range(8)]
            for y in range(8)]


def codes_for(mode, first, count):
    return list(range(first, first + count, 4 if mode == "full" else 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vram")
    ap.add_argument("out")
    ap.add_argument("--chr", type=lambda s: int(s, 0), default=0xA000)
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=0x400)
    ap.add_argument("--mode", choices=("full", "narrow", "grid"), default="full")
    ap.add_argument("--bpp", type=int, default=2)
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    vram = open(a.vram, "rb").read()
    layout = {"full": [(0, 0, 0), (1, 8, 0), (2, 0, 8), (3, 8, 8)], "narrow": [(0, 0, 0), (1, 0, 8)],
              "grid": [(0, 0, 0), (1, 8, 0), (16, 0, 8), (17, 8, 8)]}[a.mode]
    if a.mode == "grid":
        codes = [n for n in range(a.first, a.first + a.count, 2) if not (n & 0x10)]
    else:
        codes = codes_for(a.mode, a.first, a.count)
    cols, cw, ch = 16, 44, 32
    img = Image.new("RGB", (cols * cw, ((len(codes) + cols - 1) // cols) * ch), (40, 40, 60))
    d = ImageDraw.Draw(img)
    grey = [(i * 17, i * 17, i * 17) for i in range(16)]
    pal = [(0, 0, 0), (255, 255, 255), (160, 160, 160), (90, 90, 200)] if a.bpp == 2 else grey
    for i, n in enumerate(codes):
        ox, oy = (i % cols) * cw, (i // cols) * ch
        d.text((ox + 1, oy), "%03X" % n, fill=(255, 220, 0))
        for k, tx, ty in layout:
            for y, row in enumerate(tile(vram, a.chr, n + k, a.bpp)):
                for x, c in enumerate(row):
                    img.putpixel((ox + 20 + tx + x, oy + ty + y), pal[c])
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    img.save(a.out)


if __name__ == "__main__":
    main()
