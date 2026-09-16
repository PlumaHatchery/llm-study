"""第24回 ステートマシン ── 制御回路の原型。

  信号機で。状態を丸、遷移を矢印。
  それを「現在状態を持つレジスタ」＋「次状態を決める論理回路」の
  2ブロックに還元する。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 20, 35, 51, 61],
    caps=[
        "",                                            # 0 タイトル
        "信号機は、3つの状態を順にめぐっている",         # 1
        "状態を丸、移り変わりを矢印で描き直す",           # 2
        "中身は、この2つの箱だけ",                      # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

NAMES = ["赤", "青", "黄"]
COLS = [C.DEEP, C.OKC, C.HOT]
DUR = [3.6, 3.6, 1.6]
CYCLE = sum(DUR)

LAMP_X, LAMP_Y0, LAMP_R = 28.0, 66.0, 5.2
# 黄の丸が数式の行(y=24)に届かないよう、全体を上へ寄せてある
NODE = [(72.0, 73.0), (120.0, 58.0), (86.0, 42.0)]
NODE_R = 9.0


def st(lo):
    u = lo % CYCLE
    acc = 0.0
    for j, d in enumerate(DUR):
        acc += d
        if u < acc:
            return j, (acc - u)
    return 2, 0.0


def lamps(s, al=1.0):
    C.rrect(ax, LAMP_X - 9.0, LAMP_Y0 - 30.0, 18.0, 38.0, C.FILL, C.EDGE,
            r=1.6, lw=1.4, al=al, z=3)
    for j in range(3):
        y = LAMP_Y0 - 3.0 - j * 11.0
        on = (j == s)
        ax.scatter([LAMP_X], [y], s=520, c=COLS[j] if on else C.BG,
                   edgecolors=COLS[j] if on else C.EDGE,
                   linewidths=1.4, zorder=5, alpha=al)
    ax.text(LAMP_X, LAMP_Y0 + 12.0, "信号機", ha="center", va="center",
            fontsize=14, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def graph(s, al=1.0):
    th = np.linspace(0, 2 * np.pi, 80)
    for j, (x, y) in enumerate(NODE):
        on = (j == s)
        ax.plot(x + NODE_R * np.cos(th), y + NODE_R * np.sin(th),
                color=COLS[j] if on else C.GRAY, lw=2.4 if on else 1.4,
                zorder=5, alpha=al)
        if on:
            ax.scatter([x], [y], s=1050, c=C.FILL, zorder=4, linewidths=0,
                       alpha=al * 0.8)
        ax.text(x, y, NAMES[j], ha="center", va="center", fontsize=17,
                color=COLS[j] if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=6)
    for j in range(3):
        x0, y0 = NODE[j]
        x1, y1 = NODE[(j + 1) % 3]
        d = np.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / d, (y1 - y0) / d
        live = (j == s)
        ax.annotate("", xy=(x1 - ux * (NODE_R + 1.5),
                            y1 - uy * (NODE_R + 1.5)),
                    xytext=(x0 + ux * (NODE_R + 1.5),
                            y0 + uy * (NODE_R + 1.5)),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=C.HOT if live else C.GRAY,
                                    lw=2.2 if live else 1.4, alpha=al),
                    zorder=4)


def blocks(lo, al=1.0):
    b = C.ease((lo - 2.0) / 1.5)
    C.rrect(ax, 22.0, 48.0, 44.0, 20.0, C.FILL, C.EDGE, r=1.4, lw=1.5,
            al=al, z=4)
    ax.text(44.0, 61.0, "状態レジスタ", ha="center", va="center",
            fontsize=15, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.text(44.0, 53.5, "いまどれかを覚える", ha="center", va="center",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    C.rrect(ax, 94.0, 48.0, 48.0, 20.0, C.FILL, C.OKC, r=1.4, lw=1.5,
            al=al * b, z=4)
    ax.text(118.0, 61.0, "次の状態を決める論理", ha="center", va="center",
            fontsize=15, color=C.OKC, fontproperties=C.FPB, alpha=al * b,
            zorder=5)
    ax.text(118.0, 53.5, "第18回までの組み合わせ回路", ha="center",
            va="center", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al * b, zorder=5)
    ax.annotate("", xy=(92.0, 62.0), xytext=(68.0, 62.0),
                arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=2.2,
                                alpha=al), zorder=6)
    ax.text(80.0, 64.5, "いまの状態", ha="center", va="bottom", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=6)
    ax.plot([142.0, 150.0, 150.0, 14.0, 14.0, 22.0],
            [58.0, 58.0, 40.0, 40.0, 58.0, 58.0], color=C.HOT, lw=2.0,
            zorder=3, alpha=al * b)
    ax.text(82.0, 37.5, "次の状態を書き戻す（クロックの立ち上がりで）",
            ha="center", va="center", fontsize=13, color=C.HOT,
            fontproperties=C.FPB, alpha=al * b, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "ステートマシン",
                     sub="第24回 ── 制御回路の原型")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "覚える箱と、決める回路",
                     main2="制御と名のつくものは、だいたいこの形",
                     sub="第27回のCPUの制御部も、大きくしただけの同じもの")
        SC.caption(ax, t)
        return []

    if k == 3:
        blocks(lo, al)
        ax.text(80, 24, "状態は22回、論理は18回で作った", ha="center",
                va="center", fontsize=23, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "新しい部品は1つもない。つなぎ方が新しいだけ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    s, left = st(lo)
    lamps(s, al)
    if k == 2:
        graph(s, al)
        ax.text(80, 24, "丸が状態、矢印が移り変わり", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "信号機でも自動販売機でも、描けば同じ形になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(95.0, 58.0, NAMES[s], ha="center", va="center", fontsize=44,
                color=COLS[s], fontproperties=C.FPB, alpha=al, zorder=6)
        ax.text(95.0, 44.0, "あと %.1f 秒" % left, ha="center", va="center",
                fontsize=16, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=6)
        ax.text(80, 24, "次に何になるかは、いま何であるかで決まる",
                ha="center", va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "青の次は必ず黄。順番そのものが仕様になっている",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep24_state.mp4")
