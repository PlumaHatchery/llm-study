"""第13回 水晶振動子 ── 32,768 が 1秒になるまで。

  圧電は双方向。電圧をかけると変形し、変形させると電圧が出る。
  いろいろな周波数で揺すってみて、固有振動数だけが大きく振れる。
  32,768 = 2の15乗。15段で割ると 1Hz、つまり1秒。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 17, 31, 43, 56, 65],
    caps=[
        "",                                            # 0 タイトル
        "電圧で形が変わり、形を変えると電圧が出る",       # 1
        "いろいろな速さで揺すってみる",                  # 2
        "この石が得意な速さは、1秒に32,768回",           # 3
        "2で15回割ると、ちょうど1になる",                # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

QX, QY, QW, QH = 30.0, 48.0, 28.0, 14.0        # 水晶片
FX0, FX1, FY0, FY1 = 88.0, 150.0, 42.0, 68.0   # 共振カーブのパネル
Q_FACTOR = 26.0
F0 = 0.5                                        # パネル上での固有振動数の位置


def resp(f):
    """共振の応答。f は 0..1 に正規化した周波数"""
    f = max(f, 1e-3)
    return 1.0 / np.sqrt(1.0 + (Q_FACTOR * (f / F0 - F0 / f)) ** 2)


def sweep_f(lo):
    """左から右へ掃いてから、固有振動数へ戻す。場面の最後を山で終える"""
    if lo < 8.0:
        return 0.10 + 0.80 * (lo / 8.0)
    return 0.90 + (F0 - 0.90) * C.ease((lo - 8.5) / 2.0)


def crystal(amp, ph, al=1.0, elec=True, dx=0.0):
    """振幅 amp で縦横に伸び縮みする。dx で左右にずらす"""
    d = 0.14 * amp * np.sin(ph)
    w, h = QW * (1 + d), QH * (1 - d)
    cx = QX + QW / 2 + dx
    x, y = cx - w / 2, QY + QH / 2 - h / 2
    C.rrect(ax, x, y, w, h, C.FILL, C.EDGE, r=1.2, lw=1.4, al=al, z=5)
    ax.text(cx, QY + QH / 2, "水晶", ha="center", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=6)
    if elec:
        for xx, col in ((x - 2.0, C.EL), (x + w + 2.0, C.DEEP)):
            ax.plot([xx, xx], [y + 1, y + h - 1], color=col, lw=4,
                    solid_capstyle="round", zorder=4, alpha=al)
    return x, y, w, h


def piezo(lo, al=1.0):
    """双方向。前半は電圧→変形、後半は変形→電圧。この場面は画面中央で"""
    dx = 80.0 - (QX + QW / 2)
    cx = 80.0
    fwd = (lo % 8.0) < 4.0
    ph = 2 * np.pi * lo * 1.1
    x, y, w, h = crystal(1.0, ph, al, dx=dx)
    if fwd:
        ax.annotate("", xy=(cx, 70.0), xytext=(cx, 78.0),
                    arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=2.6,
                                    alpha=al), zorder=8)
        ax.text(cx, 79.5, "電圧をかける", ha="center", va="bottom",
                fontsize=15, color=C.EL, fontproperties=C.FPB, alpha=al,
                zorder=8)
        ax.text(cx, 38.0, "→  形が変わる", ha="center", va="center",
                fontsize=16, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=6)
    else:
        for s, xx in ((1, x - 10.0), (-1, x + w + 10.0)):
            ax.annotate("", xy=(xx + s * 5.0, y + h / 2),
                        xytext=(xx, y + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.8,
                                        alpha=al), zorder=8)
        ax.text(cx, 79.5, "押して形を変える", ha="center",
                va="bottom", fontsize=15, color=C.HOT, fontproperties=C.FPB,
                alpha=al, zorder=8)
        ax.text(cx, 38.0, "→  電圧が出る", ha="center", va="center",
                fontsize=16, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=6)


def curve_panel(fnow, al=1.0):
    fs = np.linspace(0.05, 0.95, 320)
    ax.plot([FX0, FX1], [FY0, FY0], color=C.GRAY, lw=1.6, zorder=3, alpha=al)
    ax.plot([FX0, FX0], [FY0, FY1], color=C.GRAY, lw=1.6, zorder=3, alpha=al)
    xs = FX0 + (FX1 - FX0) * (fs - 0.05) / 0.90
    ax.plot(xs, FY0 + (FY1 - FY0) * np.array([resp(f) for f in fs]),
            color=C.GRAY, lw=2.0, zorder=4, alpha=al * 0.8)
    xn = FX0 + (FX1 - FX0) * (fnow - 0.05) / 0.90
    a = resp(fnow)
    ax.plot([xn, xn], [FY0, FY0 + (FY1 - FY0) * a], color=C.HOT, lw=1.4,
            ls=(0, (4, 3)), zorder=6, alpha=al)
    ax.scatter([xn], [FY0 + (FY1 - FY0) * a], s=140, c=C.HOT, zorder=7,
               linewidths=0, alpha=al)
    ax.text(FX0 - 2.5, FY1, "揺れの大きさ", ha="right", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    ax.text(FX1, 38.5, "揺する速さ →", ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    xr = FX0 + (FX1 - FX0) * (F0 - 0.05) / 0.90
    ax.text(xr, 72.0, "固有振動数", ha="center", va="center", fontsize=13,
            color=C.OKC, fontproperties=C.FPB, alpha=al, zorder=6)


def divider(lo, al=1.0):
    """15段の分周。段ごとに半分になる"""
    x0, x1, y = 22.0, 138.0, 56.0
    n = 15
    step = (x1 - x0) / n
    lit = int(np.clip((lo - 1.0) / 0.55, 0, n))
    for j in range(n):
        C.rrect(ax, x0 + j * step + 0.6, y, step - 1.2, 8.0,
                C.FILL if j < lit else C.BG,
                C.OKC if j < lit else C.EDGE, r=0.7, lw=1.1, al=al, z=4)
    ax.text((x0 + x1) / 2, y + 12.0, "÷2 を 15回", ha="center", va="center",
            fontsize=15, color=C.OKC, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text(x0 - 2.5, y + 4.0, "32,768 Hz", ha="right", va="center",
            fontsize=15, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text(x1 + 2.5, y + 4.0, "1 Hz", ha="left", va="center", fontsize=15,
            color=C.OKC if lit >= n else C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=5)
    if lit:
        v = 32768 >> lit
        ax.text(x0 + lit * step, y - 5.0, "%d Hz" % v, ha="center",
                va="top", fontsize=14, color=C.HOT, fontproperties=C.FPB,
                alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "水晶振動子", sub="第13回 ── 32,768 の意味")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "石の得意な速さを、2で15回割る",
                     main2="それが、腕時計の1秒",
                     sub="正確なのは回路ではなく、石の固有振動数のほう")
        SC.caption(ax, t)
        return []

    if k == 1:
        piezo(lo, al)
    elif k == 2:
        f = sweep_f(lo)
        crystal(resp(f), 2 * np.pi * lo * 3.2, al)
        curve_panel(f, al)
    elif k == 3:
        crystal(1.0, 2 * np.pi * lo * 3.2, al)
        curve_panel(F0, al)
    else:
        divider(lo, al)

    if k == 1:
        ax.text(80, 24, "圧電  ──  行きも帰りもある", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "だから、揺らす側にも、読み取る側にも使える",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "ある速さのときだけ、大きく振れる", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "外れた速さでは、ほとんど動かない", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "32,768  =  2 の 15乗", ha="center", va="center",
                fontsize=27, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "半端な数に見えて、2で割りきれる数として選ばれている",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "1秒に1回。これが時計の針を動かす", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "1段は、第22回のフリップフロップ1個でできる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep13_suisho.mp4")
