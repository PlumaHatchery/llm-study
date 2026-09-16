"""第21回 加算器 ── 論理が計算になる回。第4部の山場。

  1桁の足し算の真理値表を書き、和が XOR、繰り上がりが AND と一致することに
  気付かせる。半加算器 → 全加算器 → 4桁に連結。
  繰り上がりが左へ伝播していくのをコマ送りで見せる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 33, 46, 64, 74],
    caps=[
        "",                                            # 0 タイトル
        "1桁の足し算を、全部書き出してみる",             # 1
        "和は XOR、繰り上がりは AND と同じ形",            # 2
        "桁上げを受け取る口を足すと、全加算器",           # 3
        "4桁つなぐ。繰り上がりが左へ伝わっていく",         # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

ROWS = [(0, 0), (0, 1), (1, 0), (1, 1)]
NB = 4
BX = [132.0 - j * 32.0 for j in range(NB)]      # bit0 が右端
BW, BH, BY = 26.0, 16.0, 44.0
A_VAL, B_VAL = 0b0111, 0b0001
STEP_T = 1.7


def col(v):
    return C.DEEP if v else C.EL


def table(al=1.0, show_logic=False):
    x = [46.0, 62.0, 86.0, 112.0]
    heads = ["A", "B", "和", "繰り上がり"]
    if show_logic:
        heads = ["A", "B", "和 = XOR", "繰り上がり = AND"]
    for xx, h in zip(x, heads):
        ax.text(xx, 72.0, h, ha="center", va="center", fontsize=14,
                color=C.OKC if (show_logic and xx > 70) else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=5)
    ax.plot([36.0, 130.0], [68.0, 68.0], color=C.GRAY, lw=1.2, zorder=3,
            alpha=al)
    for j, (a, b) in enumerate(ROWS):
        y = 62.0 - j * 7.5
        s, c = a ^ b, a & b
        for xx, v in zip(x, (a, b, s, c)):
            ax.text(xx, y, str(v), ha="center", va="center", fontsize=17,
                    color=col(v) if xx > 70 else C.INK,
                    fontproperties=C.FPB, alpha=al, zorder=5)
    if show_logic:
        for xx in (86.0, 112.0):
            C.rrect(ax, xx - 11, 27.5, 22, 48, C.BG, C.OKC, r=1.2, lw=1.5,
                    al=al * 0.9, z=2)


def adder_box(cx, lab, al=1.0, lit=False, done=False):
    ec = C.OKC if lit else (C.EDGE if not done else C.GRAY)
    C.rrect(ax, cx - BW / 2, BY, BW, BH, C.FILL if lit else C.BG, ec,
            r=1.3, lw=1.8 if lit else 1.3, al=al, z=4)
    ax.text(cx, BY + BH / 2, lab, ha="center", va="center", fontsize=13,
            color=C.OKC if lit else C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=5)


def ripple(lo, al=1.0):
    step = int(max(lo - 1.0, 0.0) / STEP_T)
    carry = 0
    sums = []
    carries = [0]
    for j in range(NB):
        a = (A_VAL >> j) & 1
        b = (B_VAL >> j) & 1
        tot = a + b + carry
        sums.append(tot & 1)
        carry = tot >> 1
        carries.append(carry)
    for j in range(NB):
        cx = BX[j]
        known = j < step
        lit = (j == step)
        adder_box(cx, "全加算器", al, lit, known)
        a = (A_VAL >> j) & 1
        b = (B_VAL >> j) & 1
        ax.text(cx - 6.0, 70.0, str(a), ha="center", va="center",
                fontsize=16, color=col(a), fontproperties=C.FPB, alpha=al,
                zorder=6)
        ax.text(cx + 6.0, 70.0, str(b), ha="center", va="center",
                fontsize=16, color=col(b), fontproperties=C.FPB, alpha=al,
                zorder=6)
        for dx in (-6.0, 6.0):
            ax.plot([cx + dx, cx + dx], [BY + BH, 67.0], color=C.GRAY,
                    lw=1.2, zorder=3, alpha=al * 0.8)
        if known or lit:
            ax.plot([cx, cx], [38.5, BY], color=C.GRAY, lw=1.2, zorder=3,
                    alpha=al * 0.8)
            ax.text(cx, 36.0, str(sums[j]), ha="center", va="center",
                    fontsize=18, color=col(sums[j]) if known else C.HOT,
                    fontproperties=C.FPB, alpha=al, zorder=6)
        # 左へ渡る繰り上がり
        if j < NB - 1 and known:
            x0, x1 = cx - BW / 2, BX[j + 1] + BW / 2
            live = carries[j + 1] == 1
            ax.plot([x0, x1], [BY + BH / 2, BY + BH / 2],
                    color=C.HOT if live else C.GRAY, lw=2.4 if live else 1.4,
                    zorder=3, alpha=al)
            ax.text((x0 + x1) / 2, BY + BH / 2 + 2.2, str(carries[j + 1]),
                    ha="center", va="bottom", fontsize=14,
                    color=C.HOT if live else C.MUTED, fontproperties=C.FPB,
                    alpha=al, zorder=6,
                    bbox=dict(facecolor=C.BG, edgecolor="none", pad=0.6,
                              alpha=al * 0.9))
    ax.text(18.0, 70.0, "A ＋ B", ha="right", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(18.0, 36.0, "和", ha="right", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    if step >= NB:
        ax.text(80.0, 26.0, "0111 ＋ 0001  =  1000      （7 ＋ 1 = 8）",
                ha="center", va="center", fontsize=22, color=C.OKC,
                fontproperties=C.FPB, alpha=al, zorder=6)
    else:
        ax.text(80.0, 26.0, "%d桁目を計算中" % (step + 1), ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al, zorder=6)


def half_full(lo, al=1.0):
    b = C.ease((lo - 3.0) / 1.2)
    C.rrect(ax, 22.0, 46.0, 44.0, 22.0, C.BG, C.EDGE, r=1.4, lw=1.4, al=al,
            z=4)
    ax.text(44.0, 62.0, "半加算器", ha="center", va="center", fontsize=15,
            color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(44.0, 54.0, "A・B → 和・桁上げ", ha="center", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    ax.annotate("", xy=(84.0, 57.0), xytext=(70.0, 57.0),
                arrowprops=dict(arrowstyle="-|>", color=C.OKC, lw=2.4,
                                alpha=al * b), zorder=6)
    C.rrect(ax, 88.0, 42.0, 50.0, 30.0, C.FILL, C.OKC, r=1.4, lw=1.6,
            al=al * b, z=4)
    ax.text(113.0, 66.0, "全加算器", ha="center", va="center", fontsize=15,
            color=C.OKC, fontproperties=C.FPB, alpha=al * b, zorder=5)
    ax.text(113.0, 57.0, "A・B・下からの桁上げ", ha="center", va="center",
            fontsize=13, color=C.INK, fontproperties=C.FP, alpha=al * b,
            zorder=5)
    ax.text(113.0, 48.0, "→ 和・上への桁上げ", ha="center", va="center",
            fontsize=13, color=C.INK, fontproperties=C.FP, alpha=al * b,
            zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "加算器",
                     sub="第21回 ── 論理が、計算になる")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "真理値表を並べただけのものが、足し算になった",
                     main2="論理回路は、ここで計算機になる",
                     sub="引き算は第20回の約束で、同じ回路が使い回せる")
        SC.caption(ax, t)
        return []

    if k in (1, 2):
        table(al, show_logic=(k == 2))
        if k == 1:
            ax.text(80, 22, "1 ＋ 1 だけ、桁が増える", ha="center",
                    va="center", fontsize=25, color=C.INK,
                    fontproperties=C.FPB, alpha=al)
            ax.text(80, 14, "答えを「和」と「繰り上がり」の2列に分けて書く",
                    ha="center", va="center", fontsize=15, color=C.MUTED,
                    fontproperties=C.FP, alpha=al)
        else:
            ax.text(80, 22, "足し算は、XOR と AND でできている", ha="center",
                    va="center", fontsize=24, color=C.OKC,
                    fontproperties=C.FPB, alpha=al)
            ax.text(80, 14, "第17回・第18回で作った部品が、そのまま使える",
                    ha="center", va="center", fontsize=15, color=C.MUTED,
                    fontproperties=C.FP, alpha=al)
    elif k == 3:
        half_full(lo, al)
        ax.text(80, 24, "下の桁からの1を、受け取れるようにする", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "これで、何桁でも横に並べられる", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ripple(lo, al)
        ax.text(80, 15, "下の桁が決まらないと、上の桁は決められない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep21_adder.mp4")
