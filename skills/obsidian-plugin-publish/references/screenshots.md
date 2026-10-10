# Screenshots, GIFs and in-app testing

Everything here drives the real Obsidian desktop app through the official `obsidian` CLI (`/usr/local/bin/obsidian`: `eval`, `dev:cdp`, `dev:css`, `plugins:restrict`, `plugin:reload`, `vaults`). The user's own vault is used only for functional checks of their real setup; all images come from a demo vault.

## Contents
1. Demo vault
2. Running JavaScript in a vault
3. Capturing images
4. The settings window
5. English UI for the English README
6. Mobile layout
7. Demo GIF
8. Cleanup checklist

## 1. Demo vault

Build it with `scripts/make_demo_vault.py <spec.json> <dir> --plugin-dist <repo>/dist`. The spec lists folders and notes (made-up, generic English names; deep enough to show the feature; one note with real-looking body text so the editor isn't empty). Put it in the session scratchpad, not inside the user's vault or iCloud.

Open it from a window that already has a vault:

```js
require("electron").ipcRenderer.sendSync("vault-open", "/abs/path/to/DemoVault", false)
```

A new vault starts in restricted mode: `obsidian vault=DemoVault plugins:restrict off` (this reloads that window). A plugin folder that appeared while Obsidian was running needs `await app.plugins.loadManifests()` before `enablePlugin`. After rebuilding, reload with `await app.plugins.disablePlugin(id); await app.plugins.enablePlugin(id)`.

Window setup inside the demo window: `require("@electron/remote").getCurrentWindow().setContentSize(w, h)`, `app.workspace.rightSplit.collapse()`, reveal the view you need, open the example note, set folds through `view.fileItems[path].setCollapsed(bool, false)` for the file explorer. Hide noise with an injected `<style>` (e.g. `.status-bar{display:none}`) — only in the demo window.

## 2. Running JavaScript in a vault

`scripts/obsidian_eval.sh <vault> <file.js>` runs a file of JS and prints the result, giving up after ~20 s. Write the JS to a file: quoting inline code through zsh is fragile. Wrap async code in `(async()=>{ ... return JSON.stringify(x) })()`.

Quirks seen in practice:
- The CLI sometimes hangs or answers `Command "eval" not found` / `Vault not found` for a few seconds (e.g. while a window reloads). Retry after a pause; never block the session on it.
- A window that is hidden or fully covered pauses `requestAnimationFrame`. Plugins that update on rAF won't redraw; call their update function directly before reading DOM state or capturing.
- Install small helpers on `window` (e.g. `window.__demo = { scroll(y), hover(path), rows() }`) so each frame/check is a one-line eval. A window reload wipes them — re-install after `plugins:restrict off`, `emulateMobile`, or a crash.
- `require("obsidian")` doesn't resolve in eval; test plugin APIs through the plugin instance (`app.plugins.plugins[id]`).
- `obsidian vault=X dev:css selector=".foo" prop=cursor` shows which rules apply — use it to find the CSS variable to override instead of reaching for `!important`.

## 3. Capturing images

`scripts/capture.py --vault DemoVault --clip x,y,w,h --scale 1 out.png [--cursor x,y]` calls `Page.captureScreenshot` through `obsidian dev:cdp`. Coordinates are CSS pixels of the window; the PNG comes out at clip × scale × devicePixelRatio (2 on Retina), so scale 1 already gives crisp 2× images. Get clip rectangles from `el.getBoundingClientRect()`.

Why CDP: `obsidian dev:screenshot` and Electron's `capturePage()` return a stale frame when the window is covered. CDP forces a fresh render.

Cursor: synthetic `mousemove` events don't draw a pointer, so `--cursor` paints an arrow at the event's client coordinates (scaled with the image). Hover effects themselves come from dispatching `new MouseEvent("mousemove", {bubbles:true, clientX, clientY})` on `document.elementFromPoint(x, y)`.

Check each capture. Two captures with identical bytes mean one of them was stale; captures taken right after a timed-out CLI call can be off by one.

## 4. The settings window

In Obsidian 1.13 `app.setting.open()` opens settings in a separate BrowserWindow (title `设置 - <vault> - Obsidian …` or `Settings - …`). Find it with `require("@electron/remote").BrowserWindow.getAllWindows()` (not the current window, title contains the vault name), open the tab with `app.setting.openTabById(id)`, size it with `setContentSize`, then capture through its debugger:

```js
const d = sw.webContents.debugger; let a=false; try { d.attach("1.3"); a=true } catch {}
const res = await d.sendCommand("Page.captureScreenshot", { format: "png", clip: { x, y, width, height, scale: 2 } });
if (a) d.detach();
require("fs").writeFileSync(out, Buffer.from(res.data, "base64"));
```

`capturePage()` returned stale frames here too. Measure the clip from `.vertical-tab-content .setting-group` (or the union of `.setting-item` rects) via `sw.webContents.executeJavaScript`, so the image contains only the plugin's settings and not Obsidian's own (possibly Chinese) sidebar. Declarative settings (`getSettingDefinitions`) are cached: after changing language call the tab's `update()`. Close with `app.setting.close()`.

Settings search check: type a word into the settings search box (`input[type=search]`) through `executeJavaScript` and confirm the plugin's setting appears.

## 5. English UI for the English README

If the user's Obsidian follows a non-English system language, switch only the demo window: `await window.i18next.changeLanguage("en")`, then reopen the note/view so it re-renders. Read `localStorage.getItem("language")` before and after — it must stay unchanged, because localStorage is shared by every vault window and would switch the user's main vault on its next launch. Some already-rendered items (status bar word count) keep the old language; hide or recapture them.

## 6. Mobile layout

`app.emulateMobile(true)` writes the **shared** localStorage key `EmulateMobile` and reloads only that window. Do it in the demo window, set `setContentSize(390, 760)` first, test and capture quickly, then `app.emulateMobile(false)` and confirm `localStorage.getItem("EmulateMobile") === null` from the user's main window. In the mobile layout the file explorer is a drawer: `app.workspace.leftSplit.expand()`. Row heights change (37 px vs 25 px) — a good check that the plugin measures instead of hard-coding. Crop the image to the plugin's area so drawer chrome in another language isn't shown.

## 7. Demo GIF

Plan a short story (3–8 s): start state → the main interaction → one or two highlights (hover, click) → end state. Capture frames with a loop that sets state, updates, captures (`capture.py`), and records a duration per frame (0.04 s while moving, 1–2 s holds on key moments). Draw the cursor on hover/click frames. Assemble with `scripts/make_gif.py frames.json out.gif --width 450`, which uses an ffmpeg palette with variable frame timing; ~80 frames at 450 px landed at 2.6 MB. Look at a contact sheet of key frames before using it.

## 8. Cleanup checklist

- Close the demo window: `setTimeout(()=>require("@electron/remote").getCurrentWindow().close(),200)` from inside it.
- Remove it from Obsidian's vault list from the main window: `require("electron").ipcRenderer.sendSync("vault-remove", "/abs/path")`, then check `ipcRenderer.sendSync("vault-list")` shows only the user's vaults (the CLI's own `vault-remove` path can hang).
- Language and mobile emulation reverted (see above); plugin in the user's vault reloaded on the released build and its version refreshed with `app.plugins.loadManifests()`.
