#!/usr/bin/env python3
"""Build a throwaway demo vault for screenshots, with the plugin build installed and enabled.

usage: make_demo_vault.py spec.json /abs/path/DemoVault [--plugin-dist repo/dist] [--force]

spec.json:
{
  "notes": {                                   # path -> body (null = short placeholder body)
    "Work/Meetings/2026/2026-05/2026-05-21/Weekly product sync.md": "**Attendees:** Alex, Sam\\n\\n## Agenda\\n- ...",
    "Work/Projects/Website redesign/Brief.md": null
  },
  "folders": ["Archive/Empty folder"],         # optional: folders without notes
  "theme": "moonstone"                         # moonstone = light, obsidian = dark
}

Use made-up, generic names only — never copy the user's real notes, people or projects.
The vault goes in a scratch folder, not inside the user's vault or iCloud.
"""
import argparse, json, os, shutil, sys

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("vault")
    ap.add_argument("--plugin-dist", help="folder with main.js, manifest.json, styles.css")
    ap.add_argument("--force", action="store_true", help="replace an existing vault folder")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    vault = os.path.abspath(a.vault)
    if os.path.exists(vault):
        if not a.force:
            sys.exit(f"{vault} exists (use --force to replace it)")
        shutil.rmtree(vault)
    os.makedirs(vault)

    notes = spec.get("notes", {})
    if isinstance(notes, list):
        notes = {p: None for p in notes}
    for rel, body in notes.items():
        path = os.path.join(vault, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        title = os.path.splitext(os.path.basename(rel))[0]
        with open(path, "w") as f:
            f.write(body if body else f"Notes for **{title}**.\n")
    for rel in spec.get("folders", []):
        os.makedirs(os.path.join(vault, rel), exist_ok=True)

    cfg = os.path.join(vault, ".obsidian")
    os.makedirs(cfg, exist_ok=True)
    json.dump({"theme": spec.get("theme", "moonstone")}, open(os.path.join(cfg, "appearance.json"), "w"))
    json.dump({"promptDelete": False}, open(os.path.join(cfg, "app.json"), "w"))

    if a.plugin_dist:
        manifest = json.load(open(os.path.join(a.plugin_dist, "manifest.json")))
        pid = manifest["id"]
        dest = os.path.join(cfg, "plugins", pid)
        os.makedirs(dest, exist_ok=True)
        for name in ("main.js", "manifest.json", "styles.css"):
            src = os.path.join(a.plugin_dist, name)
            if os.path.exists(src):
                shutil.copy2(src, dest)
        json.dump([pid], open(os.path.join(cfg, "community-plugins.json"), "w"))
        print(f"installed {pid} {manifest.get('version')}")
    print(f"{vault}: {len(notes)} notes")
    print('open it: require("electron").ipcRenderer.sendSync("vault-open", "%s", false)' % vault)
    print(f"then:    obsidian vault={os.path.basename(vault)} plugins:restrict off")

if __name__ == "__main__":
    main()
