"""第32回 特権モードとシステムコール ── 扉は1枚だけ。

  ユーザ空間とカーネルを2部屋に分け、間に1枚だけ扉を置く。
  勝手に壁を越えようとすると弾かれる。扉を通るときだけ特権が切り替わる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 34, 50, 60],
    caps=[
        "",                                            # 0 タイトル
        "部屋は2つ。壁には扉が1枚しかない",              # 1
        "壁を直接越えようとすると、弾かれる",             # 2
        "扉を通るときだけ、特権が切り替わる",             # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

UX0, UX1 = 14.0, 74.0
KX0, KX1 = 86.0, 146.0
RY0, RY1 = 38.0, 74.0
WALL_X = 80.0
DOOR_Y0, DOOR_Y1 = 52.0, 60.0
BAD_Y = 44.0


def rooms(mode, al=1.0):
    for x0, x1, name, col, on in ((UX0, UX1, "ユーザ空間", C.EL,
                                   mode == "user"),
                                  (KX0, KX1, "カーネル", C.DEEP,
                                   mode == "kernel")):
        C.rrect(ax, x0, RY0, x1 - x0, RY1 - RY0, C.FILL if on else C.BG,
                col if on else C.EDGE, r=1.4, lw=1.8 if on else 1.2,
                al=al, z=3)
        ax.text((x0 + x1) / 2, RY1 + 4.0, name, ha="center", va="bottom",
                fontsize=15, color=col if on else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=5)
    # 壁と、1枚だけの扉
    for y0, y1 in ((RY0, DOOR_Y0), (DOOR_Y1, RY1)):
        ax.plot([WALL_X, WALL_X], [y0, y1], color=C.NGC, lw=5.0,
                solid_capstyle="butt", zorder=5, alpha=al)
    ax.plot([WALL_X, WALL_X], [DOOR_Y0, DOOR_Y1], color=C.OKC, lw=2.0,
            ls=(0, (2, 2)), zorder=5, alpha=al)
    ax.text(WALL_X, (DOOR_Y0 + DOOR_Y1) / 2, "扉", ha="center", va="center",
            fontsize=13, color=C.OKC, fontproperties=C.FPB, alpha=al,
            zorder=7, bbox=dict(facecolor=C.BG, edgecolor="none", pad=1.0,
                                alpha=al))
    ax.text(WALL_X, RY1 + 4.0, "壁", ha="center", va="bottom", fontsize=13,
            color=C.NGC, fontproperties=C.FPB, alpha=al, zorder=5)


def mode_tag(mode, al=1.0):
    col = C.EL if mode == "user" else C.DEEP
    ax.text(80.0, 30.0, "いまのモード： %s"
            % ("ユーザー（できることが限られる）" if mode == "user"
               else "カーネル（何でもできる）"),
            ha="center", va="center", fontsize=16, color=col,
            fontproperties=C.FPB, alpha=al, zorder=6)


def bounce(lo):
    """(位置x, y, 弾かれたか)"""
    cyc = 5.0
    u = (lo % cyc) / cyc
    if u < 0.45:
        return 30.0 + (WALL_X - 4.0 - 30.0) * (u / 0.45), BAD_Y, False
    if u < 0.58:
        return WALL_X - 4.0, BAD_Y, True
    return (WALL_X - 4.0) - (WALL_X - 4.0 - 30.0) * ((u - 0.58) / 0.42), \
        BAD_Y, True


def through(lo):
    """(x, y, モード)"""
    cyc = 8.0
    u = (lo % cyc) / cyc
    my = (DOOR_Y0 + DOOR_Y1) / 2
    if u < 0.30:
        return 30.0 + (WALL_X - 30.0) * (u / 0.30), my, "user"
    if u < 0.45:
        return WALL_X + (116.0 - WALL_X) * ((u - 0.30) / 0.15), my, "kernel"
    if u < 0.65:
        return 116.0, my, "kernel"
    if u < 0.80:
        return 116.0 - (116.0 - WALL_X) * ((u - 0.65) / 0.15), my, "kernel"
    return WALL_X - (WALL_X - 30.0) * ((u - 0.80) / 0.20), my, "user"


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "特権モードとシステムコール",
                     sub="第32回 ── 通れる場所は1か所")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "禁じるのではなく、通り道を1本にする",
                     main2="通った瞬間に、立場が入れ替わる",
                     sub="だからアプリは、頼むことしかできない")
        SC.caption(ax, t)
        return []

    if k == 1:
        rooms("user", al)
        mode_tag("user", al)
        ax.text(80, 22, "アプリは左の部屋から出られない", ha="center",
                va="center", fontsize=20, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "ディスクも画面も、右の部屋の持ち物",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 2:
        x, y, hit = bounce(lo)
        rooms("user", al)
        mode_tag("user", al)
        ax.scatter([x], [y], s=210, c=C.HOT if hit else C.EL, zorder=7,
                   linewidths=0, alpha=al)
        if hit:
            ax.text(WALL_X - 6.0, BAD_Y + 6.0, "弾かれる", ha="right",
                    va="center", fontsize=15, color=C.HOT,
                    fontproperties=C.FPB, alpha=al, zorder=7)
        ax.text(80, 22, "勝手に触りにいくと、そこで止められる", ha="center",
                va="center", fontsize=20, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "止めるのはCPU自身。壁は回路で作られている",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    x, y, mode = through(lo)
    rooms(mode, al)
    mode_tag(mode, al)
    ax.scatter([x], [y], s=210, c=C.DEEP if mode == "kernel" else C.EL,
               zorder=7, linewidths=0, alpha=al)
    ax.text(80, 22, "システムコール ── 頼んで、やってもらう", ha="center",
            va="center", fontsize=21, color=C.OKC, fontproperties=C.FPB,
            alpha=al)
    ax.text(80, 14, "扉をくぐる命令が1つあるだけ。中身はカーネルが決める",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep32_syscall.mp4")
