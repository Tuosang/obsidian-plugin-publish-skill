#!/usr/bin/env python3
"""Scan everything git would publish for personal data before a push or release.

usage: privacy_scan.py [repo] [--term NAME ...]

Checks every tracked and untracked-but-not-ignored file (text and image bytes, so metadata too)
for home-directory paths, iCloud/vault paths, email addresses that aren't GitHub noreply or
example addresses, and any --term you pass (people, company, project or vault folder names).
Also lists the author/committer emails in git history — they become public with the first push.
Exit code 1 when something is found.
"""
import argparse, os, re, subprocess, sys

EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
OK_EMAIL = re.compile(rb"(noreply|no-reply)@|users\.noreply\.github\.com|@example\.(com|org)|@anthropic\.com$")
PATTERNS = [rb"/Users/[A-Za-z0-9._-]+", rb"/home/[A-Za-z0-9._-]+", rb"Mobile Documents", rb"iCloud~", rb"C:\\\\Users\\\\"]
SKIP = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--term", action="append", default=[], help="extra word to flag (case-insensitive)")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    files = sorted(set(git(repo, "ls-files", "--cached", "--others", "--exclude-standard").split("\n")) - {""})
    terms = [re.compile(re.escape(t.encode()), re.I) for t in a.term]
    found = 0
    for rel in files:
        if os.path.basename(rel) in SKIP:
            continue
        path = os.path.join(repo, rel)
        if not os.path.isfile(path) or os.path.realpath(path) == os.path.realpath(__file__):
            continue                            # the scanner's own patterns aren't findings
        data = open(path, "rb").read()
        hits = []
        for p in PATTERNS:
            hits += [m.group(0) for m in re.finditer(p, data)]
        hits += [m.group(0) for m in EMAIL.finditer(data) if not OK_EMAIL.search(m.group(0))]
        for t in terms:
            hits += [m.group(0) for m in t.finditer(data)]
        if hits:
            found += 1
            uniq = sorted(set(h.decode("utf-8", "replace") for h in hits))
            print(f"{rel}: {', '.join(uniq[:8])}{' …' if len(uniq) > 8 else ''}")
    print(f"scanned {len(files)} files, {found} with findings")
    emails = sorted(set(git(repo, "log", "--all", "--format=%ae%n%ce").split()))
    personal = [e for e in emails if not OK_EMAIL.search(e.encode())]
    if emails:
        print("commit emails:", ", ".join(emails))
    if personal:
        print("note: these commit emails become public on push:", ", ".join(personal))
    sys.exit(1 if found else 0)

if __name__ == "__main__":
    main()
