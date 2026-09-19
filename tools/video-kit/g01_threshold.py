"""G検定① 適合率と再現率 ── しきい値を動かすと、逆に振れる。

  同じモデル・同じ予測スコアのまま、しきい値だけを左右に動かす。
  適合率と再現率が逆方向に動き、混同行列の4マスが入れ替わる。
  最後にROC曲線へ落とす。

  ノート「② 機械学習の手法」の「評価：99%正解でも無意味なモデル」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 17, 31, 46, 60, 70],
    caps=[
        "",                                            # 0 タイトル
        "モデルが出すのは 0か1 ではなく、0〜1 のスコア",  # 1
        "しきい値を下げると、取りこぼしは減るが誤検出が増える",  # 2
        "上げると、誤検出は減るが取りこぼしが増える",     # 3
        "全部のしきい値をなぞった軌跡が ROC 曲線",        # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

# --- 30件のサンプル。陽性と陰性でスコアの分布をずらす -----------------
_rng = np.random.default_rng(11)
N_POS, N_NEG = 12, 18
S_POS = np.clip(_rng.normal(0.68, 0.16, N_POS), 0.05, 0.98)
S_NEG = np.clip(_rng.normal(0.34, 0.17, N_NEG), 0.02, 0.95)

AX0, AX1, AY = 24.0, 136.0, 60.0     # スコアの数直線
# 2行とも数直線の上に置く。下に置くと目盛りのラベルと点が重なる
ROW_P, ROW_N = 73.0, 66.0            # 陽性の行・陰性の行
BOX = 30.0                           # 混同行列の左端


def thr_at(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 2:
        return 0.5 + (0.18 - 0.5) * C.ease(lo / 5.0)
    if k == 3:
        return 0.18 + (0.82 - 0.18) * C.ease(lo / 6.0)
    if k == 4:
        return 0.95 - 0.93 * ((lo / 9.0) % 1.0)
    return 0.5


def counts(thr):
    tp = int((S_POS >= thr).sum())
    fn = N_POS - tp
    fp = int((S_NEG >= thr).sum())
    tn = N_NEG - fp
    return tp, fn, fp, tn


def sx(s):
    return AX0 + (AX1 - AX0) * s


def number_line(thr, al=1.0):
    ax.plot([AX0, AX1], [AY, AY], color=C.GRAY, lw=1.6, zorder=3, alpha=al)
    for v in (0.0, 0.5, 1.0):
        ax.plot([sx(v), sx(v)], [AY - 2.0, AY + 2.0], color=C.GRAY, lw=1.2,
                zorder=3, alpha=al)
        ax.text(sx(v), AY - 3.5, "%.1f" % v, ha="center", va="top",
                fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=4)
    ax.text(AX0 - 3.0, ROW_P, "陽性", ha="right", va="center", fontsize=13,
            color=C.DEEP, fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(AX0 - 3.0, ROW_N, "陰性", ha="right", va="center", fontsize=13,
            color=C.EL, fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(AX0 - 3.0, AY, "スコア", ha="right", va="center", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=4)
    # 点。しきい値の右にいれば「陽性と判定」
    for ss, row, col in ((S_POS, ROW_P, C.DEEP), (S_NEG, ROW_N, C.EL)):
        hit = ss >= thr
        ax.scatter(sx(ss[hit]), [row] * int(hit.sum()), s=110, c=col,
                   zorder=6, linewidths=0, alpha=al)
        ax.scatter(sx(ss[~hit]), [row] * int((~hit).sum()), s=110,
                   facecolors="none", edgecolors=col, linewidths=1.5,
                   zorder=6, alpha=al * 0.85)
    # しきい値の線
    ax.plot([sx(thr), sx(thr)], [AY - 1.0, ROW_P + 5.0], color=C.HOT,
            lw=2.2, zorder=7, alpha=al)
    ax.text(sx(thr), ROW_P + 6.0, "しきい値 %.2f" % thr, ha="center",
            va="bottom", fontsize=14, color=C.HOT, fontproperties=C.FPB,
            alpha=al, zorder=8)
    ax.text(AX1 + 2.0, (ROW_P + ROW_N) / 2, "→ 陽性と判定", ha="left",
            va="center", fontsize=11, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)


def matrix(thr, al=1.0):
    tp, fn, fp, tn = counts(thr)
    cells = [(0, 0, tp, "正しく拾えた", C.OKC),
             (1, 0, fp, "誤って拾った", C.HOT),
             (0, 1, fn, "取りこぼした", C.NGC),
             (1, 1, tn, "正しく捨てた", C.MUTED)]
    w, h = 27.0, 11.0
    for cx, cy, v, lab, col in cells:
        x = BOX + cx * w
        y = 40.0 - cy * h
        C.rrect(ax, x, y, w, h, C.FILL if v else C.BG, col, r=0.9,
                lw=1.4, al=al, z=4)
        ax.text(x + 5.0, y + h / 2, str(v), ha="center", va="center",
                fontsize=17, color=col, fontproperties=C.FPB, alpha=al,
                zorder=5)
        ax.text(x + 10.0, y + h / 2, lab, ha="left", va="center",
                fontsize=11, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    for j, (name, val, col) in enumerate(
            (("適合率", prec, C.HOT), ("再現率", rec, C.OKC))):
        y = 44.0 - j * 11.0
        ax.text(96.0, y, name, ha="left", va="center", fontsize=14,
                color=col, fontproperties=C.FPB, alpha=al, zorder=5)
        C.rrect(ax, 112.0, y - 3.0, 30.0, 6.0, "#EFEDE5", "#D3D1C7",
                r=0.8, lw=0.8, al=al, z=3)
        C.rrect(ax, 112.0, y - 3.0, max(1.5, 30.0 * val), 6.0, col, "none",
                r=0.8, al=al * 0.9, z=4)
        ax.text(144.0, y, "%.0f%%" % (val * 100), ha="left", va="center",
                fontsize=13, color=col, fontproperties=C.FPB, alpha=al,
                zorder=5)
    return prec, rec


def roc(thr, al=1.0):
    # 数直線(y=60〜73)の下に収める。上げると点の行とぶつかる
    x0, x1, y0, y1 = 96.0, 144.0, 24.0, 52.0
    ax.plot([x0, x1], [y0, y0], color=C.GRAY, lw=1.4, zorder=3, alpha=al)
    ax.plot([x0, x0], [y0, y1], color=C.GRAY, lw=1.4, zorder=3, alpha=al)
    ax.plot([x0, x1], [y0, y1], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            zorder=3, alpha=al * 0.7)
    ts = np.linspace(1.0, 0.0, 120)
    pts = []
    for tv in ts:
        tp, fn, fp, tn = counts(tv)
        pts.append((fp / N_NEG, tp / N_POS))
    pts = np.array(pts)
    ax.plot(x0 + (x1 - x0) * pts[:, 0], y0 + (y1 - y0) * pts[:, 1],
            color=C.EL, lw=2.6, zorder=5, alpha=al)
    tp, fn, fp, tn = counts(thr)
    ax.scatter([x0 + (x1 - x0) * fp / N_NEG], [y0 + (y1 - y0) * tp / N_POS],
               s=170, c=C.HOT, zorder=7, linewidths=0, alpha=al)
    ax.text(x0 - 2.5, y1, "再現率", ha="right", va="center", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=4)
    ax.text(x1, y0 - 3.0, "誤検出の割合 →", ha="right", va="top",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=4)
    ax.text((x0 + x1) / 2, y1 + 4.0, "ROC 曲線", ha="center", va="bottom",
            fontsize=14, color=C.EL, fontproperties=C.FPB, alpha=al,
            zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "適合率と再現率",
                     sub="G検定② 評価 ── しきい値ひとつで両方動く")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "どちらを優先するかは、後から決める",
                     main2="モデルを作り直すのではなく、線を動かすだけ",
                     sub="見逃しが怖い検査は再現率、誤報が困る検知は適合率")
        SC.caption(ax, t)
        return []

    thr = thr_at(t)
    number_line(thr, al)

    if k == 4:
        roc(thr, al)
        ax.text(56.0, 44.0, "しきい値を 1 から 0 へ", ha="center",
                va="center", fontsize=17, color=C.INK,
                fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(56.0, 36.0, "動かしたときの点の軌跡", ha="center",
                va="center", fontsize=17, color=C.INK,
                fontproperties=C.FPB, alpha=al, zorder=5)
        ax.text(56.0, 27.0, "左上に寄るほど良いモデル", ha="center",
                va="center", fontsize=13, color=C.MUTED,
                fontproperties=C.FP, alpha=al, zorder=5)
        ax.text(80, 14, "AUC は、この曲線の下の面積", ha="center",
                va="center", fontsize=15, color=C.MUTED,
                fontproperties=C.FPB, alpha=al)
        SC.caption(ax, t)
        return []

    prec, rec = matrix(thr, al)

    if k == 1:
        ax.text(80, 22, "スコアのどこで線を引くかは、こちらが決める",
                ha="center", va="center", fontsize=20, color=C.INK,
                fontproperties=C.FPB, alpha=al)
    elif k == 2:
        ax.text(80, 22, "しきい値を下げる  →  再現率↑  適合率↓",
                ha="center", va="center", fontsize=21, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
    else:
        ax.text(80, 22, "しきい値を上げる  →  適合率↑  再現率↓",
                ha="center", va="center", fontsize=21, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
    ax.text(80, 14, "モデルは何も変えていない。線を動かしただけ",
            ha="center", va="center", fontsize=14, color=C.MUTED,
            fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g01_threshold.mp4")
