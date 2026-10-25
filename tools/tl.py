"""tl.py: the authored English script (script/en.tsv) -> script/*.json "en", plus the reviewer's pairs file.

    python -X utf8 tools/tl.py units            # every translatable unit: key, box, columns, JP (display form)
    python -X utf8 tools/tl.py merge            # check en.tsv, write "en" into script/*.json, run the lint
    python -X utf8 tools/tl.py pairs OUT        # reviewer pairs file: >> key | JP / EN, +-2 context units

en.tsv: `key<TAB>English`, one line per unit, `#` lines are comments.
- Paged units (story box msg 15-19, 48-55; master bubble msg 36) are one JP page each, key `msg:15.2` = page 2.
  The English is wrapped to the box (26 or 15 columns, 2 lines a page); ` / ` forces a line break, ` // ` a page
  break; extra pages are added with the script's own key-wait + clear sequence (D4: add pages, don't cut). The JP
  page's {mode}/{page} prefix stays at the start of its first English page.
- Every other unit is the raw string without the final {end} (control codes as in the JP). msg 9/10 keep their
  picture tail. Engine-2 `{sp4}` slots (a number or rank the code draws at a fixed column) must start at the same
  column as in the JP.
"""
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402
from text import Codec  # noqa: E402

TSV = ROOT / "script" / "en.tsv"
SEP = {"story": "{key}{page}{rep:1A} {nl}{nl}{nl}{rep:1A} ", "master": "{key}{page}{rep:0F} {nl}{nl}{rep:0F} "}
NL = {"story": "{nl}{nl}{nl}", "master": "{nl}{nl}"}
PREFIX = re.compile(r"^((?:\{page\}|\{mode:[0-9A-F]{2}\})*)")
SUFFIX = re.compile(r"((?:\{key\})?(?:\{page\})*\{end\})?$")
MODE = re.compile(r"\{mode:[0-9A-F]{2}\}")
# kept as the JP: digits drawn by index, debug title, credits except the EXECTIVE typo, an empty string
KEEP = {"msg": set(range(21, 22)) | set(range(38, 48)) | set(range(65, 91)),
        "screen": set(range(0, 10)) | {26}}


def load(block):
    return json.loads((ROOT / "script" / f"{block}.json").read_text(encoding="utf-8"))


def segments(jp, box):
    """JP paged string -> [(prefix, body, suffix)]; body '' = a page with no text (kept as is)."""
    out = []
    for seg in jp.split(SEP[box]):
        pre = PREFIX.match(seg)[1]
        rest = seg[len(pre):]
        suf = SUFFIX.search(rest)[1] or ""
        body = rest[:len(rest) - len(suf)]
        pre += "".join(MODE.findall(body))  # a mode switch inside a page moves to the page start
        out.append((pre, MODE.sub("", body), suf))
    return out


def show(s, box=None):
    """JP/EN display form: line breaks as ' / ', layout codes dropped."""
    s = s.replace(NL.get(box, "{nl}{nl}{nl}"), " / ") if box else s
    return re.sub(r"\{(?:end|page|key|mode:..)\}", "", s)


def units():
    """[(key, block, id, box, jp display)] in script order."""
    out = []
    for block in ("msg", "screen"):
        for e in load(block):
            i, box = e["id"], lint.box_of(block, e["id"])
            if i in KEEP[block] or e.get("alias") is not None:  # an alias is built from its first id's text
                continue
            if box in SEP:
                for n, (_, body, _) in enumerate(segments(e["jp"], box), 1):
                    if body.strip():
                        out.append((f"{block}:{i}.{n}", block, i, box, show(body, box)))
            else:
                out.append((f"{block}:{i}", block, i, box, show(e["jp"].split("{nl}")[0] if i in (9, 10) and block == "msg"
                                                                else e["jp"])))
    return out


def wrap(en, box):
    cols, per = lint.BOXES[box][:2]
    pages = []
    for forced in en.split(" // "):
        lines = []
        for part in forced.split(" / "):
            w = textwrap.wrap(part, cols, break_long_words=False, break_on_hyphens=False)
            if not w or max(map(len, w)) > cols:
                raise ValueError(f"cannot wrap {part!r} to {cols} columns")
            lines += w
        pages += [NL[box].join(lines[k:k + per]) for k in range(0, len(lines), per)]
    return (SEP[box] + "{page}").join(pages)


