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
    errs, _ = lint.check("msg", {"id": 36, "jp": "{end}", "en": "x" * 16 + "{end}"}, c)
    assert "16 columns" in errs[0]
    errs, _ = lint.check("msg", {"id": 15, "jp": "{end}", "en": "a{nl}b{nl}c{end}"}, c)
    assert "3 lines" in errs[0]
    errs, _ = lint.check("msg", {"id": 15, "jp": "{end}", "en": "あ{end}"}, c)
    assert any("Japanese" in e for e in errs)


def test_control_codes_match_but_layout_may_change():
    c = font.codec("msg")
    jp = "{mode:01}あ{nl}い{key}{page}う{end}"
    assert lint.check("msg", {"id": 15, "jp": jp, "en": "{mode:01}a b{key}{page}{rep:1A} {page}c{key}{page}d{end}"},
                      c)[0] == []
    errs, _ = lint.check("msg", {"id": 15, "jp": jp, "en": "a{key}{page}c{end}"}, c)
    assert "control codes differ" in errs[0]
    errs, _ = lint.check("msg", {"id": 15, "jp": jp, "en": "{mode:01}a c{end}"}, c)
    assert "fewer" in errs[0]
