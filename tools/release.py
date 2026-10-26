"""release.py: build, gate and package the patch. Stops at the first failure.

    python -X utf8 tools/release.py [--version v1.0] [--force]

Steps: build -> tests + lint -> smoke boot -> leftover Japanese in the text banks -> visual-QA gate ->
plain build (no marker/--qa; the debug tool is Lua-only, never in the ROM) -> SNES checksum -> BPS patch ->
re-apply to the clean original and compare -> zip (patch + README.txt) in release/.
The playable image stays in build/. Refuses to overwrite an existing version's files without --force.
Publishing (gh release create) is the user's call, never this script's."""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402

ORIG = ROOT / "rom" / "Dharma Doujou (Japan).sfc"
BUILT = ROOT / "build" / "dharma_en.sfc"
# text blocks and their spill space (docs/re/text.md)
BANKS = {"jp.tbl": ["127E4-13DD1", "16910-17FFF"], "jp2.tbl": ["25B06-2609B", "270A0-27FFF"]}


def run(*cmd):
    print(">", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout[-1500:], r.stderr[-1500:], sep="", end="")
    if r.returncode:
        sys.exit(f"release stopped: {cmd[2] if len(cmd) > 2 else cmd[0]} failed (exit {r.returncode})")
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()

    name = f"Dharma_Doujou_EN_{a.version}"
    out = ROOT / "release"
    patch, zpath = out / f"{name}.bps", out / f"{name}.zip"
    if not a.force and (patch.exists() or zpath.exists()):
        sys.exit(f"{zpath.name} or {patch.name} already exists: pass --force to overwrite")

    py = [sys.executable, "-X", "utf8"]
    skill = run(sys.executable, ROOT / "tools" / "skill.py").strip()
    run(*py, "tools/build.py")
    run(*py, "tools/check.py")
    run(*py, f"{skill}/scripts/emu.py", BUILT, "--out", "work/qa/smoke", "--route", "tools/routes/boot.txt", "--smoke")
    for tbl, ranges in BANKS.items():
        rng = [x for r in ranges for x in ("--range", r)]
        res = run(*py, f"{skill}/scripts/jp_left.py", BUILT, "--orig", ORIG, "--tbl", f"tbl/{tbl}", "--min", "2", *rng)
        if not res.strip().endswith("0 Japanese runs, 0 bytes (unchanged from original)"):
            sys.exit(f"release stopped: untranslated text in the {tbl} banks")
    run(*py, f"{skill}/scripts/qa_gate.py", "check", "work/qa/manifest.tsv", "work/qa/verdicts")

    src = ORIG.read_bytes()
    tgt, total = bps.snes_checksum(BUILT.read_bytes())
    p = bps.make(src, tgt)
    if bps.apply(src, p) != tgt:
        sys.exit("release stopped: the patch does not reproduce the build")
    play = ROOT / "build" / f"{name}.sfc"
    out.mkdir(exist_ok=True)
    patch.write_bytes(p)
    play.write_bytes(tgt)

    readme = (ROOT / "docs" / "release-readme.txt").read_text(encoding="utf-8").format(
        version=a.version, patch=patch.name, size=f"{len(src):,}", crc=f"{zlib.crc32(src):08X}",
        md5=hashlib.md5(src).hexdigest(), sha1=hashlib.sha1(src).hexdigest(),
        pcrc=f"{zlib.crc32(tgt):08X}", psha1=hashlib.sha1(tgt).hexdigest())
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    with zipfile.ZipFile(zpath) as z:  # what the player gets: patch + README only, and the patch still applies
        assert sorted(z.namelist()) == sorted([patch.name, "README.txt"]), z.namelist()
        assert bps.apply(src, z.read(patch.name)) == tgt
    print(f"{zpath.relative_to(ROOT)}: {zpath.stat().st_size} bytes; patch {len(p)} bytes, checksum {total:04X}, "
          f"patched crc32 {zlib.crc32(tgt):08X}; playable image {play.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