def slot_cols(text, engine2):
    """Start column of each {sp4} slot. JP widths: 16x16 glyph 2 columns, narrow/8x8 1; EN: 1 per character."""
    cols, col = [], 0
    if engine2 is None:
        for m in re.finditer(r"\{sp(\d)\}|\{\w+\}|(.)", text):
            if m[1] == "4":
                cols.append(col)
            col += int(m[1]) if m[1] else (1 if m[2] else 0)
        return cols
    for w in engine2.encode_words(text):
        if w >> 8 == 0xFF and w != 0xFFFF:
            if w & 0xFF == 4:
                cols.append(col)
            col += w & 0xFF
        elif w < 0x8000:
            col += 2 if w & 0x6000 == 0 else 1
    return cols


def read_tsv():
    tr = {}
    for n, line in enumerate(TSV.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        key, sep, en = line.partition("\t")
        if not sep or "\t" in en:
            raise SystemExit(f"en.tsv line {n}: want key<TAB>English")
        if key in tr:
            raise SystemExit(f"en.tsv line {n}: duplicate key {key}")
        tr[key] = en
    return tr


def compose(tr):
    """{block: {id: en string}} from the TSV; errors for missing/extra keys, non-ASCII, slot moves."""
    errs, out = [], {"msg": {}, "screen": {}}
    us = units()
    keys = {u[0] for u in us}
    errs += [f"{k}: not a unit" for k in tr if k not in keys]
    errs += [f"{k}: missing" for k in sorted(keys - set(tr))]
    errs += [f"{k}: non-ASCII {sorted(set(c for c in v if ord(c) > 126))}" for k, v in tr.items()
             if any(ord(c) > 126 for c in v)]
    if errs:
        return errs, out
    jp2 = Codec.load(ROOT / "tbl" / "jp2.tbl")
    for block in ("msg", "screen"):
        for e in load(block):
            i, box, jp = e["id"], lint.box_of(block, e["id"]), e["jp"]
            if box in SEP:
                segs = segments(jp, box)
                parts = []
                for n, (pre, body, suf) in enumerate(segs, 1):
                    try:
                        en = wrap(tr[f"{block}:{i}.{n}"], box) if body.strip() else body
                        if SEP[box] in en:
                            print(f"note: {block}:{i}.{n} takes {en.count(SEP[box]) + 1} pages")
                        parts.append(pre + en + suf)
                    except ValueError as x:
                        errs.append(f"{block}:{i}.{n}: {x}")
                out[block][i] = SEP[box].join(parts)
            elif f"{block}:{i}" in tr:
                en = tr[f"{block}:{i}"]
                if block == "screen" and slot_cols(en, None) != slot_cols(jp, jp2):
                    errs.append(f"{block}:{i}: {{sp4}} slots at columns {slot_cols(en, None)}, JP has them at "
                                f"{slot_cols(jp, jp2)} (the code draws there)")
                # msg 9/10 keep the JP picture tail unless en.tsv gives its own (G2: the pictures redrawn as words)
                tail = jp[jp.index("{nl}"):-len("{end}")] if block == "msg" and i in (9, 10) and "{nl}" not in en \
                    else ""
                out[block][i] = en + tail + "{end}"
    return errs, out


def merge():
    errs, out = compose(read_tsv())
    if errs:
        print("\n".join(errs))
        sys.exit(f"tl: {len(errs)} errors, nothing written")
    for block, by_id in out.items():
        items = load(block)
        for e in items:
            e["en"] = by_id.get(e["id"], "")  # en.tsv is the only source of "en"
        (ROOT / "script" / f"{block}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8", newline="\n")
    errs, warns = lint.run()
    print("\n".join(errs))
    print(f"tl: merged {sum(map(len, out.values()))} strings; lint {len(errs)} errors, {len(warns)} guessed-box warnings")
    sys.exit(1 if errs else 0)


def pairs(path):
    tr = read_tsv()
    us = units()
    lines = []
    for n, (key, _, _, box, jp) in enumerate(us):
        for k in range(max(0, n - 2), min(len(us), n + 3)):
            if k == n:
                lines.append(f">> {key} [{box}] | {jp}\n   EN: {tr.get(key, '(missing)')}")
            elif abs(k - n) <= 2 and us[k][1:3] == us[n][1:3]:
                lines.append(f"   ({us[k][0]}) {us[k][4]} -> {tr.get(us[k][0], '')}")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"{path}: {len(us)} units")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "units"
    if cmd == "units":
        for key, _, _, box, jp in units():
            print(f"{key}\t{box}\t{lint.BOXES[box][0] if box else ''}\t{jp}")
    elif cmd == "merge":
        merge()
    elif cmd == "pairs":
        pairs(sys.argv[2])
    else:
        sys.exit(__doc__)
