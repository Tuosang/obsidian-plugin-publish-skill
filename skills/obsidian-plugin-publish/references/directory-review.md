# Community directory: submission and review

Docs: `obsidianmd/obsidian-developer-docs` → `en/Community directory/*.md` and `en/Plugins/Releasing/*.md` (read them with `gh api` if anything below looks out of date — the process changed in 2026 and may change again).

## Contents
1. Before submitting
2. Submission walkthrough
3. The automated review
4. Findings and fixes seen so far
5. New versions after listing

## 1. Before submitting

- Public GitHub repo with `README.md`, `LICENSE` (GitHub must detect it — `gh api repos/O/R/license --jq .license.spdx_id`), `manifest.json` at the default branch HEAD (the directory reads it from there).
- A published GitHub release whose tag equals `manifest.version` exactly (`x.y.z`, no `v`), with `main.js`, `manifest.json`, `styles.css` attached.
- `npm run lint` clean with `eslint-plugin-obsidianmd` recommended config; `npm run build` is the production build (the scanner runs the first of `build`, `build:plugin`, `compile`).
- The scanner ignores these paths, so keep tests and tooling under these names: `node_modules, dist, build, pkg, test-vault, .pnpm-store, .obsidian, esbuild.config.mjs, version-bump.mjs, automation, *.test.*, *.spec.*, test, tests, __tests__, e2e-tests, mocks, *.cjs, *.mjs, *.cts, *.mts, vite, scripts, docs, i18n, i18next, locale, locales, translations, l10n`.

## 2. Submission walkthrough

1. **community.obsidian.md** (not obsidian.md/account, which is the Sync/Publish/licence page). Top-right **Sign in** with the user's Obsidian account — the user signs in.
2. User menu → **Account** → Community profile (`/account/profile`). **GitHub → Connect** goes to GitHub's OAuth page: "Obsidian Community by Obsidian.md … Profile information (read-only)", scope `read:user`. Check that before anyone authorises.
   - GitHub disables **Authorize** while the page is hidden (`document.visibilityState === "hidden"`), which is always the case for a Claude-in-Chrome tab the user isn't looking at. Don't try to bypass it. Ask the user to open the profile page in their own active tab, press Connect and Authorize; then confirm "Connected as <login>" yourself.
   - An AppleScript `tell application "Google Chrome"` tab switch needs macOS automation permission; if nobody answers the prompt it times out (-1712).
   - Leave **Action required notifications** on (email when the listing needs attention).
   - The public profile username is optional for submitting.
3. **Plugins → New plugin** (`/account/plugins/new`): repository URL `https://github.com/<owner>/<repo>`, Owner **Myself** (or an organisation).
4. Two checkboxes: *I have read and agree to the Developer Policies* and *I commit to continue supporting this plugin, and remove it or transfer it if I can no longer provide support.* Summarise the policies for the user — not allowed: obfuscation, network-loaded ads, ads outside the plugin's UI, client-side telemetry, self-updating; must disclose in README: payments, accounts, network use, access outside the vault, server-side telemetry; must have a licence and respect the Obsidian trademark; forks need the original author's permission — and tick them only after the user agrees. Then **Submit**.
5. The entry (`/account/plugins/<id>`) opens as a **draft**: "This entry is in draft mode and not yet visible to the public." The first review starts automatically.
6. When the review is clean, ask the user, then **Publish**. The draft banner disappears and the buttons become *View listing / Edit listing*. Check the public page `/plugins/<id>`: health, review status, auto-generated About text and tags, README rendering.

## 3. The automated review

Shown on the entry page per version and commit, status *Pending* → *Completed*, typically 3–5 minutes; it fills in section by section. Each item is Error, Warning, Recommendation or Pass, with a **Copy as Markdown** button. Errors block installation; warnings and recommendations don't, but fix them — they show up as the listing's health.

Sections seen: Releases, Network requests, CSS lint, Dependencies, Code obfuscation, Build verification (plus Manifest and Source code checks that only appear when something is wrong).

Reading it from Claude in Chrome: the page is a client-rendered app, so `get_page_text` returns only the sidebar; use `read_page` (filter `all`) or `find`. The tab's own auto-refresh may stall while hidden — re-navigate to the entry URL to see new results.

After a fix: release a new patch version, then open `/account/plugins/<id>/check-release` → "Your manifest points at version x.y.z. A scan has been queued." There is also **Review branch** to scan a branch/tag/commit without releasing.

## 4. Findings and fixes seen so far

| Finding | Fix that worked |
| --- | --- |
| ESLint `obsidianmd/no-static-styles-assignment` on `el.style.setProperty(..., 'important')` | Move static styling to CSS; to undo an inline style from a cloned element use `el.style.removeProperty(...)`. Dynamic positions (`top/left/width` from measurements) were accepted. |
| `obsidianmd/prefer-window-timers` | `window.requestAnimationFrame`, `window.cancelAnimationFrame`, `window.setTimeout` (popout-window safe). |
| `obsidianmd/prefer-get-language` (reading `localStorage.getItem("language")`) | Use `getLanguage()` from `obsidian`. Prefer `window.i18next.language` first: with "follow system language" `getLanguage()` can report `en` while the UI is Chinese. |
| `settings-tab/prefer-setting-definitions`, deprecated `display()`, `setDynamicTooltip` | With `minAppVersion` ≥ 1.13.0: implement `getSettingDefinitions()` (slider/dropdown/toggle controls with `key` and `defaultValue`; `disabled` lives inside `control`), override `setControlValue` to validate, save and refresh, call `this.update()` when one setting changes another's state. Remove `display()`. |
| `@typescript-eslint/no-unnecessary-type-assertion` | Drop the cast. |
| CSS lint: "Avoid `!important`" | Raise specificity; for Obsidian's own rules set the variable they read (`.tree-item-self.is-clickable { cursor: var(--cursor) }` → set `--cursor: pointer` on the container; indent guides use `--nav-indentation-guide-color`). |
| Releases: "Missing GitHub artifact attestations" (recommendation) | `actions/attest-build-provenance@v2` in the release workflow with `permissions: id-token: write, attestations: write` (see `assets/release.yml`). Verify with `gh attestation verify main.js --owner <login>`. |
| Submission requirement: `minAppVersion` | Set it to the version actually tested; record the same in `versions.json`. Unknown → latest stable (`desktop-releases.json` in `obsidianmd/obsidian-releases`). |
| Build verification | Passes when CI builds from the tag with a committed lockfile and the build is deterministic ("Build reproduced the release main.js byte-for-byte"). |

Add new rows here when a review reports something new.

## 5. New versions after listing

1. Code change → tests, lint, in-app check.
2. Bump `manifest.json`, `package.json`, `versions.json` (and CHANGELOG). `npm version patch` creates a `v`-prefixed git tag by default — either use `--no-git-tag-version` or edit the files by hand, then `git tag x.y.z`.
3. Push commit and tag → CI drafts the release → compare assets with `dist/`, verify attestation, add notes → publish with the user's approval.
4. `check-release` on the directory entry; confirm the new review is clean.
