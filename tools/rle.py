"""rle.py: the game's graphics compression (decoder at $80:9D97, resource table at $87:8000; docs/re/graphics.md).

A resource is a 2-byte header (address of the even-byte stream, same bank) followed by the odd-byte stream.
Each stream: control byte c; 0 ends; 1-7F = literal run of 0x80-c bytes; 80-FF = 0x100-c copies of the next byte.
The even stream fills bytes 0,2,4..., the odd stream bytes 1,3,5...
"""
import struct

TABLE = 0x38000  # $87:8000, 3-byte entries (addr16, bank)


def lorom(addr):
    return ((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)


def entry(rom, idx):
    lo, bank = struct.unpack_from("<HB", rom, TABLE + 3 * idx)
    return lorom(bank << 16 | lo), bank


def decode_stream(rom, off):
    """-> (bytes, end offset)"""
    out = bytearray()
    while True:
        c = rom[off]
        off += 1
        if c == 0:
            return bytes(out), off
        if c < 0x80:
            n = 0x80 - c
            out += rom[off:off + n]
            off += n
        else:
            out += bytes([rom[off]]) * (0x100 - c)
            off += 1


def decode(rom, idx):
    """-> (data, file offset, total compressed size)"""
    off, bank = entry(rom, idx)
    even_addr = struct.unpack_from("<H", rom, off)[0]
    even, e_end = decode_stream(rom, lorom(bank << 16 | even_addr))
    odd, o_end = decode_stream(rom, off + 2)
    data = bytearray(max(len(even), len(odd)) * 2)
    data[0:2 * len(even):2] = even
    data[1:2 * len(odd):2] = odd
    return bytes(data), off, max(e_end, o_end) - off


def encode_stream(data):
    """Greedy: runs of 3+ equal bytes become run codes, the rest literals (max 127 per code)."""
    out, i, lit = bytearray(), 0, bytearray()

    def flush():
        while lit:
            chunk = lit[:127]
            out.append(0x80 - len(chunk))
            out.extend(chunk)
            del lit[:len(chunk)]

    while i < len(data):
        j = i
        while j < len(data) and data[j] == data[i] and j - i < 128:
            j += 1
        if j - i >= 3:
            flush()
            out += bytes([0x100 - (j - i), data[i]])
            i = j
        else:
            lit.append(data[i])
            i += 1
    flush()
    out.append(0)
    return bytes(out)


def encode(data, base_addr):
    """Resource bytes for `data`, to be placed at CPU address base_addr (the header holds the even stream's address)."""
    assert len(data) % 2 == 0
    odd = encode_stream(data[1::2])
    even = encode_stream(data[0::2])
    even_addr = (base_addr & 0xFFFF) + 2 + len(odd)
    assert even_addr <= 0xFFFF, "resource crosses a bank"
    return struct.pack("<H", even_addr) + odd + even


if __name__ == "__main__":
    import sys
    rom = open(sys.argv[1], "rb").read()
    n = (min(entry(rom, i)[0] for i in range(4)) - TABLE) // 3 if len(sys.argv) < 3 else int(sys.argv[2])
    for i in range(n):
        try:
            data, off, size = decode(rom, i)
            print("%3d %06X  %5d -> %5d" % (i, off, size, len(data)))
        except Exception as e:  # table may hold non-resource entries
            print("%3d error %s" % (i, e))
