"""第28回 メモリ階層 ── アクセス時間を、歩数に換算する。

  レジスタ/L1/L2/DRAM/SSD を距離と面積で並べ、1クロックを1歩として
  どれだけ遠いかを見せる。最後にヒットとミス。

  クロック数は「だいたいこの桁」という一般的な目安で、機種によって変わる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 20, 36, 53, 63],
    caps=[
        "",                                            # 0 タイトル
        "速いものほど小さく、近い",                      # 1
        "1クロックを1歩とすると、こう離れている",         # 2
        "L1 にあれば4歩。なければ200歩だ",               # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

# (名前, おおよそのクロック数, 容量の目安, ピラミッドの幅)
LEV = [("レジスタ", 1, "数百バイト", 22.0),
       ("L1キャッシュ", 4, "数十KB", 34.0),
       ("L2キャッシュ", 12, "数百KB", 48.0),
       ("DRAM（主記憶）", 200, "数GB", 70.0),
       ("SSD", 100000, "数百GB〜", 96.0)]
PYX = 58.0
TRK_Y = 56.0
TRK_X0, TRK_X1 = 20.0, 146.0


def tx(clk):
    return TRK_X0 + (TRK_X1 - TRK_X0) * np.log10(clk) / 5.0


def pyramid(al=1.0, show_steps=False):
    for j, (name, clk, cap, w) in enumerate(LEV):
        y = 74.0 - j * 10.0
        C.rrect(ax, PYX - w / 2, y - 4.2, w, 8.4, C.FILL, C.EDGE, r=1.0,
                lw=1.2, al=al, z=4)
        ax.text(PYX, y, name, ha="center", va="center", fontsize=13,
                color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(PYX + 52.0, y, cap, ha="left", va="center", fontsize=13,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
        if show_steps:
            ax.text(PYX - 54.0, y, "%s 歩" % format(clk, ","), ha="left",
                    va="center", fontsize=14, color=C.HOT,
                    fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(PYX + 52.0, 82.0, "容量の目安", ha="left", va="center",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    if show_steps:
        ax.text(PYX - 54.0, 82.0, "待ち時間", ha="left", va="center",
                fontsize=12, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=5)


def track(lo, al=1.0, target=None, walk=None):
    ax.plot([TRK_X0, TRK_X1], [TRK_Y, TRK_Y], color=C.GRAY, lw=2.0,
            zorder=3, alpha=al)
    for name, clk, cap, w in LEV:
        x = tx(clk)
        hot = (target is not None and name == target)
        ax.plot([x, x], [TRK_Y - 3.0, TRK_Y + 3.0],
                color=C.HOT if hot else C.GRAY, lw=2.4 if hot else 1.4,
                zorder=4, alpha=al)
        ax.text(x, TRK_Y + 5.0, name, ha="center", va="bottom", fontsize=12,
                color=C.HOT if hot else C.MUTED,
                fontproperties=C.FPB if hot else C.FP, alpha=al, zorder=5,
                rotation=32)
        ax.text(x, TRK_Y - 5.0, format(clk, ",") + " 歩", ha="center",
                va="top", fontsize=12,
                color=C.HOT if hot else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
    ax.text(TRK_X0 - 3.0, TRK_Y, "CPU", ha="right", va="center",
            fontsize=14, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    if walk is not None:
        ax.scatter([walk], [TRK_Y], s=200, c=C.EL, zorder=7, linewidths=0,
                   alpha=al)


def hitmiss(lo, al=1.0):
    """前半はヒット、後半はミス"""
    cyc = 9.0
    u = (lo % cyc) / cyc
    hit = (lo % (cyc * 2)) < cyc
    goal = tx(4) if hit else tx(200)
    if u < 0.45:
        x = TRK_X0 + (goal - TRK_X0) * (u / 0.45)
    elif u < 0.55:
        x = goal
    else:
        x = goal - (goal - TRK_X0) * ((u - 0.55) / 0.45)
    track(lo, al, target="L1キャッシュ" if hit else "DRAM（主記憶）", walk=x)
    ax.text(80.0, 82.0, "ヒット ── L1 にあった" if hit
            else "ミス ── L1 になくて、DRAM まで行く",
            ha="center", va="center", fontsize=18,
            color=C.OKC if hit else C.HOT, fontproperties=C.FPB, alpha=al,
            zorder=6)
    ax.text(80.0, 76.0, "往復 8歩" if hit else "往復 400歩", ha="center",
            va="center", fontsize=15, color=C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "メモリ階層",
                     sub="第28回 ── 待ち時間を、歩数で測る")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "速い記憶は、小さくしか作れない",
                     main2="だから、よく使うものを手元に置く",
                     sub="当たれば数歩、外れれば数百歩。差はそこに出る")
        SC.caption(ax, t)
        return []

    if k == 1:
        pyramid(al)
        ax.text(80, 24, "容量と速さは、両立しない", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "近くて速いものは高くつくので、少ししか置けない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        pyramid(al, show_steps=True)
        ax.text(80, 24, "SSD は、10万歩", ha="center", va="center",
                fontsize=26, color=C.HOT, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "レジスタの1歩に対して、これだけの開きがある",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        hitmiss(lo, al)
        ax.text(80, 24, "当たるかどうかで、50倍変わる", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "だから、次に使いそうなものを先に近くへ運んでおく",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep28_memory.mp4")
