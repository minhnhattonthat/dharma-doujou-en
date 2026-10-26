"""gfx.py: English redraws of graphics text (docs/re/graphics.md, G-rows), from PPU dumps of the screens.

    python -X utf8 tools/gfx.py dump SCENE.. [--hold 900 --every 30 --mash 0]  # warp + PPU dumps -> work/gfx/dumps/SCENE/
    python -X utf8 tools/gfx.py show PREFIX OUT.png [--rect x,y,w,h]   # layers of one dump, 8 px grid, owner of rect
    python -X utf8 tools/gfx.py gen [NAME ..]                          # apply EDITS (tools/gfx_edits.py) -> gfx/*.png
    python -X utf8 tools/gfx.py preview NAME OUT.png                   # dump's screen region before / after

An edit names a dump (a PPU dump of the screen), a layer (bg1 bg2 bg3 obj) and a screen rect. The cells of that
layer inside the rect are traced to their tiles in VRAM and from there to a compressed resource (tools/rle.py):
the resource whose decoded bytes sit at that VRAM address in the dump. The Japanese pixels in the rect are
painted over and the English drawn, in the screen layout, then written back to those resource tiles.
gen writes each changed resource as gfx/resNN.png (index image, grey = index * 255 / (2^bpp - 1), 16 tiles a row);
the build (patch()) re-encodes those and writes them in place, or in free space with the table repointed.
A tile that the rect shares with a cell outside it may not change: gen stops with the cell named.
"""
import argparse
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rle  # noqa: E402

ORIG = ROOT / "rom" / "Dharma Doujou (Japan).sfc"
OUT_DIR = ROOT / "gfx"
DUMPS = ROOT / "work" / "gfx" / "dumps"
NRES = 83  # resources 0-82 decode; 83+ are empty entries (docs/re/graphics.md)
RAW_BLOCK = 0x800  # raw-tile edits are kept as pngs of this many bytes (64 4bpp tiles)
OBJ_SIZES = [(8, 16), (8, 32), (8, 64), (16, 32), (16, 64), (32, 64), (16, 32), (16, 32)]


# ---- PPU dumps

