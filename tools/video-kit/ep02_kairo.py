import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
from matplotlib.animation import FuncAnimation, FFMpegWriter

FP = FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
FPB = FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc")

BG, INK, MUTED = "#FAF9F5", "#2C2C2A", "#5F5E5A"
WIRE = "#B4B2A9"
EL, HOT, ACC = "#185FA5", "#A32D2D", "#0F6E56"
RFILL, REDGE = "#E8E6DE", "#888780"

FPS = 20
BOUND = [0, 5, 12, 19, 26, 34, 42, 49, 57, 65, 73]
NSC = len(BOUND) - 1
DUR = BOUND[-1]
NF = int(FPS * DUR)

CAPS = ["",
        "電池、抵抗、導線。回路図はこの3つで書ける",
        "6ボルトで押して、3オームの抵抗。流れるのは2アンペア",
        "抵抗を倍にすると、電流は半分になる",
        "直列につなぐと抵抗は足し算。電流はどこも同じ",
        "そのかわり電圧が分かれる。足すと元の6ボルトに戻る",
        "抵抗の比で電圧を取り出せる。これが分圧",
        "並列は道が2本。どちらの抵抗にも6ボルトがまるごとかかる",
        "そのかわり電流が分かれる。合わせると4.5アンペア",
        ""]

LOOP = [(28, 78), (132, 78), (132, 22), (28, 22), (28, 78)]
PAR_LO = [(28, 78), (60, 78), (60, 60), (100, 60), (100, 78), (132, 78),
          (132, 22), (28, 22), (28, 78)]


def sc(t):
    for i in range(NSC):
        if BOUND[i] <= t < BOUND[i + 1]:
            return i
    return NSC - 1


def ease(u):
    return (lambda v: v * v * (3 - 2 * v))(min(max(u, 0.0), 1.0))


def plen(pts):
    p = np.array(pts, dtype=float)
    d = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    return p, np.concatenate([[0], np.cumsum(d)])


def ppt(pts, u):
    p, cs = plen(pts)
    s = (u % 1.0) * cs[-1]
    j = int(np.clip(np.searchsorted(cs, s) - 1, 0, len(cs) - 2))
    f = (s - cs[j]) / max(cs[j + 1] - cs[j], 1e-9)
    return p[j] + (p[j + 1] - p[j]) * f


def wire(ax, pts, skip=None):
    p = np.array(pts, dtype=float)
    ax.plot(p[:, 0], p[:, 1], color=WIRE, lw=5, solid_capstyle="round",
            solid_joinstyle="round", zorder=3)


def battery(ax):
    ax.plot([28, 28], [56, 44], color=BG, lw=9, zorder=4)
    ax.plot([23, 33], [52, 52], color=INK, lw=3, zorder=5)
    ax.plot([25.5, 30.5], [47, 47], color=INK, lw=3, zorder=5)
    ax.text(19, 56, "＋", ha="center", va="center", fontsize=17, color=HOT,
            fontproperties=FPB, zorder=5)
    ax.text(19, 43, "−", ha="center", va="center", fontsize=20, color=INK,
            fontproperties=FPB, zorder=5)
    ax.text(37, 49, "6V", ha="left", va="center", fontsize=18, color=INK,
            fontproperties=FPB, zorder=5)


def res(ax, cx, cy, lab, sub=None, hi=False):
    w, h = 22, 9
    ax.plot([cx - w / 2, cx + w / 2], [cy, cy], color=BG, lw=9, zorder=4)
    ax.add_patch(FancyBboxPatch((cx - w / 2 + 1, cy - h / 2 + 1), w - 2, h - 2,
                                boxstyle="round,pad=1",
                                fc="#F7E4DC" if hi else RFILL,
                                ec=HOT if hi else REDGE, lw=1.4, zorder=5))
    ax.text(cx, cy, lab, ha="center", va="center", fontsize=17, color=INK,
            fontproperties=FPB, zorder=6)
    if sub:
        ax.text(cx, cy + h / 2 + 2.5, sub, ha="center", va="bottom",
                fontsize=17, color=HOT, fontproperties=FPB, zorder=6)


def flow(ax, path, t, amps, seed=0):
    n = max(2, int(round(amps * 2)))
    for k in range(n):
        u = (t * 0.055 * max(amps, 0.4) + k / n + seed) % 1.0
        p = ppt(path, u)
        ax.scatter([p[0]], [p[1]], s=130, c=EL, zorder=7, linewidths=0)


fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])


