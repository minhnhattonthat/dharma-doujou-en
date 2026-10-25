import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import dump  # noqa: E402
from text import Codec  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ORIG_ROM.is_file(), reason="no ROM dump in rom/")


def items(block):
    return json.loads((ROOT / "script" / f"{block[0]}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("block", build.BLOCKS, ids=lambda b: b[0])
def test_script_shape(block):
    es = items(block)
    assert [e["id"] for e in es] == list(range(block[3]))
    c = Codec.load(ROOT / "tbl" / block[1])
    for e in es:
        assert e["jp"].endswith("{end}") and c.encode(e["jp"])
        assert not (e.get("alias") is not None and e["en"]), f"{block[0]} {e['id']}: translate alias {e['alias']}"


@needs_rom
@pytest.mark.parametrize("block", build.BLOCKS, ids=lambda b: b[0])
def test_script_matches_rom_and_covers_block(block):
    """jp re-encodes to the original bytes at ptr, and the strings cover the text range with no gap."""
    rom = build.ORIG_ROM.read_bytes()
    c = Codec.load(ROOT / "tbl" / block[1])
    es, covered = items(block), set()
    assert [e["jp"] for e in es] == [e["jp"] for e in dump.entries(rom, block)]
    for e in es:
        off, enc = int(e["ptr"], 16), c.encode(e["jp"])
        assert rom[off:off + len(enc)] == enc, e["id"]
        covered |= set(range(off, off + len(enc)))
    assert covered == set(range(block[5], block[6]))


@needs_rom
def test_dump_never_clobbers_en(tmp_path, monkeypatch):
    monkeypatch.setattr(dump, "SCRIPT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["dump.py"])
    dump.main()
    path = tmp_path / "msg.json"
    es = json.loads(path.read_text(encoding="utf-8"))
    es[5]["en"] = "Options{end}"
    dump.write(path, es)
    dump.main()  # no --force: skipped
    monkeypatch.setattr(sys, "argv", ["dump.py", "--force"])
    dump.main()  # --force: jp rewritten, en kept
    assert json.loads(path.read_text(encoding="utf-8"))[5]["en"] == "Options{end}"


@needs_rom
def test_untranslated_script_builds_the_original(tmp_path):
    orig = build.ORIG_ROM.read_bytes()
    texts = build.load_script("xx")  # no such field: every string falls back to jp
    assert build.build(orig, tmp_path / "id.sfc", texts) == orig
