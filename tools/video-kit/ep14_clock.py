"""第14回 クロックとパルス ── 立ち上がりで、一斉に。

  矩形波を1本流し、立ち上がりの瞬間に離れた部品が同時に動く。
  デューティ比。最後に、速くしすぎると遠い部品に届く前に次の波が出る。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 6, 20, 34, 50, 62],
    caps=[
        "",                                            # 0 タイトル
        "立ち上がりの瞬間、離れた部品が同時に動く",       # 1
        "高い時間の割合を、デューティ比という",           # 2
        "速くしすぎると、届く前に次が出る",               # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

TX0, TX1 = 16.0, 150.0          # タイミング図の横軸(時間)
CY, CA = 70.0, 5.0              # クロック波形
PARTS = [30.0, 80.0, 130.0]
PY0, PH_ = 42.0, 14.0
PERIOD_X = 40.0                 # タイミング図での1周期の幅

LINE_Y = 56.0                   # 第3場面。こちらの横軸は距離
SRC_X, END_X = 16.0, 148.0
FAR = [52.0, 96.0, 140.0]
VPROP = 45.0                    # 信号が線を伝わる速さ(単位/秒)


def duty_at(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 2 and lo > 6.0:
        return 0.5 + (0.25 - 0.5) * C.ease((lo - 6.0) / 2.0)
    return 0.5


def period_at(lo):
    """第3場面。だんだん短くする"""
    return 3.4 + (0.75 - 3.4) * C.ease(lo / 9.0)


def timing(t, duty, al=1.0):
    """x が時間のタイミング図。波は右から左へ流れる"""
    xs = np.linspace(TX0, TX1, 700)
    ph = (xs - TX1) / PERIOD_X + t / 2.0
    hi = (ph % 1.0) < duty
    ax.plot(xs, CY - CA + 2 * CA * hi, color=C.EL, lw=3.0, zorder=6,
            alpha=al, drawstyle="steps-post", solid_capstyle="butt")
    ax.text(TX0, CY + CA + 2.0, "クロック", ha="left", va="bottom",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    return (t / 2.0) % 1.0


def parts(fire_ph, al=1.0, offs=None):
    """立ち上がり直後だけ光らせる"""
    for j, px in enumerate(PARTS):
        p = fire_ph if offs is None else (fire_ph - offs[j]) % 1.0
        lit = p < 0.16
        C.rrect(ax, px - 11, PY0, 22, PH_, C.OKC if lit else C.FILL,
                C.OKC if lit else C.EDGE, r=1.2, lw=1.2, al=al, z=5)
        ax.text(px, PY0 + PH_ / 2, "部品 %d" % (j + 1), ha="center",
                va="center", fontsize=13,
                color=C.BG if lit else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=6)
        ax.plot([px, px], [PY0 + PH_, CY - CA], color=C.GRAY, lw=1.4,
                zorder=3, alpha=al * 0.9)


def duty_marks(t, duty, al=1.0):
    # 目盛りは実際の立ち上がりに合わせる。固定位置に置くとずれる
    n0 = np.ceil((TX0 + 8.0 - TX1) / PERIOD_X + t / 2.0)
    x0 = TX1 + PERIOD_X * (n0 - t / 2.0)
    xh = x0 + PERIOD_X * duty
    x1 = x0 + PERIOD_X
    ax.annotate("", xy=(xh, 82.0), xytext=(x0, 82.0),
                arrowprops=dict(arrowstyle="<|-|>", color=C.HOT, lw=1.6,
                                alpha=al, shrinkA=0, shrinkB=0), zorder=8)
    ax.text((x0 + xh) / 2, 83.5, "高い時間", ha="center", va="bottom",
            fontsize=13, color=C.HOT, fontproperties=C.FPB, alpha=al,
            zorder=8)
    ax.annotate("", xy=(x1, 60.0), xytext=(x0, 60.0),
                arrowprops=dict(arrowstyle="<|-|>", color=C.MUTED, lw=1.4,
                                alpha=al, shrinkA=0, shrinkB=0), zorder=8)
    ax.text((x0 + x1) / 2, 58.5, "1周期", ha="center", va="top", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=8)


def propagation(lo, al=1.0):
    """x が距離。パルスが左から右へ走る"""
    ax.plot([SRC_X, END_X], [LINE_Y, LINE_Y], color=C.GRAY, lw=2.4,
            solid_capstyle="round", zorder=3, alpha=al)
    ax.text(SRC_X, LINE_Y + 4.0, "クロック源", ha="left", va="bottom",
            fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    # 出発した時刻の一覧。周期が縮むので積分して求める
    ts, acc, T = [], 0.0, period_at(0.0)
    while acc < lo:
        ts.append(acc)
        acc += max(period_at(acc), 0.2)
    xs = [SRC_X + (lo - te) * VPROP for te in ts]
    live = [x for x in xs if SRC_X <= x <= END_X]
    for x in live:
        ax.plot([x, x], [LINE_Y - 3.0, LINE_Y + 3.0], color=C.EL, lw=3.0,
                solid_capstyle="round", zorder=6, alpha=al)
    for j, px in enumerate(FAR):
        lit = any(abs(x - px) < 3.2 for x in live)
        C.rrect(ax, px - 10, 36.0, 20, 12, C.OKC if lit else C.FILL,
                C.OKC if lit else C.EDGE, r=1.1, lw=1.2, al=al, z=5)
        ax.text(px, 42.0, "部品 %d" % (j + 1), ha="center", va="center",
                fontsize=12, color=C.BG if lit else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=6)
        ax.plot([px, px], [48.0, LINE_Y], color=C.GRAY, lw=1.4, zorder=3,
                alpha=al * 0.9)
    n = len(live)
    ax.text(82.0, 72.0, "線の上にいるパルス： %d 個" % n, ha="center",
            va="center", fontsize=16,
            color=C.HOT if n > 1 else C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=6)
    ax.text(82.0, 65.5, "周期 %.2f 秒" % period_at(lo), ha="center",
            va="center", fontsize=13, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "クロックとパルス",
                     sub="第14回 ── 全体をそろえる合図")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "そろえる合図が、速さの上限を決める",
                     main2="いちばん遠い部品に届くまで、待つしかない",
                     sub="この壁が、第29回のパイプラインを呼ぶ")
        SC.caption(ax, t)
        return []

    if k == 3:
        propagation(lo, al)
        ax.text(80, 24, "まだ届いていないのに、次が出発した", ha="center",
                va="center", fontsize=23, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "信号が線を渡る時間より短くすると、そろわなくなる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    duty = duty_at(t)
    ph = timing(t, duty, al)
    parts(ph, al)

    if k == 1:
        ax.text(80, 24, "0から1に変わる、その瞬間だけを見る", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "離れた部品どうしが、打ち合わせなしにそろう",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        duty_marks(t, duty, al)
        ax.text(80, 24, "デューティ比  =  高い時間 ÷ 1周期", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "%d%% 。合図に使うのは立ち上がりだけなので、"
                        "比そのものは自由" % int(round(duty * 100)),
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep14_clock.mp4")
