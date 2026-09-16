"""第5回 なぜシリコンなのか ── 手が4本。

  原子1個から始めて、格子で手が全部ふさがり、動ける電子が0になる。
  導体(手が余る)・半導体(ぎりぎり)・絶縁体(固く結ばれて動かない)を
  横に並べ、同じ電圧をかけて流れる量を比べる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 15, 27, 38, 50, 60],
    caps=[
        "",                                          # 0 タイトル
        "シリコンは、手を4本もっている",               # 1
        "隣と手をつなぐと、余る手がなくなる",           # 2
        "手の余り具合で、3種類に分かれる",             # 3
        "同じ電圧をかけると、流れる量がまるで違う",      # 4
        "",                                          # 5 まとめ
    ],
)

fig, ax = C.new_axes()

# --- 3枚のパネル ---------------------------------------------------
PW, PH = 44.0, 24.0
PY0, PY1 = 42.0, 66.0
PXS = [6.0, 58.0, 110.0]
NAMES = ["導体（金属）", "半導体（シリコン）", "絶縁体（ガラス）"]
SUBS = ["手が余っている", "ぎりぎり足りている", "固く結ばれている"]
NFREE = [10, 2, 0]           # 動ける電子の数
VEL = [7.0, 1.1, 0.0]        # 電圧をかけたときの流れる速さ

_rng = np.random.default_rng(5)
# 原子は y=46/54/62 の3行。自由電子はその行間に置いて、重ならないようにする
_LANES = np.array([50.0, 58.0])
FREE_Y = [_LANES[_rng.integers(0, 2, n)] + _rng.uniform(-1.0, 1.0, n)
          for n in NFREE]
FREE_U = [_rng.uniform(0, 1, n) for n in NFREE]

# 流れは累積。全フレーム分を先に積む
N = SC.nframes
DRIFT = np.zeros((3, N + 1))
for _i in range(N):
    _on = 1.0 if SC.idx(_i / C.FPS) == 4 else 0.0
    for _m in range(3):
        DRIFT[_m, _i + 1] = DRIFT[_m, _i] + _on * VEL[_m] / C.FPS / PW


def atom(x, y, r=2.6, al=1.0, lab="Si"):
    ax.scatter([x], [y], s=430 * (r / 2.6) ** 2, c=C.FILL, edgecolors=C.EDGE,
               linewidths=1.2, zorder=5, alpha=al)
    if lab:
        ax.text(x, y, lab, ha="center", va="center", fontsize=11,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=6)


def bond(x0, y0, x1, y1, al=1.0, color=C.GRAY, lw=1.6, pair=True):
    """結合の手。2本の平行線＝電子2個で1組"""
    dx, dy = x1 - x0, y1 - y0
    d = np.hypot(dx, dy)
    ox, oy = (-dy / d * 0.55, dx / d * 0.55) if pair else (0.0, 0.0)
    for s in ((1, -1) if pair else (0,)):
        ax.plot([x0 + s * ox, x1 + s * ox], [y0 + s * oy, y1 + s * oy],
                color=color, lw=lw, alpha=al, zorder=3)


def lattice(cx, cy, cols, rows, dx, dy, al=1.0, stub=True, color=C.GRAY,
            lw=1.6, lab="Si", r=2.6):
    """正方格子に並べ、隣同士を手でつなぐ(2次元の教科書表現)"""
    xs = cx + (np.arange(cols) - (cols - 1) / 2) * dx
    ys = cy + (np.arange(rows) - (rows - 1) / 2) * dy
    for j, y in enumerate(ys):
        for i2, x in enumerate(xs):
            if i2 < cols - 1:
                bond(x + r, y, xs[i2 + 1] - r, y, al, color, lw)
            if j < rows - 1:
                bond(x, y + r, x, ys[j + 1] - r, al, color, lw)
    if stub:
        for y in ys:
            bond(xs[0] - r, y, xs[0] - r - 2.4, y, al, color, lw)
            bond(xs[-1] + r, y, xs[-1] + r + 2.4, y, al, color, lw)
        for x in xs:
            bond(x, ys[0] - r, x, ys[0] - r - 2.0, al, color, lw)
            bond(x, ys[-1] + r, x, ys[-1] + r + 2.0, al, color, lw)
    for y in ys:
        for x in xs:
            atom(x, y, r, al, lab)


def panel(m, i, al=1.0, live=False):
    px = PXS[m]
    C.rrect(ax, px, PY0, PW, PH, C.BG, C.EDGE, r=1.4, lw=1.0, al=al * 0.9, z=1)
    hard = (m == 2)
    lattice(px + PW / 2, (PY0 + PY1) / 2, 4, 3, 10.0, 8.0, al,
            stub=False, color=C.NGC if hard else C.GRAY,
            lw=2.2 if hard else 1.6, lab="", r=2.2)
    n = NFREE[m]
    if n:
        u = (FREE_U[m] + DRIFT[m, i]) % 1.0
        ax.scatter(px + 2 + u * (PW - 4), FREE_Y[m], s=85, c=C.EL,
                   zorder=7, linewidths=0, alpha=al)
    ax.text(px + PW / 2, 74.5, NAMES[m], ha="center", va="center",
            fontsize=15, color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(px + PW / 2, 69.5, SUBS[m], ha="center", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    if live:
        ax.plot([px - 1.8, px - 1.8], [PY0 + 1, PY1 - 1], color=C.EL, lw=4,
                solid_capstyle="round", alpha=al, zorder=4)
        ax.plot([px + PW + 1.8, px + PW + 1.8], [PY0 + 1, PY1 - 1],
                color=C.DEEP, lw=4, solid_capstyle="round", alpha=al, zorder=4)
        cnt = int(DRIFT[m, i] * 9)
        ax.text(px + PW / 2, 36.0, "通った数 %d" % cnt, ha="center",
                va="center", fontsize=15,
                color=C.HOT if cnt else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "なぜシリコンなのか", sub="第5回 ── 手が4本")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "半導体は、ぎりぎり",
                     main2="流すことも、止めることもできる",
                     sub="この「どっちつかず」が、次回からの全部の土台になる")
        SC.caption(ax, t)
        return []

    if k == 1:
        # 原子1個。手を4本、順に伸ばす
        cx, cy, r = 80.0, 54.0, 5.0
        atom(cx, cy, r, al, "Si")
        for j, ang in enumerate([45, 135, 225, 315]):
            b = C.ease((SC.local(t) - 1.0 - j * 0.9) / 0.7)
            if b <= 0:
                continue
            a = np.radians(ang)
            x1 = cx + (r + 1 + 12 * b) * np.cos(a)
            y1 = cy + (r + 1 + 12 * b) * np.sin(a)
            bond(cx + r * np.cos(a), cy + r * np.sin(a), x1, y1, al * b,
                 pair=False, lw=2.2)
            ax.scatter([x1], [y1], s=95, c=C.EL, zorder=7, linewidths=0,
                       alpha=al * b)
        ax.text(80, 24, "いちばん外に、電子が4個", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "この4本の手を、どう使うかで性質が決まる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 2:
        # 格子に組む。手が全部ふさがり、動ける電子が0になる
        b = C.ease(SC.local(t) / 2.5)
        lattice(80, 54, 5, 3, 13.0, 10.0, al, stub=True, lab="Si", r=3.2)
        ax.text(80, 24, "動ける電子  =  0 個", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al * b)
        ax.text(80, 15, "手はすべて相手と組んでいる。純粋なシリコンは流れない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al * b)
        SC.caption(ax, t)
        return []

    live = (k == 4)
    for m in range(3):
        panel(m, i, al, live)

    if k == 3:
        ax.text(80, 24, "違いは「余った手」があるかどうか", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "青い点が、動ける電子", ha="center", va="center",
                fontsize=15, color=C.MUTED, fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "同じ電圧。流れる量は桁違いに違う", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "左から右へ、電子が押される", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep05_silicon.mp4")
