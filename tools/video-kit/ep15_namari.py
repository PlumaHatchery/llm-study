"""第15回 波形は汚れる ── しきい値を2つ持つ。

  きれいな矩形を入れたのに、受け側ではなまって丸くなる(第3回の時定数)。
  しきい値の近くでふらつくと0か1か決まらない。
  シュミットトリガでしきい値を上下2つ持たせ、角を立て直す。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 32, 48, 60],
    caps=[
        "",                                            # 0 タイトル
        "きれいな矩形が、受け側では丸くなっている",       # 1
        "しきい値が1本だと、ふらついて決まらない",        # 2
        "しきい値を上下2つ持たせる（シュミットトリガ）",   # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

X0, X1 = 30.0, 152.0
RATE = 12.0                     # 波が流れる速さ(単位/秒)
PER_T = 2.2                     # 1周期の秒数
ROW_IN, A_IN = 74.0, 4.0
ROW_RX, A_RX = 56.0, 8.0
ROW_OUT, A_OUT = 38.0, 4.0
THR = 0.5
THR_HI, THR_LO = 0.64, 0.36
TAU_X = 3.2                     # なまりの時定数(x方向の長さ)

XS = np.linspace(X0, X1, 620)
DX = XS[1] - XS[0]
ALPHA = 1.0 - np.exp(-DX / TAU_X)


def noise_on(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 2:
        return 0.16 * C.ease(lo / 2.0)
    if k >= 3:
        return 0.16
    return 0.0


def signals(t):
    """入力の矩形、なまってノイズが乗った受信波、そのときの判定"""
    u = (XS - X1) / RATE + t
    raw = ((u / PER_T) % 1.0 < 0.5).astype(float)
    # 一次遅れ。これが第3回の充電カーブそのもの
    rx = np.empty_like(raw)
    acc = raw[0]
    for n in range(len(raw)):
        acc += (raw[n] - acc) * ALPHA
        rx[n] = acc
    amp = noise_on(t)
    if amp > 0:
        rx = rx + amp * (np.sin(41.0 * u) + np.sin(57.0 * u + 1.1)
                         + np.sin(83.0 * u + 2.3)) / 3.0
    return raw, rx


def decide(rx, hyst):
    if not hyst:
        return (rx > THR).astype(float)
    out = np.empty_like(rx)
    s = 1.0 if rx[0] > THR_HI else 0.0
    for n in range(len(rx)):
        if s < 0.5 and rx[n] > THR_HI:
            s = 1.0
        elif s > 0.5 and rx[n] < THR_LO:
            s = 0.0
        out[n] = s
    return out


def row(y, a, vals, color, lab, al=1.0, lw=3.0, step=False):
    ax.plot([X0, X1], [y - a, y - a], color=C.GRAY, lw=0.8, ls=(0, (3, 3)),
            alpha=al * 0.6, zorder=3)
    ax.plot(XS, y - a + 2 * a * vals, color=color, lw=lw,
            drawstyle="steps-post" if step else "default",
            solid_capstyle="butt" if step else "round", alpha=al, zorder=6)
    ax.text(X0 - 3.0, y, lab, ha="right", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def thr_lines(hyst, al=1.0):
    y0, a = ROW_RX, A_RX
    if hyst:
        for v, lab, col in ((THR_HI, "上のしきい値", C.OKC),
                            (THR_LO, "下のしきい値", C.OKC)):
            yy = y0 - a + 2 * a * v
            ax.plot([X0, X1], [yy, yy], color=col, lw=1.3, ls=(0, (4, 3)),
                    alpha=al, zorder=7)
            ax.text(X1, yy, lab, ha="right", va="bottom" if v > 0.5 else "top",
                    fontsize=12, color=col, fontproperties=C.FPB, alpha=al,
                    zorder=8, bbox=dict(facecolor=C.BG, edgecolor="none",
                                        pad=0.8, alpha=al * 0.85))
    else:
        yy = y0 - a + 2 * a * THR
        ax.plot([X0, X1], [yy, yy], color=C.HOT, lw=1.3, ls=(0, (4, 3)),
                alpha=al, zorder=7)
        ax.text(X1, yy + 0.8, "しきい値", ha="right", va="bottom",
                fontsize=12, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=8, bbox=dict(facecolor=C.BG, edgecolor="none",
                                    pad=0.8, alpha=al * 0.85))


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "波形は汚れる",
                     sub="第15回 ── 角を立て直す")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "汚れるのは避けられない",
                     main2="だから、決め方のほうを変える",
                     sub="1本で迷うなら、2本にして迷う区間をなくす")
        SC.caption(ax, t)
        return []

    hyst = (k == 3)
    raw, rx = signals(t)
    out = decide(rx, hyst)

    row(ROW_IN, A_IN, raw, C.EL, "入力", al, 2.6, step=True)
    row(ROW_RX, A_RX, np.clip(rx, -0.25, 1.25), C.MUTED, "受信", al, 2.6)
    thr_lines(hyst, al)
    row(ROW_OUT, A_OUT, out, C.OKC if hyst else C.HOT, "出力", al, 2.8,
        step=True)

    if k == 1:
        ax.text(80, 24, "角が丸くなる  ──  線の時定数のせい", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "第3回の充電カーブが、そのまま出てきている",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        ax.text(80, 24, "境目をまたぐたびに、出力が暴れる", ha="center",
                va="center", fontsize=23, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "1回の変化のはずが、何回も変化したことになる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "上を越えたら1、下を割ったら0", ha="center",
                va="center", fontsize=24, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "間にいる限り、前の答えを保つ。だから揺れても動かない",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep15_namari.mp4")
