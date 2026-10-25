"""lint.py: check every translated string (script/*.json "en") against its box budget (docs/re/windows.md).

    python -X utf8 tools/lint.py          # exit 1 on any error; check.py runs it through tests/test_lint.py

Per string: encodable with the English table, no Japanese, ends in {end}, every drawn line within its box's
columns (one column per character, {rep:nn}+char = nn columns, {spN} = N), lines per page within the box. A box
still tagged "guess" makes a warning line for each string that uses it, so it gets measured before release.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402

JP = re.compile(r"[぀-ヿ㐀-鿿＀-￯]")
TOKEN = re.compile(r"\{rep:([0-9A-Fa-f]{2})\}(.)|\{sp(\d)\}|\{(\w+)(?::[0-9A-Fa-f]{2})?\}|\[[0-9A-Fa-f]{4}\]|(.)")

# box name: (columns, lines per page, how the budget is known); see docs/re/windows.md for the shots
BOXES = {
    "story": (26, 2, "measured"),        # narration box, story intro / outros / ending
    "intro": (25, 1, "measured"),        # msg 14 box
    "subtitle": (19, 1, "measured"),     # msg 9/10 under the mode pictures, runs to the screen edge
    "stage": (19, 1, "measured"),        # STAGE n line on the stage card
    "master": (15, 2, "measured"),       # msg 36 bubble (its clears are {rep:0F} = 15)
    "choice": (8, 2, "measured"),        # msg 56 continue / quit box
    "quiz": (20, 1, "measured"),         # engine-2 quiz bubble (border at column 21)
    "tutorial": (17, 1, "measured"),     # engine-2 tutorial bubble (column 18 overwrites the border)
    "header": (12, 1, "measured"),       # msg 0-5 also head their mode's menu in a framed plate
    "menu": (24, 1, "measured"),         # msg 6/7 story menu items, column 8 to the screen edge
    "prompt": (21, 1, "measured"),       # msg 8 character-select plate
    "password": (14, 1, "guess"),
    "certificate": (26, 6, "measured"),  # msg 30: lines from column 5; rank names drawn at column 11, rows 11 and 14
    "rank": (6, 1, "guess"),             # rank names: certificate slot and the engine-2 rank plate
    "record": (32, 1, "guess"),          # msg 37 versus record: code draws digits at fixed columns
    "end": (26, 1, "guess"),
    "qchoice": (8, 1, "guess"),
}


def box_of(block, i):
    if block == "msg":
        table = [((0, 5), "header"), ((6, 7), "menu"), ((8, 8), "prompt"), ((9, 10), "subtitle"),
                 ((11, 13), "password"), ((14, 14), "intro"), ((15, 19), "story"), ((20, 20), "end"),
                 ((22, 29), "stage"), ((30, 30), "certificate"), ((31, 35), "rank"), ((36, 36), "master"),
                 ((37, 37), "record"), ((48, 55), "story"), ((56, 56), "choice")]
    else:
        table = [((10, 37), "quiz"), ((38, 39), "qchoice"), ((40, 51), "quiz"), ((52, 56), "rank"),
                 ((57, 97), "tutorial")]
    for (lo, hi), name in table:
        if lo <= i <= hi:
            return name
    return None  # kept strings (digits, credits, debug)


def lines(text):
    """[(page, width)] for every drawn line: {nl} ends a line, {page} starts a page."""
    out, page, width, drawn = [], 0, 0, False
    for m in TOKEN.finditer(text):
        rep, rch, sp, ctrl, ch = m.groups()
        if rep:
            width += int(rep, 16)
            drawn |= rch != " "
        elif sp:
            width += int(sp)
        elif ch:
            width += 1
            drawn |= ch != " "
        elif ctrl in ("nl", "page", "end"):
            if width:
                out.append((page, width, drawn))
            width, drawn = 0, False
            page += ctrl == "page"
    return out


def check(block, e, codec):
    errs, warns = [], []
    en, tag = e.get("en", ""), f"{block} {e['id']}"
    if not en:
        return errs, warns
    if not en.endswith("{end}"):
        errs.append(f"{tag}: does not end in {{end}}")
    if JP.search(en):
        errs.append(f"{tag}: Japanese left: {JP.findall(en)}")
    try:
        codec.encode(en)
    except ValueError as x:
        errs.append(f"{tag}: {x}")
    box = box_of(block, e["id"])
    if box:
        cols, per_page, how = BOXES[box]
        if how == "guess":
            warns.append(f"{tag}: box {box} budget is a guess")
        ls = lines(en)
        for page, width, _ in ls:
            if width > cols:
                errs.append(f"{tag}: line of {width} columns in a {cols}-column {box} box")
        for page in {p for p, _, _ in ls}:
            n = sum(1 for p, _, d in ls if p == page and d)
            if n > per_page:
                errs.append(f"{tag}: {n} lines on page {page}, {box} box holds {per_page}")
    return errs, warns


def run():
    errs, warns = [], []
    for block in ("msg", "screen"):
        codec = font.codec(block)
        for e in json.loads((ROOT / "script" / f"{block}.json").read_text(encoding="utf-8")):
            a, b = check(block, e, codec)
            errs += a
            warns += b
    return errs, warns


if __name__ == "__main__":
    errs, warns = run()
    print("\n".join(errs))
    if warns:
        print(f"{len(warns)} strings use guessed box budgets (first: {warns[0]})")
    print(f"lint: {len(errs)} errors")
    sys.exit(1 if errs else 0)
