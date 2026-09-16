"""第23回 レジスタ・カウンタ・シフト ── 並べ方だけで機能が変わる。

  フリップフロップを8個並べて8ビット保持。クロックごとに+1するカウンタ、
  1個ずつ横にずれるシフトレジスタ。部品はどれも同じ。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 33, 48, 60, 70],
    caps=[
        "",                                            # 0 タイトル
        "8個ならべると、8ビットを保持できる",            # 1
        "上の桁へつなぐと、クロックごとに +1",            # 2
        "横へつなぐと、1個ずつずれていく",               # 3
        "部品は同じ。つなぎ方だけが違う",                # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

NB = 8
CW, CH, CY = 12.5, 15.0, 54.0
CX = [18.0 + j * 17.6 for j in range(NB)]      # 左が上位ビット
CLK_Y = 36.0
TICK = 1.1                                      # クロック1発の秒数


def ticks(lo, delay=1.0):
    return max(0, int((lo - delay) / TICK))


def state(t):
    """(8ビットの並び, いま光っているセル)"""
    k, lo = SC.idx(t), SC.local(t)
    n = ticks(lo)
    if k == 1:
        v = [0, 1, 0, 0, 1, 1, 0, 1]
        return v, (min(n, NB) - 1 if n else -1)
    if k == 2:
        val = n % 256
        return [(val >> (NB - 1 - j)) & 1 for j in range(NB)], -1
    if k == 3:
        src = [1, 0, 1, 1, 0, 0, 1, 0]
        out = [0] * NB
        for j in range(NB):
            idx = j - n
            out[j] = src[idx] if 0 <= idx < NB else 0
        return out, (n if n < NB else -1)
    return [0, 1, 0, 0, 1, 1, 0, 1], -1


def cells(bits, lit, al=1.0, arrows=None):
    for j, (x, b) in enumerate(zip(CX, bits)):
        on = b == 1
        hot = (j == lit)
        C.rrect(ax, x - CW / 2, CY - CH / 2, CW, CH,
                C.FILL if on else C.BG,
                C.HOT if hot else (C.OKC if on else C.EDGE), r=1.0,
                lw=1.8 if hot else 1.3, al=al, z=4)
        ax.text(x, CY + 1.0, str(b), ha="center", va="center", fontsize=18,
                color=C.OKC if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.text(x, CY - CH / 2 + 2.6, "FF", ha="center", va="center",
                fontsize=9, color=C.MUTED, fontproperties=C.FP,
                alpha=al * 0.8, zorder=5)
        ax.plot([x, x], [CLK_Y + 4.5, CY - CH / 2], color=C.GRAY, lw=1.0,
                zorder=3, alpha=al * 0.7)
    if arrows:
        for j in range(NB - 1):
            x0, x1 = CX[j] + CW / 2, CX[j + 1] - CW / 2
            ax.annotate("", xy=(x1 - 1.0, CY), xytext=(x0 + 1.0, CY),
                        arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=1.8,
                                        alpha=al * 0.9), zorder=6)


def clockline(lo, al=1.0):
    xs = np.linspace(12.0, 150.0, 600)
    hi = ((xs - 148.0) / 13.0 + lo / TICK) % 1.0 < 0.5
    ax.plot(xs, CLK_Y - 3.0 + 6.0 * hi, color=C.EL, lw=2.2, zorder=5,
            alpha=al, drawstyle="steps-post", solid_capstyle="butt")
    ax.text(10.0, CLK_Y, "クロック", ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "レジスタ・カウンタ・シフト",
                     sub="第23回 ── 同じ部品を、どう並べるか")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "覚える・数える・ずらす",
                     main2="どれも、同じ1ビットの箱の並べ方",
                     sub="この3つが、第25回からのCPUの手足になる")
        SC.caption(ax, t)
        return []

    if k == 4:
        rows = [("レジスタ", "そのまま保つ", "つながない"),
                ("カウンタ", "クロックごとに +1", "上の桁へ渡す"),
                ("シフトレジスタ", "1個ずつずれる", "隣へ渡す")]
        for j, (name, what, how) in enumerate(rows):
            y = 68.0 - j * 12.0
            C.rrect(ax, 22.0, y - 5.0, 116.0, 10.0, C.BG, C.EDGE, r=1.0,
                    lw=1.1, al=al, z=3)
            ax.text(28.0, y, name, ha="left", va="center", fontsize=15,
                    color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
            ax.text(76.0, y, what, ha="left", va="center", fontsize=14,
                    color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
            ax.text(132.0, y, how, ha="right", va="center", fontsize=13,
                    color=C.OKC, fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(80, 24, "違うのは、出口をどこへ返すかだけ", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "回路を作り替えるのではなく、配線を変えている",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    bits, lit = state(t)
    cells(bits, lit, al, arrows=(k == 3))
    clockline(lo, al)
    ax.text(80.0, 74.0, "フリップフロップ 8個", ha="center", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    val = int("".join(str(b) for b in bits), 2)

    if k == 1:
        ax.text(80, 24, "8個で 1バイト", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "書き込んだあとは、クロックが来ても変わらない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "いま  %d" % val, ha="center", va="center",
                fontsize=27, color=C.OKC, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "下の桁が1から0に戻るとき、上の桁がひっくり返る",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "中身が、まるごと右へ動く", ha="center", va="center",
                fontsize=25, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "左が上位桁。右へ1回ずらせば半分、左へずらせば2倍",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep23_register.mp4")
