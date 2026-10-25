"""Cold-boot warp to named scenes (tools/debug/scenes.lua) in MesenCE, one run per scene.

    python -X utf8 tools/warp.py stage3 [stage4 ..] [--rom R] [--save] [--hold 300] [--shot-every 60] [--mash 40]
    python -X utf8 tools/warp.py --all --save --jobs 3     # regenerate every work/states/<scene>.mss
    python -X utf8 tools/warp.py --list

Output: work/qa/warp/<scene>/<scene>.png (+ sheet with --shot-every). --save writes work/states/<scene>.mss.
ROM default: build/dharma_en.sfc if it exists, else the original. Exit 1 if any scene was not reached.
"""
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from skill import SKILL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBG = os.path.join(ROOT, "tools", "debug")
ORIG = os.path.join(ROOT, "rom", "Dharma Doujou (Japan).sfc")
BUILT = os.path.join(ROOT, "build", "dharma_en.sfc")


def scene_names():
    src = open(os.path.join(DBG, "scenes.lua"), encoding="utf-8").read()
    names = re.findall(r'^S\.(\w+) =', src, re.M)
    # loop-made names: `for n = A, B do ...` with `S["x" .. n] =` on the next line
    for lo, hi, stem in re.findall(r'^for n = (\d+), (\d+) do[^\n]*\n\s*S\["(\w+)" \.\. n\]', src, re.M):
        names += [stem + str(n) for n in range(int(lo), int(hi) + 1)]
    return names


def run(scene, a):
    out = os.path.join(ROOT, "work", "qa", "warp", scene)
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), a.rom, "--out", out,
           "--script", os.path.join(DBG, "scenes.lua"), "--script", os.path.join(DBG, "warp.lua"),
           "--script", os.path.join(DBG, "modelog.lua"),
           "--var", f"SCENE='{scene}'", "--var", f"HOLD={a.hold}", "--frames", str(a.frames), "--timeout", "1200"]
    if a.save:
        state = os.path.join(ROOT, "work", "states", scene + ".mss").replace("\\", "/")
        os.makedirs(os.path.dirname(state), exist_ok=True)
        cmd += ["--var", f"SAVE='{state}'"]
    if a.mash:
        cmd += ["--var", f"AFTER_MASH={a.mash}"]
    for s in a.script:
        cmd += ["--script", s]
    if a.shot_every:
        cmd += ["--shot-every", str(a.shot_every), "--sheet"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read() if os.path.exists(
        os.path.join(out, "log.txt")) else ""
    ok = p.returncode == 0 and f"WARP ok {scene} " in log
    err = "" if ok else (p.stdout + p.stderr).strip().splitlines()[-3:]
    return scene, ok, os.path.join(out, scene + ".png"), err


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--rom", default=BUILT if os.path.exists(BUILT) else ORIG)
    ap.add_argument("--save", action="store_true", help="write work/states/<scene>.mss")
    ap.add_argument("--hold", type=int, default=60, help="frames to wait after arrival before the shot")
    ap.add_argument("--frames", type=int, default=20000, help="timeout in frames")
    ap.add_argument("--shot-every", type=int, default=0)
    ap.add_argument("--mash", type=int, default=0, help="after arrival, press A every N frames during --hold")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe, e.g. tools/debug/freetrap.lua")
    a = ap.parse_args()
    names = scene_names()
    if a.list:
        print("\n".join(names))
        return 0
    todo = names if a.all else a.scenes
    bad = [s for s in todo if s not in names]
    if bad or not todo:
        sys.exit(f"unknown scene(s) {bad}; --list shows them" if bad else "name a scene, or --all")
    print("rom:", a.rom)
    fails = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for scene, ok, png, err in ex.map(lambda s: run(s, a), todo):
            print(f"{'ok  ' if ok else 'FAIL'} {scene:16} {png if ok else err}")
            fails += not ok
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
