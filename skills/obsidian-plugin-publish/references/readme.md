# README for an Obsidian plugin

The directory shows an excerpt of `README.md` on the plugin's public page and rewrites relative image links against the repo, so the README is the plugin's storefront. Good references: Better Explorer (demo GIF + plain features), obsidian-git (one image per view), Omnisearch (badges + GIF first), Neat File Tree (one strong hero image).

## Files

- `README.md` — English, the one the directory shows.
- `README.zh-CN.md` — Chinese, same structure and images. Link the two at the top: `**English** · [简体中文](README.zh-CN.md)` and the reverse.
- `CHANGELOG.md` — newest first, one section per version, user-facing bullets.
- `.github/ISSUE_TEMPLATE/bug_report.yml`, `feature_request.yml`, `config.yml` — bilingual labels, ask for plugin version, Obsidian version + OS, theme and other explorer/UI plugins, screenshots.
- `docs/images/` — everything the READMEs reference (the scanner ignores `docs/`). Delete images nothing references.

## Structure (both languages)

1. Centred title, one- or two-line pitch that names the problem, badges, language switch.
2. Demo GIF (`<img width="380">` for a sidebar-shaped capture), with alt text that describes what happens in it.
3. **Why** — the situation that hurts, in the reader's words; then a before/after table (two images side by side, same position, plugin off vs on).
4. **Features** — `###` per feature: what it does in one or two sentences, then its image. Put comparisons (e.g. two modes) in a two-column table.
5. **Installation** — directory (or "not listed yet"), BRAT (`<owner>/<repo>`), manual (download the three files from the latest release into `<vault>/.obsidian/plugins/<id>/`).
6. **Usage** — a table *action → what happens*. Mention anything non-obvious (click behaviour, right-click, scrolling over overlays).
7. **Settings** — table *setting / default / what it does*, then a screenshot of the settings tab (English UI for the English README, Chinese UI for the Chinese one).
8. **Compatibility** — minimum Obsidian version and what it was actually tested on (OS, version, mobile layout), core-view assumptions, themes tested.
9. **Known limitations** — honest, short, with the workaround.
10. **Privacy** — network use (or "no network requests"), data collected (or none), what the plugin reads, where settings live. The Developer Policies require disclosure of network use, accounts, payments, and access outside the vault.
11. **How it works** — two or three bullets for curious users and reviewers; name any internal Obsidian API used and the fallback.
12. **Development** — clone, `npm install`, `npm test`, `npm run lint`, `npm run build`, `npm run dev`; how to install builds into a local vault; how releases are cut.
13. **Changelog** link, **Feedback** (issues, any language), **Acknowledgements**, **License** (`[MIT](LICENSE) © <year> <name>`).

## Badges (shields.io)

```html
<a href="https://github.com/OWNER/REPO/releases/latest"><img src="https://img.shields.io/github/v/release/OWNER/REPO?label=release&color=7c3aed" alt="Latest release"></a>
<a href="https://github.com/OWNER/REPO/releases"><img src="https://img.shields.io/github/downloads/OWNER/REPO/total?color=7c3aed" alt="Downloads"></a>
<img src="https://img.shields.io/badge/Obsidian-1.13%2B-7c3aed?logo=obsidian&logoColor=white" alt="Obsidian 1.13+">
<img src="https://img.shields.io/badge/platform-desktop%20%7C%20mobile-lightgrey" alt="Desktop and mobile">
<a href="LICENSE"><img src="https://img.shields.io/github/license/OWNER/REPO?color=lightgrey" alt="MIT license"></a>
```

The release and downloads badges show red "no releases" until a release is published — warn the user rather than worrying them later. Keep the Obsidian badge in sync with `minAppVersion`.

## Images to capture

| Image | What it shows | Typical size |
| --- | --- | --- |
| `demo.gif` | the main interaction end to end, 3–8 s, loops | 450 px wide, < 3 MB |
| `before.png` / `after.png` | same scroll position, plugin off / on | 600 px wide (2× of a 300 px sidebar) |
| one per feature | the feature in its most telling state, cursor drawn where it matters | same width as above |
| `dark-theme.png` | proof it respects themes | |
| `mobile.png` | mobile layout, cropped to the plugin's area (no OS/UI chrome in another language) | |
| `settings.png`, `settings-zh.png` | the plugin's settings card only, not Obsidian's sidebar | ~1200 px wide |

Every image comes from the demo vault. Before committing, open each one: is it the state you meant, in the right language, with nothing private?

## Wording

- Lead with what the user gets, then how. Short sentences, no hype, no emoji.
- Use the same names as the UI (setting names exactly as shown).
- Describe colour as "accent colour" — themes differ, so "blue" is often wrong.
- Example paths are generic (`Work / Meetings / 2026 / 2026-05 / 2026-05-21`), never the user's real folders.
- Don't promise roadmap items.
