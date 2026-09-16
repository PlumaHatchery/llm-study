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
ROAD = "#B4B2A9"
EL, ELD = "#378ADD", "#0C447C"
GFILL, GEDGE = "#E8E6DE", "#888780"
OKC, NGC = "#0F6E56", "#993C1D"

FPS = 20
BOUND = [0, 5, 11, 17, 23, 30, 37, 43, 49, 55, 61, 68, 75]
NSC = len(BOUND) - 1
DUR = BOUND[-1]
NF = int(FPS * DUR)

CAPS = [
    "",
    "一本道の途中に、橋を2つ置く。板AとB、2枚で操る",
    "Aだけ入れても、Bのところで止まってしまう",
    "Bだけでも同じ。今度はAのところで止まる",
    "両方入れたときだけ、向こう側まで渡れる",
    "「AもBも」のときだけ通る。これが「かつ」",
    "今度は道を2本に分けて、それぞれに橋を置く",
    "Aだけでも、上の道を通って渡れる",
    "Bだけでも、下の道を通って渡れる",
    "両方切ったときだけ、どこも渡れない",
    "「AかBのどちらか」で通る。これが「または」",
    "",
]
ST = [(0, 0), (0, 0), (1, 0), (0, 1), (1, 1), (1, 1),
      (0, 0), (1, 0), (0, 1), (0, 0), (0, 0), (0, 0)]
MODE = ["title", "ser", "ser", "ser", "ser", "tblA",
        "par", "par", "par", "par", "tblO", "end"]

SER_SEG = [(20, 55), (70, 95), (110, 140)]
SER_GAP = [(55, 70), (95, 110)]
SER_Y = 50.0
SER_PATH = [(20, 50), (140, 50)]

PAR_UP, PAR_DN = 63.0, 37.0
PAR_GAP = (72, 87)
PAR_PATH_U = [(20, 50), (45, 50), (45, PAR_UP), (115, PAR_UP), (115, 50), (140, 50)]
PAR_PATH_D = [(20, 50), (45, 50), (45, PAR_DN), (115, PAR_DN), (115, 50), (140, 50)]


def sc(t):
    for i in range(NSC):
        if BOUND[i] <= t < BOUND[i + 1]:
            return i
    return NSC - 1


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def state(t):
    i = sc(t)
    a, b = ST[i]
    pa, pb = ST[i - 1] if i > 0 else (0, 0)
    k = ease((t - BOUND[i]) / 0.55)
    return pa + (a - pa) * k, pb + (b - pb) * k


def plen(pts):
    p = np.array(pts, dtype=float)
    d = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    return p, np.concatenate([[0], np.cumsum(d)])


def ppt(pts, u):
    p, cs = plen(pts)
    s = u * cs[-1]
    j = int(np.clip(np.searchsorted(cs, s) - 1, 0, len(cs) - 2))
    f = (s - cs[j]) / max(cs[j + 1] - cs[j], 1e-9)
    return p[j] + (p[j + 1] - p[j]) * f


def road(ax, x0, x1, y, al=1.0):
    ax.plot([x0, x1], [y, y], color=ROAD, lw=7, solid_capstyle="round",
            zorder=3, alpha=al)


def plate(ax, cx, top, lab, on, al=1.0):
    w, h = 22, 7
    ax.add_patch(FancyBboxPatch((cx - w / 2 + 1, top + 1), w - 2, h - 2,
                                boxstyle="round,pad=1", fc=GFILL, ec=GEDGE,
                                lw=1.2, alpha=al, zorder=7))
    ax.text(cx, top + h / 2, lab, ha="center", va="center", fontsize=17,
            color=INK, fontproperties=FPB, alpha=al, zorder=8)
    if on > 0.02:
        for k, px in enumerate((-6.5, 0, 6.5)):
            ax.text(cx + px, top - 3.5, "+", ha="center", va="center",
                    fontsize=15, color="#A32D2D", fontproperties=FPB,
                    alpha=al * on, zorder=8)
    ax.text(cx, top + h + 2.0, "ON" if on > 0.5 else "OFF", ha="center",
            va="bottom", fontsize=13, fontproperties=FPB,
            color=OKC if on > 0.5 else MUTED, alpha=al, zorder=8)


def bridge(ax, x0, x1, y, on):
    if on <= 0.02:
        ax.text((x0 + x1) / 2, y, "×", ha="center", va="center", fontsize=20,
                color=NGC, fontproperties=FPB, zorder=6)
        return
    xm = x0 + (x1 - x0) * on
    ax.plot([x0, xm], [y, y], color=EL, lw=7, solid_capstyle="round",
            zorder=4, alpha=on)


def flow(ax, path, t, live):
    if live <= 0.5:
        return
    for k in range(3):
        u = ((t * 0.34) + k / 3.0) % 1.0
        p = ppt(path, u)
        ax.scatter([p[0]], [p[1]], s=150, c=ELD, zorder=9, linewidths=0)


