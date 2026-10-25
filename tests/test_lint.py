import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import lint  # noqa: E402


def test_script_lints_clean():
    errs, _ = lint.run()
    assert errs == []


def test_story_page_widths_and_clears():
    s = "A{nl}{nl}{nl}" + "b" * 26 + "{key}{page}{rep:1A} {nl}{nl}{nl}{rep:1A} {page}C{end}"
    assert lint.lines(s) == [(0, 1, True), (0, 26, True), (1, 26, False), (1, 26, False), (2, 1, True)]


def test_overflow_and_japanese_are_errors():
    c = font.codec("msg")
    errs, _ = lint.check("msg", {"id": 36, "en": "x" * 16 + "{end}"}, c)
    assert "16 columns" in errs[0]
    errs, _ = lint.check("msg", {"id": 15, "en": "a{nl}b{nl}c{end}"}, c)
    assert "3 lines" in errs[0]
    errs, _ = lint.check("msg", {"id": 15, "en": "あ{end}"}, c)
    assert any("Japanese" in e for e in errs)
