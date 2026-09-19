"""G検定⑤ 勾配降下法 ── 学習率で、収束も振動も発散もする。

  谷の上を玉が転がる。学習率を変えると、進まない／ちょうど／振動／発散。
  ノート「⑤ 数理・統計」の「第3幕：学ぶ — 坂を下る」に対応。
  第9回(増幅回路)・第12回(発振)と同じ「行きすぎると壊れる」構造。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 29, 43, 57, 67],
    caps=[
        "",                                            # 0 タイトル
        "傾きを見て、下る向きへ一歩進む",                # 1
        "歩幅が小さすぎると、いつまでも着かない",         # 2
        "ちょうどよければ、底で止まる",                  # 3
        "大きすぎると、飛び越えて発散する",              # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

VX0, VX1 = 18.0, 142.0        # 谷のパネル
VY0, VY1 = 34.0, 76.0
X_MIN, X_MAX = -2.0, 2.0      # 谷の横軸
# 学習率は「見て分かる」値に取る。1.02 だと1歩4%しか育たず横ばいに見えた
STEPS = [(2, 0.02, "小さすぎる", C.NGC),
         (3, 0.35, "ちょうどいい", C.OKC),
         (4, 1.15, "大きすぎる", C.HOT)]
START = -1.5


def loss(x):
    return x * x


def gx(x):
    return VX0 + (VX1 - VX0) * (x - X_MIN) / (X_MAX - X_MIN)


def gy(y):
    # 配列で呼ばれる（谷の曲線）ので min ではなく np.minimum
    return VY0 + (VY1 - VY0) * np.minimum(y / (X_MAX ** 2), 1.0)


def lr_of(k):
    for kk, lr, lab, col in STEPS:
        if kk == k:
            return lr, lab, col
    return 0.34, "", C.EL


def path_of(lr, n=40):
    """更新の軌跡。x ← x - lr * 2x"""
    xs = [START]
    for _ in range(n):
        x = xs[-1]
        nx = x - lr * 2.0 * x
        if abs(nx) > X_MAX + 0.45:
            xs.append(np.sign(nx) * (X_MAX + 0.45))
            break
        xs.append(nx)
    return xs


def valley(al=1.0):
    xs = np.linspace(X_MIN, X_MAX, 260)
    ax.plot(gx(xs), gy(loss(xs)), color=C.GRAY, lw=2.4, zorder=4, alpha=al)
    ax.plot([gx(0), gx(0)], [VY0, gy(loss(0)) + 2.0], color=C.GRAY, lw=1.0,
            ls=(0, (3, 3)), zorder=3, alpha=al * 0.7)
    ax.text(gx(0), VY0 - 3.5, "底（最小）", ha="center", va="top",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    # 発散した玉が左上へ抜けるので、軸ラベルは中ほどに縦置きして避ける
    ax.text(VX0 - 4.0, (VY0 + VY1) / 2, "損失", ha="center", va="center",
            rotation=90, fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)
    ax.text(VX1, VY0 - 3.5, "パラメータ →", ha="right", va="top",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def slope_arrow(x, al=1.0):
    """いる場所の傾きと、進む向き"""
    y = loss(x)
    g = 2.0 * x
    d = -np.sign(g) * 0.22
    ax.annotate("", xy=(gx(x + d), gy(loss(x)) ), xytext=(gx(x), gy(y)),
                arrowprops=dict(arrowstyle="-|>", color=C.HOT, lw=2.4,
                                alpha=al), zorder=8)
    ax.text(gx(x), gy(y) + 5.5, "傾き %.1f" % g, ha="center", va="bottom",
            fontsize=13, color=C.HOT, fontproperties=C.FPB, alpha=al,
            zorder=8)


def run(k, lo, al=1.0):
    lr, lab, col = lr_of(k)
    xs = path_of(lr)
    n = int(np.clip(lo / 0.75, 0, len(xs) - 1))
    pts = xs[:n + 1]
    vis = [p for p in pts if X_MIN - 0.3 <= p <= X_MAX + 0.3]
    if len(vis) >= 2:
        ax.plot([gx(p) for p in vis], [gy(loss(p)) for p in vis],
                color=col, lw=1.6, ls=(0, (2, 2)), zorder=6, alpha=al * 0.8)
    for p in pts[:-1]:
        if X_MIN - 0.3 <= p <= X_MAX + 0.3:
            ax.scatter([gx(p)], [gy(loss(p))], s=60, c=col, zorder=6,
                       linewidths=0, alpha=al * 0.45)
    cur = pts[-1]
    ax.scatter([gx(np.clip(cur, X_MIN - 0.2, X_MAX + 0.2))],
               [gy(loss(np.clip(cur, X_MIN, X_MAX)))],
               s=260, c=col, zorder=9, linewidths=0, alpha=al)
    ax.text(VX0, VY1 + 8.0, "学習率 %.2f  ── %s" % (lr, lab), ha="left",
            va="bottom", fontsize=16, color=col, fontproperties=C.FPB,
            alpha=al, zorder=7)
    ax.text(VX1, VY1 + 8.5, "%d 歩目" % n, ha="right", va="bottom",
            fontsize=13, color=C.MUTED, fontproperties=C.FPB, alpha=al,
            zorder=7)
    return cur


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "勾配降下法",
                     sub="G検定⑤ ── 歩幅を間違えると、底に着かない")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "向きは傾きが教えてくれる",
                     main2="決めるのは、歩幅のほう",
                     sub="小さければ遅く、大きければ壊れる。第12回の発振と同じ形")
        SC.caption(ax, t)
        return []

    valley(al)

    if k == 1:
        x = START + 0.75 * C.ease((lo - 1.0) / 4.0)
        ax.scatter([gx(x)], [gy(loss(x))], s=260, c=C.EL, zorder=9,
                   linewidths=0, alpha=al)
        slope_arrow(x, al)
        ax.text(80, 22, "傾きが急なほど、大きく動かす", ha="center",
                va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 14, "更新は「いまの値 − 学習率 × 傾き」。これだけ",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    cur = run(k, lo, al)
    notes = {
        2: ("40歩かけても、まだ坂の途中", "学習率を下げすぎると、時間だけがかかる"),
        3: ("数歩で底に落ち着いた", "傾きが小さくなるほど、歩幅も自然に縮む"),
        4: ("行きすぎて、反対側のもっと高い所へ", "跳ね返るたびに大きくなる。これが発散"),
    }
    main, sub = notes[k]
    ax.text(80, 22, main, ha="center", va="center", fontsize=21,
            color=lr_of(k)[2], fontproperties=C.FPB, alpha=al)
    ax.text(80, 14, sub, ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g03_gradient.mp4")
