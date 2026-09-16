"""第7回 pn接合とダイオード ── 誰もいない帯。

  n側とp側を近づけて接触。境界で電子が穴に落ちて埋まり、空乏層ができる。
  順方向で帯が薄くなって流れ、逆方向で厚くなって止まる。
  最後に正弦波を入れて、片側だけが残るところまで。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 15, 27, 39, 51, 64, 73],
    caps=[
        "",                                            # 0 タイトル
        "n型とp型。別々なら、それぞれ運び手をもっている",  # 1
        "くっつけると、境目で電子が穴に落ちて埋まる",      # 2
        "順方向。帯が薄くなって、流れ出す",               # 3
        "逆方向。帯が厚くなって、止まる",                 # 4
        "交流を入れると、片側だけが残る",                 # 5
        "",                                            # 6 まとめ
    ],
)

fig, ax = C.new_axes()

BX0, BX1, JX = 30.0, 130.0, 80.0
BY0, BY1 = 44.0, 66.0
NE = 13

_rng = np.random.default_rng(7)
EU = np.linspace(0.06, 0.94, NE) + _rng.uniform(-0.02, 0.02, NE)
EY = np.array([49.0, 55.5, 61.5])[_rng.integers(0, 3, NE)] \
    + _rng.uniform(-1.2, 1.2, NE)
HU = np.linspace(0.06, 0.94, NE) + _rng.uniform(-0.02, 0.02, NE)
HY = np.array([49.0, 55.5, 61.5])[_rng.integers(0, 3, NE)] \
    + _rng.uniform(-1.2, 1.2, NE)

# 順方向のときだけ流れる。距離は累積なので先に積む
N = SC.nframes
DRIFT = np.zeros(N + 1)
for _i in range(N):
    _k = SC.idx(_i / C.FPS)
    DRIFT[_i + 1] = DRIFT[_i] + (0.16 if _k == 3 else 0.0) / C.FPS


def gap(t):
    k = SC.idx(t)
    if k <= 1:
        return 4.0
    if k == 2:
        return 4.0 * (1 - C.ease(SC.local(t) / 1.5))
    return 0.0


def width(t):
    """空乏層の半分の幅"""
    k, lo = SC.idx(t), SC.local(t)
    if k <= 1:
        return 0.0
    if k == 2:
        return 6.0 * C.ease((lo - 2.0) / 2.5)
    if k == 3:
        return 6.0 + (2.0 - 6.0) * C.ease(lo / 2.0)
    if k == 4:
        return 2.0 + (9.0 - 2.0) * C.ease(lo / 2.0)
    return 6.0


def electrodes(sign, al=1.0):
    """sign: +1 で順方向(pに＋)、-1 で逆方向、0 でなし"""
    if sign == 0:
        return
    lc = C.DEEP if sign < 0 else C.EL
    rc = C.EL if sign < 0 else C.DEEP
    ax.plot([BX0 - 3, BX0 - 3], [BY0 + 1, BY1 - 1], color=lc, lw=4,
            solid_capstyle="round", zorder=5, alpha=al)
    ax.plot([BX1 + 3, BX1 + 3], [BY0 + 1, BY1 - 1], color=rc, lw=4,
            solid_capstyle="round", zorder=5, alpha=al)
    ax.text(BX0 - 6, 55, "−" if sign > 0 else "＋", ha="right", va="center",
            fontsize=17, color=lc, fontproperties=C.FPB, alpha=al, zorder=6)
    ax.text(BX1 + 6, 55, "＋" if sign > 0 else "−", ha="left", va="center",
            fontsize=17, color=rc, fontproperties=C.FPB, alpha=al, zorder=6)


def block(t, al=1.0):
    g = gap(t)
    C.rrect(ax, BX0 - g, BY0, JX - BX0, BY1 - BY0, C.FILL, C.EDGE, r=1.4,
            al=al, z=2)
    C.rrect(ax, JX + g, BY0, BX1 - JX, BY1 - BY0, C.FILL, C.EDGE, r=1.4,
            al=al, z=2)
    ax.text((BX0 + JX) / 2 - g, 70.5, "n型（電子）", ha="center", va="bottom",
            fontsize=14, color=C.EL, fontproperties=C.FPB, alpha=al, zorder=6)
    ax.text((JX + BX1) / 2 + g, 70.5, "p型（穴）", ha="center", va="bottom",
            fontsize=14, color=C.DEEP, fontproperties=C.FPB, alpha=al,
            zorder=6)
    return g


def depletion(w, al=1.0):
    if w < 0.4:
        return
    C.rrect(ax, JX - w, BY0 + 0.4, 2 * w, BY1 - BY0 - 0.8, C.BG, C.HOT,
            r=0.8, lw=1.4, al=al * 0.95, z=3)
    n = max(1, int(round(w / 2.2)))
    for y in (50.0, 60.0):
        for x in np.linspace(JX - w + 1.6, JX - 1.6, n):
            ax.text(x, y, "＋", ha="center", va="center", fontsize=11,
                    color=C.DEEP, fontproperties=C.FPB, alpha=al * 0.85,
                    zorder=4)
        for x in np.linspace(JX + 1.6, JX + w - 1.6, n):
            ax.text(x, y, "−", ha="center", va="center", fontsize=13,
                    color=C.EL, fontproperties=C.FPB, alpha=al * 0.85,
                    zorder=4)
    ax.plot([JX - w, JX - w], [BY0 - 1.5, BY0 - 3.5], color=C.HOT, lw=1.2,
            alpha=al, zorder=4)
    ax.plot([JX + w, JX + w], [BY0 - 1.5, BY0 - 3.5], color=C.HOT, lw=1.2,
            alpha=al, zorder=4)
    ax.text(JX, 38.0, "空乏層（誰もいない帯）", ha="center", va="center",
            fontsize=14, color=C.HOT, fontproperties=C.FPB, alpha=al,
            zorder=5)


def carriers(i, k, w, g, al=1.0):
    if k == 3:
        # 順方向。電子は右へ、穴は左へ、ブロック全体を流れる
        ex = BX0 + 3 + ((EU + DRIFT[i]) % 1.0) * (BX1 - BX0 - 6)
        hx = BX1 - 3 - ((HU + DRIFT[i]) % 1.0) * (BX1 - BX0 - 6)
        eshow = np.ones(NE, dtype=bool)
        hshow = np.ones(NE, dtype=bool)
    else:
        push = 0.0
        if k == 4:
            push = 7.0 * C.ease(SC.local(i / C.FPS) / 2.0)
        # 押し出されても電極の外には出さない。端で詰まるのが正しい
        ex = np.clip(BX0 + 3 - g + EU * (JX - BX0 - 6) - push,
                     BX0 - g + 2.5, JX - g - 2.5)
        hx = np.clip(JX + 3 + g + HU * (BX1 - JX - 6) + push,
                     JX + g + 2.5, BX1 + g - 2.5)
        eshow = ex < JX - w - 0.5
        hshow = hx > JX + w + 0.5
    if eshow.any():
        ax.scatter(ex[eshow], EY[eshow], s=105, c=C.EL, zorder=7,
                   linewidths=0, alpha=al)
    if hshow.any():
        ax.scatter(hx[hshow], HY[hshow], s=115, facecolors="none",
                   edgecolors=C.DEEP, linewidths=1.6, zorder=7, alpha=al)


# --- 整流の画面 ----------------------------------------------------
IX0, IX1 = 14.0, 70.0
OX0, OX1 = 92.0, 148.0
WY, WA = 55.0, 11.0
WPER = 26.0          # 1周期の横幅


def _wave(x0, x1, ph, rect=False):
    xs = np.linspace(x0, x1, 300)
    v = np.sin(2 * np.pi * (xs - x0) / WPER + ph)
    if rect:
        v = np.maximum(v, 0.0)
    return xs, WY + WA * v


def rectify(t, al=1.0):
    ph = -2 * np.pi * SC.local(t) / 2.2
    for x0, x1, lab in ((IX0, IX1, "入力（交流）"), (OX0, OX1, "出力")):
        ax.plot([x0, x1], [WY, WY], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
                alpha=al * 0.8, zorder=3)
        ax.text((x0 + x1) / 2, 72.0, lab, ha="center", va="bottom",
                fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
    xs, ys = _wave(IX0, IX1, ph)
    ax.plot(xs, ys, color=C.EL, lw=3.0, solid_capstyle="round", alpha=al,
            zorder=6)
    xs2, ys2 = _wave(OX0, OX1, ph, rect=True)
    ax.plot(xs2, ys2, color=C.OKC, lw=3.0, solid_capstyle="round", alpha=al,
            zorder=6)
    # ダイオード記号(三角＋棒)。向きは「右へだけ通す」
    ax.fill([76.0, 76.0, 84.0], [50.0, 60.0, 55.0], color=C.FILL,
            edgecolor=C.EDGE, lw=1.4, zorder=5, alpha=al)
    ax.plot([84.5, 84.5], [49.5, 60.5], color=C.EDGE, lw=2.6, zorder=5,
            alpha=al)
    ax.text(80.5, 45.0, "ダイオード", ha="center", va="top", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "pn接合とダイオード",
                     sub="第7回 ── 片側だけ通す")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "つないだだけで、一方通行ができる",
                     main2="部品ではなく、境目が働いている",
                     sub="次はこれを3層にする。トランジスタになる")
        SC.caption(ax, t)
        return []

    if k == 5:
        rectify(t, al)
        ax.text(80, 24, "交流  →  直流（半分だけ）", ha="center", va="center",
                fontsize=25, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "コンセントの交流を、機器の直流に変える入口がこれ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    w = width(t)
    g = block(t, al)
    depletion(w, al)
    electrodes({3: 1, 4: -1}.get(k, 0), al)
    carriers(i, k, w, g, al)

    if k == 1:
        ax.text(80, 24, "まだ、ただの2つの半導体", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "青が電子、赤い輪が穴", ha="center", va="center",
                fontsize=15, color=C.MUTED, fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "境目に、運び手のいない帯ができる", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "残るのは動けない＋と−のイオン。これが壁になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "帯が薄い  →  通る", ha="center", va="center",
                fontsize=26, color=C.OKC, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "外から押すと壁が縮み、運び手が境目を越えていく",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "帯が厚い  →  通らない", ha="center", va="center",
                fontsize=26, color=C.NGC, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "逆向きに押すと運び手は境目から遠ざかり、壁が広がる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep07_pn.mp4")
