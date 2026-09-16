"""第25回 ALUとバス ── 全部計算して、1つだけ選ぶ。

  加算器と論理回路を束ね、セレクタで「どの結果を出すか」を選ぶ。
  バスは1本の共用道路で、時刻をずらして使い分けている。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 34, 50, 61],
    caps=[
        "",                                            # 0 タイトル
        "4つとも、いつも同時に計算している",             # 1
        "選ぶのは、出口のセレクタだけ",                  # 2
        "行き先は1本の道。時間で分け合う",               # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

OPS = ["＋（加算）", "AND", "OR", "XOR"]
OP_Y = [72.0, 62.0, 52.0, 42.0]
OP_X, OP_W, OP_H = 66.0, 34.0, 8.0
SEL_X = 104.0
A_VAL, B_VAL = 12, 10
STEP = 3.0

BUS_Y = 52.0
BUS_X0, BUS_X1 = 20.0, 146.0
DEVS = [(38.0, "レジスタ"), (68.0, "ALU"), (98.0, "メモリ"), (128.0, "入出力")]


def results():
    return [A_VAL + B_VAL, A_VAL & B_VAL, A_VAL | B_VAL, A_VAL ^ B_VAL]


def alu(sel, al=1.0, show_sel=True):
    res = results()
    for j, (name, y) in enumerate(zip(OPS, OP_Y)):
        on = (j == sel) and show_sel
        C.rrect(ax, OP_X - OP_W / 2, y - OP_H / 2, OP_W, OP_H,
                C.FILL if on else C.BG, C.OKC if on else C.EDGE, r=1.0,
                lw=1.7 if on else 1.2, al=al, z=4)
        ax.text(OP_X - OP_W / 2 + 3.0, y, name, ha="left", va="center",
                fontsize=13, color=C.OKC if on else C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(OP_X + OP_W / 2 - 3.0, y, str(res[j]), ha="right",
                va="center", fontsize=14,
                color=C.INK if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.plot([OP_X + OP_W / 2, SEL_X - 6.0], [y, y],
                color=C.OKC if on else C.GRAY, lw=2.2 if on else 1.2,
                zorder=3, alpha=al)
        for xx in (OP_X - OP_W / 2 - 8.0,):
            ax.plot([xx, OP_X - OP_W / 2], [y, y], color=C.GRAY, lw=1.2,
                    zorder=3, alpha=al * 0.9)
    ax.plot([38.0, 38.0], [OP_Y[-1], OP_Y[0]], color=C.GRAY, lw=1.6,
            zorder=3, alpha=al)
    ax.plot([38.0, OP_X - OP_W / 2 - 8.0], [OP_Y[-1], OP_Y[-1]],
            color=C.GRAY, lw=0.1, zorder=3, alpha=0)
    ax.text(30.0, 64.0, "A = %d" % A_VAL, ha="right", va="center",
            fontsize=16, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text(30.0, 56.0, "B = %d" % B_VAL, ha="right", va="center",
            fontsize=16, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.plot([32.0, 38.0], [64.0, 64.0], color=C.GRAY, lw=1.4, zorder=3,
            alpha=al)
    ax.plot([32.0, 38.0], [56.0, 56.0], color=C.GRAY, lw=1.4, zorder=3,
            alpha=al)
    # セレクタ(台形)
    ax.fill([SEL_X - 6, SEL_X - 6, SEL_X + 6, SEL_X + 6],
            [OP_Y[0] + 4, OP_Y[-1] - 4, OP_Y[-1] + 9, OP_Y[0] - 9],
            color=C.FILL, edgecolor=C.EDGE, lw=1.4, zorder=5, alpha=al)
    ax.text(SEL_X, 57.0, "選ぶ", ha="center", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=6)
    if show_sel:
        ax.plot([SEL_X + 6, 130.0], [57.0, 57.0], color=C.OKC, lw=2.4,
                zorder=4, alpha=al)
        ax.text(132.0, 57.0, "%d" % res[sel], ha="left", va="center",
                fontsize=22, color=C.OKC, fontproperties=C.FPB, alpha=al,
                zorder=6)
        ax.text(SEL_X, 31.0, "演算コード：%s" % OPS[sel].split("（")[0],
                ha="center", va="center", fontsize=14, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=6)
        ax.plot([SEL_X, SEL_X], [34.0, 47.0], color=C.HOT,
                lw=1.4, ls=(0, (4, 3)), zorder=6, alpha=al)


def bus(lo, al=1.0):
    ax.plot([BUS_X0, BUS_X1], [BUS_Y, BUS_Y], color=C.GRAY, lw=4.0,
            solid_capstyle="round", zorder=3, alpha=al)
    ax.text(BUS_X0 - 2.0, BUS_Y, "バス", ha="right", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    slot = int(max(lo - 0.8, 0) / 2.4)
    src_i = slot % len(DEVS)
    dst_i = (src_i + 2) % len(DEVS)
    for j, (x, name) in enumerate(DEVS):
        role = "出す" if j == src_i else ("受ける" if j == dst_i else "休み")
        act = j in (src_i, dst_i)
        col = C.HOT if j == src_i else (C.OKC if j == dst_i else C.EDGE)
        C.rrect(ax, x - 15.0, 62.0, 30.0, 14.0, C.FILL if act else C.BG,
                col, r=1.2, lw=1.6 if act else 1.2, al=al, z=4)
        ax.text(x, 71.0, name, ha="center", va="center", fontsize=14,
                color=C.INK if act else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.text(x, 65.5, role, ha="center", va="center", fontsize=12,
                color=col if act else C.MUTED, fontproperties=C.FP,
                alpha=al, zorder=5)
        ax.plot([x, x], [BUS_Y, 62.0], color=col if act else C.GRAY,
                lw=2.2 if act else 1.2, zorder=3, alpha=al)
    # 道の上を進む荷物
    u = (max(lo - 0.8, 0) % 2.4) / 2.4
    sx, dx = DEVS[src_i][0], DEVS[dst_i][0]
    px = sx + (dx - sx) * C.ease(min(u / 0.75, 1.0))
    ax.scatter([px], [BUS_Y], s=190, c=C.HOT, zorder=7, linewidths=0,
               alpha=al)
    ax.text(80.0, 38.0, "いまは %s → %s。ほかは黙って待つ"
            % (DEVS[src_i][1], DEVS[dst_i][1]), ha="center", va="center",
            fontsize=15, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "ALUとバス",
                     sub="第25回 ── 計算する所と、運ぶ道")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "全部やって、1つだけ採る",
                     main2="道は1本で足りる。同時に使わなければいい",
                     sub="あとは「いつ何を選ぶか」を決める係がいればいい")
        SC.caption(ax, t)
        return []

    if k == 3:
        bus(lo, al)
        ax.text(80, 24, "配線を減らすかわりに、時間で順番を決める",
                ha="center", va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "2つが同時に出すと壊れる。だから交通整理がいる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    sel = int(max(lo - 1.0, 0) / STEP) % 4
    alu(sel, al, show_sel=(k == 2 or lo > 4.0))

    if k == 1:
        ax.text(80, 24, "止めておくより、やらせておくほうが速い",
                ha="center", va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "どれが要るか決まる前から、答えは出そろっている",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "コードを変えるだけで、出てくる答えが変わる",
                ha="center", va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "この数個のコードが、次回の「命令」になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep25_alu_bus.mp4")
