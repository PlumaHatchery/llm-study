"""第8回 バイポーラトランジスタ ── 細い流れが太い流れを支配する。

  ベースに細い流れを少し通すと、コレクタ→エミッタに太い流れが出る。
  細い流れを2倍にすると太い流れも2倍。第1回のスイッチとは違い、
  「比例している」ことを強調する。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 15, 26, 38, 50, 61, 70],
    caps=[
        "",                                          # 0 タイトル
        "3つの端子。細い線が1本と、太い線が2本",       # 1
        "細い流れを止めると、太い流れも出ない",        # 2
        "細い流れを少し通すと、太い流れが出る",        # 3
        "細いほうを2倍にすると、太いほうも2倍",        # 4
        "比例している。だから、増幅に使える",          # 5
        "",                                          # 6 まとめ
    ],
)

fig, ax = C.new_axes()

# --- 本体。npn の3層をそのまま帯で描く -----------------------------
BX, BW = 62.0, 26.0
CXM = BX + BW / 2
BANDS = [(60.0, 8.0, "n"), (56.0, 4.0, "p"), (46.0, 10.0, "n")]
BODY_TOP, BODY_BOT = 68.0, 46.0
CY_TOP, CY_BOT = 76.0, 33.0
BASE_X, BASE_Y = 26.0, 58.0

MAIN = [(CXM, CY_TOP), (CXM, CY_BOT)]        # コレクタ→エミッタの太い道
BASE = [(BASE_X, BASE_Y), (BX, BASE_Y)]      # ベースの細い道

BETA = 6.0
IC_MAX = 12.0                                 # ゲージの満目盛り


def ib_at(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 3:
        return 1.0 * C.ease(lo / 2.0)
    if k == 4:
        return 1.0 + 1.0 * C.ease(lo / 2.5)
    if k == 5:
        return 2.0
    return 0.0


N = SC.nframes
DB = np.zeros(N + 1)
DC = np.zeros(N + 1)
for _i in range(N):
    _ib = ib_at(_i / C.FPS)
    DB[_i + 1] = DB[_i] + 0.26 * _ib / C.FPS
    DC[_i + 1] = DC[_i] + 0.26 * _ib * BETA / 6.0 / C.FPS

NB, NC = 4, 9
BU = np.arange(NB) / NB
CU = np.arange(NC) / NC


def body(al=1.0):
    for y, h, lab in BANDS:
        C.rrect(ax, BX, y, BW, h, C.FILL, C.EDGE, r=0.9, lw=1.1, al=al, z=4)
        ax.text(BX + 4.5, y + h / 2, lab, ha="center", va="center",
                fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=5)


def wire(path, lw, al=1.0):
    p = np.array(path, dtype=float)
    ax.plot(p[:, 0], p[:, 1], color=C.GRAY, lw=lw, solid_capstyle="round",
            zorder=2, alpha=al)


def flow(path, u_off, drift, size, color, al=1.0, z=3):
    """z=3 にして本体(z=4)の裏に潜らせる。中に入って出ていくように見える"""
    if drift <= 0:
        return
    u = (u_off + drift) % 1.0
    pts = np.array([C.ppt(path, v) for v in u])
    ax.scatter(pts[:, 0], pts[:, 1], s=size, c=color, zorder=z,
               linewidths=0, alpha=al)


def gauge(y, frac, color, lab, al=1.0):
    """細いと太いを同じ物差しで並べる。でないと比が見えない"""
    x, w = 106.0, 38.0
    C.rrect(ax, x, y, w, 4.6, "#EFEDE5", "#D3D1C7", r=0.8, lw=0.8, al=al, z=3)
    if frac > 0.005:
        C.rrect(ax, x, y, max(2.2, w * min(frac, 1.0)), 4.6, color, "none",
                r=0.8, al=al * 0.9, z=4)
    ax.text(x - 2.5, y + 2.3, lab, ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "バイポーラトランジスタ",
                     sub="第8回 ── 細い流れが、太い流れを決める")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "小さな入力が、大きな出力を支配する",
                     main2="しかも、比例して",
                     sub="オンとオフだけではない。ここが次回の増幅につながる")
        SC.caption(ax, t)
        return []

    ib = ib_at(t)
    ic = ib * BETA

    wire(MAIN, 4.2, al)
    wire(BASE, 1.8, al)
    flow(MAIN, CU, DC[i], 120, C.EL, al)
    flow(BASE, BU, DB[i], 62, C.HOT, al, z=3)
    body(al)

    ax.text(CXM + 4.5, CY_TOP - 1.5, "コレクタ", ha="left", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    ax.text(CXM + 4.5, CY_BOT + 1.5, "エミッタ", ha="left", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    ax.text(BASE_X - 2.5, BASE_Y, "ベース", ha="right", va="center",
            fontsize=14, color=C.HOT, fontproperties=C.FPB, alpha=al,
            zorder=5)

    gauge(62.0, ib / IC_MAX, C.HOT, "細い", al)
    gauge(50.0, ic / IC_MAX, C.EL, "太い", al)
    ax.text(125.0, 70.5, "流れの量（同じ物差し）", ha="center", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)

    if k == 1:
        ax.text(80, 24, "細い線が、太い線の蛇口になる", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "薄い p の層に少し流すかどうかで、上下の流れが決まる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "ベース 0  →  コレクタ 0", ha="center", va="center",
                fontsize=26, color=C.NGC, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "太い線に電圧はかかっている。それでも流れない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "ベース 1  →  コレクタ 6", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "わずかな流れが、6倍の流れを呼び出す", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 4:
        ax.text(80, 24, "ベース 2  →  コレクタ 12", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "2倍にしたら、きっちり2倍になった", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "コレクタ電流  =  β × ベース電流", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "スイッチなら0か1だけ。これは間の値も出せる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep08_bipolar.mp4")
