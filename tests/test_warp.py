import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import warp  # noqa: E402


def test_scene_names_cover_loops_and_are_unique():
    names = warp.scene_names()
    assert len(names) == len(set(names))
    for n in ["title", "stage2", "stage8", "ending", "credits", "quiz_lv5", "quiz_rank1", "quiz_rank5", "versus_win"]:
        assert n in names
