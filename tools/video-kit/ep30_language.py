"""第30回 機械語から高級言語へ ── 上から下へ、一本で貫く。

  1行のコードが、アセンブラ → 機械語のビット列 → ゲートの開閉へ
  落ちていく縦の連鎖。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 17, 29, 41, 54, 64],
    caps=[
        "",                                            # 0 タイトル
        "人が書くのは、この1行",                        # 1
        "機械の言葉に置き換える（アセンブラ）",           # 2
        "さらに、ただの0と1に置き換える",                # 3
        "最後はゲートが開くか閉じるか、それだけ",         # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

LAYERS = [("高級言語", "a = a + 5;", C.INK, 20),
          ("アセンブラ", "ADD  A, 5", C.INK, 19),
          ("機械語", "0 0 0 0 0 1 0 1", C.EL, 19),
          ("ゲート", "", C.OKC, 0)]
LY = [80.0, 65.0, 50.0, 35.0]
LX, LW, LH = 44.0, 76.0, 11.0
GATE_N = 8


def layer(j, al=1.0, active=False):
    name, text, col, fs = LAYERS[j]
    y = LY[j]
    C.rrect(ax, LX, y - LH / 2, LW, LH, C.FILL if active else C.BG,
            C.OKC if active else C.EDGE, r=1.2, lw=1.7 if active else 1.1,
            al=al, z=4)
    ax.text(LX - 3.0, y, name, ha="right", va="center", fontsize=14,
            color=C.OKC if active else C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=5)
    if j < 3:
        ax.text(LX + LW / 2, y, text, ha="center", va="center", fontsize=fs,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)
    else:
        bits = [0, 0, 0, 0, 0, 1, 0, 1]
        for m in range(GATE_N):
            x = LX + 6.0 + m * (LW - 12.0) / (GATE_N - 1)
            on = bits[m] == 1
            ax.scatter([x], [y], s=150, c=C.OKC if on else C.BG,
                       edgecolors=C.OKC if on else C.EDGE, linewidths=1.4,
                       zorder=6, alpha=al)
        ax.text(LX + LW + 3.0, y, "開 / 閉", ha="left", va="center",
                fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)


def chain(upto, al=1.0):
    for j in range(upto + 1):
        layer(j, al, active=(j == upto))
    for j in range(upto):
        ax.annotate("", xy=(LX + LW / 2, LY[j + 1] + LH / 2 + 0.5),
                    xytext=(LX + LW / 2, LY[j] - LH / 2 - 0.5),
                    arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.0,
                                    alpha=al), zorder=6)
        ax.text(LX + LW / 2 + 3.0, (LY[j] + LY[j + 1]) / 2,
                ["翻訳", "組み立て", "電圧に"][j], ha="left", va="center",
                fontsize=12, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "機械語から高級言語へ",
                     sub="第30回 ── 1行が、ゲートに届くまで")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "上と下は、同じことを言っている",
                     main2="言い方が違うだけ",
                     sub="この縦の連鎖が切れていないから、書けば動く")
        SC.caption(ax, t)
        return []

    chain(k - 1, al)
    notes = ["読みやすさのために、人の側へ寄せてある",
             "レジスタと命令の名前で書く。1行が1命令",
             "命令表に当てはめると、この8桁になる",
             "1 のところが開き、0 のところが閉じる"]
    ax.text(80, 18, notes[k - 1], ha="center", va="center", fontsize=16,
            color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=5)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep30_language.mp4")
