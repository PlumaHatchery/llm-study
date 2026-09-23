"""G検定③ CNN ── フィルタが滑り、プーリングが縮める。

  同じフィルタを全位置で使い回すから、パラメータが減り、位置がずれても
  同じ特徴を拾える。プーリングは代表値に集約して、微小なずれに強くする。
  ノート「③ ディープラーニング」の「CNN — 画像の専門家」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 19, 34, 48, 62, 72],
    caps=[
        "",                                            # 0 タイトル
        "小さなフィルタを、画像じゅうに滑らせる",        # 1
        "同じフィルタを全位置で使い回す",                # 2
        "プーリングで、代表値だけ残して縮める",          # 3
        "位置がずれても、同じ特徴が立つ",                # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

# --- 8x8 の入力。縦線のある「画像」 --------------------------------
GN = 8
_rng = np.random.default_rng(3)
IMG = _rng.uniform(0.05, 0.28, (GN, GN))
IMG[:, 2] = 0.88            # 縦線
IMG[1:7, 5] = 0.72          # もう1本
KER = np.array([[-1.0, 1.0, -1.0]])      # 縦線に反応するフィルタ

CELL = 5.2
IX, IY = 16.0, 70.0          # 入力の左上
FX, FY = 78.0, 70.0          # 特徴マップの左上
PX, PY = 126.0, 66.0         # プーリング後の左上
FN = GN - 2


def feat():
    out = np.zeros((GN, FN))
    for r in range(GN):
        for c in range(FN):
            out[r, c] = float((IMG[r, c:c + 3] * KER[0]).sum())
    return np.clip(out, 0, None)


FEAT = feat()
POOL = FEAT.reshape(4, 2, 3, 2).max(axis=(1, 3))


def grid(vals, x0, y0, cell, al=1.0, col=C.EL, lab=None, hi=None):
    rows, cols = vals.shape
    m = float(vals.max()) or 1.0
    for r in range(rows):
        for c in range(cols):
            v = float(vals[r, c]) / m
            x = x0 + c * cell
            y = y0 - r * cell
            C.rrect(ax, x, y - cell, cell - 0.5, cell - 0.5,
                    col if v > 0.02 else C.BG, C.EDGE, r=0.4, lw=0.7,
                    al=al * (0.18 + 0.82 * v) if v > 0.02 else al * 0.5, z=4)
    if hi is not None:
        r, c, w = hi
        ax.plot([x0 + c * cell - 0.6, x0 + (c + w) * cell - 0.6,
                 x0 + (c + w) * cell - 0.6, x0 + c * cell - 0.6,
                 x0 + c * cell - 0.6],
                [y0 - r * cell + 0.6, y0 - r * cell + 0.6,
                 y0 - (r + 1) * cell + 0.6, y0 - (r + 1) * cell + 0.6,
                 y0 - r * cell + 0.6],
                color=C.HOT, lw=2.4, zorder=8, alpha=al)
    if lab:
        ax.text(x0 + cols * cell / 2 - 0.3, y0 + 3.0, lab, ha="center",
                va="bottom", fontsize=13, color=C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=6)


def slide_pos(lo, period=0.32):
    n = int(max(lo - 0.6, 0) / period)
    total = GN * FN
    n = min(n, total - 1)
    return n // FN, n % FN, n


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "CNN",
                     sub="G検定③ ── 同じフィルタを、使い回す")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "画像の都合を、構造に作り込んだ",
                     main2="隣どうしはまとまって意味を持つ／猫はどこにいても猫",
                     sub="使い回すからパラメータが減り、縮めるからずれに強くなる")
        SC.caption(ax, t)
        return []

    r, c, n = slide_pos(lo)
    shown = FEAT.copy()
    if k in (1, 2):
        mask = np.zeros_like(FEAT)
        flat = mask.reshape(-1)
        flat[:n + 1] = 1.0
        shown = FEAT * mask

    grid(IMG, IX, IY, CELL, al, C.INK, "入力（8×8）",
         hi=(r, c, 3) if k in (1, 2) else None)
    grid(shown, FX, FY, CELL, al, C.EL, "特徴マップ（8×6）")

    if k >= 3:
        grid(POOL, PX, PY, CELL * 1.5, al, C.OKC, "プーリング後（4×3）")
        ax.annotate("", xy=(PX - 3.0, 58.0), xytext=(FX + FN * CELL + 1.0,
                                                     58.0),
                    arrowprops=dict(arrowstyle="-|>", color=C.OKC, lw=2.2,
                                    alpha=al), zorder=6)
    if k in (1, 2):
        ax.annotate("", xy=(FX - 3.0, 58.0), xytext=(IX + GN * CELL + 1.0,
                                                     58.0),
                    arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=2.2,
                                    alpha=al), zorder=6)
        # フィルタの中身
        ax.text((IX + GN * CELL + FX) / 2 - 1.5, 54.0, "−1  +1  −1",
                ha="center", va="top", fontsize=13, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=6)
        ax.text((IX + GN * CELL + FX) / 2 - 1.5, 48.5, "フィルタ",
                ha="center", va="top", fontsize=11, color=C.MUTED,
                fontproperties=C.FP, alpha=al, zorder=6)

    notes = [
        ("3マスを見て、1マスぶんの答えを出す", "縦線があるところで、値が大きくなるフィルタ"),
        ("重みは 3つだけ。全位置で同じものを使う",
         "位置ごとに別の重みを持たない。だからパラメータが激減する"),
        ("2×2 の中の最大値だけを残す", "情報を捨てて縮める。計算も軽くなる"),
        ("線が1マスずれても、立つ場所がずれるだけ",
         "プーリングのあとでは、その差も消える。これが位置ずれへの強さ"),
    ]
    main, sub = notes[k - 1]
    ax.text(80, 24, main, ha="center", va="center", fontsize=21,
            color=C.OKC if k >= 3 else C.INK, fontproperties=C.FPB, alpha=al)
    ax.text(80, 15, sub, ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g05_cnn.mp4")
