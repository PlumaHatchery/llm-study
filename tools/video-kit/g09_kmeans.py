"""G検定② k-means ── 割り当てて、重心を動かす。それだけ。

  ①適当にk個の中心を置く ②各点を最寄りの中心に割り当てる
  ③中心をメンバーの重心へ動かす を繰り返す。
  最後に「kは人間が先に決める」「初期値に左右される」を見せる。
  ノート「② 機械学習の手法」の「教師なし：正解なしで構造を見つける」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 15, 30, 45, 59, 69],
    caps=[
        "",                                            # 0 タイトル
        "正解ラベルはない。あるのは点だけ",              # 1
        "最寄りに割り当てて、重心へ動かす",              # 2
        "動かなくなったら、そこで終わり",                # 3
        "k は人間が決める。初期値でも変わる",            # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

PX0, PX1, PY0, PY1 = 38.0, 122.0, 30.0, 76.0
_rng = np.random.default_rng(21)
CL = np.array([[0.24, 0.72], [0.70, 0.74], [0.50, 0.24]])
PTS = np.vstack([_rng.normal(c, 0.085, (12, 2)) for c in CL])
PTS = np.clip(PTS, 0.04, 0.96)
K = 3
INIT = np.array([[0.14, 0.22], [0.30, 0.34], [0.22, 0.46]])   # わざと偏った初期値
INIT_B = np.array([[0.80, 0.20], [0.86, 0.60], [0.15, 0.85]])
COLS = [C.EL, C.DEEP, C.OKC]
STEP_T = 1.5


def sx(u):
    return PX0 + (PX1 - PX0) * u


def sy(v):
    return PY0 + (PY1 - PY0) * v


def run(init, n):
    """n回ぶん回したあとの (中心, 割り当て)"""
    cen = init.copy()
    lab = np.zeros(len(PTS), int)
    for _ in range(n):
        d = ((PTS[:, None, :] - cen[None, :, :]) ** 2).sum(-1)
        lab = d.argmin(1)
        for j in range(K):
            if (lab == j).any():
                cen[j] = PTS[lab == j].mean(0)
    d = ((PTS[:, None, :] - cen[None, :, :]) ** 2).sum(-1)
    return cen, d.argmin(1)


def scatter(cen, lab, al=1.0, show_lab=True, links=False):
    C.rrect(ax, PX0 - 3, PY0 - 3, PX1 - PX0 + 6, PY1 - PY0 + 6, "none",
            C.EDGE, r=1.2, lw=1.1, al=al * 0.9, z=3)
    if links and cen is not None:
        for p, l in zip(PTS, lab):
            ax.plot([sx(p[0]), sx(cen[l][0])], [sy(p[1]), sy(cen[l][1])],
                    color=COLS[l], lw=0.8, zorder=4, alpha=al * 0.35)
    if show_lab and cen is not None:
        for j in range(K):
            m = lab == j
            ax.scatter(sx(PTS[m, 0]), sy(PTS[m, 1]), s=100, c=COLS[j],
                       zorder=6, linewidths=0, alpha=al)
    else:
        ax.scatter(sx(PTS[:, 0]), sy(PTS[:, 1]), s=100, c=C.MUTED,
                   zorder=6, linewidths=0, alpha=al * 0.8)
    if cen is not None:
        for j in range(K):
            ax.scatter(sx(cen[j, 0]), sy(cen[j, 1]), s=330, c=COLS[j],
                       marker="X", zorder=8, linewidths=0, alpha=al)
            ax.scatter(sx(cen[j, 0]), sy(cen[j, 1]), s=520,
                       facecolors="none", edgecolors=COLS[j], linewidths=1.6,
                       zorder=8, alpha=al * 0.6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "k-means",
                     sub="G検定② ── 割り当てて、重心へ動かす")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "やっているのは、2つの操作の繰り返しだけ",
                     main2="最寄りに割り当てる／重心へ動かす",
                     sub="k を決めるのも、初期値を選ぶのも、人間の仕事")
        SC.caption(ax, t)
        return []

    if k == 1:
        scatter(None, None, al, show_lab=False)
        ax.text(80, 22, "どこに、いくつの塊があるか", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "教師なし ── 正解が与えられないまま、構造を探す",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 4:
        # 同じ k で、初期値だけ変えた2つの結果
        for init, x_off, lab_t in ((INIT, -21.0, "初期値 A"),
                                   (INIT_B, 21.0, "初期値 B")):
            cen, lab = run(init, 12)
            for j in range(K):
                m = lab == j
                ax.scatter(sx(PTS[m, 0]) * 0.45 + 40 + x_off,
                           sy(PTS[m, 1]) * 0.72 + 14,
                           s=48, c=COLS[j], zorder=6, linewidths=0, alpha=al)
                ax.scatter(sx(cen[j, 0]) * 0.45 + 40 + x_off,
                           sy(cen[j, 1]) * 0.72 + 14, s=140, c=COLS[j],
                           marker="X", zorder=8, linewidths=0, alpha=al)
            ax.text(40 + x_off + sx(0.5) * 0.45, 76.0, lab_t, ha="center",
                    va="bottom", fontsize=14, color=C.MUTED,
                    fontproperties=C.FPB, alpha=al, zorder=6)
        ax.text(80, 22, "同じ k でも、出発点が違えば結果が違う", ha="center",
                va="center", fontsize=21, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "k も人間が先に決める。データが教えてはくれない",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    n = int(np.clip((lo - 0.8) / STEP_T, 0, 12))
    cen, lab = run(INIT, n)
    moved = n == 0 or not np.allclose(cen, run(INIT, max(n - 1, 0))[0],
                                      atol=1e-4)
    scatter(cen, lab, al, show_lab=n > 0, links=(k == 2))
    ax.text(PX0, PY1 + 5.0, "%d 回目" % n, ha="left", va="bottom",
            fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=6)
    if k == 3 and not moved:
        ax.text(PX1, PY1 + 5.0, "もう動かない（収束）", ha="right",
                va="bottom", fontsize=14, color=C.OKC,
                fontproperties=C.FPB, alpha=al, zorder=6)

    if k == 2:
        ax.text(80, 22, "① 最寄りの中心へ割り当てる  ② 中心を重心へ動かす",
                ha="center", va="center", fontsize=19, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "線は、いまどの中心に属しているかを示している",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 22, "割り当てが変わらなくなったら、そこで止まる",
                ha="center", va="center", fontsize=21, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "偏った初期値からでも、塊のところへ落ち着いた",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g09_kmeans.mp4")
