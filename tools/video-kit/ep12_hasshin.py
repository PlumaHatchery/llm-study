"""第12回 発振 ── 出力を入力に戻す線を1本。

  遅れと利得が合うと、小さな揺れが勝手に育って持続する。
  足りなければ減衰し、強すぎれば暴れる。ブランコを押すタイミングと同じ。
  遅れを決めているのは第3回の時定数。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 29, 41, 53, 64, 73],
    caps=[
        "",                                            # 0 タイトル
        "出力を入力に戻す線を、1本つなぐ",               # 1
        "タイミングが合うと、小さな揺れが育つ",           # 2
        "戻す量が足りないと、消えてしまう",               # 3
        "戻しすぎると、頭を打って暴れる",                 # 4
        "ブランコを押すのと、まったく同じ",               # 5
        "",                                            # 6 まとめ
    ],
)

fig, ax = C.new_axes()

WX0, WX1 = 80.0, 150.0
WY, WA = 54.0, 14.0
WRATE = 10.0                 # 波形が流れる速さ(単位/秒)
FREQ = 0.8                   # 発振の周波数(Hz)

AMP_IN = [(26.0, 46.0), (48.0, 62.0)]     # 増幅器の三角
LOOP = [(46.0, 55.0), (62.0, 55.0), (62.0, 68.0), (16.0, 68.0),
        (16.0, 55.0), (26.0, 55.0)]


def env_at(t):
    """そのときの揺れの大きさ(1.0で満振幅)"""
    k, lo = SC.idx(t), SC.local(t)
    if k == 2:
        return min(1.0, 0.07 * np.exp(lo * 0.62))
    if k == 3:
        return 0.95 * np.exp(-lo * 0.42)
    if k == 4:
        return min(1.75, 0.10 * np.exp(lo * 0.70))
    if k == 5:
        return 1.0
    return 0.0


N = SC.nframes
ENV = np.array([env_at(j / C.FPS) for j in range(N + 1)])
ANG = 2 * np.pi * FREQ * np.arange(N + 1) / C.FPS
DRIFT = np.zeros(N + 1)
for _i in range(N):
    DRIFT[_i + 1] = DRIFT[_i] + 0.22 * min(ENV[_i] * 3, 1.0) / C.FPS

DOT_U = np.arange(6) / 6.0


def waveform(i, al=1.0):
    xs = np.linspace(WX0, WX1, 420)
    # フレーム番号に丸めると波が階段になる。連続値のまま補間する
    fj = np.clip(i - (WX1 - xs) / WRATE * C.FPS, 0.0, float(N))
    envx = np.interp(fj, np.arange(N + 1), ENV)
    raw = envx * np.sin(2 * np.pi * FREQ * fj / C.FPS)
    over = np.any(np.abs(raw) > 1.001)
    ax.plot([WX0, WX1], [WY, WY], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            alpha=al * 0.8, zorder=3)
    for s in (1, -1):
        ax.plot([WX0, WX1], [WY + s * WA, WY + s * WA], color=C.NGC, lw=1.0,
                ls=(0, (5, 3)), alpha=al * 0.55, zorder=3)
    ax.plot(xs, WY + WA * np.clip(raw, -1, 1),
            color=C.HOT if over else C.EL, lw=3.0, solid_capstyle="round",
            alpha=al, zorder=6)
    ax.text((WX0 + WX1) / 2, 72.5, "回路の中の揺れ", ha="center", va="bottom",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def loop_diagram(i, al=1.0):
    p = np.array(LOOP, dtype=float)
    ax.plot(p[:, 0], p[:, 1], color=C.GRAY, lw=2.0, solid_capstyle="round",
            solid_joinstyle="round", zorder=2, alpha=al)
    ax.fill([AMP_IN[0][0], AMP_IN[0][0], AMP_IN[0][1]],
            [AMP_IN[1][0], AMP_IN[1][1], 55.0], color=C.FILL,
            edgecolor=C.EDGE, lw=1.4, zorder=5, alpha=al)
    ax.text(33.5, 55.0, "増幅", ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=6)
    C.rrect(ax, 32.0, 65.4, 14.0, 5.2, C.FILL, C.EDGE, r=0.9, lw=1.1,
            al=al, z=5)
    ax.text(39.0, 68.0, "遅れ", ha="center", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=6)
    ax.text(39.0, 74.5, "出力を入力へ戻す（帰還）", ha="center", va="center",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    if DRIFT[i] > 0:
        u = (DOT_U + DRIFT[i]) % 1.0
        pts = np.array([C.ppt(LOOP, v) for v in u])
        ax.scatter(pts[:, 0], pts[:, 1], s=85, c=C.EL, zorder=7,
                   linewidths=0, alpha=al)


def swing(i, al=1.0):
    """ブランコ。押すのは、いちばん速い瞬間"""
    px, py, L = 39.0, 74.0, 22.0
    a = 0.55 * np.sin(ANG[i])
    bx, by = px + L * np.sin(a), py - L * np.cos(a)
    ax.plot([px - 9, px + 9], [py, py], color=C.GRAY, lw=2.4, zorder=3,
            alpha=al)
    ax.plot([px, bx], [py, by], color=C.EDGE, lw=2.0, zorder=4, alpha=al)
    ax.scatter([bx], [by], s=300, c=C.FILL, edgecolors=C.EDGE, linewidths=1.4,
               zorder=5, alpha=al)
    if abs(np.sin(ANG[i])) < 0.35:
        d = 7.0 * np.sign(np.cos(ANG[i]))
        ax.annotate("", xy=(bx + d * 1.4, by), xytext=(bx + d * 0.5, by),
                    arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.6,
                                    alpha=al), zorder=8)
        ax.text(bx, by - 6.0, "いま押す", ha="center", va="top", fontsize=13,
                color=C.HOT, fontproperties=C.FPB, alpha=al, zorder=8)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "発振",
                     sub="第12回 ── 勝手に揺れつづける回路")
        SC.caption(ax, t)
        return []

    if k == 6:
        C.title_card(ax, SC, t, "遅れと利得が合えば、放っておいても揺れる",
                     main2="時間をつくる装置ができた",
                     sub="遅れを決めているのは、第3回の時定数")
        SC.caption(ax, t)
        return []

    if k == 5:
        swing(i, al)
    else:
        loop_diagram(i, al)
    waveform(i, al)

    if k == 1:
        ax.text(80, 24, "輪になった。ここから先は自分で回る", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "戻す量（利得）と、戻すまでの時間（遅れ）で決まる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "利得 1 ちょうど、位相 1周ぴったり", ha="center",
                va="center", fontsize=23, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "雑音程度の小さな揺れが、育って居座る", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 3:
        ax.text(80, 24, "利得が 1 より小さい  →  消える", ha="center",
                va="center", fontsize=24, color=C.NGC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "一周するたびに小さくなるので、いずれ止まる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 4:
        ax.text(80, 24, "利得が大きすぎる  →  天井を叩く", ha="center",
                va="center", fontsize=24, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "揺れは続くが、形は正弦波でなくなる（第9回の歪み）",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "毎回、同じところで押す", ha="center", va="center",
                fontsize=25, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "ずれて押せば止まる。合って押せば大きくなる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep12_hasshin.mp4")