def table(ax, kind, t):
    a = ease((t - BOUND[sc(t)]) / 0.7)
    rows = [("0", "0", "0"), ("1", "0", "0"), ("0", "1", "0"), ("1", "1", "1")]
    if kind == "or":
        rows = [("0", "0", "0"), ("1", "0", "1"), ("0", "1", "1"), ("1", "1", "1")]
    x0, y0, cw, rh = 52, 62, 18, 8
    heads = ["A", "B", "結果"]
    for c in range(3):
        ax.text(x0 + cw * c + cw / 2, y0 + rh / 2, heads[c], ha="center",
                va="center", fontsize=16, color=MUTED, fontproperties=FPB,
                alpha=a, zorder=8)
    for r, row in enumerate(rows):
        yy = y0 - rh * (r + 1)
        ra = ease((t - BOUND[sc(t)] - 0.5 - r * 0.45) / 0.5)
        ax.add_patch(FancyBboxPatch((x0 + 1, yy + 1), cw * 3 - 2, rh - 2,
                                    boxstyle="round,pad=1",
                                    fc="#F1EFE8" if r % 2 == 0 else BG,
                                    ec="#D3D1C7", lw=0.8, alpha=ra, zorder=4))
        for c in range(3):
            col = INK if c < 2 else (OKC if row[2] == "1" else NGC)
            ax.text(x0 + cw * c + cw / 2, yy + rh / 2, row[c], ha="center",
                    va="center", fontsize=17, color=col, fontproperties=FPB,
                    alpha=ra, zorder=8)
    ax.text(80, y0 - rh * 4 - 5, "1 = 通る / 0 = 通らない", ha="center",
            va="top", fontsize=14, color=MUTED, fontproperties=FP, alpha=a,
            zorder=8)


fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])


def draw(i):
    t = i / FPS
    ax.clear()
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    k = sc(t)
    m = MODE[k]
    a, b = state(t)
    al = ease((t - BOUND[k]) / 0.5)

    if m == "title":
        ax.text(80, 56, "スイッチを2つ並べると、", ha="center", va="center",
                fontsize=30, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 44, "「意味」が生まれる", ha="center", va="center",
                fontsize=30, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 28, "第2回 ── 直列と並列", ha="center", va="center",
                fontsize=18, color=MUTED, fontproperties=FP, alpha=al)
    elif m == "end":
        ax.text(80, 58, "電圧の高い低いが、", ha="center", va="center",
                fontsize=27, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 46, "「かつ」「または」になった", ha="center", va="center",
                fontsize=27, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 28, "ここから先は、全部この積み上げです", ha="center",
                va="center", fontsize=18, color=MUTED, fontproperties=FP,
                alpha=al)
    elif m.startswith("tbl"):
        table(ax, "and" if m == "tblA" else "or", t)
    elif m == "ser":
        for s in SER_SEG:
            road(ax, s[0], s[1], SER_Y, al)
        bridge(ax, *SER_GAP[0], SER_Y, a)
        bridge(ax, *SER_GAP[1], SER_Y, b)
        plate(ax, 62.5, 58, "A", a, al)
        plate(ax, 102.5, 58, "B", b, al)
        ax.text(16, SER_Y, "入口", ha="right", va="center", fontsize=15,
                color=MUTED, fontproperties=FP, alpha=al)
        ax.text(144, SER_Y, "出口", ha="left", va="center", fontsize=15,
                color=MUTED, fontproperties=FP, alpha=al)
        flow(ax, SER_PATH, t, min(a, b))
        live = min(a, b) > 0.5
        ax.text(80, 26, "通った" if live else "通らない", ha="center",
                va="center", fontsize=20, fontproperties=FPB,
                color=OKC if live else NGC, alpha=al)
    else:
        road(ax, 20, 45, 50, al)
        road(ax, 115, 140, 50, al)
        ax.plot([45, 45], [PAR_DN, PAR_UP], color=ROAD, lw=7, zorder=3,
                solid_capstyle="round", alpha=al)
        ax.plot([115, 115], [PAR_DN, PAR_UP], color=ROAD, lw=7, zorder=3,
                solid_capstyle="round", alpha=al)
        for y in (PAR_UP, PAR_DN):
            road(ax, 45, PAR_GAP[0], y, al)
            road(ax, PAR_GAP[1], 115, y, al)
        bridge(ax, *PAR_GAP, PAR_UP, a)
        bridge(ax, *PAR_GAP, PAR_DN, b)
        plate(ax, 79.5, PAR_UP + 8, "A", a, al)
        plate(ax, 79.5, PAR_DN + 8, "B", b, al)
        ax.text(16, 50, "入口", ha="right", va="center", fontsize=15,
                color=MUTED, fontproperties=FP, alpha=al)
        ax.text(144, 50, "出口", ha="left", va="center", fontsize=15,
                color=MUTED, fontproperties=FP, alpha=al)
        flow(ax, PAR_PATH_U, t, a)
        flow(ax, PAR_PATH_D, t, b)
        live = max(a, b) > 0.5
        ax.text(80, 24, "通った" if live else "通らない", ha="center",
                va="center", fontsize=20, fontproperties=FPB,
                color=OKC if live else NGC, alpha=al)

    c = CAPS[k]
    if c:
        ca = min(1.0, (t - BOUND[k]) / 0.5, (BOUND[k + 1] - t) / 0.4)
        ax.text(80, 9, c, ha="center", va="center", fontsize=21, color=INK,
                fontproperties=FPB, alpha=max(0.0, ca), zorder=12)
    return []


if __name__ == "__main__":
    ani = FuncAnimation(fig, draw, frames=NF, interval=1000 / FPS, blit=False)
    w = FFMpegWriter(fps=FPS, bitrate=2600,
                     extra_args=["-pix_fmt", "yuv420p", "-vcodec", "libx264"])
    ani.save("/home/claude/lesson2.mp4", writer=w, dpi=100,
             savefig_kwargs={"facecolor": BG})
    print("done", DUR)
