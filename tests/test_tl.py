import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tl  # noqa: E402


def test_en_tsv_is_merged():
    errs, out = tl.compose(tl.read_tsv())
    assert errs == []
    for block, by_id in out.items():
        en = {e["id"]: e["en"] for e in tl.load(block)}
        stale = [i for i, s in by_id.items() if en[i] != s]
        assert not stale, f"script/{block}.json out of date for {stale}: run tools/tl.py merge"


def test_segments_rebuild_the_jp():
    for e in tl.load("msg"):
        box = tl.lint.box_of("msg", e["id"])
        if box in tl.SEP and "{mode" not in e["jp"]:
            assert tl.SEP[box].join(p + b + s for p, b, s in tl.segments(e["jp"], box)) == e["jp"]


def test_wrap_adds_pages_with_the_clear():
    s = tl.wrap("a" * 20 + " " + "b" * 20 + " " + "c" * 6, "story")
    assert s == "a" * 20 + "{nl}{nl}{nl}" + "b" * 20 + tl.SEP["story"] + "{page}" + "c" * 6
    assert tl.wrap("x / y", "master") == "x{nl}{nl}y"


def test_slots_keep_their_jp_column():
    jp2 = tl.Codec.load(ROOT / "tbl" / "jp2.tbl")
    assert tl.slot_cols("{sp4}の第{sp4}問。{end}", jp2) == [0, 8]
    assert tl.slot_cols("{sp4}{sp2} Q{sp4}", None) == [0, 8]
