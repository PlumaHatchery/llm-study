import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
from matplotlib.animation import FuncAnimation, FFMpegWriter

# フォントは common.py が環境を見て選ぶ（元はLinuxのNotoを直指定していた）
import common as _C
FP, FPB = _C.FP, _C.FPB

BG, INK, MUTED = "#FAF9F5", "#2C2C2A", "#5F5E5A"
WIRE, ATOM = "#DEDBD1", "#B4B2A9"
EL, HOT, ACC = "#185FA5", "#D85A30", "#0F6E56"

FPS = 20
BOUND = [0, 5, 13, 21, 28, 36, 44, 52, 64, 73]
NSC = len(BOUND) - 1
DUR = BOUND[-1]
NF = int(FPS * DUR)

CAPS = ["",
        "金属の中には、自由に動ける電子がうようよいる",
        "電池をつなぐと、電子がいっせいに同じ向きへ動き出す",
        "1秒間にどれだけ通ったか。それが電流(アンペア)",
        "電圧は、電子を押す力。強く押せば、たくさん流れる",
        "抵抗は、通りにくさ。ぶつかった分が熱になる",
        "電流 = 電圧 ÷ 抵抗。これがオームの法則",
        "ところが電子そのものは、とんでもなく遅い",
        ""]

X0, X1, YC = 22, 138, 50
rng = np.random.default_rng(3)
NE = 22
ebx = rng.uniform(X0, X1, NE)
eby = rng.uniform(YC - 6.2, YC + 6.2, NE)
efx = rng.uniform(1.4, 2.6, NE)
efy = rng.uniform(1.0, 2.0, NE)
eph = rng.uniform(0, 7, NE)
ax_, ay_ = np.meshgrid(np.linspace(X0 + 4, X1 - 4, 13),
                       np.array([YC - 8.5, YC, YC + 8.5]))
atoms = np.column_stack([ax_.ravel(), ay_.ravel()])


def speed(t):
    if t < 13:
        return 0.0
    if t < 28:
        return 3.0
    if t < 36:
        return 3.0 + 5.0 * min(1.0, (t - 30) / 4.0)
    if t < 52:
        return 4.0
    return 1.1


DRIFT = np.zeros(NF + 1)
for i in range(NF):
    DRIFT[i + 1] = DRIFT[i] + speed(i / FPS) / FPS


def sc(t):
    for i in range(NSC):
        if BOUND[i] <= t < BOUND[i + 1]:
            return i
    return NSC - 1


def ease(u):
    return (lambda v: v * v * (3 - 2 * v))(min(max(u, 0.0), 1.0))


