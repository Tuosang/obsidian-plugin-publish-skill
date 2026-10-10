#!/usr/bin/env python3
"""Screenshot a region of an Obsidian vault window through the DevTools protocol.

usage: capture.py --vault DemoVault --clip x,y,w,h [--scale 1] [--cursor x,y] out.png

Coordinates are CSS pixels of the vault window (take them from getBoundingClientRect()).
The PNG comes out at w * scale * devicePixelRatio. CDP renders a fresh frame even when the
window is covered, unlike `obsidian dev:screenshot` or Electron's capturePage().
--cursor draws an arrow pointer at window coordinates x,y (synthetic mouse events draw none).
"""
import argparse, base64, json, os, re, subprocess, sys

def capture(vault, clip, scale, out, timeout=40, tries=4):
    x, y, w, h = clip
    params = json.dumps({"format": "png", "captureBeyondViewport": False,
                         "clip": {"x": x, "y": y, "width": w, "height": h, "scale": scale}})
    for _ in range(tries):
        try:
            p = subprocess.run(["obsidian", f"vault={vault}", "dev:cdp", "method=Page.captureScreenshot",
                                f"params={params}"], capture_output=True, text=True, timeout=timeout,
                               cwd=os.path.expanduser("~"))
        except subprocess.TimeoutExpired:
            continue
        m = re.search(r'"data"\s*:\s*"([A-Za-z0-9+/=]+)"', p.stdout)
        if m:
            with open(out, "wb") as f:
                f.write(base64.b64decode(m.group(1)))
            return out
    sys.exit(f"capture failed for {out}")

def draw_cursor(path, cx, cy, clip):
    from PIL import Image, ImageDraw
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    s = im.width / clip[2]                      # image pixels per CSS pixel
    px, py, k = (cx - clip[0]) * s, (cy - clip[1]) * s, s / 1.6
    shape = [(0, 0), (0, 17), (4.5, 13), (7.5, 19.5), (10, 18.5), (7, 12.5), (12.5, 12.5)]
    poly = [(px + a * k, py + b * k) for a, b in shape]
    d.polygon(poly, fill=(0, 0, 0))
    d.line(poly + [poly[0]], fill=(255, 255, 255), width=max(2, int(k * 1.2)))
    d.polygon(poly, fill=(0, 0, 0))
    im.save(path)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--vault", required=True)
    ap.add_argument("--clip", required=True, help="x,y,w,h in CSS pixels")
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--cursor", help="x,y in CSS pixels of the window")
    a = ap.parse_args()
    clip = [float(v) for v in a.clip.split(",")]
    capture(a.vault, clip, a.scale, a.out)
    if a.cursor:
        cx, cy = (float(v) for v in a.cursor.split(","))
        draw_cursor(a.out, cx, cy, clip)
    print(a.out)

if __name__ == "__main__":
    main()
