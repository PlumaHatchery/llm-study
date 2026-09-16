"""第18回 CMOSとNOT・NAND・NOR ── 役が固定されている。

  pMOSを上、nMOSを下に積むと、出力は必ず反転する。
  下段を直列に組み替えるとNAND、並列だとNOR。
  素直なANDが作れないのは、pが1を伝える担当、nが0を伝える担当だから。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 34, 49, 62, 72],
    caps=[
        "",                                            # 0 タイトル
        "上と下で、必ずどちらか片方だけが開く",           # 1
        "下を直列にすると NAND",                        # 2
        "下を並列にすると NOR",                         # 3
        "役が決まっているから、出力は必ず裏返る",         # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

VDD_Y, GND_Y, OUT_Y = 80.0, 32.0, 56.0
CXm = 50.0
MW, MH = 15.0, 6.5
P_UP, P_LO = 69.0, 60.0          # 直列のときの上段/下段
N_UP, N_LO = 44.5, 35.0
PAR_L, PAR_R = 36.0, 64.0        # 並列のときの左右
RAIL_L, RAIL_R = 24.0, 78.0
OUT_END = 86.0
TBL_X = 114.0                    # 真理値表の左端
STEP = 2.6                       # 入力の切り替え周期(秒)


def inputs(lo, two=True):
    n = int(lo / STEP) % (4 if two else 2)
    if not two:
        return (n % 2, None)
    return ((n >> 1) & 1, n & 1)


def rail(y, lab, al=1.0):
    ax.plot([RAIL_L, RAIL_R], [y, y], color=C.GRAY, lw=2.6,
            solid_capstyle="round", zorder=2, alpha=al)
    ax.text(RAIL_L - 2.0, y, lab, ha="right", va="center", fontsize=13,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)


def mos(cx, cy, kind, on, lab, al=1.0):
    col = C.OKC if on else C.EDGE
    C.rrect(ax, cx - MW / 2, cy - MH / 2, MW, MH,
            C.FILL if on else C.BG, col, r=0.9, lw=1.6, al=al, z=5)
    ax.text(cx, cy, ("p" if kind == "p" else "n") + lab, ha="center",
            va="center", fontsize=13, color=col if on else C.MUTED,
            fontproperties=C.FPB, alpha=al, zorder=6)
    # 開閉は箱の横に出す。上に置くと縦の配線と重なる
    ax.text(cx + MW / 2 + 1.5, cy, "開" if on else "閉", ha="left",
            va="center", fontsize=11, color=col if on else C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=6)


def vline(x, y0, y1, live, al=1.0):
    ax.plot([x, x], [y0, y1], color=C.OKC if live else C.GRAY,
            lw=2.8 if live else 2.0, solid_capstyle="round", zorder=3,
            alpha=al)


def out_node(val, al=1.0):
    ax.plot([CXm, OUT_END], [OUT_Y, OUT_Y], color=C.GRAY, lw=2.2, zorder=3,
            alpha=al)
    ax.scatter([CXm], [OUT_Y], s=60, c=C.GRAY, zorder=4, linewidths=0,
               alpha=al)
    ax.text(OUT_END + 2.0, OUT_Y, "出力 %d" % val, ha="left", va="center",
            fontsize=19, color=C.DEEP if val else C.EL,
            fontproperties=C.FPB, alpha=al, zorder=6)


def gate_in(items, al=1.0):
    """入力の値は左上にまとめて出す。どの箱が誰かは pA / nA の名前で分かる"""
    for j, (name, val) in enumerate(items):
        ax.text(10.0, 72.0 - j * 7.0, "%s = %d" % (name, val), ha="left",
                va="center", fontsize=16, color=C.INK, fontproperties=C.FPB,
                alpha=al, zorder=5)


def truth(kind, a, b, al=1.0):
    x0, y0 = TBL_X, 74.0
    cols = [(x0, "A"), (x0 + 11, "B"), (x0 + 27, "出力")]
    for x, lab in cols:
        ax.text(x, y0, lab, ha="center", va="center", fontsize=13,
                color=C.MUTED, fontproperties=C.FPB, alpha=al, zorder=5)
    rows = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for j, (ra, rb) in enumerate(rows):
        y = y0 - 6.5 - j * 6.5
        o = int(not (ra and rb)) if kind == "nand" else int(not (ra or rb))
        here = (ra == a and rb == b)
        if here:
            C.rrect(ax, x0 - 7, y - 3.0, 45, 6.0, C.FILL, C.OKC, r=0.7,
                    lw=1.2, al=al, z=3)
        for x, v in ((cols[0][0], ra), (cols[1][0], rb), (cols[2][0], o)):
            ax.text(x, y, str(v), ha="center", va="center", fontsize=14,
                    color=C.INK if here else C.MUTED,
                    fontproperties=C.FPB, alpha=al, zorder=5)


def roles(al=1.0):
    """なぜ素直なANDが作れないのか"""
    for x, kind, good, bad, col in ((50.0, "pMOS（上段）", "1 を伝える",
                                     "0 は伝えきれない", C.DEEP),
                                    (110.0, "nMOS（下段）", "0 を伝える",
                                     "1 は伝えきれない", C.EL)):
        C.rrect(ax, x - 30, 46.0, 60, 26, C.BG, col, r=1.4, lw=1.5, al=al,
                z=3)
        ax.text(x, 66.5, kind, ha="center", va="center", fontsize=16,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(x, 58.0, "得意：" + good, ha="center", va="center",
                fontsize=14, color=C.INK, fontproperties=C.FPB, alpha=al,
                zorder=5)
        ax.text(x, 51.0, "苦手：" + bad, ha="center", va="center",
                fontsize=13, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
    ax.text(80, 38.0, "上は1側、下は0側。役が入れ替われない",
            ha="center", va="center", fontsize=15, color=C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "CMOSとNOT・NAND・NOR",
                     sub="第18回 ── 上はp、下はn")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "作れるのは、必ず裏返るものだけ",
                     main2="AND は NAND のうしろに NOT を足して作る",
                     sub="部品の都合が、論理の形を決めている")
        SC.caption(ax, t)
        return []

    if k == 4:
        roles(al)
        ax.text(80, 24, "だから素直な AND は作れない", ha="center",
                va="center", fontsize=25, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "CMOSの基本形は、NAND と NOR。どちらも反転つき",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    rail(VDD_Y, "電源", al)
    rail(GND_Y, "地面", al)

    if k == 1:
        a, _ = inputs(lo, two=False)
        p_on, n_on = (a == 0), (a == 1)
        out = 1 - a
        mos(CXm, P_LO + 4.5, "p", p_on, "MOS", al)
        mos(CXm, N_UP - 0.5, "n", n_on, "MOS", al)
        vline(CXm, P_LO + 4.5 + MH / 2, VDD_Y, p_on, al)
        vline(CXm, OUT_Y, P_LO + 4.5 - MH / 2, p_on, al)
        vline(CXm, N_UP - 0.5 + MH / 2, OUT_Y, n_on, al)
        vline(CXm, GND_Y, N_UP - 0.5 - MH / 2, n_on, al)
        gate_in([("入力", a)], al)
        out_node(out, al)
        ax.text(80, 24, "入力 %d  →  出力 %d" % (a, out), ha="center",
                va="center", fontsize=26, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "上が開けば1につながり、下が開けば0につながる",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    a, b = inputs(lo)
    nand = (k == 2)
    out = int(not (a and b)) if nand else int(not (a or b))

    if nand:
        # 上は並列、下は直列
        for cx, v, lab in ((PAR_L, a, "A"), (PAR_R, b, "B")):
            mos(cx, P_LO, "p", v == 0, lab, al)
            vline(cx, P_LO + MH / 2, VDD_Y, v == 0, al)
            vline(cx, OUT_Y, P_LO - MH / 2, v == 0, al)
        ax.plot([PAR_L, PAR_R], [OUT_Y, OUT_Y], color=C.GRAY, lw=2.2,
                zorder=3, alpha=al)
        mos(CXm, N_UP, "n", a == 1, "A", al)
        mos(CXm, N_LO, "n", b == 1, "B", al)
        vline(CXm, N_UP + MH / 2, OUT_Y, a == 1, al)
        vline(CXm, N_LO + MH / 2, N_UP - MH / 2, a == 1 and b == 1, al)
        vline(CXm, GND_Y, N_LO - MH / 2, a == 1 and b == 1, al)
        gate_in([("A", a), ("B", b)], al)
    else:
        # 上は直列、下は並列
        mos(CXm, P_UP, "p", a == 0, "A", al)
        mos(CXm, P_LO, "p", b == 0, "B", al)
        vline(CXm, P_UP + MH / 2, VDD_Y, a == 0, al)
        vline(CXm, P_LO + MH / 2, P_UP - MH / 2, a == 0 and b == 0, al)
        vline(CXm, OUT_Y, P_LO - MH / 2, a == 0 and b == 0, al)
        for cx, v, lab in ((PAR_L, a, "A"), (PAR_R, b, "B")):
            mos(cx, N_UP, "n", v == 1, lab, al)
            vline(cx, N_UP + MH / 2, OUT_Y, v == 1, al)
            vline(cx, GND_Y, N_UP - MH / 2, v == 1, al)
        ax.plot([PAR_L, PAR_R], [OUT_Y, OUT_Y], color=C.GRAY, lw=2.2,
                zorder=3, alpha=al)
        gate_in([("A", a), ("B", b)], al)

    out_node(out, al)
    truth("nand" if nand else "nor", a, b, al)
    ax.text(80, 13.0, "NAND ── どちらも1のときだけ0" if nand
            else "NOR ── どちらも0のときだけ1",
            ha="center", va="center", fontsize=20, color=C.INK,
            fontproperties=C.FPB, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep18_cmos.mp4")
