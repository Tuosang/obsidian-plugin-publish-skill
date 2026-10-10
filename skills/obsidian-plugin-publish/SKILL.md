---
name: obsidian-plugin-publish
description: Take an Obsidian plugin from working code to a polished public GitHub release and a live listing in the Obsidian community directory (community.obsidian.md). Covers a bilingual README with real screenshots and a demo GIF captured from a throwaway demo vault (never the user's own notes), a privacy scan before anything goes public, Obsidian's official ESLint rules, a GitHub repo with a tag-driven release workflow and build attestations, BRAT/manual install, the directory submission, and fixing the automated review until everything passes. Use this whenever the user wants to publish, share, release, open-source, or list an Obsidian plugin, wants its README, screenshots or GIF improved, wants it in the community plugin store or installable via BRAT, asks about the directory review results, or ships a new version of a plugin that is already listed — including Chinese requests such as 上架、发布插件、社区插件市场、分享插件、写 README、截图、动图、提交审核、发新版本.
compatibility: Claude Code with shell access on macOS or Linux. Uses git, the GitHub CLI (gh), Node.js and npm, Python 3 with Pillow, ffmpeg, and the Obsidian desktop app with its obsidian command-line tool. Claude in Chrome (or another browser tool) helps with the community directory submission.
---

# Publish an Obsidian plugin

This skill turns a plugin that works on the developer's machine into something strangers can trust and install: a clean public repo, a README that shows what the plugin does, reproducible releases, and an approved listing in the Obsidian community directory.

It was distilled from publishing *Sticky Folders* (github.com/Tuosang/obsidian-sticky-folders), which went from working code to an approved directory listing in one session. Most of the steps are mechanical; the parts that need judgment are what goes public, what the user must do or approve personally, and how to get honest screenshots without leaking anyone's notes.

## Ground rules

- **Talk in the user's language.** Reply in whatever language the user writes in; keep commands, file names and identifiers as they are.
- **Nothing private goes public.** A real vault is full of people's names, meetings and work notes. Screenshots and examples come from a demo vault with made-up content (see `references/screenshots.md`). Run `scripts/privacy_scan.py` before the first push and before every release that adds images or docs. Don't quote the user's email address back in chat.
- **The user approves every outward step.** Ask for a clear yes before: creating the public repo, the first push, publishing a GitHub release, ticking the directory's policy/maintenance agreements, and pressing the directory's **Publish** button. Do the preparation yourself, then ask in one short message that says exactly what will happen. Sign-ins, OAuth approvals, passwords and API keys are the user's to enter.
- **Verify, don't assume.** After each build, release or review, check the real result (asset bytes, CI steps, review text, the plugin running in Obsidian) and report what you saw.
- **Leave the user's Obsidian as you found it.** Demo vaults are removed from Obsidian's vault list after use; language or mobile-emulation switches are reverted and checked.

## The pipeline

Work through these phases in order. Skip what's already done (check the repo and the GitHub/directory state first), but don't skip the checks.

### 1. Survey

- Read `manifest.json`, `package.json`, the build config, the README and git status. Note the plugin `id`, version, `minAppVersion`, `isDesktopOnly`, and which Obsidian version it was actually tested on.
- Check identity facts: is there a GitHub remote and account (`gh auth status`)? Is the plugin already in the directory (`community.obsidian.md/plugins/<id>`)? Is the id taken by someone else (search `community-plugins.json` in `obsidianmd/obsidian-releases`)? Do similar plugins exist? Mention them honestly — the user may want to differentiate.
- Plan the README story with the user only if the plugin's purpose is unclear; otherwise draft it and show it.

### 2. Make the code pass the directory's checks

The directory runs an automated review (Manifest, Releases, Source code, CSS lint, Dependencies, Network requests, Code obfuscation, Build verification). Run the same checks locally first — it's far faster than release→review→fix loops.

1. Add Obsidian's ESLint rules (`assets/eslint.config.mjs`, `npm i -D eslint eslint-plugin-obsidianmd typescript-eslint`, script `"lint": "eslint src"`) and fix everything, warnings included where reasonable.
2. Check the CSS for `!important` and hard-coded colours; prefer specificity and Obsidian's CSS variables.
3. Set `minAppVersion` to the version the plugin was really tested on (not a guess). If it is ≥ 1.13, use the declarative settings API so settings show up in Obsidian's settings search.
4. Manifest: description ≤ 250 characters, starts with what it does, ends with a period, no "Obsidian"/"This is a plugin"; `id` and `name` don't contain "obsidian"; no `fundingUrl` unless the user takes donations; `isDesktopOnly: true` if Node/Electron APIs are used.
5. Make sure `npm run build` is the production build and is deterministic — the scanner rebuilds `main.js` from the tagged commit and compares it byte for byte.

`references/directory-review.md` lists every rule and finding seen so far with the fix that worked.

### 3. Test it for real

Unit tests for pure logic (`node --test`), then run the plugin inside Obsidian: build into a vault, reload the plugin, exercise the features, read the DOM/state through `obsidian eval`. Use the demo vault for anything visual. Test light and dark themes, and Obsidian's mobile layout if `isDesktopOnly` is false. `references/screenshots.md` has the Obsidian CLI recipes and their quirks (hidden windows pause `requestAnimationFrame`, stale screenshots, restricted mode on new vaults).

### 4. README, screenshots and demo GIF

Follow `references/readme.md`: README.md (English) and README.zh-CN.md (Chinese) with a language switch, badges, a demo GIF at the top, a before/after table, one image per feature, install (directory, BRAT, manual), usage and settings tables, compatibility, known limitations, privacy, how it works, development, changelog, feedback, license. Add CHANGELOG.md and issue templates.

Capture every image from a demo vault (`scripts/make_demo_vault.py`), with the CDP capture script (`scripts/capture.py`) and the GIF builder (`scripts/make_gif.py`). Look at every image before using it: stale frames, wrong cursor positions and half-switched languages are common and only visible by looking.

### 5. Repository and release

- Repo hygiene: `LICENSE` (MIT unless the user wants otherwise; GitHub must recognise it), `versions.json`, `version-bump.mjs` (`assets/`), `.gitignore` with `node_modules/`, `dist/` and any local vault-path file, build output in `dist/` (optionally also copied into a local vault via a git-ignored `.vault` file).
- Privacy scan (`scripts/privacy_scan.py --term <names…>`), then ask the user about the commit email: a repo-local `git config user.email <id>+<login>@users.noreply.github.com` keeps their real address out of public history. Set it before the first push — rewriting pushed history is painful.
- GitHub CLI: install with Homebrew if missing (ask), log in with `gh auth login --hostname github.com --git-protocol https --web` started in the background so you can hand the user the one-time code, then `gh auth setup-git`. Pushing `.github/workflows/*` needs the `workflow` scope: `gh auth refresh -h github.com -s workflow`.
- Release workflow: `assets/release.yml` (test, lint, build, build-provenance attestations, draft release with `main.js`, `manifest.json`, `styles.css`). Tag = version without `v`. After CI: download the draft's assets, `cmp` them with `dist/`, verify the attestation (`gh attestation verify <file> --owner <login>`), add release notes from CHANGELOG, then publish only when the user says so (`gh release edit <tag> --draft=false --latest`).
- A draft release that hasn't been published can be deleted and re-tagged at a newer commit; a published one should get a new patch version instead.

### 6. Directory submission

As of 2026 plugins are submitted on community.obsidian.md, not by pull request. The user signs in with their Obsidian account (not obsidian.md/account — a different site) and connects GitHub; you can drive the rest in their browser with Claude in Chrome. Details, gotchas and the review loop are in `references/directory-review.md`. In short:

1. Community profile → GitHub → **Connect**. GitHub keeps the **Authorize** button disabled while the tab is hidden, so the user usually has to click it in a tab they're looking at.
2. Plugins → **New plugin** → repository URL, owner. Summarise the Developer Policies and the maintenance commitment for the user and tick the two boxes only after they agree.
3. The entry starts as a draft and the automated review runs (a few minutes). Read every section. Fix findings, cut a new patch release, then open `/account/plugins/<id>/check-release` to queue a rescan.
4. When the review is clean, ask, then press **Publish** and check the public page (`/plugins/<id>`): health, review status, README rendering.

### 7. After publishing

- Update memory/notes with the repo URL, listing URL, release process and anything learned.
- Offer (don't post) announcement drafts for the forum's Share & showcase and Discord `#updates`.
- For later versions: `npm version patch` (or edit the three version fields), CHANGELOG entry, commit, tag, CI draft, verify, publish with approval, then `check-release` so the directory rescans.

## Files in this skill

- `references/readme.md` — README structure, wording rules, image list, bilingual layout.
- `references/screenshots.md` — demo vault, Obsidian CLI recipes, CDP captures, settings window, English UI, mobile emulation, GIF frames, cleanup.
- `references/directory-review.md` — submission walkthrough, review sections, every rule and fix seen so far.
- `scripts/obsidian_eval.sh` — run JS in a vault window with a bounded wait (the CLI can hang).
- `scripts/capture.py` — screenshot a region of a vault window through CDP, optional cursor overlay.
- `scripts/make_gif.py` — frames + durations → small, clean GIF via ffmpeg.
- `scripts/make_demo_vault.py` — build a demo vault from a JSON spec and install the plugin build into it.
- `scripts/privacy_scan.py` — scan everything git would publish (text and image metadata) for personal data.
- `assets/release.yml`, `assets/eslint.config.mjs`, `assets/version-bump.mjs` — drop-in files.
