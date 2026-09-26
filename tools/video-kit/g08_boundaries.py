"""G検定② 線の引き方の思想くらべ ── 同じ点に、4通りの境界。

  ロジスティック回帰 / SVM / 決定木 / k-NN を、同じ点群に当てて並べる。
  境界の形そのものが、その手法の思想になっている。
  ノート「② 機械学習の手法」の「教師あり：線の引き方の思想くらべ」に対応。
"""
import numpy as np
from matplotlib.colors import ListedColormap
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 29, 42, 55, 68, 78],
    caps=[
        "",                                            # 0 タイトル
        "同じ点を、どう分けるか",                       # 1
        "ロジスティック回帰 ── まっすぐ1本",            # 2
        "SVM ── 最前線から、いちばん余裕をとる",         # 3
        "決定木 ── たて・よこの質問を繰り返す",          # 4
        "k-NN ── 線を引かず、近所に聞く",               # 5
        "",                                            # 6 まとめ
    ],
)

fig, ax = C.new_axes()

PX0, PX1, PY0, PY1 = 46.0, 114.0, 30.0, 76.0     # 散布図の枠
_rng = np.random.default_rng(12)
NA = 14
A = np.column_stack([_rng.normal(0.34, 0.12, NA), _rng.normal(0.62, 0.13, NA)])
B = np.column_stack([_rng.normal(0.68, 0.12, NA), _rng.normal(0.36, 0.13, NA)])
A = np.clip(A, 0.05, 0.95)
B = np.clip(B, 0.05, 0.95)
GRID = np.stack(np.meshgrid(np.linspace(0, 1, 120), np.linspace(0, 1, 120)),
                -1).reshape(-1, 2)


def sx(u):
    return PX0 + (PX1 - PX0) * u


def sy(v):
    return PY0 + (PY1 - PY0) * v


CMAP = ListedColormap([C.EL, C.DEEP])


def region(pred, al=1.0):
    """判定結果で背景を薄く塗る。点で敷き詰めると方眼紙になるので imshow"""
    lab = pred(GRID).reshape(120, 120)
    ax.imshow(lab, extent=[sx(0), sx(1), sy(0), sy(1)], origin="lower",
              cmap=CMAP, vmin=0, vmax=1, alpha=al * 0.16, zorder=2,
              aspect="auto", interpolation="nearest")


def points(al=1.0):
    ax.scatter(sx(A[:, 0]), sy(A[:, 1]), s=105, c=C.EL, zorder=7,
               linewidths=0, alpha=al)
    ax.scatter(sx(B[:, 0]), sy(B[:, 1]), s=105, c=C.DEEP, zorder=7,
               linewidths=0, alpha=al)
    C.rrect(ax, PX0 - 3, PY0 - 3, PX1 - PX0 + 6, PY1 - PY0 + 6, "none",
            C.EDGE, r=1.2, lw=1.1, al=al * 0.9, z=3)


# --- 4つの手法。どれも「点→クラス」を返すだけ ---------------------
W = np.array([1.0, -1.0])
B0 = 0.0


def p_logi(g):
    return ((g @ W + B0) > 0).astype(int)


SV_M = 0.075          # マージンの幅（この動画での見た目用）


def p_svm(g):
    return ((g @ W + B0) > 0).astype(int)


TH_X, TH_Y = 0.52, 0.5


def p_tree(g):
    out = np.zeros(len(g), dtype=int)
    right = g[:, 0] > TH_X
    out[right & (g[:, 1] < 0.62)] = 1
    out[~right & (g[:, 1] < TH_Y)] = 1
    return out


ALL = np.vstack([A, B])
LAB = np.r_[np.zeros(NA, int), np.ones(NA, int)]


def p_knn(g, k=5):
    d = ((g[:, None, :] - ALL[None, :, :]) ** 2).sum(-1)
    idx = np.argpartition(d, k, axis=1)[:, :k]
    return (LAB[idx].mean(1) > 0.5).astype(int)


def line_logi(al=1.0, col=C.INK, lw=2.6):
    xs = np.linspace(0.02, 0.98, 60)
    ys = xs - B0
    m = (ys >= 0) & (ys <= 1)
    ax.plot(sx(xs[m]), sy(ys[m]), color=col, lw=lw, zorder=6, alpha=al)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "線の引き方の思想くらべ",
                     sub="G検定② ── 同じ点に、4通りの境界")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "どれが正解、という話ではない",
                     main2="何を信じて引いたか、が違うだけ",
                     sub="直線を信じる／余裕を信じる／質問を重ねる／近所に聞く")
        SC.caption(ax, t)
        return []

    if k == 1:
        points(al)
        ax.text(80, 22, "青と赤を分ける線は、1通りではない", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "どこに引くかで、初見のデータの行き先が変わる",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    pred = {2: p_logi, 3: p_svm, 4: p_tree, 5: p_knn}[k]
    region(pred, al)
    points(al)

    if k == 2:
        line_logi(al)
    elif k == 3:
        line_logi(al)
        for s in (1, -1):
            xs = np.linspace(0.02, 0.98, 60)
            ys = xs + s * SV_M * 1.414
            m = (ys >= 0) & (ys <= 1)
            ax.plot(sx(xs[m]), sy(ys[m]), color=C.OKC, lw=1.6,
                    ls=(0, (4, 3)), zorder=6, alpha=al)
        d = (ALL @ W + B0) / np.sqrt(2)
        for cls, col in ((0, C.EL), (1, C.DEEP)):
            sel = LAB == cls
            j = np.argmin(np.abs(d[sel]))
            p = ALL[sel][j]
            ax.scatter(sx(p[0]), sy(p[1]), s=240, facecolors="none",
                       edgecolors=C.OKC, linewidths=2.2, zorder=8, alpha=al)
        ax.text(sx(0.5), sy(0.97), "マージン", ha="center", va="bottom",
                fontsize=13, color=C.OKC, fontproperties=C.FPB, alpha=al,
                zorder=8)
    elif k == 4:
        ax.plot([sx(TH_X), sx(TH_X)], [sy(0), sy(1)], color=C.INK, lw=2.4,
                zorder=6, alpha=al)
        ax.plot([sx(0), sx(TH_X)], [sy(TH_Y), sy(TH_Y)], color=C.INK,
                lw=2.4, zorder=6, alpha=al)
        ax.plot([sx(TH_X), sx(1)], [sy(0.62), sy(0.62)], color=C.INK,
                lw=2.4, zorder=6, alpha=al)

    notes = {
        2: ("世界は直線で説明できる、と信じる",
            "出力をシグモイドで0〜1に潰す。名前に反して分類の手法"),
        3: ("同じ分けるなら、いちばん余裕をとって引く",
            "緑の丸がサポートベクター。この2点だけで線の位置が決まる"),
        4: ("「この特徴はしきい値以上か？」を繰り返す",
            "境界は必ず、たてとよこ。人がそのまま読める"),
        5: ("線を引かない。聞かれてから近所のk個に多数決させる",
            "学習らしい学習をしない。境界はギザギザになる"),
    }
    main, sub = notes[k]
    ax.text(80, 22, main, ha="center", va="center", fontsize=21,
            color=C.OKC if k == 3 else C.INK, fontproperties=C.FPB, alpha=al)
    ax.text(80, 14, sub, ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g08_boundaries.mp4")
