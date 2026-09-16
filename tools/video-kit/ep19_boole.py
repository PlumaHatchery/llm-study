"""第19回 ブール代数とド・モルガン ── 同じ部品が役を変える。

  NANDを1個だけ置く。配線を変えるだけで NOT → AND → OR が順に出来上がる。
  最後にド・モルガンの式で、なぜそれで足りるのかを回収する。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 32, 47, 60, 70],
    caps=[
        "",                                            # 0 タイトル
        "入力を2本ともつなぐと、NOT になる",             # 1
        "うしろに NOT を足すと、AND になる",             # 2
        "手前に NOT を2つ置くと、OR になる",             # 3
        "AND と OR は、裏返せば行き来できる",             # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

GW, GH = 24.0, 15.0
STEP = 2.4


def inputs(lo, two=True):
    n = int(lo / STEP) % (4 if two else 2)
    if not two:
        return (n % 2, None)
    return ((n >> 1) & 1, n & 1)


def val_col(v):
    return C.DEEP if v else C.EL


def gate(cx, cy, ins, out, al=1.0, lab="NAND"):
    """NANDの箱。入力は左、出力は右"""
    C.rrect(ax, cx - GW / 2, cy - GH / 2, GW, GH, C.FILL, C.EDGE, r=1.4,
            lw=1.4, al=al, z=5)
    ax.text(cx, cy, lab, ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=6)
    ys = [cy + 4.0, cy - 4.0] if len(ins) == 2 else [cy]
    for y, v in zip(ys, ins):
        ax.plot([cx - GW / 2 - 7, cx - GW / 2], [y, y], color=val_col(v),
                lw=2.0, zorder=4, alpha=al)
    ax.plot([cx + GW / 2, cx + GW / 2 + 7], [cy, cy], color=val_col(out),
            lw=2.2, zorder=4, alpha=al)
    return ys


def wirelabel(x, y, v, al=1.0, ha="center", va="bottom"):
    ax.text(x, y, str(v), ha=ha, va=va, fontsize=14, color=val_col(v),
            fontproperties=C.FPB, alpha=al, zorder=7,
            bbox=dict(facecolor=C.BG, edgecolor="none", pad=0.8,
                      alpha=al * 0.9))


def src(x, y, name, v, al=1.0):
    ax.text(x, y, "%s = %d" % (name, v), ha="right", va="center",
            fontsize=15, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=6)


def result(val, name, al=1.0):
    ax.text(142.0, 54.0, "%s\n%d" % (name, val), ha="center", va="center",
            fontsize=21, color=val_col(val), fontproperties=C.FPB,
            alpha=al, zorder=6, linespacing=1.5)


def morgan(lo, al=1.0):
    b = C.ease((lo - 1.5) / 1.2)
    ax.text(80, 66, "NOT（A かつ B）  =  NOT A  または  NOT B",
            ha="center", va="center", fontsize=20, color=C.INK,
            fontproperties=C.FPB, alpha=al, zorder=6)
    ax.text(80, 52, "NOT（A または B）  =  NOT A  かつ  NOT B",
            ha="center", va="center", fontsize=20, color=C.INK,
            fontproperties=C.FPB, alpha=al * b, zorder=6)
    ax.text(80, 38, "かつ と または は、NOT をはさんで入れ替わる",
            ha="center", va="center", fontsize=15, color=C.OKC,
            fontproperties=C.FPB, alpha=al * b, zorder=6)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "ブール代数とド・モルガン",
                     sub="第19回 ── NAND 1種類で足りる")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "部品は1種類でいい",
                     main2="配線を変えるだけで、役が変わる",
                     sub="作りやすい1つを大量に並べる。これが集積回路の前提")
        SC.caption(ax, t)
        return []

    if k == 4:
        morgan(lo, al)
        ax.text(80, 24, "だから NAND だけで全部つくれる", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "NOT・AND・OR が出れば、あとはその組み合わせ",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 1:
        a, _ = inputs(lo, two=False)
        out = 1 - a
        ys = gate(70.0, 54.0, [a, a], out, al)
        ax.plot([51.0, 51.0], [ys[0], ys[1]], color=val_col(a), lw=2.0,
                zorder=4, alpha=al)
        ax.plot([40.0, 51.0], [54.0, 54.0], color=val_col(a), lw=2.0,
                zorder=4, alpha=al)
        src(38.0, 54.0, "A", a, al)
        wirelabel(60.0, ys[0] + 1.5, a, al)
        result(out, "NOT A", al)
        ax.text(80, 24, "1本の入力を、2本に分ける", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "両方に同じ値が入るので、NAND は反転器になる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    a, b = inputs(lo)

    if k == 2:
        m = int(not (a and b))
        out = 1 - m
        g1 = gate(56.0, 54.0, [a, b], m, al)
        src(22.0, g1[0], "A", a, al)
        src(22.0, g1[1], "B", b, al)
        ax.plot([24.0, 56.0 - GW / 2 - 7], [g1[0], g1[0]], color=val_col(a),
                lw=2.0, zorder=4, alpha=al)
        ax.plot([24.0, 56.0 - GW / 2 - 7], [g1[1], g1[1]], color=val_col(b),
                lw=2.0, zorder=4, alpha=al)
        g2 = gate(104.0, 54.0, [m, m], out, al)
        ax.plot([85.0, 85.0], [g2[0], g2[1]], color=val_col(m), lw=2.0,
                zorder=4, alpha=al)
        ax.plot([75.0, 85.0], [54.0, 54.0], color=val_col(m), lw=2.0,
                zorder=4, alpha=al)
        wirelabel(80.0, 56.0, m, al)
        result(out, "A かつ B", al)
        ax.text(80, 24, "NAND のあとに NOT  →  AND", ha="center",
                va="center", fontsize=24, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "2個目の NAND が、さっきの反転器そのもの",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    na, nb = 1 - a, 1 - b
    out = int(a or b)
    ga = gate(52.0, 70.0, [a, a], na, al)
    gb = gate(52.0, 38.0, [b, b], nb, al)
    for g, v, y0 in ((ga, a, 70.0), (gb, b, 38.0)):
        ax.plot([33.0, 33.0], [g[0], g[1]], color=val_col(v), lw=2.0,
                zorder=4, alpha=al)
        ax.plot([26.0, 33.0], [y0, y0], color=val_col(v), lw=2.0, zorder=4,
                alpha=al)
    src(24.0, 70.0, "A", a, al)
    src(24.0, 38.0, "B", b, al)
    g3 = gate(104.0, 54.0, [na, nb], out, al)
    ax.plot([64.0, 73.0, 73.0], [70.0, 70.0, g3[0]], color=val_col(na),
            lw=2.0, zorder=4, alpha=al)
    ax.plot([73.0, 104.0 - GW / 2 - 7], [g3[0], g3[0]], color=val_col(na),
            lw=2.0, zorder=4, alpha=al)
    ax.plot([64.0, 73.0, 73.0], [38.0, 38.0, g3[1]], color=val_col(nb),
            lw=2.0, zorder=4, alpha=al)
    ax.plot([73.0, 104.0 - GW / 2 - 7], [g3[1], g3[1]], color=val_col(nb),
            lw=2.0, zorder=4, alpha=al)
    wirelabel(68.0, 71.5, na, al)
    wirelabel(68.0, 39.5, nb, al)
    result(out, "A または B", al)
    ax.text(80, 24, "先に両方を裏返してから NAND  →  OR", ha="center",
            va="center", fontsize=22, color=C.INK, fontproperties=C.FPB,
            alpha=al)
    ax.text(80, 15, "同じ NAND が3個。つないだ形が違うだけ", ha="center",
            va="center", fontsize=15, color=C.MUTED, fontproperties=C.FP,
            alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep19_boole.mp4")