class Dump:
    def __init__(self, prefix):
        self.prefix = str(prefix)
        self.vram = bytearray(open(self.prefix + ".vram.bin", "rb").read())
        self.pal = open(self.prefix + ".pal.bin", "rb").read()
        self.oam = open(self.prefix + ".oam.bin", "rb").read()
        self.reg = dict(ln.split("=", 1) for ln in open(self.prefix + ".ppu.txt").read().split("\n") if "=" in ln)

    def r(self, k):
        v = self.reg["ppu." + k]
        return {"true": 1, "false": 0}.get(v, None) if v in ("true", "false") else int(v)

    def colour(self, pal, idx, bpp, obj=False):
        n = (128 if obj else 0) + pal * (1 << bpp) + idx
        c = struct.unpack_from("<H", self.pal, 2 * n)[0]
        return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)

    def cells(self, layer):
        """[(sx, sy, byte addr, bpp, pal, hflip, vflip)] of the layer's visible 8x8 cells, front first for obj."""
        if layer == "obj":
            return self.obj_cells()
        assert self.r("bgMode") == 1, f"{self.prefix}: BG mode {self.r('bgMode')}, mode 1 only"
        n = {"bg1": 0, "bg2": 1, "bg3": 2}[layer]
        if not (self.r("mainScreenLayers") | self.r("subScreenLayers")) >> n & 1:
            return []  # layer off: its leftover tilemap shows nothing
        bpp = 2 if n == 2 else 4
        L = f"layers[{n}]."
        chr_, tmap = self.r(L + "chrAddress") * 2, self.r(L + "tilemapAddress") * 2
        dw, dh = self.r(L + "doubleWidth"), self.r(L + "doubleHeight")
        hs, vs = self.r(L + "hscroll"), self.r(L + "vscroll")
        w, h = 32 * (1 + dw), 32 * (1 + dh)
        out = []
        for cy in range(h):
            for cx in range(w):
                sx, sy = (cx * 8 - hs) % (w * 8), (cy * 8 - vs) % (h * 8)
                if sx > 255 or sy > 223:
                    continue
                scr = (cx // 32) + (cy // 32) * (2 if dw else 1)
                e = struct.unpack_from("<H", self.vram, (tmap + scr * 0x800 + ((cy % 32) * 32 + cx % 32) * 2)
                                       & 0xFFFF)[0]
                out.append((sx, sy, (chr_ + (e & 0x3FF) * 8 * bpp) & 0xFFFF, bpp, e >> 10 & 7, e >> 14 & 1,
                            e >> 15 & 1))
        return out

    def obj_cells(self):
        base, off = self.r("oamBaseAddress") * 2, self.r("oamAddressOffset") * 2
        small, large = OBJ_SIZES[self.r("oamMode")]
        out = []
        for i in range(128):
            x, y, t, at = self.oam[4 * i:4 * i + 4]
            hi = self.oam[512 + i // 4] >> (i % 4 * 2)
            x |= (hi & 1) << 8
            x = x - 512 if x >= 256 else x
            size = large if hi & 2 else small
            y = y - 256 if y + size > 256 else y
            if y >= 224 or y + size <= 0 or x + size <= 0:
                continue
            t |= (at & 1) << 8
            pal, hf, vf = at >> 1 & 7, at >> 6 & 1, at >> 7 & 1
            n = size // 8
            for r in range(n):
                for c in range(n):
                    tc, tr = (n - 1 - c if hf else c), (n - 1 - r if vf else r)
                    tile = (t & 0x100) | ((((t >> 4) + tr) & 0xF) << 4) | ((t + tc) & 0xF)
                    addr = (base + (tile & 0xFF) * 32 + (off if tile & 0x100 else 0)) & 0xFFFF
                    out.append((x + 8 * c, y + 8 * r, addr, 4, pal, hf, vf))
        return out


def tile_get(buf, addr, bpp):
    return [[sum(((buf[addr + 16 * (p // 2) + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(bpp))
             for x in range(8)] for y in range(8)]


def tile_put(buf, addr, bpp, px):
    for y in range(8):
        for p in range(bpp):
            buf[addr + 16 * (p // 2) + 2 * y + (p & 1)] = sum(((px[y][x] >> p) & 1) << (7 - x) for x in range(8))


# ---- resources in VRAM

_res = {}


def resource(orig, r):
    if r == "rom":  # raw tiles: the ROM itself
        return orig
    if r not in _res:
        _res[r] = rle.decode(orig, r)[0]
    return _res[r]


def placements(dump, orig):
    """{resource: VRAM byte base} for every resource whose tiles mostly sit at one tile-aligned spot in the dump."""
    out = {}
    for r in range(NRES):
        data = resource(orig, r)
        tiles = [i for i in range(0, len(data) - 31, 32) if any(data[i:i + 32])]
        if not tiles:
            continue
        best = (0, None)
        probe = data[tiles[0]:tiles[0] + 32]
        pos = dump.vram.find(probe)
        while pos >= 0:
            base = pos - tiles[0]
            if base % 16 == 0 and base >= 0:
                hits = sum(dump.vram[base + i:base + i + 32] == data[i:i + 32] for i in tiles if base + i + 32 <= 0x10000)
                best = max(best, (hits, base), key=lambda b: b[0])
            pos = dump.vram.find(probe, pos + 1)
        if best[1] is not None and best[0] * 2 >= len(tiles):
            out[r] = best[1]
    return out


def owner(place, orig, addr, bpp, vram=None):
    """(resource, byte offset) holding the tile at VRAM addr: the resource placed there, if its bytes still match
    (vram given); else the only match anywhere. None when unknown or ambiguous (see candidates())."""
    c = candidates(place, orig, addr, bpp, vram)
    return c[0] if len(c) == 1 else None


def candidates(place, orig, addr, bpp, vram=None):
    """Every (source, byte offset) whose tile equals the VRAM tile at addr: the resource placed there, other
    resources (a part DMA'd on its own), raw ROM tiles (the よーい / どん sprites at 0xCA000). A plain tile (solid
    colour) can match several; apply() then takes the one in line with the rest of the rect."""
    for r, base in place.items():
        if base <= addr and addr + 8 * bpp <= base + len(resource(orig, r)):
            off = addr - base
            if vram is None or resource(orig, r)[off:off + 8 * bpp] == vram[addr:addr + 8 * bpp] and any(
                    vram[addr:addr + 8 * bpp]):
                return [(r, off)]  # the resource loaded there wins over identical copies elsewhere
    if vram is None or not any(vram[addr:addr + 8 * bpp]):
        return []
    tile = bytes(vram[addr:addr + 8 * bpp])
    hits = [(r, i) for r in range(NRES) for i in find_all(resource(orig, r), tile, bpp)]
    return hits + [("rom", i) for i in find_all(orig, tile, 1) if i % 16 == 0]


def pick(cands_by_cell):
    """{cell: candidates} -> {cell: (source, offset)}: every cell takes the candidate whose (source, offset - VRAM
    address) agrees with the most cells, so a solid tile that also occurs elsewhere follows its neighbours."""
    from collections import Counter
    votes = Counter((src, off - addr) for (addr, _), cands in cands_by_cell.items() for src, off in cands)
    out = {}
    for (addr, key), cands in cands_by_cell.items():
        if cands:
            src, off = max(cands, key=lambda c: votes[(c[0], c[1] - addr)])
            out[(addr, key)] = (src, off)
        elif votes:  # an empty tile: where the rect's main source would have it (apply() checks it is empty)
            src, delta = votes.most_common(1)[0][0]
            out[(addr, key)] = (src, addr + delta)
    return out


def find_all(data, tile, bpp):
    i = data.find(tile)
    while i >= 0:
        if i % (8 * bpp) == 0:
            yield i
        i = data.find(tile, i + 1)


# ---- drawing

FONTS = {"sans": "LiberationSans-Bold.ttf", "serif": "LiberationSerif-Bold.ttf"}


def text_mask(text, height, width, font="sans", gap=1, bitmap=False, bold=0):
    """1-bit mask (list of rows) of text, its cap height scaled to about `height` px, squeezed to fit `width`."""
    if bitmap:  # fonts/en8x16.txt (True) or fonts/en_cond.txt ("cond"), 13 rows
        import font as en
        gl = en.parse(en.COND, None) if bitmap == "cond" else en.parse(en.SRC)
        cols = []
        for ch in text:
            if ch == " ":
                cols += [[0] * 13] * 3
                continue
            g = gl[ch]
            xs = [x for row in g for x, p in enumerate(row) if p]
            cols += [[g[y][x] for y in range(13)] for x in range(min(xs), max(xs) + 1)] + [[0] * 13] * gap
        rows = [[cols[x][y] for x in range(len(cols) - gap)] for y in range(13)]
        while rows and not any(rows[-1]):
            rows.pop()
    else:
        f = ImageFont.truetype(str(ROOT / "fonts" / FONTS[font]), 200)
        top = f.getbbox("H")[1]
        bot = f.getbbox("H")[3]
        scale = height / (bot - top)
        f = ImageFont.truetype(str(ROOT / "fonts" / FONTS[font]), max(6, round(200 * scale)))
        img = Image.new("1", (2000, 400), 0)
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        x = 0
        for ch in text:
            d.text((x, 50), ch, font=f, fill=1)
            x += f.getlength(ch) + gap
        bb = img.getbbox()
        img = img.crop(bb)
        rows = [[img.getpixel((x, y)) for x in range(img.width)] for y in range(img.height)]
    for _ in range(bold):
        rows = [[p or (x > 0 and r[x - 1]) for x, p in enumerate(r)] + [r[-1]] for r in rows]
    if len(rows[0]) > width:
        im = Image.new("1", (len(rows[0]), len(rows)))
        im.putdata([p for r in rows for p in r])
        im = im.resize((width, len(rows)), Image.NEAREST)
        rows = [[im.getpixel((x, y)) for x in range(width)] for y in range(len(rows))]
    return [[int(bool(p)) for p in r] for r in rows]


def shear_mask(m, slope):
    """Each column moved up slope px per px to the right (whole pixels, so strokes stay crisp)."""
    h, w = len(m), len(m[0])
    lift = [round(x * slope) for x in range(w)]
    top = max(lift)
    out = [[0] * w for _ in range(h + top)]
    for y in range(h):
        for x in range(w):
            out[y + top - lift[x]][x] = m[y][x]
    return out


def draw(canvas, e, tex=None):
    """Paint edit e on canvas (rows of indices, the rect): erase the Japanese, then the English lines.
    tex(x, y): the background pixel at canvas (x, y) (edit key "tex": a clean patch of a periodic texture)."""
    h, w = len(canvas), len(canvas[0])
    erase = set(e.get("erase", ()))
    keep = [[p not in erase for p in row] for row in canvas]
    for _ in range(e.get("halo", 0)):  # also erase n px around the Japanese (a glow drawn in background colours)
        keep = [[keep[y][x] and all(keep[yy][xx] for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
                                    if 0 <= yy < h and 0 <= xx < w) for x in range(w)] for y in range(h)]
    if tex:
        for y in range(h):
            for x in range(w):
                if not keep[y][x]:
                    canvas[y][x] = tex(x, y)
    elif "fill" in e:
        for y in range(h):
            for x in range(w):
                if not keep[y][x]:
                    canvas[y][x] = e["fill"]
    else:  # inpaint: the nearest kept pixel up or down the column, else along the row
        src = [row[:] for row in canvas]
        for y in range(h):
            for x in range(w):
                if keep[y][x]:
                    continue
                for d in range(1, max(h, w)):
                    col = [src[yy][x] for yy in (y - d, y + d) if 0 <= yy < h and keep[yy][x]]
                    row = [src[y][xx] for xx in (x - d, x + d) if 0 <= xx < w and keep[y][xx]]
                    hits = (row or col) if e.get("grain") == "h" else (col or row)  # along a horizontal grain
                    if hits:
                        canvas[y][x] = hits[0]
                        break
    if not e["text"]:
        return canvas
    lines = e["text"].split("\n")
    pad = e.get("pad", 1)
    cap = e.get("cap") or (h - 2 * pad - (len(lines) - 1) * e.get("lead", 2)) // len(lines) - 2 * bool(e.get("edge"))
    masks = [text_mask(t, cap, w - 2 * pad - 2 * bool(e.get("edge")), e.get("font", "sans"), e.get("gap", 1),
                       e.get("bitmap", False), e.get("bold", 0)) for t in lines]
    if e.get("shear"):  # text on a slanted sign
        masks = [shear_mask(m, e["shear"]) for m in masks]
    total = sum(len(m) for m in masks) + (len(lines) - 1) * e.get("lead", 2)
    y0 = (h - total) // 2 + e.get("dy", 0)
    for m in masks:
        mw = len(m[0])
        x0 = {"c": (w - mw) // 2, "l": pad + bool(e.get("edge")), "r": w - pad - mw - bool(e.get("edge"))}[
            e.get("align", "c")] + e.get("dx", 0)
        ink = set()
        for y, row in enumerate(m):
            for x, p in enumerate(row):
                if p:
                    ink.add((x0 + x, y0 + y))
        if e.get("shadow") is not None:
            for x, y in ink:
                for xx, yy in ((x + 1, y + 1),) + (((x + 1, y), (x, y + 1)) if e.get("shadow_full") else ()):
                    if (xx, yy) not in ink and 0 <= yy < h and 0 <= xx < w:
                        canvas[yy][xx] = e["shadow"]
        if e.get("edge2") is not None:  # an outer ring around the edge ring
            n = e.get("edge_w", 1) + 1
            ring = {(x + dx, y + dy) for x, y in ink for dx in range(-n, n + 1) for dy in range(-n, n + 1)
                    if abs(dx) + abs(dy) <= n + 1} - ink
            for x, y in ring:
                if 0 <= y < h and 0 <= x < w:
                    canvas[y][x] = e["edge2"]
        if e.get("edge") is not None:
            n = e.get("edge_w", 1)
            ring = {(x + dx, y + dy) for x, y in ink for dx in range(-n, n + 1) for dy in range(-n, n + 1)
                    if abs(dx) + abs(dy) <= n + 1} - ink
            for x, y in ring:
                if 0 <= y < h and 0 <= x < w:
                    canvas[y][x] = e["edge"]
        for x, y in ink:
            if 0 <= y < h and 0 <= x < w:
                canvas[y][x] = e["ink"] if not isinstance(e["ink"], list) else e["ink"][
                    min(len(e["ink"]) - 1, (y - y0) * len(e["ink"]) // len(m))]
        y0 += len(m) + e.get("lead", 2)
    return canvas


# ---- edits -> resources

BPP = {}  # resource -> bits per pixel, as apply() met it


def load_edits():
    import gfx_edits
    return gfx_edits.EDITS


def apply(orig, edits, data):
    """data: {resource: bytearray} (updated in place). Returns {name: (before, after, dump, layer, rect)}."""
    shown = {}
    for e in edits:
        if "pics" in e or "grid" in e:
            shown[e["name"]] = apply_pics(orig, e, data)
            continue
        d = Dump(DUMPS / e["dump"])
        place = placements(d, orig)
        rx, ry, rw, rh = e["rect"]
        mine, others = [], []
        for layer in ("bg1", "bg2", "bg3", "obj"):
            for c in d.cells(layer):
                inside = layer == e["layer"] and rx <= c[0] + 7 and c[0] < rx + rw and ry <= c[1] + 7 and c[1] < ry + rh
                (mine if inside else others).append((layer,) + c)
        canvas = [[0] * rw for _ in range(rh)]
        cands = {(addr, (sx, sy)): candidates(place, orig, addr, bpp, d.vram)
                 for layer, sx, sy, addr, bpp, *_ in mine}
        chosen = pick(cands)
        cellpx, blank = {}, []
        for layer, sx, sy, addr, bpp, pal, hf, vf in reversed(mine):
            got = chosen.get((addr, (sx, sy)))
            if got and not any(d.vram[addr:addr + 8 * bpp]) and (
                    not 0 <= got[1] <= len(resource(orig, got[0])) - 8 * bpp
                    or any(resource(orig, got[0])[got[1]:got[1] + 8 * bpp])):
                got = None  # an empty tile whose would-be source isn't empty: not this rect's
            if got is None:
                if any(d.vram[addr:addr + 8 * bpp]):
                    sys.exit(f"{e['name']}: cell {layer} ({sx},{sy}) tile 0x{addr:04X} is in no known resource")
                blank.append((sx, sy))  # an empty tile from elsewhere: nothing may be drawn here
                continue
            r, off = got
            px = tile_get(data.setdefault(r, bytearray(resource(orig, r))), off, bpp)
            BPP[r] = bpp
            px = [row[::-1] if hf else row for row in (px[::-1] if vf else px)]
            cellpx[(sx, sy)] = (r, off, bpp, hf, vf, addr)
            for y in range(8):
                for x in range(8):
                    if 0 <= sx + x - rx < rw and 0 <= sy + y - ry < rh:
                        canvas[sy + y - ry][sx + x - rx] = px[y][x]
        before = [row[:] for row in canvas]
        draw(canvas, e, texture(d, e) if "tex" in e else None)
        for sx, sy in blank:
            if any(canvas[y - ry][x - rx] for y in range(max(sy, ry), min(sy + 8, ry + rh))
                   for x in range(max(sx, rx), min(sx + 8, rx + rw))):
                sys.exit(f"{e['name']}: the English reaches the empty tile at ({sx},{sy}); shrink the text or rect")
        new = {}
        for (sx, sy), (r, off, bpp, hf, vf, addr) in cellpx.items():
            px = tile_get(data[r], off, bpp)
            px = [row[::-1] if hf else row for row in (px[::-1] if vf else px)]
            for y in range(8):
                for x in range(8):
                    if 0 <= sx + x - rx < rw and 0 <= sy + y - ry < rh:
                        px[y][x] = canvas[sy + y - ry][sx + x - rx]
            px = [row[::-1] if hf else row for row in (px[::-1] if vf else px)]
            if (r, off) in new and new[(r, off)][0] != px:
                sys.exit(f"{e['name']}: tile res{r}+0x{off:X} is used twice in the rect with different pixels "
                         f"(at {new[(r, off)][1]} and ({sx},{sy})); move the rect or split it")
            new[(r, off)] = (px, (sx, sy), addr)
        for (r, off), (px, at, vaddr) in new.items():
            if px == tile_get(data[r], off, bpp_of(e)):
                continue
            for layer, sx, sy, addr, bpp, *_ in ([] if e.get("shared") else others):
                if addr == vaddr:
                    sys.exit(f"{e['name']}: tile res{r}+0x{off:X} (cell {at}) is also shown at {layer} ({sx},{sy}) "
                             "outside the rect")
            tile_put(data[r], off, bpp_of(e), px)
        shown[e["name"]] = (before, canvas, d, e["layer"], e["rect"])
    return shown


def layer_pixels(d, layer):
    """{(x, y): index} of a layer as the dump shows it (front sprite wins)."""
    out = {}
    for sx, sy, addr, bpp, pal, hf, vf in reversed(d.cells(layer)):
        px = tile_get(d.vram, addr, bpp)
        px = [row[::-1] if hf else row for row in (px[::-1] if vf else px)]
        for y in range(8):
            for x in range(8):
                out[(sx + x, sy + y)] = px[y][x]
    return out


def texture(d, e):
    """tex(x, y) for edit e: e["tex"] = (x, y, w, h), a clean patch of the layer that repeats every w x h px."""
    tx, ty, tw, th = e["tex"]
    rx, ry = e["rect"][:2]
    pix = layer_pixels(d, e["layer"])
    return lambda x, y: pix[(tx + (rx + x - tx) % tw, ty + (ry + y - ty) % th)]


def apply_pics(orig, e, data):
    """Edit of engine-1 24x24 pictures (text code 6000|N = tiles N..N+8, 3x3 row-major, in font resources 1-4,
    0x100 tiles each): e["pics"] = picture codes side by side, drawn as one canvas."""
    cells = []
    if "pics" in e:
        for k, code in enumerate(e["pics"]):
            for t in range(9):
                n = (code & 0x1FFF) + t
                cells.append((24 * k + t % 3 * 8, t // 3 * 8, 1 + n // 0x100, n % 0x100 * 16))
    else:  # grid: (resource, rows of tile numbers), for tiles no dump shows (一 of 一本勝負)
        r, rows = e["grid"]
        cells = [(8 * x, 8 * y, r, t * 8 * bpp_of(e)) for y, row in enumerate(rows) for x, t in enumerate(row)]
    bpp = bpp_of(e)
    canvas = [[0] * (max(c[0] for c in cells) + 8) for _ in range(max(c[1] for c in cells) + 8)]
    for x0, y0, r, off in cells:
        px = tile_get(data.setdefault(r, bytearray(resource(orig, r))), off, bpp)
        BPP[r] = bpp
        for y in range(8):
            canvas[y0 + y][x0:x0 + 8] = px[y]
    before = [row[:] for row in canvas]
    draw(canvas, e)
    for x0, y0, r, off in cells:
        tile_put(data[r], off, bpp, [canvas[y0 + y][x0:x0 + 8] for y in range(8)])
    return before, canvas, Dump(DUMPS / e["dump"]) if "dump" in e else None, e.get("layer", "bg3"), None


def bpp_of(e):
    return 2 if "pics" in e or e.get("layer") == "bg3" else 4


def base(orig, r):
    """Resource r as the build should start from: its gfx/ png if there is one, else the original."""
    for rr, bpp, path in pngs()[0]:
        if rr == r:
            return from_png(path, resource(orig, r), bpp)
    return resource(orig, r)


def to_png(data, bpp, path):
    n = len(data) // (8 * bpp)
    img = Image.new("L", (128, (n + 15) // 16 * 8))
    for t in range(n):
        for y, row in enumerate(tile_get(data, t * 8 * bpp, bpp)):
            for x, p in enumerate(row):
                img.putpixel((t % 16 * 8 + x, t // 16 * 8 + y), p * 255 // ((1 << bpp) - 1))
    img.save(path)


def from_png(path, orig_data, bpp):
    img = Image.open(path).convert("L")
    out = bytearray(orig_data)
    for t in range(len(orig_data) // (8 * bpp)):
        px = [[round(img.getpixel((t % 16 * 8 + x, t // 16 * 8 + y)) * ((1 << bpp) - 1) / 255) for x in range(8)]
              for y in range(8)]
        tile_put(out, t * 8 * bpp, bpp, px)
    return bytes(out)


def pngs():
    """[(resource, bpp, path)] of gfx/res<NN>_<bpp>bpp.png, and [(file offset, bpp, path)] of
    gfx/rom_<OFFSET>_<bpp>bpp.png (raw tiles, RAW_BLOCK bytes each)."""
    out, raw = [], []
    for p in sorted(OUT_DIR.glob("*_*bpp.png")):
        m = re.fullmatch(r"(res|rom_)([0-9A-F]+)_(\d)bpp\.png", p.name)
        if m:
            (out if m[1] == "res" else raw).append((int(m[2], 10 if m[1] == "res" else 16), int(m[3]), p))
    return out, raw


def patch(rom, put, free):
    """Write every gfx/resNN png into rom (a build.py Rom): re-encoded in place, else in free space + repointed;
    and every gfx/rom_OFFSET png (raw tiles) in place."""
    import font
    fonts = {r for _, res, _, _ in font.ENGINES.values() for r, _ in res}
    res, raw = pngs()
    for off, bpp, path in raw:
        data = from_png(path, rom.orig[off:off + RAW_BLOCK], bpp)
        for i in range(0, RAW_BLOCK, 8 * bpp):  # changed tiles only, so the write log stays readable
            if data[i:i + 8 * bpp] != rom.orig[off + i:off + i + 8 * bpp]:
                put(off + i, data[i:i + 8 * bpp], f"gfx-rom-{off:X}")
    for r, bpp, path in res:
        if r in fonts:
            continue  # font.patch starts from base() and writes these
        orig_data, off, size_was = rle.decode(rom.orig, r)
        data = from_png(path, orig_data, bpp)
        if data == orig_data:
            continue
        bank = rom.orig[rle.TABLE + 3 * r + 2]
        blob = rle.encode(data, bank << 16 | 0x8000 | (off & 0x7FFF))
        if len(blob) > size_was:
            off = font.alloc(rom.orig, free, len(blob))
            bank = 0x80 | (off >> 15)
            blob = rle.encode(data, bank << 16 | 0x8000 | (off & 0x7FFF))
            put(rle.TABLE + 3 * r, struct.pack("<HB", 0x8000 | (off & 0x7FFF), bank), f"gfx-res{r}-ptr")
        put(off, blob, f"gfx-res{r}")


# ---- commands

def cmd_dump(a):
    from skill import SKILL
    probe = os.path.join(SKILL, "scripts", "lua", "probes", "ppudump.lua")
    cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "warp.py"), *a.scene, "--rom", a.rom, "--hold",
           str(a.hold), "--shot-every", str(a.every), "--out", str(DUMPS), "--script", probe,
           "--var", f"DUMP_EVERY={a.every}"] + (["--mash", str(a.mash)] if a.mash else [])
    sys.exit(subprocess.call(cmd))


def cmd_show(a):
    d = Dump(a.prefix)
    orig = ORIG.read_bytes()
    place = placements(d, orig)
    print("resources in VRAM:", " ".join(f"{r}@{b:04X}" for r, b in sorted(place.items(), key=lambda x: x[1])))
    img = Image.new("RGB", (2 * 264, 2 * 232), (40, 0, 40))
    for k, layer in enumerate(("bg1", "bg2", "bg3", "obj")):
        ox, oy = (k % 2) * 264, (k // 2) * 232
        for sx, sy, addr, bpp, pal, hf, vf in reversed(d.cells(layer)):
            px = tile_get(d.vram, addr, bpp)
            px = [row[::-1] if hf else row for row in (px[::-1] if vf else px)]
            for y in range(8):
                for x in range(8):
                    if px[y][x] and 0 <= sx + x < 256 and 0 <= sy + y < 224:
                        img.putpixel((ox + sx + x, oy + sy + y), d.colour(pal, px[y][x], bpp, layer == "obj"))
        ImageDraw.Draw(img).text((ox + 2, oy + 224), layer, fill=(255, 255, 0))
    if a.rect:
        rx, ry, rw, rh = a.rect
        for k in range(4):
            ox, oy = (k % 2) * 264, (k // 2) * 232
            ImageDraw.Draw(img).rectangle((ox + rx, oy + ry, ox + rx + rw - 1, oy + ry + rh - 1), outline=(255, 0, 0))
        for layer in ("bg1", "bg2", "bg3", "obj"):
            got = {}
            for sx, sy, addr, bpp, *_ in d.cells(layer):
                if rx <= sx + 7 and sx < rx + rw and ry <= sy + 7 and sy < ry + rh:
                    o = owner(place, orig, addr, bpp, d.vram)
                    if any(d.vram[addr:addr + 8 * bpp]):
                        got.setdefault(o and o[0], []).append(o[1] // (8 * bpp) if o else addr)
            for r, ts in got.items():
                print(f"{layer}: res {r}: tiles {' '.join('%X' % t for t in sorted(set(ts)))}")
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    img.save(a.out)


def cmd_gen(a):
    orig = ORIG.read_bytes()
    edits = load_edits()
    data = {}
    apply(orig, edits, data)
    OUT_DIR.mkdir(exist_ok=True)
    bpps = BPP
    for old in list(OUT_DIR.glob("res*_*bpp.png")) + list(OUT_DIR.glob("rom_*_*bpp.png")):
        old.unlink()
    for r, buf in sorted(data.items(), key=lambda kv: str(kv[0]).zfill(3)):
        if r == "rom":  # raw tiles: one png per changed RAW_BLOCK-byte block
            for off in sorted({i - i % RAW_BLOCK for i in range(len(orig)) if buf[i] != orig[i]}):
                path = OUT_DIR / f"rom_{off:06X}_{bpps.get(r, 4)}bpp.png"
                to_png(buf[off:off + RAW_BLOCK], bpps.get(r, 4), path)
                print("wrote", path.relative_to(ROOT))
        elif bytes(buf) != resource(orig, r):
            path = OUT_DIR / f"res{r:02d}_{bpps.get(r, 4)}bpp.png"
            to_png(buf, bpps.get(r, 4), path)
            print("wrote", path.relative_to(ROOT))


def cmd_preview(a):
    orig = ORIG.read_bytes()
    edits = [e for e in load_edits() if e["name"] in a.names] if a.names else load_edits()
    shown = apply(orig, load_edits(), {})
    rows = []
    for e in edits:
        before, after, d, layer, rect = shown[e["name"]]
        bpp = bpp_of(e)
        if d is None:  # pictures: grey by index
            colour = lambda p: (p * 255 // ((1 << bpp) - 1),) * 3  # noqa: E731
        else:
            pal = e.get("pal") if rect is None else e.get("pal", next(
                (c[4] for c in d.cells(layer) if rect[0] <= c[0] + 7 and c[0] < rect[0] + rect[2]
                 and rect[1] <= c[1] + 7 and c[1] < rect[1] + rect[3]), 0))
            colour = lambda p: d.colour(pal, p, bpp, layer == "obj")  # noqa: E731
        for img in (before, after):
            im = Image.new("RGB", (len(img[0]), len(img)))
            im.putdata([colour(p) for row in img for p in row])
            rows.append(im)
    w = max(im.width for im in rows) + 4
    out = Image.new("RGB", (w * 2, sum(im.height + 4 for im in rows[::2])), (255, 0, 255))
    y = 0
    for i in range(0, len(rows), 2):
        out.paste(rows[i], (0, y))
        out.paste(rows[i + 1], (w, y))
        y += rows[i].height + 4
    out.resize((out.width * a.zoom, out.height * a.zoom), Image.NEAREST).save(a.out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dump")
    p.add_argument("scene", nargs="+")
    p.add_argument("--rom", default=str(ORIG))
    p.add_argument("--hold", type=int, default=900)
    p.add_argument("--every", type=int, default=30)
    p.add_argument("--mash", type=int, default=0)
    p = sub.add_parser("show")
    p.add_argument("prefix")
    p.add_argument("out")
    p.add_argument("--rect", type=lambda s: [int(v) for v in s.split(",")])
    p.add_argument("--zoom", type=int, default=2)
    p = sub.add_parser("gen")
    p.add_argument("names", nargs="*")
    p = sub.add_parser("preview")
    p.add_argument("names", nargs="*")
    p.add_argument("--out", default=str(ROOT / "work" / "gfx" / "preview.png"))
    p.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    {"dump": cmd_dump, "show": cmd_show, "gen": cmd_gen, "preview": cmd_preview}[a.cmd](a)


if __name__ == "__main__":
    main()
