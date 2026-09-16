import json
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
NFILL, NEDGE = "#E6F1FB", "#378ADD"
PFILL, PEDGE = "#FAECE7", "#D85A30"
EL = "#185FA5"
GFILL, GEDGE = "#E8E6DE", "#888780"

FPS = 20
PAD = 1.2
LEAD = 0.5

durs = json.load(open("/home/claude/durs.json"))
T = [0.0]
for d in durs:
    T.append(T[-1] + d + PAD)
DUR = T[-1]
NF = int(FPS * DUR)

CAPS = [
    "トランジスタは、どうやって電気を通したり止めたりするのか",
    "電気が流れる = 「電子」という粒が移動すること",
    "左と右は粒だらけ。でも真ん中は空き地で、渡れない",
    "空き地の上にフタをして、金属の板を置く",
    "板にプラスの電気をためる",
    "プラスはマイナスを引き寄せる",
    "集まった粒が橋になった。左から右へ電気が流れる",
    "板の電気を抜けば、橋は散って消える",
    "電気で入り切りできるスイッチ。CPUには何百億個",
]

SUB = (20, 28, 120, 28)
LN = (26, 44, 32, 12)
RN = (102, 44, 32, 12)
SURF = 56.0
GAPL = 58.0
OX = (62, 57, 36, 2.6)
GT = (62, 60.5, 36, 7)

rng = np.random.default_rng(7)
src = np.column_stack([rng.uniform(29, 55, 9), rng.uniform(46.5, 53.5, 9)])
drn = np.column_stack([rng.uniform(105, 131, 9), rng.uniform(46.5, 53.5, 9)])
NS = 7
stray0 = np.column_stack([rng.uniform(60, 100, NS), rng.uniform(34, 43, NS)])
chan1 = np.column_stack([np.linspace(60.5, 99.5, NS), np.full(NS, SURF - 1.8)])

T_LBL = T[1]
T_OFF0, T_OFF1 = T[2] + 1.0, T[3]
T_GATE = T[3] + 0.6
T_PLUS0 = T[4] + 0.6
T_PULL0, T_PULL1 = T[5] + 2.0, T[5] + durs[5] - 1.5
T_FLOW0 = T[6] + 1.0
T_FLOW1 = T[7] + 1.2
T_PLUS1 = T[7] + 1.0
T_REL0, T_REL1 = T[7] + 1.6, T[7] + 3.4


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def cap(t):
    for i in range(len(CAPS)):
        a = T[i]
        b = T[i + 1]
        if a <= t < b:
            return CAPS[i], max(0.0, min(1.0, (t - a) / 0.5, (b - t) / 0.4))
    return CAPS[-1], 1.0


def rrect(ax, x, y, w, h, fc, ec, r=1.2, lw=1.2, al=1.0, z=2):
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2 * r, h - 2 * r,
                                boxstyle="round,pad=%f" % r, fc=fc, ec=ec,
                                lw=lw, alpha=al, zorder=z))


fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])