def info(ax, s, col=INK, y=12):
    ax.text(80, y, s, ha="center", va="center", fontsize=23, color=col,
            fontproperties=FPB, zorder=9)


def draw(i):
    t = i / FPS
    ax.clear()
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    k = sc(t)
    al = ease((t - BOUND[k]) / 0.5)

    if k == 0:
        ax.text(80, 55, "回路の読み方", ha="center", va="center", fontsize=34,
                color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 38, "第2回 ── オームの法則と、直列・並列", ha="center",
                va="center", fontsize=18, color=MUTED, fontproperties=FP,
                alpha=al)
        return []

    if k == 9:
        rows = [("直列", "電流が共通", "電圧が分かれる"),
                ("並列", "電圧が共通", "電流が分かれる")]
        for r, row in enumerate(rows):
            yy = 58 - r * 16
            ra = ease((t - BOUND[9] - r * 0.6) / 0.6)
            ax.add_patch(FancyBboxPatch((33, yy - 6), 94, 12,
                                        boxstyle="round,pad=1",
                                        fc="#F1EFE8" if r == 0 else BG,
                                        ec="#D3D1C7", lw=0.8, alpha=ra,
                                        zorder=4))
            ax.text(45, yy, row[0], ha="center", va="center", fontsize=21,
                    color=INK, fontproperties=FPB, alpha=ra, zorder=6)
            ax.text(78, yy, row[1], ha="center", va="center", fontsize=18,
                    color=ACC, fontproperties=FPB, alpha=ra, zorder=6)
            ax.text(112, yy, row[2], ha="center", va="center", fontsize=18,
                    color=HOT, fontproperties=FPB, alpha=ra, zorder=6)
        ax.text(80, 26, "つなぎ方を変えると、何が共通で何が分かれるかが入れ替わる",
                ha="center", va="center", fontsize=17, color=MUTED,
                fontproperties=FP, alpha=al)
        return []

    par = k >= 7
    wire(ax, PAR_LO if par else LOOP)
    if par:
        wire(ax, LOOP)
    battery(ax)

    if k == 1:
        res(ax, 80, 78, "抵抗")
        ax.text(80, 18, "導線は0Ω、抵抗は「通りにくさ」", ha="center",
                va="center", fontsize=19, color=MUTED, fontproperties=FP)
        flow(ax, LOOP, t, 1.0)
    elif k == 2:
        res(ax, 80, 78, "3Ω", hi=True)
        flow(ax, LOOP, t, 2.0)
        info(ax, "6V ÷ 3Ω = 2A")
    elif k == 3:
        res(ax, 80, 78, "6Ω", hi=True)
        flow(ax, LOOP, t, 1.0)
        info(ax, "6V ÷ 6Ω = 1A")
    elif k in (4, 5, 6):
        res(ax, 62, 78, "2Ω", sub="2V" if k >= 5 else None, hi=(k == 6))
        res(ax, 104, 78, "4Ω", sub="4V" if k >= 5 else None, hi=(k == 6))
        flow(ax, LOOP, t, 1.0)
        if k == 4:
            info(ax, "2Ω + 4Ω = 6Ω  →  6V ÷ 6Ω = 1A")
        elif k == 5:
            info(ax, "2V + 4V = 6V")
        else:
            info(ax, "抵抗の比 2 : 4 が、そのまま電圧の比になる", ACC)
    else:
        res(ax, 80, 78, "2Ω", sub="3A" if k == 8 else "6V", hi=(k == 8))
        res(ax, 80, 60, "4Ω", sub="1.5A" if k == 8 else "6V", hi=(k == 8))
        flow(ax, LOOP, t, 3.0)
        flow(ax, PAR_LO, t, 1.5, seed=0.5)
        info(ax, "どちらにも6Vがかかる" if k == 7 else "3A + 1.5A = 4.5A")

    c = CAPS[k]
    if c:
        ca = min(1.0, (t - BOUND[k]) / 0.5, (BOUND[k + 1] - t) / 0.4)
        ax.text(80, 6, c, ha="center", va="center", fontsize=20, color=INK,
                fontproperties=FPB, alpha=max(0.0, ca), zorder=12)
    return []


if __name__ == "__main__":
    ani = FuncAnimation(fig, draw, frames=NF, interval=1000 / FPS, blit=False)
    w = FFMpegWriter(fps=FPS, bitrate=2600,
                     extra_args=["-pix_fmt", "yuv420p", "-vcodec", "libx264"])
    ani.save("/home/claude/ep02.mp4", writer=w, dpi=100,
             savefig_kwargs={"facecolor": BG})
    print("ep02 done", DUR)
