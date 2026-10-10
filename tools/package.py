#!/usr/bin/env python3
"""Package skills/obsidian-plugin-publish into dist/obsidian-plugin-publish.skill (a zip whose
single top-level folder is the skill), the format Claude.ai accepts for uploads."""
import pathlib, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "obsidian-plugin-publish"
OUT = ROOT / "dist" / f"{SKILL.name}.skill"
SKIP_DIRS, SKIP_FILES = {"__pycache__", "node_modules"}, {".DS_Store"}

OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for path in sorted(SKILL.rglob("*")):
        rel = path.relative_to(SKILL.parent)
        if path.is_dir() or path.name in SKIP_FILES or path.suffix == ".pyc" or set(rel.parts) & SKIP_DIRS:
            continue
        z.write(path, rel.as_posix())
print(f"{OUT.relative_to(ROOT)}: {len(zipfile.ZipFile(OUT).namelist())} files, {OUT.stat().st_size // 1024} KB")
