"""G検定③ 自己注意 ── 順に読むのをやめて、全部を一度に見る。

  各単語が文中の全単語を見渡し、関連の強い単語から情報を集める。
  逐次処理がないので並列化でき、どんなに離れた語も直接つながる。
  代償として計算量は系列長の2乗。
  ノート「③ ディープラーニング」の「Transformer — 全部を一度に見る」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 34, 50, 63, 73],
    caps=[
        "",                                            # 0 タイトル
        "RNN は1語ずつ。遠い語ほど弱くなる",            # 1
        "各語が、全語を一度に見渡す",                   # 2
        "関連の強い語から、多く受け取る",               # 3
        "代償は、計算量が系列長の2乗になること",         # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

WORDS = ["昨日", "私", "は", "寿司", "を", "食べた"]
NT = len(WORDS)
# 左の「見られる側」が画面外に出ないよう、行を右へ寄せてある
WX = [30.0 + j * 22.4 for j in range(NT)]
WY_TOP, WY_BOT = 72.0, 42.0
BW, BH = 18.0, 11.0

# 「食べた」から各語への注意の重み（この動画かぎりの例）
ATT = {5: np.array([0.06, 0.14, 0.04, 0.46, 0.22, 0.08])}
for _q in range(NT):
    if _q not in ATT:
        _w = np.exp(-0.55 * np.abs(np.arange(NT) - _q))
        ATT[_q] = _w / _w.sum()


def words(y, al=1.0, hi=None, dim=None):
    for j, x in enumerate(WX):
        on = (hi is None or j == hi)
        a = al * (1.0 if on else 0.55)
        if dim is not None and j in dim:
            a = al * 0.3
        C.rrect(ax, x - BW / 2, y - BH / 2, BW, BH,
                C.FILL if on else C.BG, C.HOT if j == hi else C.EDGE,
                r=1.0, lw=1.7 if j == hi else 1.1, al=a, z=5)
        ax.text(x, y, WORDS[j], ha="center", va="center", fontsize=13,
                color=C.INK, fontproperties=C.FPB, alpha=a, zorder=6)


def attn_lines(q, al=1.0, weighted=True):
    w = ATT[q]
    for j, x in enumerate(WX):
        v = float(w[j])
        lw = 0.6 + 6.0 * v if weighted else 1.2
        col = C.OKC if (weighted and v > 0.18) else C.EL
        ax.plot([WX[q], x], [WY_TOP - BH / 2, WY_BOT + BH / 2],
                color=col, lw=lw, zorder=4,
                alpha=al * (0.25 + 0.75 * v if weighted else 0.4))
        if weighted and v > 0.18:
            ax.text((WX[q] + x) / 2, (WY_TOP + WY_BOT) / 2, "%.2f" % v,
                    ha="center", va="center", fontsize=11, color=C.OKC,
                    fontproperties=C.FPB, alpha=al, zorder=7,
                    bbox=dict(facecolor=C.BG, edgecolor="none", pad=0.7,
                              alpha=al * 0.9))


def cost_grid(n, x0, ycen, size, al=1.0, grown=1.0):
    """n×n の総当たり。外形を size に固定するので、はみ出さない"""
    cell = size / n
    y0 = ycen + size / 2
    shown = int(round(n * n * grown))
    for r in range(n):
        for c in range(n):
            if r * n + c >= shown:
                continue
            C.rrect(ax, x0 + c * cell, y0 - (r + 1) * cell,
                    cell * 0.82, cell * 0.82, C.EL, "none",
                    r=min(0.3, cell * 0.2), al=al * 0.6, z=4)
    ax.text(x0 + size / 2, ycen - size / 2 - 3.0,
            "%d語 → %d 通り" % (n, n * n), ha="center", va="top",
            fontsize=15, color=C.EL, fontproperties=C.FPB, alpha=al,
            zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "自己注意（Self-Attention）",
                     sub="G検定③ ── 順に読むのを、やめた")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "距離をなくした。そのかわり総当たりになった",
                     main2="並列に計算できるので、それでも速い",
                     sub="語順は位置エンコーディングで別に入れる")
        SC.caption(ax, t)
        return []

    if k == 1:
        n = int(np.clip((lo - 0.6) / 1.4, 0, NT - 1))
        words(WY_TOP, al, dim=set(range(n + 1, NT)))
        for j in range(min(n, NT - 1)):
            ax.annotate("", xy=(WX[j + 1] - BW / 2 - 1, WY_TOP),
                        xytext=(WX[j] + BW / 2 + 1, WY_TOP),
                        arrowprops=dict(arrowstyle="-|>", color=C.EL,
                                        lw=2.0, alpha=al), zorder=6)
        ax.text(80, 52, "「食べた」から「昨日」までは 5 ステップ",
                ha="center", va="center", fontsize=19, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=6)
        ax.text(80, 24, "1語ずつしか進めない  →  並列化できない",
                ha="center", va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "しかも遠い語ほど、途中で薄れる（第6回のLSTMの話）",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 4:
        # ここは語の行を出さない。格子と重なって読めなくなる
        g1 = C.ease((lo - 0.8) / 1.6)
        g2 = C.ease((lo - 3.2) / 2.4)
        cost_grid(6, 26.0, 56.0, 34.0, al, g1)
        if g2 > 0:
            cost_grid(12, 100.0, 56.0, 34.0, al * g2, g2)
            ax.annotate("", xy=(96.0, 56.0), xytext=(66.0, 56.0),
                        arrowprops=dict(arrowstyle="-|>", color=C.MUTED,
                                        lw=2.0, alpha=al * g2), zorder=6)
            ax.text(81.0, 59.0, "語数を2倍", ha="center", va="bottom",
                    fontsize=13, color=C.MUTED, fontproperties=C.FPB,
                    alpha=al * g2, zorder=6)
        ax.text(80, 78.0, "1マスが、1組の「見る・見られる」", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FP, alpha=al, zorder=6)
        ax.text(80, 24, "語数が2倍になると、計算は4倍", ha="center",
                va="center", fontsize=22, color=C.EL,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "長い文章を扱うときに、ここが効いてくる",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    q = 5 if k == 3 else int(np.clip((lo - 0.8) / 2.0, 0, NT - 1))
    words(WY_TOP, al, hi=q)
    attn_lines(q, al, weighted=(k == 3))
    words(WY_BOT, al)
    ax.text(WX[0] - BW / 2 - 3.0, WY_TOP, "見る側", ha="right",
            va="center", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)
    ax.text(WX[0] - BW / 2 - 3.0, WY_BOT, "見られる側", ha="right",
            va="center", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)

    if k == 2:
        ax.text(80, 24, "距離が消えた。どの語へも、一手で届く", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "順番に読まないので、全部まとめて計算できる",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "「食べた」が見ているのは、主に「寿司」",
                ha="center", va="center", fontsize=22, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "線の太さが重み。合計すると 1 になるように配分する",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g07_attention.mp4")
