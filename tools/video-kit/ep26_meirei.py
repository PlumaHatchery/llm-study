"""第26回 命令という発明 ── 同じ数値を、読み方で変える。

  メモリの同じ数値を、データとして読む場合と命令として読む場合を並べる。
  プログラムカウンタが指す先が、次の行為になる（プログラム内蔵方式）。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 34, 51, 62],
    caps=[
        "",                                            # 0 タイトル
        "メモリに入っているのは、ただの数の列",           # 1
        "同じ数を「命令」として読むこともできる",         # 2
        "どちらで読むかは、指されているかどうかで決まる",   # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

# この動画かぎりの命令表（実在の命令セットではない）
MEM = [
    ("0", "00111100", 60, "A に 60 を入れる"),
    ("1", "00000101", 5, "A に 5 を足す"),
    ("2", "01101000", 104, "A をメモリ 8番地へ"),
    ("3", "00000010", 2, "A から 2 を引く"),
    ("4", "11110000", 240, "止まる"),
]
RX, RY0, RW, RH, GAP = 30.0, 72.0, 46.0, 8.0, 9.6
NOTE_X = 92.0


def row_y(j):
    return RY0 - j * GAP


def memory(pc, mode, al=1.0):
    ax.text(RX + RW / 2, 80.0, "メモリ", ha="center", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    for j, (addr, bits, num, mean) in enumerate(MEM):
        y = row_y(j)
        here = (j == pc)
        C.rrect(ax, RX, y - RH / 2, RW, RH, C.FILL if here else C.BG,
                C.HOT if here else C.EDGE, r=0.9, lw=1.7 if here else 1.1,
                al=al, z=4)
        ax.text(RX - 3.0, y, addr, ha="right", va="center", fontsize=13,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(RX + RW / 2, y, bits, ha="center", va="center", fontsize=15,
                color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
        if mode == "data":
            ax.text(NOTE_X, y, "= %d" % num, ha="left", va="center",
                    fontsize=15, color=C.EL, fontproperties=C.FPB, alpha=al,
                    zorder=5)
        elif mode == "code" or here:
            ax.text(NOTE_X, y, mean, ha="left", va="center", fontsize=14,
                    color=C.OKC if (here or mode == "code") else C.MUTED,
                    fontproperties=C.FPB if here else C.FP, alpha=al,
                    zorder=5)
        if here:
            ax.annotate("", xy=(RX - 8.5, y), xytext=(RX - 19.0, y),
                        arrowprops=dict(arrowstyle="-|>", color=C.HOT,
                                        lw=2.4, alpha=al), zorder=6)
            ax.text(RX - 20.5, y, "PC", ha="right", va="center", fontsize=15,
                    color=C.HOT, fontproperties=C.FPB, alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "命令という発明",
                     sub="第26回 ── プログラム内蔵方式")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "命令もデータも、同じメモリに置く",
                     main2="指された数が、そのまま次の行為になる",
                     sub="プログラムを書き換えられる機械は、ここから始まった")
        SC.caption(ax, t)
        return []

    if k == 1:
        memory(-1, "data", al)
        ax.text(80, 24, "どれも、ただの8桁の 0 と 1", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "数として読めば、60・5・104・2・240",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        memory(-1, "code", al)
        ax.text(80, 24, "同じ並びが、命令表を通すと動作になる",
                ha="center", va="center", fontsize=22, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "中身は1ビットも変わっていない。読み方が変わっただけ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        pc = min(int(max(lo - 1.0, 0) / 2.6), len(MEM) - 1)
        memory(pc, "none", al)
        ax.text(80, 24, "PC が指している行が、いまの命令", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "終わったら PC が1つ進む。それだけで順に実行される",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep26_meirei.mp4")
