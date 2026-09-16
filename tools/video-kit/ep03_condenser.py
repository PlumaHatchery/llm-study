"""第3回 コンデンサとコイル ── 主役は時定数。

  2枚の板に電荷が溜まるのを点の数で見せ、同時に充電カーブを右に描き足す。
  63%に達した時刻に目盛りを立てて「時定数」と呼ぶ。
  コイルは逆に、流れを保とうとして立ち上がりが遅れる。
  第12回(発振)・第15回(なまり)で二度使うので、曲線の形を焼き付ける。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 14, 24, 34, 44, 54, 64, 73],
    caps=[
        "",                                               # 0 タイトル
        "コンデンサは2枚の板。電荷が溜まっていく",           # 1
        "溜まり具合を時間で追うと、この曲線になる",          # 2
        "63%に届くまでの時間。これを時定数と呼ぶ",           # 3
        "抵抗を大きくすると、同じ形のまま横に伸びる",        # 4
        "コイルは逆に、いまの流れを保とうとする",            # 5
        "だから電流の立ち上がりが遅れる",                   # 6
        "",                                               # 7 まとめ
    ],
)

fig, ax = C.new_axes()

# --- 装置(左) 座標 -------------------------------------------------
LX, RX = 18.0, 59.0          # 回路の左辺・右辺
TY, BY = 64.0, 40.0          # 上の導線・下の導線
PLT_Y_HI, PLT_Y_LO = 56.0, 50.0   # 上の板・下の板
PLT_X0, PLT_X1 = 50.0, 68.0

# 導体の経路。点はこの上だけを走る。コンデンサは極板で切れているので
# 開いた折れ線にし、端まで行った点は反対側の板から出てくる(=電荷が渡る)
CAP_PATH = [(RX, PLT_Y_LO), (RX, BY), (LX, BY), (LX, TY), (RX, TY),
            (RX, PLT_Y_HI)]


def _coil_path():
    """右辺にコイルの巻きを差し込んだ閉ループ"""
    th = np.linspace(-np.pi / 2, np.pi / 2, 18)
    pts = [(RX, BY), (RX, 46.0)]
    for j in range(4):
        cy = 47.5 + j * 3.0
        pts += list(zip(RX + 2.6 * np.cos(th), cy + 1.5 * np.sin(th)))
    pts += [(RX, TY), (LX, TY), (LX, BY), (RX, BY)]
    return pts


COIL_PATH = _coil_path()
COIL_ARCS = COIL_PATH[2:2 + 4 * 18]

# --- グラフ(右) 座標 -----------------------------------------------
GX0, GX1, GY0, GY1 = 88.0, 149.0, 42.0, 68.0
TMAX = 5.0                   # 横軸は時定数の5倍まで


def gx(tn):
    return GX0 + (GX1 - GX0) * tn / TMAX


def gy(v):
    return GY0 + (GY1 - GY0) * v


# --- 充電の進み具合と電流。scene ごとに定義し、draw では読むだけ ----
def _phase(t):
    """(充電率 0..1, 電流 0..1, 曲線を描いた割合 0..1)"""
    k = SC.idx(t)
    lo = SC.local(t)
    if k == 1:
        u = min(lo / 6.0, 1.0) * TMAX
        return 1 - np.exp(-u), np.exp(-u), 0.0
    if k == 2:
        u = min(lo / 7.0, 1.0)
        return 1 - np.exp(-u * TMAX), np.exp(-u * TMAX), u
    if k in (3, 4):
        return 1.0, 0.0, 1.0
    if k == 5:
        u = min(lo / 6.0, 1.0) * TMAX
        return 0.0, 1 - np.exp(-u), 0.0
    if k == 6:
        u = min(lo / 5.0, 1.0)
        return 0.0, 1 - np.exp(-u * TMAX), u
    return 0.0, 0.0, 0.0


# 点の走行距離は累積なので、全フレーム分を先に積んでおく(状態を持たせない)
DRIFT = np.zeros(SC.nframes + 1)
for _i in range(SC.nframes):
    DRIFT[_i + 1] = DRIFT[_i] + 0.9 * _phase(_i / C.FPS)[1] / C.FPS

NDOT = 9
DOT_U = np.arange(NDOT) / NDOT


def wires(path, al=1.0):
    """導線と、そこに乗る電池・抵抗"""
    p = np.array(path, dtype=float)
    ax.plot(p[:, 0], p[:, 1], color=C.GRAY, lw=2.4, solid_capstyle="round",
            solid_joinstyle="round", zorder=2, alpha=al)
    C.rrect(ax, 13.5, 45, 9, 14, C.FILL, C.EDGE, r=1.0, al=al, z=4)
    ax.text(LX, 52, "電池", ha="center", va="center", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(12.0, 57, "＋", ha="right", va="center", fontsize=14,
            color=C.DEEP, fontproperties=C.FPB, alpha=al, zorder=8)
    ax.text(12.0, 47, "−", ha="right", va="center", fontsize=16,
            color=C.EL, fontproperties=C.FPB, alpha=al, zorder=8)
    C.rrect(ax, 29.5, 61.2, 13, 5.6, C.FILL, C.EDGE, r=1.0, al=al, z=4)
    ax.text(36, 68.5, "抵抗 R", ha="center", va="bottom", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def dots(i, path, al=1.0):
    """導線を流れる点。速さ=電流"""
    u = (DOT_U + DRIFT[i]) % 1.0
    pts = np.array([C.ppt(path, v) for v in u])
    ax.scatter(pts[:, 0], pts[:, 1], s=95, c=C.EL, zorder=6,
               linewidths=0, alpha=al)


def capacitor(q, al=1.0):
    """2枚の板。溜まった電荷を点の数で出す"""
    for y in (PLT_Y_HI, PLT_Y_LO):
        ax.plot([PLT_X0, PLT_X1], [y, y], color=C.EDGE, lw=3.4,
                solid_capstyle="round", zorder=5, alpha=al)
    # 引き出し線が RX を通るので、電荷の列は中央を空けて左右に分ける
    slots = np.concatenate([np.linspace(PLT_X0 + 0.8, RX - 3.5, 4),
                            np.linspace(RX + 3.5, PLT_X1 - 0.8, 4)])
    n = int(round(q * 8))
    if n:
        xs = slots[:n]
        ax.scatter(xs, [PLT_Y_HI + 2.1] * n, s=90, c=C.DEEP, zorder=6,
                   linewidths=0, alpha=al)
        ax.scatter(xs, [PLT_Y_LO - 2.1] * n, s=90, c=C.EL, zorder=6,
                   linewidths=0, alpha=al)
    ax.text(RX, 36.0, "コンデンサ C", ha="center", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def coil(al=1.0):
    """巻きを濃く描き直して、導線と区別する"""
    p = np.array(COIL_ARCS, dtype=float)
    ax.plot(p[:, 0], p[:, 1], color=C.EDGE, lw=3.0, solid_capstyle="round",
            zorder=5, alpha=al)
    ax.text(RX, 36.0, "コイル L", ha="center", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def graph(ylab, drawn, tau=1.0, color=C.EL, al=1.0):
    """軸と立ち上がりカーブ。drawn は描き終えた割合"""
    ax.plot([GX0, GX1], [GY0, GY0], color=C.GRAY, lw=1.8, zorder=3, alpha=al)
    ax.plot([GX0, GX0], [GY0, GY1], color=C.GRAY, lw=1.8, zorder=3, alpha=al)
    ax.plot([GX0, GX1], [gy(1), gy(1)], color=C.GRAY, lw=1.0,
            ls=(0, (3, 3)), zorder=3, alpha=al * 0.9)
    ax.text(GX0 - 2.5, GY1, ylab, ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=4)
    ax.text(GX1, 38.5, "時間 →", ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=4)
    if drawn > 0:
        tn = np.linspace(0, TMAX * drawn, 160)
        ax.plot(gx(tn), gy(1 - np.exp(-tn / tau)), color=color, lw=3.0,
                solid_capstyle="round", zorder=6, alpha=al)


def tau_mark(tau=1.0, al=1.0, label="τ", color=C.HOT, rule=True):
    """63%の目盛り。rule=False なら横線を引かず縦の目盛りだけ足す"""
    v = 1 - np.exp(-1.0)
    if rule:
        ax.plot([GX0, gx(tau)], [gy(v), gy(v)], color=C.HOT, lw=1.4,
                ls=(0, (4, 3)), zorder=7, alpha=al)
        ax.text(GX0 - 2.5, gy(v), "63%", ha="right", va="center", fontsize=13,
                color=C.HOT, fontproperties=C.FPB, alpha=al, zorder=7)
    ax.plot([gx(tau), gx(tau)], [GY0, gy(v)], color=color, lw=1.4,
            ls=(0, (4, 3)), zorder=7, alpha=al)
    ax.text(gx(tau), 38.5, label, ha="center", va="center", fontsize=15,
            color=color, fontproperties=C.FPB, alpha=al, zorder=7)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)
    q, _cur, drawn = _phase(t)

    if k == 0:
        C.title_card(ax, SC, t, "コンデンサとコイル", sub="第3回 ── 時定数")
        SC.caption(ax, t)
        return []

    if k == 7:
        C.title_card(ax, SC, t, "溜まるのに、時間がかかる",
                     main2="その時間が τ（時定数）",
                     sub="第12回の発振、第15回のなまりで、また出てくる")
        SC.caption(ax, t)
        return []

    path = CAP_PATH if k <= 4 else COIL_PATH
    wires(path, al)
    dots(i, path, al)

    if k <= 4:
        capacitor(q, al)
    else:
        coil(al)

    if k == 1:
        ax.text(RX, 74, "＋と−が向かい合って溜まる", ha="center",
                va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(80, 24, "流れは、溜まるほど細くなる", ha="center",
                va="center", fontsize=20, color=C.INK,
                fontproperties=C.FPB, alpha=al)

    elif k == 2:
        graph("電圧", drawn, al=al)

    elif k == 3:
        graph("電圧", 1.0, al=al)
        tau_mark(1.0, al=al)
        ax.text(80, 24, "時定数 τ  =  R × C", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "抵抗が大きいほど、容量が大きいほど、遅い",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    elif k == 4:
        graph("電圧", 1.0, tau=1.0, color=C.EL, al=al)
        b = C.ease(SC.local(t) / 1.6)
        tn = np.linspace(0, TMAX, 160)
        ax.plot(gx(tn), gy(1 - np.exp(-tn / 2.0)), color=C.HOT, lw=3.0,
                solid_capstyle="round", zorder=6, alpha=al * b)
        # 63%の横線は1本。そこを横切る時刻が τ と 2τ に分かれる
        tau_mark(2.0, al=al * b, label="2τ", color=C.HOT)
        tau_mark(1.0, al=al, label="τ", color=C.EL, rule=False)
        ax.text(80, 24, "R を2倍にすると、τ も2倍", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "形は変わらない。時間軸が伸び縮みするだけ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    elif k == 5:
        ax.text(RX, 74, "流れが変わるのを嫌がる", ha="center",
                va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(80, 24, "つないだ瞬間は、まだ流れない", ha="center",
                va="center", fontsize=20, color=C.INK,
                fontproperties=C.FPB, alpha=al)

    else:
        graph("電流", drawn, color=C.OKC, al=al)
        if SC.local(t) > 5.2:
            tau_mark(1.0, al=al * C.ease((SC.local(t) - 5.2) / 0.8),
                     color=C.OKC)
        ax.text(80, 24, "時定数 τ  =  L ÷ R", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "コンデンサは電圧が遅れ、コイルは電流が遅れる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep03_condenser.mp4")
