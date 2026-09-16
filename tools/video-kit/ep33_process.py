"""第33回 プロセスとスケジューラ ── 持ち替えているだけ。

  CPUが1個しかないのに3つが同時に動いて見える。
  実際は高速で持ち替えている。持ち替えのたびに、棚への出し入れが要る。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 20, 36, 52, 62],
    caps=[
        "",                                            # 0 タイトル
        "3つとも、同時に進んでいるように見える",         # 1
        "拡大すると、1つずつしか動いていない",           # 2
        "持ち替えるたびに、棚への出し入れが要る",         # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

PROCS = [("音楽", C.EL), ("ブラウザ", C.DEEP), ("エディタ", C.OKC)]
BAR_X0, BAR_X1 = 34.0, 142.0
BAR_Y = [80.0, 72.0, 64.0]
GX0, GX1, GY, GH = 20.0, 146.0, 38.0, 9.0
SLICE = 0.55                 # 1つのプログラムが握る時間(秒)
SWITCH = 0.12                # 持ち替えにかかる時間(秒)


def owner(tt):
    """(担当プロセス, 入れ替え中か)"""
    unit = SLICE + SWITCH
    n = int(tt / unit)
    within = tt - n * unit
    return n % 3, within >= SLICE


def bars(prog, al=1.0):
    for (name, col), y, p in zip(PROCS, BAR_Y, prog):
        C.rrect(ax, BAR_X0, y - 3.0, BAR_X1 - BAR_X0, 6.0, "#EFEDE5",
                "#D3D1C7", r=0.9, lw=0.8, al=al, z=3)
        C.rrect(ax, BAR_X0, y - 3.0, max(1.5, (BAR_X1 - BAR_X0) * p), 6.0,
                col, "none", r=0.9, al=al * 0.9, z=4)
        ax.text(BAR_X0 - 3.0, y, name, ha="right", va="center", fontsize=14,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)


def gantt(tt, span, al=1.0, show_switch=False):
    """いまから過去 span 秒ぶんの持ち主を帯で描く"""
    ax.text(GX0 - 3.0, GY + GH / 2, "CPU", ha="right", va="center",
            fontsize=14, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    n = 420
    xs = np.linspace(GX0, GX1, n + 1)
    for j in range(n):
        tj = tt - span * (1 - j / n)
        if tj < 0:
            continue
        who, sw = owner(tj)
        col = C.NGC if (sw and show_switch) else PROCS[who][1]
        ax.fill_between([xs[j], xs[j + 1]], GY, GY + GH, color=col,
                        linewidth=0, alpha=al * (0.95 if not sw else 1.0),
                        zorder=4)
    C.rrect(ax, GX0, GY, GX1 - GX0, GH, "none", C.EDGE, r=0.6, lw=1.0,
            al=al, z=6)
    ax.text(GX1, GY - 3.0, "いま →", ha="right", va="top", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(GX0, GY - 3.0, "%.1f 秒ぶん" % span, ha="left", va="top",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def now_box(who, sw, al=1.0):
    name, col = PROCS[who]
    C.rrect(ax, 58.0, 50.0, 44.0, 8.0, C.FILL,
            C.NGC if sw else col, r=1.0, lw=1.8, al=al, z=5)
    ax.text(80.0, 54.0, "入れ替え中" if sw else name, ha="center",
            va="center", fontsize=15, color=C.NGC if sw else col,
            fontproperties=C.FPB, alpha=al, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "プロセスとスケジューラ",
                     sub="第33回 ── 同時に見えているだけ")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "同時に動かしているのではない",
                     main2="細かく持ち替えて、そう見せている",
                     sub="持ち替えはタダではない。速すぎても遅くなる")
        SC.caption(ax, t)
        return []

    prog = [min(1.0, 0.04 + lo / 16.0 * f) for f in (1.0, 0.82, 0.66)]
    bars(prog, al)
    who, sw = owner(lo)

    if k == 1:
        gantt(lo, 12.0, al)
        ax.text(80, 26, "見た目には、3本とも伸びつづける", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 17, "人の目には、切り替えが速すぎて分からない",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    elif k == 2:
        gantt(lo, 2.2, al)
        now_box(who, False, al)
        ax.text(80, 26, "その瞬間、CPU は1つのものでしかない", ha="center",
                va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 17, "順番が回ってくるまで、ほかは止まっている",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        gantt(lo, 2.2, al, show_switch=True)
        now_box(who, sw, al)
        ax.text(80, 26, "茶色の細い帯が、持ち替えの代金", ha="center",
                va="center", fontsize=21, color=C.NGC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 17, "レジスタを棚へ入れて、次の分を棚から出す（第31回）",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep33_process.mp4")
