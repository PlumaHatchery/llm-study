"""第22回 フリップフロップ ── ここで「過去」が生まれる。

  NANDを2個、互いの出力を相手の入力に戻す。片方を一瞬叩くと状態が固定され、
  手を離しても保持される。それまでの回路になかったものが、ここで出てくる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 32, 46, 58, 68],
    caps=[
        "",                                            # 0 タイトル
        "2つの NAND が、互いの出力を見ている",           # 1
        "S を一瞬叩くと、1 のまま止まる",                # 2
        "R を一瞬叩くと、0 のまま止まる",                # 3
        "入力が同じでも、出力が違う",                    # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

GW, GH = 26.0, 14.0
G1Y, G2Y = 64.0, 40.0
PULSE = (2.2, 3.4)          # 叩いている区間(場面内の秒)


def pulses(t):
    """(S, R)。1が通常、0が叩いている状態(負論理)"""
    k, lo = SC.idx(t), SC.local(t)
    hit = PULSE[0] <= lo < PULSE[1]
    if k == 2 and hit:
        return 0, 1
    if k == 3 and hit:
        return 1, 0
    return 1, 1


N = SC.nframes
QS = np.ones(N + 1, dtype=int)
for _i in range(N):
    _s, _r = pulses(_i / C.FPS)
    q = QS[_i]
    if _s == 0:
        q = 1
    elif _r == 0:
        q = 0
    QS[_i + 1] = q


def col(v):
    return C.DEEP if v else C.EL


def latch(cx, q, s=1, r=1, al=1.0, small=False):
    """cx を中心に、交差結線した NAND 2個"""
    sc = 0.78 if small else 1.0
    w, h = GW * sc, GH * sc
    y1 = 56.0 + (G1Y - 56.0) * sc
    y2 = 56.0 + (G2Y - 56.0) * sc
    for y, lab in ((y1, "NAND"), (y2, "NAND")):
        C.rrect(ax, cx - w / 2, y - h / 2, w, h, C.FILL, C.EDGE, r=1.2,
                lw=1.3, al=al, z=5)
        ax.text(cx, y, lab, ha="center", va="center", fontsize=12 * sc + 1,
                color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=6)
    # 交差結線。入力は箱の外側、帰りの線は箱と箱のすきまを通す
    xr, xl = cx + w / 2, cx - w / 2
    d = 3.5 * sc
    ax.plot([xr, xr + 8 * sc, xr + 8 * sc, xl - 8 * sc, xl - 8 * sc, xl],
            [y1, y1, 54.0, 54.0, y2 + d, y2 + d],
            color=col(q), lw=1.6, zorder=4, alpha=al * 0.9)
    ax.plot([xr, xr + 13 * sc, xr + 13 * sc, xl - 13 * sc, xl - 13 * sc, xl],
            [y2, y2, 50.0, 50.0, y1 - d, y1 - d],
            color=col(1 - q), lw=1.6, zorder=4, alpha=al * 0.9)
    # 入力(外側から)
    for y, v, name in ((y1 + d, s, "S"), (y2 - d, r, "R")):
        ax.plot([xl - 22 * sc, xl], [y, y],
                color=C.HOT if v == 0 else C.GRAY, lw=2.4 if v == 0 else 1.4,
                zorder=4, alpha=al)
        ax.text(xl - 24 * sc, y, name, ha="right", va="center",
                fontsize=15 * sc, color=C.HOT if v == 0 else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=6)
    # 出力
    ax.text(xr + 20 * sc, y1, "Q = %d" % q, ha="left", va="center",
            fontsize=17 * sc, color=col(q), fontproperties=C.FPB, alpha=al,
            zorder=7, bbox=dict(facecolor=C.BG, edgecolor="none", pad=1.0,
                                alpha=al))
    ax.text(xr + 20 * sc, y2, "反転 = %d" % (1 - q), ha="left",
            va="center", fontsize=14 * sc, color=C.MUTED,
            fontproperties=C.FPB, alpha=al, zorder=7,
            bbox=dict(facecolor=C.BG, edgecolor="none", pad=1.0, alpha=al))


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "フリップフロップ",
                     sub="第22回 ── 回路が、覚える")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "いまの入力だけでは、出力が決まらない",
                     main2="それは、過去を持っているということ",
                     sub="ここから先の回路は、全部この上に建つ")
        SC.caption(ax, t)
        return []

    if k == 4:
        latch(44.0, 1, al=al, small=True)
        latch(112.0, 0, al=al, small=True)
        ax.text(44.0, 78.0, "さっき S を叩いた", ha="center", va="center",
                fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=6)
        ax.text(112.0, 78.0, "さっき R を叩いた", ha="center", va="center",
                fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=6)
        ax.text(80, 24, "いまの入力は、どちらも S=1 R=1", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "それでも Q が違う。違いは、履歴のほうにある",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    s, r = pulses(t)
    q = QS[i]
    latch(66.0, q, s, r, al)
    hit = (s == 0 or r == 0)

    if k == 1:
        ax.text(80, 24, "出口が、そのまま相手の入口になっている",
                ha="center", va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "輪になっているので、決まった状態から動かない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        name = "S" if k == 2 else "R"
        ax.text(80, 24, ("%s を叩いている" % name) if hit
                else "手を離しても、そのまま", ha="center", va="center",
                fontsize=25, color=C.HOT if hit else C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "叩くのは一瞬でいい。あとは輪が自分で支える",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep22_flipflop.mp4")
