"""第34回 仮想メモリとMMU ── OSの嘘の作り方。

  各プロセスが「0番地から自分のもの」と思っている地図と、実際の物理メモリを
  並べ、MMUが間で住所を書き換えている様子。

  仮想側は縦に積む。横に並べると、片方の配線がもう片方の箱を貫く。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 35, 51, 61],
    caps=[
        "",                                            # 0 タイトル
        "どちらのプロセスも「0番地から」持っている",      # 1
        "あいだで、住所が書き換えられている",             # 2
        "同じ 0番地 が、別の場所を指している",            # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

VX, VW, PH = 14.0, 30.0, 7.0
AY = [74.0, 65.0]                    # プロセスA の仮想ページ
BY = [50.0, 41.0]                    # プロセスB の仮想ページ
PY = [74.0, 62.0, 50.0, 38.0]        # 物理フレーム
MX0, MX1 = 62.0, 92.0
PX, PW = 104.0, 38.0
MAP_A = [2, 0]
MAP_B = [3, 1]
COL_A, COL_B = C.EL, C.DEEP


def page_box(y, lab, col, al=1.0, on=False):
    C.rrect(ax, VX, y - PH / 2, VW, PH, C.FILL if on else C.BG,
            col if on else C.EDGE, r=0.9, lw=1.8 if on else 1.1, al=al, z=4)
    ax.text(VX + VW / 2, y, lab, ha="center", va="center", fontsize=13,
            color=col if on else C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=5)


def virtual(sel_a, sel_b, al=1.0):
    for ys, col, name, sel in ((AY, COL_A, "プロセスA", sel_a),
                               (BY, COL_B, "プロセスB", sel_b)):
        ax.text(VX + VW / 2, ys[0] + 6.5, name, ha="center", va="bottom",
                fontsize=14, color=col, fontproperties=C.FPB, alpha=al,
                zorder=5)
        for j, y in enumerate(ys):
            page_box(y, "%d番地" % j, col, al, on=(j == sel))


def frames(hi, al=1.0):
    ax.text(PX + PW / 2, PY[0] + 6.5, "物理メモリ（本物）", ha="center",
            va="bottom", fontsize=14, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)
    for j, y in enumerate(PY):
        if j in MAP_A:
            owner = ("A", COL_A, MAP_A.index(j))
        elif j in MAP_B:
            owner = ("B", COL_B, MAP_B.index(j))
        else:
            owner = None
        on = (hi is not None and j == hi)
        col = owner[1] if owner else C.EDGE
        C.rrect(ax, PX, y - PH / 2, PW, PH, C.FILL if on else C.BG,
                col, r=0.9, lw=1.8 if on else 1.1, al=al, z=4)
        ax.text(PX - 2.5, y, str(j), ha="right", va="center", fontsize=12,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
        if owner:
            ax.text(PX + PW / 2, y, "%s の %d番地" % (owner[0], owner[2]),
                    ha="center", va="center", fontsize=12, color=owner[1],
                    fontproperties=C.FPB, alpha=al * (1.0 if on else 0.75),
                    zorder=5)


def mmu(al=1.0, note=None):
    C.rrect(ax, MX0, 34.0, MX1 - MX0, 44.0, C.FILL, C.EDGE, r=1.4, lw=1.4,
            al=al, z=3)
    ax.text((MX0 + MX1) / 2, 74.0, "MMU", ha="center", va="center",
            fontsize=16, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text((MX0 + MX1) / 2, 68.0, "住所の読み替え表", ha="center",
            va="center", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)
    if note:
        ax.text((MX0 + MX1) / 2, 39.0, note, ha="center", va="center",
                fontsize=13, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=5, linespacing=1.5)


def link(vy, pf, col, al=1.0, lw=1.4):
    py = PY[pf]
    ax.plot([VX + VW, MX0], [vy, vy], color=col, lw=lw, zorder=3, alpha=al)
    ax.plot([MX1, PX], [py, py], color=col, lw=lw, zorder=3, alpha=al)
    ax.plot([MX0 + 1.0, MX1 - 1.0], [vy, py], color=col, lw=lw,
            ls=(0, (3, 2)), zorder=6, alpha=al * 0.9)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "仮想メモリとMMU",
                     sub="第34回 ── 全員に同じ嘘をつく")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "どのプロセスも、0番地から始まると思っている",
                     main2="本当の置き場所は、OS と MMU しか知らない",
                     sub="他人の領分に手が届かないのも、この嘘のおかげ")
        SC.caption(ax, t)
        return []

    if k == 1:
        virtual(None, None, al)
        frames(None, al)
        ax.text(80, 22, "同じ番地を、両方が使っている", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "ぶつからないのか？ ── 本当は同じ場所ではない",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 2:
        n = int(max(lo - 1.0, 0) / 2.6) % 4
        who = "A" if n < 2 else "B"
        j = n % 2
        vy = (AY if who == "A" else BY)[j]
        pf = (MAP_A if who == "A" else MAP_B)[j]
        col = COL_A if who == "A" else COL_B
        virtual(j if who == "A" else None, j if who == "B" else None, al)
        mmu(al, "%s の %d番地\n↓\n物理 %d番" % (who, j, pf))
        frames(pf, al)
        for ys, mp, c in ((AY, MAP_A, COL_A), (BY, MAP_B, COL_B)):
            for jj, yy in enumerate(ys):
                hot = (yy == vy)
                link(yy, mp[jj], c, al * (1.0 if hot else 0.28),
                     2.4 if hot else 1.2)
        ax.text(80, 22, "ページごとに、行き先が決めてある", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "並び順はばらばらでいい。表さえあれば引ける",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    virtual(0, 0, al)
    mmu(al, "同じ 0番地 でも\n行き先が違う")
    frames(None, al)
    link(AY[0], MAP_A[0], COL_A, al, 2.4)
    link(BY[0], MAP_B[0], COL_B, al, 2.4)
    ax.text(80, 22, "A の0番地は物理2番、B の0番地は物理3番", ha="center",
            va="center", fontsize=20, color=C.OKC, fontproperties=C.FPB,
            alpha=al)
    ax.text(80, 14, "表を差し替えれば、置き場所はいつでも変えられる",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep34_virtual.mp4")
