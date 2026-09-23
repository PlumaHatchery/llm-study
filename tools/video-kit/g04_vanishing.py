"""G検定③ 勾配消失 ── 1より小さい数を、何度も掛けるから。

  逆伝播で勾配が層をさかのぼるたび、各層の微分が掛け算される。
  シグモイド(最大0.25)だと指数的に痩せ、ReLU(1)だと痩せない。
  最後にスキップ接続で「足し算の迂回路」を通す。
  ノート「③ ディープラーニング」の「第一の壁：勾配が消える」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 17, 32, 47, 61, 71],
    caps=[
        "",                                            # 0 タイトル
        "学習の信号は、出口から入口へさかのぼる",        # 1
        "シグモイドの微分は、最大でも 0.25",            # 2
        "ReLU なら微分は 1。掛けても痩せない",          # 3
        "スキップ接続は、勾配の迂回路",                 # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

NL = 6                               # 層の数
LX = [24.0 + j * 22.4 for j in range(NL)]
LY, LW, LH = 60.0, 15.0, 15.0
BAR_Y = 34.0                         # 勾配の大きさの棒
D_SIG, D_RELU = 0.25, 1.0


def grads_skip(upto):
    """迂回路がある場合。指数的には痩せず、ゆるやかに減るだけ"""
    g = [0.9 ** (NL - 1 - j) for j in range(NL)]
    return [v if (NL - 1 - j) <= upto else None for j, v in enumerate(g)]


def grads(d, upto):
    """出口(右端)から入口(左端)へ、順に d を掛けていく"""
    g = [1.0]
    for _ in range(NL - 1):
        g.append(g[-1] * d)
    g = g[::-1]                      # 左端が入口
    return [v if (NL - 1 - j) <= upto else None for j, v in enumerate(g)]


def layers(al=1.0, skip=False):
    for j, x in enumerate(LX):
        C.rrect(ax, x - LW / 2, LY - LH / 2, LW, LH, C.FILL, C.EDGE, r=1.2,
                lw=1.2, al=al, z=4)
        ax.text(x, LY, "層%d" % (j + 1), ha="center", va="center",
                fontsize=12, color=C.MUTED, fontproperties=C.FPB, alpha=al,
                zorder=5)
        if j < NL - 1:
            ax.annotate("", xy=(LX[j + 1] - LW / 2 - 1, LY + 2.5),
                        xytext=(x + LW / 2 + 1, LY + 2.5),
                        arrowprops=dict(arrowstyle="-|>", color=C.GRAY,
                                        lw=1.2, alpha=al * 0.8), zorder=5)
    ax.text(LX[0] - LW / 2 - 3.0, LY, "入口", ha="right", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text(LX[-1] + LW / 2 + 3.0, LY, "出口", ha="left", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=5)
    if skip:
        for j in (0, 2):
            x0, x1 = LX[j], LX[j + 2]
            ax.plot([x0, x0, x1, x1],
                    [LY + LH / 2, LY + LH / 2 + 7.0,
                     LY + LH / 2 + 7.0, LY + LH / 2],
                    color=C.OKC, lw=2.2, zorder=6, alpha=al)
        ax.text((LX[0] + LX[4]) / 2, LY + LH / 2 + 8.0,
                "スキップ接続（足し算の迂回路）", ha="center", va="bottom",
                fontsize=13, color=C.OKC, fontproperties=C.FPB, alpha=al,
                zorder=7)


def back_flow(vals, col, al=1.0):
    """各層に届いた勾配の大きさ。棒＋数値"""
    for j, (x, v) in enumerate(zip(LX, vals)):
        if v is None:
            continue
        h = max(0.6, 15.0 * v)   # 最大でも層のブロック(y=52.5)に届かない高さ
        C.rrect(ax, x - 4.0, BAR_Y, 8.0, h, col, "none", r=0.6,
                al=al * 0.9, z=4)
        ax.text(x, BAR_Y - 3.0, ("%.3f" % v).rstrip("0").rstrip("."),
                ha="center", va="top", fontsize=12,
                color=col if v > 0.05 else C.NGC, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.annotate("", xy=(x, LY - LH / 2 - 1.0),
                    xytext=(x, BAR_Y + h + 1.0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4,
                                    alpha=al * 0.55), zorder=4)
    ax.text(LX[0] - LW / 2 - 3.0, BAR_Y + 8.0, "勾配の\n大きさ", ha="right",
            va="center", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5, linespacing=1.4)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "勾配消失",
                     sub="G検定③ ── 1より小さい数を、何度も掛ける")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "深さが問題なのではない",
                     main2="掛け算を繰り返すことが問題だった",
                     sub="ReLU も スキップ接続も、掛け算を避ける工夫")
        SC.caption(ax, t)
        return []

    if k == 1:
        layers(al)
        n = int(np.clip((lo - 0.8) / 1.4, 0, NL - 1))
        for j in range(n):
            x0, x1 = LX[NL - 1 - j], LX[NL - 2 - j]
            ax.annotate("", xy=(x1 + LW / 2 + 1, LY - 3.0),
                        xytext=(x0 - LW / 2 - 1, LY - 3.0),
                        arrowprops=dict(arrowstyle="-|>", color=C.HOT,
                                        lw=2.4, alpha=al), zorder=7)
        ax.text(80, 24, "逆伝播 ── 誤差を、後ろから前へ配る", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "さかのぼるたびに、その層の微分が掛けられる",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 4:
        layers(al, skip=True)
        back_flow(grads_skip(NL), C.OKC, al)
        ax.text(80, 24, "入口まで 0.59 が届く（0.001 ではなく）",
                ha="center", va="center", fontsize=21, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "y = F(x) + x。足し算の迂回路を勾配がそのまま通る"
                        "── ResNet が100層を超えられた理由",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    d = D_SIG if k == 2 else D_RELU
    col = C.HOT if k == 2 else C.OKC
    upto = int(np.clip((lo - 0.8) / 1.5, 0, NL - 1))
    layers(al)
    back_flow(grads(d, upto), col, al)
    ax.text(80, 24,
            "0.25 を5回掛けると 0.001" if k == 2 else "1 を5回掛けても 1",
            ha="center", va="center", fontsize=23, color=col,
            fontproperties=C.FPB, alpha=al)
    ax.text(80, 15,
            "入口の層には、ほとんど何も届かない" if k == 2
            else "正の領域では微分がずっと 1。だから深くできる",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g04_vanishing.mp4")
