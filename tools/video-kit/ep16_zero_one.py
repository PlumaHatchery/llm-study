"""第16回 0と1という取り決め ── 帯の中なら無傷。

  電圧の帯を3つに分ける。0の領域・どちらでもない禁止帯・1の領域。
  ノイズをのせても帯の中に収まれば情報は無傷。第2回の分圧がここで効く。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 17, 30, 44, 56, 66],
    caps=[
        "",                                            # 0 タイトル
        "電圧の幅を、3つに区切る",                       # 1
        "多少ゆれても、帯の中なら読みは変わらない",        # 2
        "帯をはみ出すと、禁止帯に入って読めなくなる",      # 3
        "アナログなら、同じノイズで値が変わってしまう",    # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

# 縦が電圧。0〜1に正規化して帯を切る
GX0, GX1 = 40.0, 120.0
GY0, GY1 = 36.0, 70.0
LO_TOP, HI_BOT = 0.30, 0.70      # 0の帯の上端／1の帯の下端


def gy(v):
    return GY0 + (GY1 - GY0) * v


def noise_amp(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 2:
        return 0.11 * C.ease(lo / 2.0)
    if k == 3:
        return 0.11 + 0.22 * C.ease(lo / 3.0)
    if k == 4:
        return 0.11
    return 0.0


def bands(al=1.0, dim=False):
    rows = [(0.0, LO_TOP, C.EL, "0 と読む"),
            (LO_TOP, HI_BOT, C.FILL, "どちらでもない（禁止帯）"),
            (HI_BOT, 1.0, C.DEEP, "1 と読む")]
    for v0, v1, col, lab in rows:
        mid = v1 == HI_BOT and v0 == LO_TOP
        C.rrect(ax, GX0, gy(v0), GX1 - GX0, gy(v1) - gy(v0),
                C.FILL if mid else C.BG, col if not mid else C.EDGE,
                r=0.9, lw=1.3, al=al * (0.35 if dim else 1.0), z=2)
        if not mid:
            ax.plot([GX0, GX1], [gy((v0 + v1) / 2), gy((v0 + v1) / 2)],
                    color=col, lw=0.9, ls=(0, (2, 4)), alpha=al * 0.5,
                    zorder=3)
        ax.text(GX1 + 3.0, gy((v0 + v1) / 2), lab, ha="left", va="center",
                fontsize=13 if mid else 14,
                color=C.MUTED if mid else col,
                fontproperties=C.FP if mid else C.FPB,
                alpha=al * (0.5 if dim else 1.0), zorder=5)
    ax.text(GX0 - 3.0, GY1, "電圧", ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def signal(t, al=1.0, analog=False):
    """帯の上を流れる信号。ノイズを乗せる"""
    xs = np.linspace(GX0 + 1.5, GX1 - 1.5, 420)
    u = (xs - GX1) / 11.0 + t
    if analog:
        base = 0.5 + 0.34 * np.sin(2 * np.pi * u / 3.4)
    else:
        base = np.where((u / 2.6) % 1.0 < 0.5, 0.86, 0.14)
    a = noise_amp(t)
    v = base + a * (np.sin(39.0 * u) + np.sin(58.0 * u + 1.2)
                    + np.sin(77.0 * u + 2.4)) / 3.0
    bad = (not analog) and np.any((v > LO_TOP) & (v < HI_BOT))
    ax.plot(xs, gy(np.clip(v, -0.05, 1.05)),
            color=C.HOT if bad else (C.OKC if analog else C.INK),
            lw=2.6, solid_capstyle="round", alpha=al, zorder=7)
    return bad


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "0と1という取り決め",
                     sub="第16回 ── デジタルが汚れに強い理由")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "強いのは、部品ではなく取り決めのほう",
                     main2="読みちがえない幅を、先に空けてある",
                     sub="第2回の分圧で作った幅が、そのまま余裕になる")
        SC.caption(ax, t)
        return []

    analog = (k == 4)
    bands(al, dim=analog)
    bad = signal(t, al, analog)

    if k == 1:
        ax.text(80, 24, "間を、わざと捨てる", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "使わない幅を真ん中に空けておくのが、肝心なところ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "ゆれても、読みは 0 と 1 のまま", ha="center",
                va="center", fontsize=24, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "帯の幅が、そのままノイズに耐えられる量になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "禁止帯に入った  →  判定できない" if bad
                else "ここまでは、まだ持ちこたえる",
                ha="center", va="center", fontsize=23,
                color=C.HOT if bad else C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "耐えられる量には限りがある。それを超えたら誤る",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "アナログには、逃げる幅がない", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "のった分だけ値が狂う。元がどこだったか分からない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep16_zero_one.mp4")
