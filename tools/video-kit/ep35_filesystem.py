"""第35回 ファイルシステム ── 木は、でっち上げ。

  ただのブロックの並びの上に、木構造をこしらえる。
  ディレクトリは「名前とブロック番号の対応表」でしかない。最後に断片化。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 34, 50, 64, 74],
    caps=[
        "",                                            # 0 タイトル
        "ディスクは、番号のついた箱が並んでいるだけ",     # 1
        "ディレクトリは、名前と番号の対応表",             # 2
        "表が表を指すと、木に見える",                    # 3
        "空きを拾って書くので、飛び飛びになる",           # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

NCOL, NROW = 8, 3
BW, BH = 15.0, 7.0
BX0, BY = 18.0, [52.0, 43.0, 34.0]
FILE_A = [3, 9, 10, 20]          # 写真.jpg が使うブロック
FILE_B = [5, 13]                 # メモ.txt が使うブロック


def bxy(n):
    return BX0 + (n % NCOL) * (BW + 1.0), BY[n // NCOL]


def blocks(hi_a=(), hi_b=(), al=1.0, numbers=True):
    for n in range(NCOL * NROW):
        x, y = bxy(n)
        col = C.EDGE
        fc = C.BG
        if n in hi_a:
            col, fc = C.EL, C.FILL
        elif n in hi_b:
            col, fc = C.OKC, C.FILL
        C.rrect(ax, x, y - BH / 2, BW, BH, fc, col, r=0.8,
                lw=1.7 if (n in hi_a or n in hi_b) else 1.0, al=al, z=4)
        if numbers:
            ax.text(x + BW / 2, y, str(n), ha="center", va="center",
                    fontsize=12,
                    color=col if (n in hi_a or n in hi_b) else C.MUTED,
                    fontproperties=C.FPB, alpha=al, zorder=5)
    # 上には表が来るので、ラベルは並びの下に置く
    ax.text(BX0, BY[-1] - 6.5, "ディスク（ただのブロックの並び）", ha="left",
            va="top", fontsize=14, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)


def table(x, y, title, rows, al=1.0, w=52.0):
    C.rrect(ax, x, y - 5.0 - len(rows) * 7.0, w, 5.0 + len(rows) * 7.0 + 6.0,
            C.BG, C.EDGE, r=1.0, lw=1.2, al=al, z=3)
    ax.text(x + w / 2, y + 2.0, title, ha="center", va="center",
            fontsize=13, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.plot([x + 2, x + w - 2], [y - 2.0, y - 2.0], color=C.GRAY, lw=0.9,
            zorder=4, alpha=al)
    for j, (name, val, col) in enumerate(rows):
        yy = y - 6.5 - j * 7.0
        ax.text(x + 4.0, yy, name, ha="left", va="center", fontsize=12,
                color=C.INK, fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(x + w - 4.0, yy, val, ha="right", va="center", fontsize=12,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "ファイルシステム",
                     sub="第35回 ── 木は、あとから描いたもの")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "フォルダは、入れ物ではない",
                     main2="名前と番号を書いた、ただの表",
                     sub="階層に見えているのは、表が表を指しているから")
        SC.caption(ax, t)
        return []

    if k == 1:
        blocks(al=al)
        ax.text(80, 22, "箱に順番があるだけ。名前も、階層もない",
                ha="center", va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "どこに何があるかは、この並びだけでは分からない",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 2:
        blocks(hi_a=FILE_A, hi_b=FILE_B, al=al)
        table(16.0, 80.0, "写真フォルダ",
              [("写真.jpg", "3, 9, 10, 20", C.EL),
               ("メモ.txt", "5, 13", C.OKC)], al)
        ax.text(80, 22, "名前を引くと、番号が出てくる", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "この表もまた、どこかのブロックに書かれている",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 3:
        blocks(hi_a=FILE_A, hi_b=FILE_B, al=al)
        table(10.0, 80.0, "ルート（/）",
              [("写真", "→ 表 7番", C.HOT),
               ("書類", "→ 表 15番", C.MUTED)], al, w=46.0)
        table(70.0, 80.0, "写真フォルダ（7番）",
              [("写真.jpg", "3, 9, 10, 20", C.EL),
               ("メモ.txt", "5, 13", C.OKC)], al, w=56.0)
        ax.annotate("", xy=(68.0, 73.5), xytext=(58.0, 73.5),
                    arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.2,
                                    alpha=al), zorder=6)
        ax.text(80, 22, "木構造は、表のたどり方の話でしかない", ha="center",
                va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "ディスクの上に、木の形をしたものは何もない",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    blocks(hi_a=FILE_A, hi_b=FILE_B, al=al)
    for a, b in zip(FILE_A[:-1], FILE_A[1:]):
        xa, ya = bxy(a)
        xb, yb = bxy(b)
        ax.annotate("", xy=(xb + BW / 2, yb + BH / 2 + 0.5),
                    xytext=(xa + BW / 2, ya + BH / 2 + 0.5),
                    arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=1.6,
                                    alpha=al * 0.9,
                                    connectionstyle="arc3,rad=-0.35"),
                    zorder=6)
    ax.text(80, 22, "1つのファイルが、離れた箱に散らばる", ha="center",
            va="center", fontsize=22, color=C.EL, fontproperties=C.FPB,
            alpha=al)
    ax.text(80, 14, "読むたびに探しに行く分だけ、遅くなる（断片化）",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep35_filesystem.mp4")