def epos(i):
    t = i / FPS
    x = (ebx + DRIFT[i] - X0) % (X1 - X0) + X0
    y = eby + 1.5 * np.sin(t * efy * 2.2 + eph)
    x = x + 0.9 * np.sin(t * efx * 3.1 + eph)
    return x, y


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
    al = ease((t - BOUND[k]) / 0.5)

    if k == 0:
        ax.text(80, 55, "電気とは何か", ha="center", va="center", fontsize=34,
                color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 38, "第1回 ── 電流・電圧・抵抗", ha="center", va="center",
                fontsize=18, color=MUTED, fontproperties=FP, alpha=al)
        return []
    if k == 8:
        ax.text(80, 60, "スイッチを入れて一瞬で点くのは、", ha="center",
                va="center", fontsize=25, color=INK, fontproperties=FPB,
                alpha=al)
        ax.text(80, 48, "電子が届くからではない。", ha="center", va="center",
                fontsize=25, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 33, "「押し合い」が伝わるから", ha="center", va="center",
                fontsize=25, color=ACC, fontproperties=FPB, alpha=al)
        return []

    ax.add_patch(FancyBboxPatch((X0 + 2, YC - 11), X1 - X0 - 4, 22,
                                boxstyle="round,pad=2", fc=WIRE, ec="#C9C6BC",
                                lw=1.2, zorder=2))
    ax.text(80, YC + 15, "金属(導線)の中", ha="center", va="bottom",
            fontsize=15, color=MUTED, fontproperties=FP, zorder=3)
    ax.scatter(atoms[:, 0], atoms[:, 1], s=210, c=ATOM, zorder=3,
               linewidths=0)

    ex, ey = epos(i)
    cols = [EL] * NE
    sz = [110] * NE
    if k == 7:
        cols[5] = HOT
        sz[5] = 260
    ax.scatter(ex, ey, s=sz, c=cols, zorder=6, linewidths=0)

    if k >= 2:
        b = ease((t - BOUND[2]) / 0.8)
        ax.text(X0 - 4, YC, "−", ha="right", va="center", fontsize=30,
                color=INK, fontproperties=FPB, alpha=b)
        ax.text(X1 + 4, YC, "＋", ha="right", va="center", fontsize=26,
                color="#A32D2D", fontproperties=FPB, alpha=b)
        ax.annotate("", xy=(96, 70), xytext=(64, 70),
                    arrowprops=dict(arrowstyle="-|>", color=ACC, lw=2.4,
                                    alpha=b), zorder=8)
        ax.text(80, 72.5, "電子の流れ", ha="center", va="bottom", fontsize=14,
                color=ACC, fontproperties=FP, alpha=b, zorder=8)

    if k == 3:
        ax.plot([112, 112], [YC - 12, YC + 12], color=HOT, lw=2, ls=(0, (4, 3)),
                zorder=7, alpha=al)
        n = int((t - BOUND[3]) * 14)
        ax.text(112, YC - 17, "通った数 %d" % n, ha="center", va="top",
                fontsize=17, color=HOT, fontproperties=FPB, alpha=al, zorder=8)

    if k == 4:
        f = min(1.0, (t - BOUND[4]) / 5.0)
        ax.add_patch(FancyBboxPatch((31, 21), 78, 7, boxstyle="round,pad=1",
                                    fc="#EFEDE5", ec="#D3D1C7", lw=0.8, zorder=4))
        ax.add_patch(FancyBboxPatch((31, 21), 4 + 74 * f, 7,
                                    boxstyle="round,pad=1", fc="#A32D2D",
                                    ec="none", alpha=0.85, zorder=5))
        ax.text(28, 24.5, "電圧", ha="right", va="center", fontsize=16,
                color=INK, fontproperties=FPB, zorder=5)
        ax.text(114, 24.5, "強い", ha="left", va="center", fontsize=15,
                color=MUTED, fontproperties=FP, zorder=5)

    if k == 5:
        h = ((t - BOUND[5]) * 2.3).astype(int) if False else int((t - BOUND[5]) * 2.3)
        for j in range(4):
            a2 = atoms[(h * 7 + j * 11) % len(atoms)]
            fa = 0.85 * (1 - ((t - BOUND[5]) * 2.3) % 1.0)
            ax.scatter([a2[0]], [a2[1]], s=430, c=HOT, alpha=fa * 0.5,
                       zorder=4, linewidths=0)
        ax.text(80, 24, "ぶつかる → 熱になる", ha="center", va="center",
                fontsize=18, color=HOT, fontproperties=FPB, alpha=al)

    if k == 6:
        ax.text(80, 25, "電流  =  電圧  ÷  抵抗", ha="center", va="center",
                fontsize=27, color=INK, fontproperties=FPB, alpha=al)
        ax.text(80, 15, "押す力が強いほど流れ、通りにくいほど流れない",
                ha="center", va="center", fontsize=15, color=MUTED,
                fontproperties=FP, alpha=al)

    if k == 7:
        ax.text(80, 26, "電子1個が進む速さは、秒速0.1ミリほど", ha="center",
                va="center", fontsize=20, color=HOT, fontproperties=FPB,
                alpha=al)
        ax.text(80, 16, "歩くよりはるかに遅い。押し合いだけが光の速さで伝わる",
                ha="center", va="center", fontsize=15, color=MUTED,
                fontproperties=FP, alpha=al)
        w = ((t - BOUND[7]) % 2.2) / 2.2
        if w < 0.5:
            wx = X0 + (X1 - X0) * (w / 0.5)
            ax.plot([wx, wx], [YC - 11, YC + 11], color=ACC, lw=3,
                    alpha=0.55, zorder=7)

    c = CAPS[k]
    if c:
        ca = min(1.0, (t - BOUND[k]) / 0.5, (BOUND[k + 1] - t) / 0.4)
        ax.text(80, 7, c, ha="center", va="center", fontsize=21, color=INK,
                fontproperties=FPB, alpha=max(0.0, ca), zorder=12)
    return []


if __name__ == "__main__":
    ani = FuncAnimation(fig, draw, frames=NF, interval=1000 / FPS, blit=False)
    w = FFMpegWriter(fps=FPS, bitrate=2600,
                     extra_args=["-pix_fmt", "yuv420p", "-vcodec", "libx264"])
    ani.save("out/ep01_denki.mp4", writer=w, dpi=100,
             savefig_kwargs={"facecolor": BG})
    print("ep01 done", DUR)