def draw(i):
    t = i / FPS
    ax.clear()
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")

    dev = ease(t / 1.6)
    rrect(ax, *SUB, PFILL, PEDGE, r=1.6, al=dev)
    rrect(ax, *LN, NFILL, NEDGE, al=dev, z=3)
    rrect(ax, *RN, NFILL, NEDGE, al=dev, z=3)

    if t >= T_LBL:
        a = ease((t - T_LBL) / 0.8)
        for x, s in ((42, "粒がいる"), (118, "粒がいる")):
            ax.text(x, 58.5, s, ha="center", va="bottom", fontsize=15,
                    color=MUTED, fontproperties=FP, alpha=a, zorder=6)
        ax.text(80, 31.0, "空き地", ha="center", va="center", fontsize=15,
                color="#993C1D", fontproperties=FP, alpha=a, zorder=6)

    jt = 0.35 * np.sin(t * 2.0 + np.arange(9))
    ax.scatter(src[:, 0], src[:, 1] + jt, s=90, c=EL, zorder=5, alpha=dev,
               linewidths=0)
    ax.scatter(drn[:, 0], drn[:, 1] - jt, s=90, c=EL, zorder=5, alpha=dev,
               linewidths=0)

    if t >= T_GATE:
        g = ease((t - T_GATE) / 1.2)
        dy = (1 - g) * 14
        rrect(ax, OX[0], OX[1] + dy, OX[2], OX[3], "#D3D1C7", GEDGE, r=0.6,
              al=g, z=7)
        rrect(ax, GT[0], GT[1] + dy, GT[2], GT[3], GFILL, GEDGE, r=0.8,
              al=g, z=7)
        ax.text(80, GT[1] + GT[3] + 2.2 + dy, "板(ゲート)", ha="center",
                va="bottom", fontsize=15, color=MUTED, fontproperties=FP,
                alpha=g, zorder=7)

    if T_PLUS0 <= t < T_PLUS1 + 0.8:
        pa = ease((t - T_PLUS0) / 0.7)
        if t >= T_PLUS1:
            pa = 1 - ease((t - T_PLUS1) / 0.8)
        for px in (68, 76, 84, 92):
            ax.text(px, GT[1] + GT[3] / 2, "+", ha="center", va="center",
                    fontsize=20, color="#A32D2D", fontproperties=FPB,
                    alpha=max(0.0, pa), zorder=8)

    if t < T_PULL0:
        pos = stray0.copy()
        pos[:, 1] += 0.3 * np.sin(t * 1.6 + np.arange(NS))
    elif t < T_PULL1:
        pos = stray0 + (chan1 - stray0) * ease((t - T_PULL0) /
                                               (T_PULL1 - T_PULL0))
    elif t < T_REL0:
        pos = chan1.copy()
        pos[:, 1] += 0.18 * np.sin(t * 3.0 + np.arange(NS))
    else:
        pos = chan1 + (stray0 - chan1) * ease((t - T_REL0) / (T_REL1 - T_REL0))
    ax.scatter(pos[:, 0], pos[:, 1], s=70, c=EL, zorder=6, alpha=dev * 0.85,
               linewidths=0)

    if T_OFF0 <= t < T_OFF1:
        ph = ((t - T_OFF0) % 2.6) / 2.6
        if ph < 0.55:
            x = 31 + (GAPL - 2 - 31) * ease(ph / 0.55)
        else:
            x = (GAPL - 2) - (GAPL - 2 - 31) * ease((ph - 0.55) / 0.45)
        ax.scatter([x], [50], s=150, c="#D85A30", zorder=9, linewidths=0)
        if ph > 0.45:
            ax.text(GAPL + 1.5, 50, "×", ha="left", va="center", fontsize=22,
                    color="#D85A30", fontproperties=FPB, zorder=9)

    if T_FLOW0 <= t < T_FLOW1:
        fa = min(1.0, (t - T_FLOW0) / 0.6, (T_FLOW1 - t) / 0.6)
        for k in range(3):
            x = 30 + ((t - T_FLOW0) * 26 + k * 33.0) % 100
            ax.scatter([x], [SURF - 1.8], s=150, c="#0C447C", zorder=9,
                       alpha=max(0.0, fa), linewidths=0)
        ax.annotate("", xy=(112, 77), xytext=(48, 77),
                    arrowprops=dict(arrowstyle="-|>", color="#185FA5", lw=2.2,
                                    alpha=max(0.0, fa)), zorder=9)
        ax.text(80, 79.0, "電気が流れている", ha="center", va="bottom",
                fontsize=14, color="#185FA5", fontproperties=FP,
                alpha=max(0.0, fa), zorder=9)

    s, a = cap(t)
    ax.text(80, 9, s, ha="center", va="center", fontsize=21, color=INK,
            fontproperties=FPB, alpha=a, zorder=12)

    badge = None
    if T_OFF0 <= t < T_OFF1:
        badge = ("OFF", "#993C1D")
    elif T_FLOW0 <= t < T_FLOW1:
        badge = ("ON", "#0F6E56")
    if badge:
        ax.text(150, 82, badge[0], ha="right", va="center", fontsize=26,
                color=badge[1], fontproperties=FPB, zorder=12)
    return []


if __name__ == "__main__":
    ani = FuncAnimation(fig, draw, frames=NF, interval=1000 / FPS, blit=False)
    w = FFMpegWriter(fps=FPS, bitrate=2600,
                     extra_args=["-pix_fmt", "yuv420p", "-vcodec", "libx264"])
    ani.save("/home/claude/video.mp4", writer=w, dpi=100,
             savefig_kwargs={"facecolor": BG})
    json.dump({"T": T, "LEAD": LEAD, "DUR": DUR},
              open("/home/claude/timing.json", "w"))
    print("video done", round(DUR, 1), "sec")
