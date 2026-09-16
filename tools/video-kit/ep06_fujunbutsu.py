"""第6回 不純物を混ぜる ── 穴が左へ歩く。

  完成した格子にリン(手5本)を差すと電子が1個余る。ホウ素(手3本)なら穴が空く。
  穴に隣の電子が落ちて、穴が左へ歩いていくのを繰り返し見せる。
  そこまで見せてから「穴をプラスの粒として扱える」を回収する。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 27, 39, 53, 64, 73],
    caps=[
        "",                                          # 0 タイトル
        "リンを1個だけ差し込む。手は5本ある",          # 1
        "1本あまった手の電子は、自由に動ける",         # 2
        "ホウ素なら手が3本。1か所、穴があく",          # 3
        "隣の電子が穴に落ちる。すると穴が左へ動く",     # 4
        "穴そのものを、プラスの粒として数える",        # 5
        "",                                          # 6 まとめ
    ],
)

fig, ax = C.new_axes()

NCOL, NROW = 7, 3
AX_ = 80 + (np.arange(NCOL) - (NCOL - 1) / 2) * 13.0     # 原子のx
AY_ = np.array([43.0, 54.0, 65.0])                       # 原子のy
SLOT = (AX_[:-1] + AX_[1:]) / 2                          # 中段の結合(6か所)
DOP = 3                                                  # 不純物を差す列
RAD = 3.2

H0 = 3            # 穴の初期位置(スロット番号)
JUMP_T0, JUMP_DT, JUMP_EVERY = 1.2, 0.9, 3.2


def hole_state(lo):
    """(穴の表示x, 飛んでいる電子のx or None, 穴のスロット番号)"""
    n = int(max(0.0, (lo - JUMP_T0)) // JUMP_EVERY)
    n = min(n, H0)                       # 左端まで来たら止める
    h = H0 - n
    tj = JUMP_T0 + n * JUMP_EVERY
    u = (lo - tj) / JUMP_DT
    if h > 0 and 0.0 <= u <= 1.0:
        e = C.ease(u)
        return (SLOT[h] + (SLOT[h - 1] - SLOT[h]) * e,
                SLOT[h - 1] + (SLOT[h] - SLOT[h - 1]) * e, h)
    return SLOT[h], None, h


def atom(x, y, lab, fc=C.FILL, ec=C.EDGE, tc=C.MUTED, al=1.0, r=RAD):
    ax.scatter([x], [y], s=430 * (r / 2.6) ** 2, c=fc, edgecolors=ec,
               linewidths=1.4, zorder=5, alpha=al)
    ax.text(x, y, lab, ha="center", va="center", fontsize=12, color=tc,
            fontproperties=C.FPB, alpha=al, zorder=6)


def bond(x0, y0, x1, y1, al=1.0, pair=True, color=C.GRAY, lw=1.6):
    dx, dy = x1 - x0, y1 - y0
    d = np.hypot(dx, dy)
    ox, oy = (-dy / d * 0.6, dx / d * 0.6) if pair else (0.0, 0.0)
    for s in ((1, -1) if pair else (0,)):
        ax.plot([x0 + s * ox, x1 + s * ox], [y0 + s * oy, y1 + s * oy],
                color=color, lw=lw, alpha=al, zorder=3)


def lattice(al=1.0, dop=None, watch=False):
    """格子。watch=True で中段の結合を1本線＋電子の点にする"""
    for j, y in enumerate(AY_):
        for i2, x in enumerate(AX_):
            if i2 < NCOL - 1:
                mid = (j == 1 and watch)
                bond(x + RAD, y, AX_[i2 + 1] - RAD, y, al,
                     pair=not mid, lw=1.6)
            if j < NROW - 1:
                bond(x, y + RAD, x, AY_[j + 1] - RAD, al)
    for j, y in enumerate(AY_):
        for i2, x in enumerate(AX_):
            if dop and i2 == DOP and j == 1:
                atom(x, y, dop[0], C.FILL, dop[1], dop[1], al)
            else:
                atom(x, y, "Si", al=al)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "不純物を混ぜる", sub="第6回 ── n型とp型")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "余った電子が運ぶのが n 型",
                     main2="空いた穴が運ぶのが p 型",
                     sub="この2つを向かい合わせると、次回のダイオードになる")
        SC.caption(ax, t)
        return []

    # ---- n型(リン) ------------------------------------------------
    if k in (1, 2):
        lattice(al, dop=("P", C.OKC))
        b = C.ease((lo - 1.5) / 1.2) if k == 1 else 1.0
        # 5本目の手の電子。k==2 では格子の中をうろつく
        if k == 1:
            ex, ey = AX_[DOP] + 7.0, AY_[1] + 5.5
        else:
            ph = lo * 0.9
            ex = 80 + 34 * np.sin(ph)
            ey = 54 + 7.5 * np.sin(ph * 1.7 + 1.1)
        # 格子の線の上を通っても埋もれないよう、背景色で抜いてから置く
        ax.scatter([ex], [ey], s=330, c=C.BG, zorder=7, linewidths=0,
                   alpha=al * b)
        ax.scatter([ex], [ey], s=130, c=C.EL, zorder=8, linewidths=0,
                   alpha=al * b)
        ax.text(AX_[DOP], 71.5, "リン（手が5本）", ha="center", va="bottom",
                fontsize=14, color=C.OKC, fontproperties=C.FPB, alpha=al,
                zorder=6)
        if k == 1:
            ax.text(80, 24, "手が1本あまる", ha="center", va="center",
                    fontsize=26, color=C.INK, fontproperties=C.FPB,
                    alpha=al * b)
            ax.text(80, 15, "相手のいない電子が、1個だけ残る", ha="center",
                    va="center", fontsize=15, color=C.MUTED,
                    fontproperties=C.FP, alpha=al * b)
        else:
            ax.text(80, 24, "n 型 ── 運ぶのは電子（−）", ha="center",
                    va="center", fontsize=24, color=C.INK,
                    fontproperties=C.FPB, alpha=al)
            ax.text(80, 15, "リンを増やすほど、動ける電子が増える",
                    ha="center", va="center", fontsize=15, color=C.MUTED,
                    fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    # ---- p型(ホウ素) ----------------------------------------------
    lattice(al, dop=("B", C.DEEP), watch=True)
    ax.text(AX_[DOP], 71.5, "ホウ素（手が3本）", ha="center", va="bottom",
            fontsize=14, color=C.DEEP, fontproperties=C.FPB, alpha=al,
            zorder=6)

    if k == 3:
        hx, fly, h = SLOT[H0], None, H0
    else:
        hx, fly, h = hole_state(lo)

    # 中段の結合にいる電子。穴のところだけ空ける
    filled = [s for s in range(len(SLOT)) if s != h]
    if fly is not None:
        filled = [s for s in filled if s != h - 1]
    if filled:
        ax.scatter(SLOT[filled], [AY_[1]] * len(filled), s=120, c=C.EL,
                   zorder=7, linewidths=0, alpha=al)
    if fly is not None:
        ax.scatter([fly], [AY_[1]], s=140, c=C.HOT, zorder=9, linewidths=0,
                   alpha=al)

    # 穴。第5場面でプラスの粒に置き換える
    if k == 5:
        ax.scatter([hx], [AY_[1]], s=150, c=C.DEEP, zorder=8, linewidths=0,
                   alpha=al)
        ax.text(hx, AY_[1] + 5.0, "＋", ha="center", va="center", fontsize=15,
                color=C.DEEP, fontproperties=C.FPB, alpha=al, zorder=9)
    else:
        ax.scatter([hx], [AY_[1]], s=150, facecolors="none",
                   edgecolors=C.DEEP, linewidths=1.8, zorder=8, alpha=al)
        ax.text(hx, AY_[1] - 5.2, "穴", ha="center", va="center", fontsize=14,
                color=C.DEEP, fontproperties=C.FPB, alpha=al, zorder=9)

    if k == 3:
        ax.text(80, 24, "手が1本たりない", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "電子が入るはずの席が、1つ空いたまま", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 4:
        ax.text(80, 24, "電子は右へ、穴は左へ", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "動いているのは電子。でも、目に見えるのは穴の移動",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "p 型 ── 運ぶのは穴（＋）", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "穴は、プラスの電荷をもった粒として計算していい",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep06_fujunbutsu.mp4")
