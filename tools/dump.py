"""dump.py: extract both text blocks to script/<block>.json (docs/re/text.md).

    python -X utf8 tools/dump.py [--force]

One entry per string id: id, ptr (file offset), jp, en ("" = untranslated, the build falls back to jp), and
optionally alias (an id whose copy this one shares; translate that one) and note. An existing file is never
overwritten without --force; with --force the en and note fields already in it are kept by id.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

SCRIPT = build.ROOT / "script"
PICTURE = "24x24 picture tiles [63xx]: graphics, redrawn as English tiles (survey G2/G3); keep the words"
NOTES = {
    "msg": {**{i: PICTURE for i in (9, 10, *range(22, 30))},
            **{i: "digit drawn by index; keep" for i in range(38, 48)},
            21: "already English (debug screen)",
            **{i: "credits: romaji, keep (D3); fix only typos" for i in range(57, 90)},
            90: "already English"},
    "screen": {**{i: "big digit drawn by index; keep" for i in range(10)},
               26: "empty string"},
}


def entries(rom, block):
    name = block[0]
    offs = build.ptr_offsets(rom, block)
    first, out = {}, []
    for i, (off, jp) in enumerate(zip(offs, build.unpack(rom, block))):
        e = {"id": i, "ptr": "%05X" % off, "jp": jp, "en": ""}
        if first.setdefault(off, i) != i:
            e["alias"] = first[off]
        if i in NOTES.get(name, {}):
            e["note"] = NOTES[name][i]
        out.append(e)
    return out


def write(path, items):
    path.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rewrite existing files, keeping their en and note fields")
    a = ap.parse_args()
    build.check_rom.check()
    rom = build.ORIG_ROM.read_bytes()
    SCRIPT.mkdir(exist_ok=True)
    for block in build.BLOCKS:
        path = SCRIPT / f"{block[0]}.json"
        new = entries(rom, block)
        if path.exists():
            if not a.force:
                print(f"{path} exists, skipped (--force keeps en/note and rewrites jp/ptr)")
                continue
            old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
            for e in new:
                for k in ("en", "note"):
                    if old.get(e["id"], {}).get(k):
                        e[k] = old[e["id"]][k]
        write(path, new)
        print(f"{path}: {len(new)} strings")


if __name__ == "__main__":
    main()
