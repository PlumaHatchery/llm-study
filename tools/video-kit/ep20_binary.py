"""第20回 2進数と負の数 ── 一周する時計。

  桁の重み 8/4/2/1 を皿に乗せる。次に補数を一周する時計で見せ、
  −1 が 1111 になる理由と、引き算が足し算で済む理由まで。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 32, 47, 62, 72],
    caps=[
        "",                                            # 0 タイトル
        "桁ごとに重みがある。8・4・2・1",                # 1
        "4桁で 0 から 15 まで数えられる",               # 2
        "15 の次は 0 に戻る。時計と同じ",                # 3
        "引き算のかわりに、戻る分だけ進める",             # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

WEIGHTS = [8, 4, 2, 1]
BIT_X = [24.0, 40.0, 56.0, 72.0]
BIT_Y, BW, BH = 62.0, 13.0, 12.0
CCX, CCY, CR = 116.0, 56.0, 19.0
NPOS = 16


def bits_of(v):
    return [(v >> (3 - j)) & 1 for j in range(4)]


def value_at(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 1:
        return [1, 2, 4, 8, 5, 11, 13][int(lo / 2.0) % 7]
    if k == 2:
        return int(lo / 0.8) % 16
    if k == 3:
        return int(lo / 0.55) % 16
    if k == 4:
        return (5 + min(int(max(lo - 1.5, 0) / 0.62), 13)) % 16
    return 0


def bit_boxes(v, al=1.0):
    bs = bits_of(v)
    for x, w, b in zip(BIT_X, WEIGHTS, bs):
        C.rrect(ax, x - BW / 2, BIT_Y - BH / 2, BW, BH,
                C.FILL if b else C.BG, C.OKC if b else C.EDGE, r=1.0,
                lw=1.5, al=al, z=4)
        ax.text(x, BIT_Y, str(b), ha="center", va="center", fontsize=19,
                color=C.OKC if b else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.text(x, BIT_Y - BH / 2 - 3.0, str(w), ha="center", va="top",
                fontsize=14, color=C.HOT if b else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(BIT_X[0] - BW / 2 - 4.0, BIT_Y + BH / 2 + 4.0, "重み",
            ha="left", va="bottom", fontsize=13, color=C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=5)
    terms = " + ".join(str(w) for w, b in zip(WEIGHTS, bs) if b) or "0"
    ax.text(48.0, 40.0, "%s  =  %d" % (terms, v), ha="center", va="center",
            fontsize=22, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)


def clock(v, al=1.0, mark_neg=False, start=None, steps=0):
    th = -np.pi / 2 - 2 * np.pi * np.arange(NPOS) / NPOS
    xs, ys = CCX + CR * np.cos(th), CCY + CR * np.sin(th)
    ax.plot(CCX + CR * np.cos(np.linspace(0, 2 * np.pi, 200)),
            CCY + CR * np.sin(np.linspace(0, 2 * np.pi, 200)),
            color=C.GRAY, lw=1.4, zorder=3, alpha=al * 0.8)
    for j in range(NPOS):
        neg = mark_neg and j >= 9
        ax.text(CCX + (CR + 5.0) * np.cos(th[j]),
                CCY + (CR + 5.0) * np.sin(th[j]), str(j), ha="center",
                va="center", fontsize=12,
                color=C.HOT if neg else C.MUTED, fontproperties=C.FP,
                alpha=al * (0.9 if j != v else 1.0), zorder=5)
        ax.scatter([xs[j]], [ys[j]], s=46, c=C.GRAY, zorder=4, linewidths=0,
                   alpha=al * 0.7)
    if start is not None and steps:
        seq = [(start + s) % NPOS for s in range(steps + 1)]
        ax.plot(xs[seq], ys[seq], color=C.OKC, lw=2.4, zorder=5, alpha=al)
        ax.scatter([xs[start]], [ys[start]], s=150, facecolors="none",
                   edgecolors=C.EL, linewidths=2.0, zorder=6, alpha=al)
    ax.scatter([xs[v]], [ys[v]], s=190, c=C.HOT, zorder=7, linewidths=0,
               alpha=al)
    ax.text(CCX, CCY, "%d" % v, ha="center", va="center", fontsize=22,
            color=C.INK, fontproperties=C.FPB, alpha=al, zorder=6)
    if mark_neg:
        ax.text(CCX, CCY + CR + 11.0, "9〜15 を「−7〜−1」と読み替える",
                ha="center", va="center", fontsize=13, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "2進数と負の数",
                     sub="第20回 ── 引き算を足し算にする")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "引き算の回路は、いらない",
                     main2="足し算だけで済ませる約束にした",
                     sub="この節約が、第21回の加算器ひとつで足りる理由になる")
        SC.caption(ax, t)
        return []

    v = value_at(t)
    bit_boxes(v, al)

    if k == 1:
        ax.text(80, 24, "立っている桁の重みを、足すだけ", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "10進数が 1・10・100 なのと、やっていることは同じ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        clock(v, al)
        ax.text(80, 24, "4桁で 16 通り", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "桁を1本増やすたびに、数えられる数は倍になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        clock(v, al, mark_neg=(lo > 5.0))
        ax.text(80, 24, "1111 の次は 0000  →  1111 は −1", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "1つ戻るのと、15 進むのは、同じ場所に着く",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        steps = min(int(max(lo - 1.5, 0) / 0.62), 13)
        clock(v, al, mark_neg=True, start=5, steps=steps)
        ax.text(80, 24, "5 − 3  =  5 + 13  =  2", ha="center", va="center",
                fontsize=26, color=C.OKC, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "13 は −3 の言い換え。あふれた桁は捨てる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep20_binary.mp4")
