#!/usr/bin/env python3
"""Repository checks, run locally and in CI.

- SKILL.md frontmatter follows the Agent Skills rules (name, description <= 1024 chars,
  no angle brackets, compatibility <= 500 chars, only known keys).
- plugin.json, marketplace.json and the newest CHANGELOG entry agree on the version.
- Every file SKILL.md points at exists, and every bundled Python script compiles.
- With --tag vX.Y.Z: the tag matches that version.
"""
import argparse, json, pathlib, py_compile, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "obsidian-plugin-publish"
ALLOWED = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("SKILL.md: missing frontmatter")
    fields = {}
    for line in m.group(1).splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag")
    a = ap.parse_args()
    errors = []
    text = (SKILL / "SKILL.md").read_text()
    fm = frontmatter(text)
    if set(fm) - ALLOWED:
        errors.append(f"unknown frontmatter keys: {sorted(set(fm) - ALLOWED)}")
    if fm.get("name") != SKILL.name or not re.fullmatch(r"[a-z0-9-]{1,64}", fm.get("name", "")):
        errors.append("name must match the folder and be kebab-case")
    desc = fm.get("description", "")
    if not desc or len(desc) > 1024 or "<" in desc or ">" in desc:
        errors.append(f"description must be 1-1024 chars without angle brackets (is {len(desc)})")
    if len(fm.get("compatibility", "")) > 500:
        errors.append("compatibility over 500 chars")

    for ref in sorted(set(re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", text))):
        if not (SKILL / ref).exists():
            errors.append(f"SKILL.md points at missing file {ref}")
    for script in (SKILL / "scripts").glob("*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{script.name}: {e.msg}")

    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    entry = next((p for p in market["plugins"] if p["name"] == plugin["name"]), None)
    changelog = re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGELOG.md").read_text(), re.M)
    versions = {"plugin.json": plugin.get("version"), "marketplace.json": entry and entry.get("version"),
                "CHANGELOG.md": changelog and changelog.group(1)}
    if len(set(versions.values())) != 1:
        errors.append(f"versions disagree: {versions}")
    if a.tag and a.tag.lstrip("v") != plugin.get("version"):
        errors.append(f"tag {a.tag} does not match version {plugin.get('version')}")

    for e in errors:
        print("error:", e)
    print(f"{'FAILED' if errors else 'ok'}: {fm.get('name')} {plugin.get('version')}, description {len(desc)} chars")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
