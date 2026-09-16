"""第9回 増幅回路 ── 真ん中に置く理由。

  小さな波を入れて大きな波が出る。動作点を端に寄せると頭が天井に当たって
  潰れる。だから真ん中に置く。アナログが「連続」であることと、その脆さ。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 28, 41, 53, 63],
    caps=[
        "",                                          # 0 タイトル
        "小さな波を入れると、大きな波が出る",          # 1
        "出口には天井と床がある。動作点は、その真ん中",  # 2
        "動作点を上に寄せると、頭が天井に当たる",       # 3
        "真ん中に戻すと、形がそのまま返ってくる",       # 4
        "",                                          # 5 まとめ
    ],
)

fig, ax = C.new_axes()

IX0, IX1 = 12.0, 58.0            # 入力パネル
OX0, OX1 = 92.0, 150.0           # 出力パネル
IN_Y, IN_A = 54.0, 4.0
TOP, BOT = 68.0, 42.0            # 天井と床
OUT_A = 11.0
WPER = 24.0                      # 1周期の横幅
GAIN = 2.75


def bias(t):
    k, lo = SC.idx(t), SC.local(t)
    mid = (TOP + BOT) / 2
    if k == 3:
        return mid + 9.0 * C.ease(lo / 2.5)
    if k == 4:
        return (mid + 9.0) + (mid - (mid + 9.0)) * C.ease(lo / 2.5)
    return mid


def amp_triangle(al=1.0):
    ax.fill([66.0, 66.0, 86.0], [46.0, 62.0, 54.0], color=C.FILL,
            edgecolor=C.EDGE, lw=1.4, zorder=5, alpha=al)
    ax.text(72.5, 54.0, "×%.1f" % GAIN, ha="center", va="center",
            fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=6)
    ax.plot([IX1, 66.0], [IN_Y, 54.0], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)
    ax.plot([86.0, OX0], [54.0, 54.0], color=C.GRAY, lw=1.6, zorder=3,
            alpha=al)


def panel(x0, x1, mid, lab, al=1.0):
    ax.plot([x0, x1], [mid, mid], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            alpha=al * 0.8, zorder=3)
    # 潰れる前の点線が y=75 まで届くので、パネル名はその上に逃がす
    ax.text((x0 + x1) / 2, 79.0, lab, ha="center", va="bottom", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "増幅回路", sub="第9回 ── 動作点を真ん中に")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "アナログは、間の値を全部もっている",
                     main2="だから、少し外すと壊れる",
                     sub="この脆さが、第11回で「0と1でいい」に向かわせる")
        SC.caption(ax, t)
        return []

    b = bias(t)
    ph = -2 * np.pi * t / 2.4

    panel(IX0, IX1, IN_Y, "入力（小さい）", al)
    xs = np.linspace(IX0, IX1, 260)
    ax.plot(xs, IN_Y + IN_A * np.sin(2 * np.pi * (xs - IX1) / WPER + ph),
            color=C.EL, lw=2.6, solid_capstyle="round", alpha=al, zorder=6)

    amp_triangle(al)

    # --- 出力側。天井と床、動作点、そして潰れ -----------------------
    for y, lab in ((TOP, "天井（電源電圧）"), (BOT, "床（0V）")):
        ax.plot([OX0, OX1], [y, y], color=C.NGC, lw=1.2, ls=(0, (5, 3)),
                alpha=al * 0.8, zorder=4)
        ax.text(OX1, y + (1.2 if y == TOP else -1.2), lab, ha="right",
                va="bottom" if y == TOP else "top", fontsize=12,
                color=C.NGC, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text((OX0 + OX1) / 2, 79.0, "出力（大きい）", ha="center", va="bottom",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)

    xo = np.linspace(OX0, OX1, 320)
    raw = b + OUT_A * np.sin(2 * np.pi * (xo - OX1) / WPER + ph)
    cut = np.clip(raw, BOT, TOP)
    clipped = np.any(raw > TOP) or np.any(raw < BOT)
    if clipped:
        ax.plot(xo, raw, color=C.MUTED, lw=1.2, ls=(0, (3, 3)),
                alpha=al * 0.7, zorder=5)
    ax.plot(xo, cut, color=C.HOT if clipped else C.EL, lw=3.0,
            solid_capstyle="round", alpha=al, zorder=6)

    # 動作点
    # 線はパネル内だけ。ラベルは波に埋もれないよう背景を敷いて上に載せる
    ax.plot([OX0, OX1], [b, b], color=C.OKC, lw=1.2, ls=(0, (2, 3)),
            alpha=al * 0.9, zorder=5)
    ax.text(OX0 + 1.5, b + 1.6, "動作点", ha="left", va="bottom", fontsize=12,
            color=C.OKC, fontproperties=C.FPB, alpha=al, zorder=7,
            bbox=dict(facecolor=C.BG, edgecolor="none", pad=1.0,
                      alpha=al * 0.9))

    if k == 1:
        ax.text(80, 24, "形は同じ。大きさだけが変わる", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "第8回の「比例する」を、波でやっている", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "上にも下にも、同じだけ余白がある", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "だから、上下どちらにも振れる", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "頭が潰れる（歪み）", ha="center", va="center",
                fontsize=26, color=C.HOT, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "点線が、本来出るはずだった形。その差が失われた音",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "だから、動作点は真ん中に置く", ha="center",
                va="center", fontsize=24, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "増幅とは、余白の真ん中で波を暴れさせること",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep09_zofuku.mp4")
