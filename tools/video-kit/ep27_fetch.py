"""第27回 フェッチ・デコード・実行 ── ここで「動いて」見える。

  1命令の一巡をクロックに同期させてコマ送り。
  PC → メモリ → 命令レジスタ → デコード → ALU → 書き戻し → PC+1。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 26, 48, 58],
    caps=[
        "",                                            # 0 タイトル
        "1つの命令が、6つの段を順に通る",                # 1
        "終わったらまた先頭へ。ぐるぐる回る",             # 2
        "",                                            # 3 まとめ
    ],
)

fig, ax = C.new_axes()

STAGES = ["PC が番地を出す", "メモリを読む", "命令レジスタへ",
          "デコード", "ALU で計算", "書き戻して PC+1"]
POS = [(32.0, 68.0), (80.0, 68.0), (128.0, 68.0),
       (128.0, 48.0), (80.0, 48.0), (32.0, 48.0)]
SW, SH = 40.0, 13.0

# 第26回と同じ、この動画かぎりの命令列
PROG = [("00111100", "A に 60 を入れる", 60),
        ("00000101", "A に 5 を足す", 65),
        ("01101000", "A をメモリ 8番地へ", 65),
        ("00000010", "A から 2 を引く", 63)]


def timing(t):
    k, lo = SC.idx(t), SC.local(t)
    dt = 2.6 if k == 1 else 0.85
    n = int(max(lo - 0.8, 0) / dt)
    return n // 6 % len(PROG), n % 6, dt


def stages(pc, stage, al=1.0):
    for j, ((x, y), name) in enumerate(zip(POS, STAGES)):
        on = (j == stage)
        C.rrect(ax, x - SW / 2, y - SH / 2, SW, SH,
                C.FILL if on else C.BG, C.OKC if on else C.EDGE, r=1.2,
                lw=1.8 if on else 1.1, al=al, z=4)
        ax.text(x, y, name, ha="center", va="center", fontsize=13,
                color=C.OKC if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
    arrows = [((32, 68), (80, 68)), ((80, 68), (128, 68)),
              ((128, 68), (128, 48)), ((128, 48), (80, 48)),
              ((80, 48), (32, 48))]
    for j, ((x0, y0), (x1, y1)) in enumerate(arrows):
        live = (stage == j)
        if y0 == y1:
            sx = x0 + np.sign(x1 - x0) * SW / 2
            ex = x1 - np.sign(x1 - x0) * SW / 2
            sy = ey = y0
        else:
            sx = ex = x0
            sy = y0 - SH / 2
            ey = y1 + SH / 2
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=C.HOT if live else C.GRAY,
                                    lw=2.2 if live else 1.2, alpha=al),
                    zorder=6)
    # 最後の段から先頭へ戻る線
    back = (stage == 5)
    ax.plot([32.0 - SW / 2, 12.0, 12.0, 32.0 - SW / 2],
            [48.0, 48.0, 68.0, 68.0],
            color=C.HOT if back else C.GRAY, lw=2.2 if back else 1.2,
            zorder=3, alpha=al)
    ax.text(12.0, 58.0, "次へ", ha="left", va="center", fontsize=12,
            color=C.HOT if back else C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=6,
            bbox=dict(facecolor=C.BG, edgecolor="none", pad=0.8, alpha=al))


def regs(pc, stage, al=1.0):
    bits, mean, aval = PROG[pc]
    prev = PROG[pc - 1][2] if pc else 0
    shown_ir = bits if stage >= 2 else "--------"
    shown_a = aval if stage >= 5 else prev
    items = [("PC", str(pc)), ("命令レジスタ", shown_ir), ("A", str(shown_a))]
    for j, (name, val) in enumerate(items):
        x = 28.0 + j * 46.0
        ax.text(x, 33.0, name, ha="center", va="center", fontsize=12,
                color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(x, 26.0, val, ha="center", va="center", fontsize=18,
                color=C.INK, fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(80.0, 16.0, mean if stage >= 3 else "（まだ読んでいる途中）",
            ha="center", va="center", fontsize=15,
            color=C.OKC if stage >= 3 else C.MUTED, fontproperties=C.FPB,
            alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "フェッチ・デコード・実行",
                     sub="第27回 ── 1命令の一巡")
        SC.caption(ax, t)
        return []

    if k == 3:
        C.title_card(ax, SC, t, "同じ6段を、ひたすら繰り返しているだけ",
                     main2="それが「プログラムが動いている」の正体",
                     sub="速くする工夫は、この繰り返しの詰め方（第29回）")
        SC.caption(ax, t)
        return []

    pc, stage, dt = timing(t)
    stages(pc, stage, al)
    regs(pc, stage, al)
    ax.text(80.0, 78.0,
            "%d番地の命令  ──  %d段目 / 6" % (pc, stage + 1),
            ha="center", va="center", fontsize=15, color=C.MUTED,
            fontproperties=C.FPB, alpha=al, zorder=5)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep27_fetch.mp4")
