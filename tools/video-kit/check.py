"""指定した秒のフレームをPNGに切り出す。レンダ後に必ず目で見るための道具。

  python3 check.py out/ep03.mp4 3 11 20 28
  → out/frames/ep03_t3.png ... を作る
"""
import os
import subprocess
import sys

if len(sys.argv) < 3:
    sys.exit("usage: python3 check.py <mp4> <sec> [sec ...]")

src = sys.argv[1]
name = os.path.splitext(os.path.basename(src))[0]
outdir = os.path.join(os.path.dirname(src) or ".", "frames")
os.makedirs(outdir, exist_ok=True)

for s in sys.argv[2:]:
    dst = os.path.join(outdir, "%s_t%s.png" % (name, s))
    subprocess.run(["ffmpeg", "-v", "error", "-ss", s, "-i", src,
                    "-frames:v", "1", "-y", dst], check=True)
    print(dst)
