"""第4回 交流と波形 ── 波は回転の影。

  左で矢印を回し、その縦成分を右へ描き出すと正弦波になる。
  回転が速い=周波数、スタート角度の差=位相。対応をそのまま動かす。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 15, 25, 35, 46, 57, 66],
    caps=[
        "",                                          # 0 タイトル
        "矢印が、一定の速さで回っている",              # 1
        "縦の高さを右へ描き出すと、波になる",          # 2
        "1周が1周期。1秒に何周するかが周波数",         # 3
        "速く回すほど、波は横に詰まる",                # 4
        "スタート角度をずらすと、波もずれる",          # 5
        "",                                          # 6 まとめ
    ],
)

fig, ax = C.new_axes()

CX, CY, R = 38.0, 54.0, 15.0          # 回転の円
WX0, WX1 = 62.0, 150.0                # 波形パネル
AMP = R                               # 円の半径と波の振幅を一致させる
SWEEP = 9.0                           # パネル1枚を横切るのにかかる秒数
RATE = (WX1 - WX0) / SWEEP            # ペンの進む速さ(単位/秒)

W_SLOW = 2 * np.pi / 4.0              # 4秒で1周
W_FAST = 2 * np.pi / 2.0              # 2秒で1周


def omega(t):
    k = SC.idx(t)
    lo = SC.local(t)
    if k == 4:
        return W_SLOW + (W_FAST - W_SLOW) * C.ease(lo / 3.0)
    if k >= 5:
        return W_FAST + (W_SLOW - W_FAST) * C.ease(lo / 1.5)
    return W_SLOW


# 角度もペン位置も累積。全フレーム分を先に積んでおく
N = SC.nframes
ANG = np.zeros(N + 1)
OMG = np.zeros(N + 1)
PX = np.full(N + 1, WX0)
SWEEP_ID = np.zeros(N + 1, dtype=int)
for _i in range(N):
    _t = _i / C.FPS
    _w = omega(_t)
    OMG[_i] = _w
    ANG[_i + 1] = ANG[_i] + _w / C.FPS
    # ペンが動き出すのは第2場面から。それまでは左端で待つ
    _x = PX[_i] + (RATE / C.FPS if _t >= SC.b[2] else 0.0)
    if _x >= WX1:
        _x, SWEEP_ID[_i + 1] = WX0, SWEEP_ID[_i] + 1
    else:
        SWEEP_ID[_i + 1] = SWEEP_ID[_i]
    PX[_i + 1] = _x
OMG[N] = OMG[N - 1]

YW = CY + AMP * np.sin(ANG)                    # 本体の波
YW2 = CY + AMP * np.sin(ANG - np.pi / 2)       # 位相を90°ずらした波


def sweep_slice(i):
    """いま描いている一掃きの範囲(先頭フレーム..i)"""
    s = SWEEP_ID[i]
    j = i
    while j > 0 and SWEEP_ID[j - 1] == s:
        j -= 1
    return j, i


def arrow(angle, color, al=1.0, lab=None):
    tx, ty = CX + R * np.cos(angle), CY + R * np.sin(angle)
    ax.annotate("", xy=(tx, ty), xytext=(CX, CY),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2.6,
                                alpha=al, shrinkA=0, shrinkB=0), zorder=7)
    # 縦成分(影)を落とす
    ax.plot([tx, tx], [CY, ty], color=color, lw=1.2, ls=(0, (3, 2)),
            alpha=al * 0.8, zorder=6)
    if lab:
        ax.text(tx, ty + (2.6 if ty >= CY else -2.6), lab, ha="center",
                va="bottom" if ty >= CY else "top", fontsize=13, color=color,
                fontproperties=C.FPB, alpha=al, zorder=8)
    return tx, ty


def circle(al=1.0):
    th = np.linspace(0, 2 * np.pi, 180)
    ax.plot(CX + R * np.cos(th), CY + R * np.sin(th), color=C.GRAY, lw=1.8,
            alpha=al, zorder=3)
    ax.plot([CX - R - 3, CX + R + 3], [CY, CY], color=C.GRAY, lw=1.0,
            ls=(0, (3, 3)), alpha=al * 0.8, zorder=3)
    ax.scatter([CX], [CY], s=40, c=C.GRAY, zorder=4, linewidths=0, alpha=al)


def wave_axis(al=1.0):
    ax.plot([WX0, WX1], [CY, CY], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            alpha=al * 0.8, zorder=3)


def trace(i, ys, color, al=1.0, lw=3.0):
    a, b = sweep_slice(i)
    if b - a < 1:
        return
    ax.plot(PX[a:b + 1], ys[a:b + 1], color=color, lw=lw,
            solid_capstyle="round", alpha=al, zorder=6)


def full_wave(i, shift=0.0):
    """パネルいっぱいの波。右端が「いま」で、左へ流れていく"""
    xs = np.linspace(WX0, WX1, 420)
    ph = ANG[i] - shift + OMG[i] * (xs - WX1) / RATE
    return xs, CY + AMP * np.sin(ph)


def period_bracket(i, al=1.0):
    """いまの回転の速さで1周期が横幅いくつになるか。右端から測る"""
    span = RATE * (2 * np.pi / OMG[i])
    x1 = WX1
    x0 = max(WX0, x1 - span)
    ax.annotate("", xy=(x1, 72.5), xytext=(x0, 72.5),
                arrowprops=dict(arrowstyle="<|-|>", color=C.HOT, lw=1.8,
                                alpha=al, shrinkA=0, shrinkB=0), zorder=8)
    ax.text((x0 + x1) / 2, 75.5, "1周期 T", ha="center", va="bottom",
            fontsize=14, color=C.HOT, fontproperties=C.FPB, alpha=al, zorder=8)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "交流と波形", sub="第4回 ── 回転と正弦波")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "波は、回転の影",
                     main2="速さが周波数、ずれが位相",
                     sub="この対応が、第13回の水晶振動子まで効いてくる")
        SC.caption(ax, t)
        return []

    circle(al)
    ax.text(CX, 72.5, "回転", ha="center", va="bottom", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)

    if k == 1:
        tx, ty = arrow(ANG[i], C.EL, al)
        ax.text(80, 24, "回るだけ。まだ何も起きていない", ha="center",
                va="center", fontsize=20, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(CX + R + 6, CY, "この高さに注目", ha="left", va="center",
                fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
        SC.caption(ax, t)
        return []

    wave_axis(al)
    if k != 3:
        ax.text((WX0 + WX1) / 2, 72.5, "波形", ha="center", va="bottom",
                fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)

    two = (k == 5)
    if k == 2:
        # 描き出している最中。ペンは左から右へ進む
        trace(i, YW, C.EL, al)
        px, py = PX[i], YW[i]
    else:
        # 描き終わったあと。右端が「いま」で、波は左へ流れる
        if two:
            xs2, ys2 = full_wave(i, shift=np.pi / 2)
            ax.plot(xs2, ys2, color=C.HOT, lw=3.0, solid_capstyle="round",
                    alpha=al, zorder=6)
        xs, ys = full_wave(i)
        ax.plot(xs, ys, color=C.EL, lw=3.0, solid_capstyle="round",
                alpha=al, zorder=6)
        px, py = WX1, ys[-1]

    tx, ty = arrow(ANG[i], C.EL, al)
    if k == 2:
        # 矢印の先から、いま描いているペン先まで、同じ高さで結ぶ
        ax.plot([tx, px], [ty, ty], color=C.ELL, lw=1.2, ls=(0, (4, 3)),
                alpha=al * 0.9, zorder=5)
    ax.scatter([px], [py], s=110, c=C.EL, zorder=8, linewidths=0, alpha=al)

    if two:
        arrow(ANG[i] - np.pi / 2, C.HOT, al)
        ax.scatter([WX1], [CY + AMP * np.sin(ANG[i] - np.pi / 2)], s=110,
                   c=C.HOT, zorder=8, linewidths=0, alpha=al)

    if k == 2:
        ax.text(80, 24, "高さ = sin（回った角度）", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "円をまわる点の高さ。それを時間で並べたものが波",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    elif k == 3:
        period_bracket(i, al)
        ax.text(80, 24, "周波数 f  =  1 ÷ T", ha="center", va="center",
                fontsize=26, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "1秒に50周なら 50Hz。家のコンセントがそれ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    elif k == 4:
        period_bracket(i, al)
        ax.text(80, 24, "回転が速い  =  T が短い  =  f が高い", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "波の形は同じ。横に縮んだだけ", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    else:
        ax.text(80, 24, "位相差  90°", ha="center", va="center", fontsize=26,
                color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "同じ速さで回っていても、出発点が違えば波はずれる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep04_koryu.mp4")
