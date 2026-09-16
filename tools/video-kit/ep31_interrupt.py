"""第31回 割り込み ── OSが成立する前提条件。

  CPUが仕事中に、外から札が上がる。今の状態を棚に預け、ハンドラへ飛び、
  終わって棚から戻す。これがないと、OSはCPUを取り戻せない。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 40, 54, 64],
    caps=[
        "",                                            # 0 タイトル
        "CPU は、言われた順に進んでいるだけ",            # 1
        "外から札が上がると、いったん預けて飛ぶ",         # 2
        "これがないと、OS は CPU を取り戻せない",         # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

CPU_X, CPU_Y, CPU_W, CPU_H = 58.0, 56.0, 46.0, 20.0
DEV_X, DEV_Y = 20.0, 78.0
SH_X, SH_Y, SH_W, SH_H = 116.0, 56.0, 32.0, 26.0
PHASE = [0.0, 3.0, 5.5, 9.0, 14.0, 16.5, 20.0]
LABELS = ["ふつうに実行中", "札が上がった", "いまの状態を棚へ",
          "ハンドラを実行中", "棚から戻す", "続きから再開"]


def phase_of(lo):
    for j in range(len(PHASE) - 1):
        if PHASE[j] <= lo < PHASE[j + 1]:
            return j, (lo - PHASE[j]) / (PHASE[j + 1] - PHASE[j])
    return 5, 1.0


def cpu_box(ph, al=1.0):
    handling = ph == 3
    C.rrect(ax, CPU_X - CPU_W / 2, CPU_Y - CPU_H / 2, CPU_W, CPU_H,
            C.FILL, C.HOT if handling else C.EDGE, r=1.4,
            lw=1.8 if handling else 1.3, al=al, z=4)
    ax.text(CPU_X, CPU_Y + 5.5, "CPU", ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(CPU_X, CPU_Y - 2.5,
            "割り込みハンドラ" if handling else "ユーザーの計算",
            ha="center", va="center", fontsize=15,
            color=C.HOT if handling else C.INK, fontproperties=C.FPB,
            alpha=al, zorder=5)


def device(ph, al=1.0):
    raised = ph >= 1
    C.rrect(ax, DEV_X - 13.0, DEV_Y - 6.0, 26.0, 12.0, C.FILL, C.EDGE,
            r=1.2, lw=1.2, al=al, z=4)
    ax.text(DEV_X, DEV_Y, "キーボード", ha="center", va="center",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    if raised and ph <= 3:
        ax.annotate("", xy=(CPU_X - CPU_W / 2 - 1, CPU_Y + 6.0),
                    xytext=(DEV_X + 13.0, DEV_Y - 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.4,
                                    alpha=al), zorder=6)
        ax.text(DEV_X + 20.0, DEV_Y + 3.0, "札", ha="left", va="center",
                fontsize=15, color=C.HOT, fontproperties=C.FPB, alpha=al,
                zorder=6)


def shelf(ph, u, al=1.0):
    C.rrect(ax, SH_X - SH_W / 2, SH_Y - SH_H / 2, SH_W, SH_H, C.BG, C.EDGE,
            r=1.2, lw=1.2, al=al, z=3)
    ax.text(SH_X, SH_Y + SH_H / 2 + 3.5, "棚（スタック）", ha="center",
            va="bottom", fontsize=13, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)
    stored = ph in (3,) or (ph == 2 and u > 0.6) or (ph == 4 and u < 0.4)
    if stored:
        C.rrect(ax, SH_X - SH_W / 2 + 3, SH_Y - 4.0, SH_W - 6, 8.0,
                C.FILL, C.OKC, r=1.0, lw=1.4, al=al, z=5)
        ax.text(SH_X, SH_Y, "さっきの状態", ha="center", va="center",
                fontsize=12, color=C.OKC, fontproperties=C.FPB, alpha=al,
                zorder=6)
    if ph in (2, 4):
        a, b = (CPU_X + CPU_W / 2, SH_X - SH_W / 2)
        x = a + (b - a) * (C.ease(u) if ph == 2 else 1 - C.ease(u))
        ax.scatter([x], [CPU_Y], s=170, c=C.OKC, zorder=7, linewidths=0,
                   alpha=al)
        ax.annotate("", xy=(b if ph == 2 else a, CPU_Y - 9.0),
                    xytext=(a if ph == 2 else b, CPU_Y - 9.0),
                    arrowprops=dict(arrowstyle="-|>", color=C.OKC, lw=1.8,
                                    alpha=al * 0.8), zorder=5)


def compare(al=1.0):
    rows = [("割り込みがない", "止まるまで、ずっとそのプログラムのもの",
             C.HOT, 0.98),
            ("割り込みがある", "時計の札で、いつでも取り戻せる", C.OKC, 0.42)]
    for j, (name, note, col, frac) in enumerate(rows):
        y = 66.0 - j * 22.0
        ax.text(26.0, y + 6.0, name, ha="left", va="center", fontsize=16,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)
        C.rrect(ax, 26.0, y - 5.0, 108.0, 8.0, "#EFEDE5", "#D3D1C7", r=1.0,
                lw=0.8, al=al, z=3)
        C.rrect(ax, 26.0, y - 5.0, 108.0 * frac, 8.0, col, "none", r=1.0,
                al=al * 0.9, z=4)
        ax.text(26.0, y - 9.5, note, ha="left", va="top", fontsize=13,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(80.0, 34.0, "横棒は、1つのプログラムがCPUを握っている時間",
            ha="center", va="center", fontsize=13, color=C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "割り込み",
                     sub="第31回 ── 外から声をかける仕組み")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "順番どおりに進むだけの機械が、",
                     main2="外の都合で中断できるようになった",
                     sub="ここから先のOSは、全部この上に建っている")
        SC.caption(ax, t)
        return []

    if k == 3:
        compare(al)
        ax.text(80, 22, "CPU を取り上げられること", ha="center", va="center",
                fontsize=24, color=C.INK, fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "それが、OS が「管理者」でいられる唯一の根拠",
                ha="center", va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    ph, u = (0, 0.0) if k == 1 else phase_of(lo)
    cpu_box(ph, al)
    device(ph, al)
    shelf(ph, u, al)
    ax.text(80.0, 30.0, LABELS[ph], ha="center", va="center", fontsize=20,
            color=C.HOT if ph in (1, 2, 3) else C.INK, fontproperties=C.FPB,
            alpha=al, zorder=5)
    ax.text(80.0, 21.0,
            "戻ってきたとき、中断したことに気づかない" if ph >= 4
            else "預けるのは、レジスタと PC。あとで元どおりにするため",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=5)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep31_interrupt.mp4")
