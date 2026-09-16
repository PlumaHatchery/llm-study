"""第11回 なぜデジタルはMOSFETなのか ── 増幅素子の転職。

  同じ入力波を2本の出口に分ける。上は増幅器として使った出力(なだらか)、
  下はスイッチとして使った出力(しきい値で角が立つ)。
  最後に、待機しているだけのときに流れる電流を対比する。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 29, 42, 54, 63],
    caps=[
        "",                                            # 0 タイトル
        "同じ波を、2つの使い方に通してみる",             # 1
        "増幅器として使うと、なだらかに出てくる",         # 2
        "スイッチとして使うと、しきい値で角が立つ",       # 3
        "待っているだけのとき、流れる電流が違う",         # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

IX0, IX1 = 10.0, 54.0
IN_Y, IN_A = 54.0, 7.0
OX0, OX1 = 74.0, 150.0
UP_Y, LO_Y, OA = 63.0, 42.0, 6.5
WPER = 22.0
THR = IN_Y                       # しきい値は入力の真ん中に置く


def waves(t):
    ph = -2 * np.pi * t / 2.6
    xs = np.linspace(IX0, IX1, 260)
    yi = IN_Y + IN_A * np.sin(2 * np.pi * (xs - IX1) / WPER + ph)
    xo = np.linspace(OX0, OX1, 420)
    s = np.sin(2 * np.pi * (xo - OX1) / WPER + ph)
    yu = UP_Y + OA * s                             # なだらか
    yl = LO_Y + OA * np.where(s > 0, 1.0, -1.0)    # 角が立つ
    return xs, yi, xo, yu, yl


def panel_axis(x0, x1, y, al=1.0):
    ax.plot([x0, x1], [y, y], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            alpha=al * 0.8, zorder=3)


def split(al=1.0):
    """入力から2つの出口へ分岐する線"""
    ax.plot([IX1, 64.0], [IN_Y, IN_Y], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)
    ax.plot([64.0, 64.0], [LO_Y, UP_Y], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)
    ax.plot([64.0, OX0], [UP_Y, UP_Y], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)
    ax.plot([64.0, OX0], [LO_Y, LO_Y], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)


def idle_bars(t, al=1.0):
    """待機中に流れつづける電流。棒の長さで比べる"""
    b = C.ease(SC.local(t) / 1.5)
    rows = [(62.0, 1.00, C.HOT, "増幅器として使う", "動作点に、常に流しておく"),
            (46.0, 0.02, C.OKC, "スイッチとして使う", "切れている側は流れない")]
    for y, frac, col, name, note in rows:
        x, w = 58.0, 62.0
        C.rrect(ax, x, y, w, 6.0, "#EFEDE5", "#D3D1C7", r=0.9, lw=0.8,
                al=al, z=3)
        C.rrect(ax, x, y, max(2.4, w * frac * b), 6.0, col, "none", r=0.9,
                al=al * 0.9, z=4)
        ax.text(x - 3.0, y + 3.0, name, ha="right", va="center", fontsize=14,
                color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(x + w + 2.5, y + 3.0, note, ha="left", va="center",
                fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
    ax.text(89.0, 72.0, "待機中に流れつづける電流", ha="center", va="center",
            fontsize=15, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "なぜデジタルはMOSFETなのか",
                     sub="第11回 ── 増幅素子が、スイッチに転職する")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "同じ素子を、真ん中ではなく端で使う",
                     main2="それだけで、デジタルになる",
                     sub="角の立った波だけを相手にすれば、汚れても復元できる")
        SC.caption(ax, t)
        return []

    if k == 4:
        idle_bars(t, al)
        ax.text(80, 24, "止まっている間の消費が、桁で違う", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "並べる数が億を超えると、この差が決定的になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    xs, yi, xo, yu, yl = waves(t)

    panel_axis(IX0, IX1, IN_Y, al)
    ax.plot(xs, yi, color=C.EL, lw=2.6, solid_capstyle="round", alpha=al,
            zorder=6)
    ax.text((IX0 + IX1) / 2, 72.0, "入力（同じ波）", ha="center", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    split(al)

    panel_axis(OX0, OX1, UP_Y, al)
    panel_axis(OX0, OX1, LO_Y, al)
    ax.text(OX1, 72.0, "増幅器として使う", ha="right", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    ax.text(OX1, 30.5, "スイッチとして使う", ha="right", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)

    hot_up = (k == 2)
    hot_lo = (k == 3)
    ax.plot(xo, yu, color=C.EL if hot_up else C.GRAY,
            lw=3.0 if hot_up else 1.8, solid_capstyle="round",
            alpha=al if hot_up else al * 0.55, zorder=6 if hot_up else 4)
    ax.plot(xo, yl, color=C.OKC if hot_lo else C.GRAY,
            lw=3.0 if hot_lo else 1.8, solid_capstyle="round",
            alpha=al if hot_lo else al * 0.55, zorder=6 if hot_lo else 4)

    if k == 3:
        ax.plot([IX0, IX1], [THR, THR], color=C.HOT, lw=1.4, ls=(0, (4, 3)),
                alpha=al, zorder=7)
        ax.text(IX0, THR + 1.6, "しきい値", ha="left", va="bottom",
                fontsize=12, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=8, bbox=dict(facecolor=C.BG, edgecolor="none",
                                    pad=1.0, alpha=al * 0.9))

    if k == 1:
        ax.text(80, 24, "素子は同じ。使い方だけが違う", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "真ん中で使えば増幅、端で使えばスイッチ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "中間の値が、そのまま残る", ha="center", va="center",
                fontsize=25, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "情報は濃い。でも、ノイズが乗れば元に戻せない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "中間が消えて、0か1だけになる", ha="center",
                va="center", fontsize=25, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "情報は減る。そのかわり、多少汚れても読み直せる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep11_why_digital.mp4")
