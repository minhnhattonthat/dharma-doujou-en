"""text.py: codec for Dharma Doujou's 16-bit text words (docs/re/text.md).

Each word is a tile code with mode bits (see the tables), or a control. Two engines:
- tbl/jp.tbl (main messages, BG3): controls are words >= 0x8000, high byte = code, low byte = argument
  ("#!ctrl-hibyte" in the table), {end} = 80xx, {rep:nn} takes the next word as operand.
- tbl/jp2.tbl (BG1 screens): controls are listed in the table as exact words (FFFF={end}, FF04={c04}).
Unknown words decode as [XXXX] and encode back, so encode(decode(w)) == w for every string.
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# engine 1: control code high byte -> name; low byte is the argument, written {name:XX} unless it is 00
CTRL = {0x80: "end", 0x81: "nl", 0x82: "down", 0x83: "wait", 0x84: "key", 0x85: "page", 0x86: "rep", 0x87: "mode"}
CTRL_BY_NAME = {v: k for k, v in CTRL.items()}
TOKEN = re.compile(r"\{(\w+)(?::([0-9A-Fa-f]{2}))?\}|\[([0-9A-Fa-f]{4})\]")
CTRL_VAL = re.compile(r"\{(\w+)\}$")


class Codec:
    def __init__(self, lines):
        self.dec, self.enc, self.cdec, self.cenc = {}, {}, {}, {}
        self.hibyte = False
        for n, line in enumerate(lines, 1):
            line = line.rstrip("\r\n")
            if line.startswith("#!ctrl-hibyte"):
                self.hibyte = True
            if not line or line.startswith("#"):
                continue
            key, sep, val = line.partition("=")
            val = " " if val == r"\s" else val
            if not sep or not val or len(key) != 4:
                raise ValueError(f"table line {n}: bad entry {line!r}")
            w = int(key, 16)
            if w in self.dec or w in self.cdec:
                raise ValueError(f"table line {n}: duplicate code {key}")
            m = CTRL_VAL.match(val)
            if m:
                self.cdec[w], self.cenc[m[1]] = m[1], w
                continue
            if val in self.enc:
                raise ValueError(f"table line {n}: duplicate value {val!r}")
            self.dec[w], self.enc[val] = val, w
        self.maxlen = max(map(len, self.enc), default=1)

    @classmethod
    def load(cls, path=ROOT / "tbl" / "jp.tbl"):
        return cls(Path(path).read_text(encoding="utf-8-sig").splitlines())

    def is_end(self, w):
        return w >> 8 == 0x80 if self.hibyte else self.cdec.get(w) == "end"

    def decode_words(self, words):
        out = []
        for w in words:
            if w in self.cdec:
                out.append("{%s}" % self.cdec[w])
            elif self.hibyte and w >= 0x8000 and (w >> 8) in CTRL:
                name = CTRL[w >> 8]
                out.append("{%s}" % name if w & 0xFF == 0 else "{%s:%02X}" % (name, w & 0xFF))
            elif w in self.dec:
                out.append(self.dec[w])
            else:
                out.append("[%04X]" % w)
        return "".join(out)

    def read_words(self, data, off):
        """Words from off through the end word; engine 1's {rep} takes the next word as its operand."""
        words = []
        while True:
            w = struct.unpack_from("<H", data, off)[0]
            words.append(w)
            off += 2
            if self.is_end(w):
                return words
            if self.hibyte and w >> 8 == 0x86:
                words.append(struct.unpack_from("<H", data, off)[0])
                off += 2

    def decode_at(self, data, off):
        return self.decode_words(self.read_words(data, off))

    def encode_words(self, text):
        words, i = [], 0
        while i < len(text):
            m = TOKEN.match(text, i)
            if m:
                if m[3]:
                    words.append(int(m[3], 16))
                elif m[1] in self.cenc and not m[2]:
                    words.append(self.cenc[m[1]])
                elif self.hibyte and m[1] in CTRL_BY_NAME:
                    words.append(CTRL_BY_NAME[m[1]] << 8 | int(m[2] or "0", 16))
                else:
                    raise ValueError(f"unknown control {m[0]} in {text!r}")
                i = m.end()
                continue
            for k in range(min(self.maxlen, len(text) - i), 0, -1):
                if text[i:i + k] in self.enc:
                    words.append(self.enc[text[i:i + k]])
                    i += k
                    break
            else:
                raise ValueError(f"cannot encode {text[i]!r} in {text!r}")
        return words

    def encode(self, text):
        return b"".join(struct.pack("<H", w) for w in self.encode_words(text))
