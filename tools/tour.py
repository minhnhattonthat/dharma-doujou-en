"""tour.py: QA tour: every scene of tools/debug/scenes.lua warped from a cold boot, held with A mashed, shot every
30 frames; one contact sheet per scene from its arrival on, for the visual-QA gate (qa_gate.py).

    python -X utf8 tools/tour.py [SCENE ..] [--rom R] [--out work/qa/tour] [--jobs 4] [--sheets-only]
    python -X utf8 tools/tour.py --rom "rom/Dharma Doujou (Japan).sfc" --out work/qa/tour_jp    # reference tour

Frames go to <out>_raw/<scene>/, sheets to <out>/<scene>_sheet.png (+ _sheet_2.png ... when long).
"""
import argparse
import os
import re
import subprocess
import sys

from skill import SKILL
from warp import BUILT, ROOT, scene_names

HOLD = {"credits": 4200, "ending": 2400, "story_intro": 2400, "tutorial": 3600, "quiz_break": 1500,
        "quiz_master": 1500, "versus_win": 1500, "attract": 1800}
for n in range(2, 9):
    HOLD[f"stage{n}"] = 2400  # each stage's outro story, map, stage card


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--rom", default=BUILT)
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "qa", "tour"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--sheets-only", action="store_true")
    a = ap.parse_args()
    scenes = a.scenes or scene_names()
    raw = a.out.rstrip("/\\") + "_raw"
    fails = 0
    if not a.sheets_only:
        groups = {}
        for s in scenes:
            groups.setdefault(HOLD.get(s, 900), []).append(s)
        for hold, group in sorted(groups.items()):
            fails |= subprocess.call([sys.executable, "-X", "utf8", os.path.join(ROOT, "tools", "warp.py"), *group,
                                      "--rom", a.rom, "--out", raw, "--hold", str(hold), "--mash", "60",
                                      "--shot-every", "30", "--jobs", str(a.jobs)])
    os.makedirs(a.out, exist_ok=True)
    for s in scenes:
        log = os.path.join(raw, s, "log.txt")
        m = re.search(r"WARP ok \S+ f(\d+)", open(log, encoding="utf-8", errors="replace").read()) \
            if os.path.exists(log) else None
        if not m:
            print("no arrival logged:", s)
            fails = 1
            continue
        for old in os.listdir(a.out):
            if re.fullmatch(re.escape(s) + r"_sheet(_\d+)?\.png", old):
                os.remove(os.path.join(a.out, old))
        subprocess.check_call([sys.executable, os.path.join(SKILL, "scripts", "sheet.py"), os.path.join(raw, s),
                               "--from", str(max(0, int(m[1]) - 30)), "--changed", "0.01", "--div", "1",
                               "--max", "12", "--out", os.path.join(a.out, s + "_sheet.png")],
                              stdout=subprocess.DEVNULL)
    print("sheets:", a.out)
    return fails


if __name__ == "__main__":
    sys.exit(main())
