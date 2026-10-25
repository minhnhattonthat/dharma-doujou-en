"""ressheet.py: contact sheet of compressed graphics resources (tools/rle.py) as 4bpp or 2bpp tiles, for the
graphics-text survey.

    python -X utf8 tools/ressheet.py OUT.png FIRST LAST [--bpp 4] [--zoom 1]
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rle  # noqa: E402
from fontsheet import tile  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("first", type=int)
    ap.add_argument("last", type=int)
    ap.add_argument("--bpp", type=int, default=4)
    ap.add_argument("--zoom", type=int, default=1)
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Dharma Doujou (Japan).sfc").read_bytes()
    ids = list(range(a.first, a.last + 1))
    cell_w, cell_h = 128, 128 * 4 // a.bpp + 10
    img = Image.new("RGB", (cell_w * 4 + 12, cell_h * ((len(ids) + 3) // 4)), (60, 0, 60))
    d = ImageDraw.Draw(img)
    for n, i in enumerate(ids):
        data = rle.decode(rom, i)[0]
        ox, oy = (n % 4) * (cell_w + 4), (n // 4) * cell_h
        d.text((ox, oy), str(i), fill=(255, 255, 0))
        for t in range(min(len(data) // (8 * a.bpp), 1024 // a.bpp)):
            for y, row in enumerate(tile(data, 0, t, a.bpp)):
                for x, c in enumerate(row):
                    v = c * 255 // ((1 << a.bpp) - 1)
                    img.putpixel((ox + (t % 16) * 8 + x, oy + 10 + (t // 16) * 8 + y), (v, v, v))
    img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
