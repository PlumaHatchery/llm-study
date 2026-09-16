"""第29回 現代のCPUの中身 ── ベルトコンベアと、捨てる仕掛品。

  5工程が同時に別の命令を処理している。
  分岐予測が外れた瞬間に、途中まで作ったものを全部捨てる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 20, 38, 56, 66],
    caps=[
        "",                                            # 0 タイトル
        "1つずつ通すと、4工程が遊んでいる",              # 1
        "詰めて流せば、5つが同時に進む",                 # 2
        "予測が外れると、途中のものを全部捨てる",         # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

STAGES = ["取り出し", "解読", "実行", "メモリ", "書き戻し"]
SX = [22.0 + j * 29.0 for j in range(5)]
SW, SH, SY = 26.0, 15.0, 64.0
TICK = 1.0
FLUSH_AT = 9           # 第3場面で、この周期に予測はずれが分かる


def cycle(lo):
    return int(max(lo - 0.8, 0) / TICK)


def occupancy(k, n):
    """各段にいる命令番号（None は空）。第3場面は捨てたあとの穴も返す"""
    if k == 1:
        cur, st = n // 5, n % 5
        return [cur + 1 if j == st else None for j in range(5)], cur, False
    slots = [n - j + 1 if n - j >= 0 else None for j in range(5)]
    if k != 3:
        return slots, max(n - 4, 0), False
    if n < FLUSH_AT:
        return slots, max(n - 4, 0), False
    if n == FLUSH_AT:
        # 捨てる瞬間は、まだ中身を見せたまま印をつける
        return slots, max(n - 4, 0), True
    m = n - FLUSH_AT - 1
    after = [100 + m - j if m - j >= 0 else None for j in range(5)]
    return after, FLUSH_AT - 4, False


def belt(slots, flush, al=1.0):
    ax.plot([SX[0] - SW / 2 - 6, SX[-1] + SW / 2 + 6],
            [SY - SH / 2 - 4, SY - SH / 2 - 4], color=C.GRAY, lw=2.2,
            zorder=2, alpha=al)
    for j, (x, name) in enumerate(zip(SX, STAGES)):
        v = slots[j]
        busy = v is not None
        doomed = flush and j < 4 and busy
        C.rrect(ax, x - SW / 2, SY - SH / 2, SW, SH,
                C.FILL if busy else C.BG,
                C.HOT if doomed else (C.OKC if busy else C.EDGE), r=1.2,
                lw=1.7 if busy else 1.1, al=al, z=4)
        ax.text(x, SY + 3.2, name, ha="center", va="center", fontsize=12,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
        if busy:
            lab = ("分岐後 %d" % (v - 99)) if v >= 100 else "命令 %d" % v
            ax.text(x, SY - 3.6, lab, ha="center", va="center", fontsize=13,
                    color=C.HOT if doomed else C.OKC, fontproperties=C.FPB,
                    alpha=al, zorder=5)
        if j < 4:
            ax.annotate("", xy=(SX[j + 1] - SW / 2 - 1, SY),
                        xytext=(x + SW / 2 + 1, SY),
                        arrowprops=dict(arrowstyle="-|>", color=C.GRAY,
                                        lw=1.4, alpha=al), zorder=5)
    if flush:
        # 枠線だけ。塗ると中の命令が隠れる
        C.rrect(ax, SX[0] - SW / 2 - 3, SY - SH / 2 - 3,
                SX[3] + SW / 2 - SX[0] + SW / 2 + 6, SH + 6, "none", C.HOT,
                r=1.4, lw=2.2, al=al, z=6)
        ax.text((SX[0] + SX[3]) / 2, SY + SH / 2 + 8.0, "ここまで全部、捨てる",
                ha="center", va="center", fontsize=17, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=7)


def counter(done, n, al=1.0):
    ax.text(80.0, 42.0, "終わった命令  %d 個   /   %d 周期"
            % (max(done, 0), n + 1), ha="center", va="center", fontsize=17,
            color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "現代のCPUの中身",
                     sub="第29回 ── 流れ作業と、その代償")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "速さは、並べ方から出ている",
                     main2="そのかわり、読みが外れると丸ごと無駄になる",
                     sub="1命令が速くなったのではない。重ねているだけ")
        SC.caption(ax, t)
        return []

    n = cycle(lo)
    slots, done, flush = occupancy(k, n)
    belt(slots, flush, al)
    counter(done, n, al)

    if k == 1:
        ax.text(80, 24, "1命令に5周期。ずっと4つは空いている", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "工程を分けた意味が、これでは出ていない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "1周期に1個ずつ、出口から出てくる", ha="center",
                va="center", fontsize=22, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "1命令あたりの時間は同じ。数が捌けるようになった",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "先に進めていた分が、無駄になる", ha="center",
                va="center", fontsize=23,
                color=C.HOT if n >= FLUSH_AT else C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "だから分岐の予測を当てにいく。外れたときの損が大きい",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep29_pipeline.mp4")
