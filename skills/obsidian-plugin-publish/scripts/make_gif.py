#!/usr/bin/env python3
"""Assemble captured frames into a small looping GIF with per-frame durations.

usage: make_gif.py frames.json out.gif [--width 450] [--colors 96]

frames.json: [{"file": "f001.png", "duration": 1.0}, {"file": "f002.png", "duration": 0.04}, ...]
(relative paths are resolved against the JSON file's folder). Uses an ffmpeg palette built from
frame differences and keeps variable frame timing, which keeps scroll animations smooth and the
file small (~80 frames at 450 px ≈ 2.6 MB).
"""
import argparse, json, os, subprocess, sys, tempfile

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames"); ap.add_argument("out")
    ap.add_argument("--width", type=int, default=450)
    ap.add_argument("--colors", type=int, default=96)
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.frames))
    frames = json.load(open(a.frames))
    if not frames:
        sys.exit("no frames")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lst:
        for fr in frames:
            path = fr["file"] if os.path.isabs(fr["file"]) else os.path.join(base, fr["file"])
            lst.write(f"file '{path}'\nduration {fr.get('duration', 0.04)}\n")
        lst.write(f"file '{path}'\n")          # concat demuxer needs the last file repeated
    vf = (f"scale={a.width}:-1:flags=lanczos,split[a][b];"
          f"[a]palettegen=stats_mode=diff:max_colors={a.colors}[p];"
          f"[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst.name,
                    "-fps_mode", "vfr", "-vf", vf, "-loop", "0", a.out], check=True)
    os.unlink(lst.name)
    size = os.path.getsize(a.out)
    try:
        from PIL import Image
        im = Image.open(a.out)
        print(f"{a.out}: {im.size[0]}x{im.size[1]}, {im.n_frames} frames, {size/1e6:.1f} MB")
    except ImportError:
        print(f"{a.out}: {size/1e6:.1f} MB")

if __name__ == "__main__":
    main()
