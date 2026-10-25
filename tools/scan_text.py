"""scan_text.py: find runs of 16-bit words that decode as Japanese text through tbl/jp.tbl, anywhere in the ROM.

    python -X utf8 tools/scan_text.py [--min 3] [--align 1|2]

Prints offset, length and the decoded run. Used in recon to find text outside the main message table.
"""
import argparse
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text import Codec, ROOT  # noqa: E402

JP = re.compile(r"[぀-ヿ一-鿿]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=str(ROOT / "rom" / "Dharma Doujou (Japan).sfc"))
    ap.add_argument("--min", type=int, default=3, help="minimum Japanese characters in a run")
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    c = Codec.load()
    for align in (0, 1):
        i = align
        while i + 1 < len(rom):
            j, words = i, []
            while j + 1 < len(rom):
                w = struct.unpack_from("<H", rom, j)[0]
                if w in c.dec or (w >> 8) in (0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87):
                    words.append(w)
                    j += 2
                    continue
                break
            s = c.decode_words(words)
            if len(JP.findall(s)) >= a.min:
                end = struct.unpack_from("<H", rom, j)[0] if j + 1 < len(rom) else 0
                print("%06X %3d end=%04X %s" % (i, len(words), end, s))
                i = j
            else:
                i += 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
