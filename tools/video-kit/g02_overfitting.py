"""G検定② 過学習 ── 訓練誤差と検証誤差が分かれる瞬間。

  同じ点群に、次数を上げながら曲線を当てていく。
  左で曲線がうねりはじめ、右で2本の誤差曲線が分岐する。
  ノート「② 機械学習の手法」の「最大の敵：丸暗記する優等生」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 16, 30, 45, 58, 68],
    caps=[
        "",                                            # 0 タイトル
        "点の裏には、本当の形がある",                   # 1
        "次数を上げると、点にぴったり沿っていく",        # 2
        "訓練は良くなるのに、検証は悪くなる",            # 3
        "止めどきを決めるのが、正則化と早期終了",        # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

# --- データ。真の形は sin。そこにノイズを乗せた点を観測とする ---------
_rng = np.random.default_rng(5)
NX = 11
DX = np.linspace(0.06, 0.94, NX)
TRUE = lambda x: np.sin(x * 2.2 * np.pi * 0.5 + 0.3)
DY = TRUE(DX) + _rng.normal(0, 0.16, NX)
VX = np.linspace(0.10, 0.90, 7) + 0.03
VY = TRUE(VX) + _rng.normal(0, 0.16, 7)

PX0, PX1, PY0, PY1 = 16.0, 76.0, 34.0, 72.0     # 左: 当てはめ
GX0, GX1, GY0, GY1 = 96.0, 148.0, 34.0, 72.0    # 右: 誤差曲線
DEG_MAX = 10


def px(x):
    return PX0 + (PX1 - PX0) * x


def py(y):
    return (PY0 + PY1) / 2 + (PY1 - PY0) / 2 * (y / 1.7)


def deg_at(t):
    k, lo = SC.idx(t), SC.local(t)
    if k == 1:
        return 3
    if k == 2:
        return int(np.clip(3 + lo / 1.35, 3, DEG_MAX))
    if k == 3:
        return DEG_MAX
    return 4


def fit(deg):
    c = np.polyfit(DX, DY, deg)
    return np.poly1d(c)


ERR = []
for _d in range(1, DEG_MAX + 1):
    _p = fit(_d)
    ERR.append((_d,
                float(np.sqrt(np.mean((_p(DX) - DY) ** 2))),
                float(np.sqrt(np.mean((np.clip(_p(VX), -3, 3) - VY) ** 2)))))
E_MAX = max(max(a, b) for _, a, b in ERR)


def panel_fit(deg, al=1.0, show_true=False):
    ax.plot([PX0, PX1], [py(0), py(0)], color=C.GRAY, lw=1.0, ls=(0, (3, 3)),
            zorder=3, alpha=al * 0.7)
    xs = np.linspace(0.02, 0.98, 260)
    if show_true:
        ax.plot(px(xs), py(TRUE(xs)), color=C.GRAY, lw=2.0, ls=(0, (5, 3)),
                zorder=4, alpha=al * 0.9)
        ax.text(px(0.5), PY1 + 3.0, "本当の形", ha="center", va="bottom",
                fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
                zorder=5)
    p = fit(deg)
    ax.plot(px(xs), np.clip(py(p(xs)), PY0 - 4, PY1 + 4),
            color=C.HOT if deg >= 8 else C.EL, lw=2.8, zorder=6, alpha=al)
    ax.scatter(px(DX), py(DY), s=110, c=C.INK, zorder=7, linewidths=0,
               alpha=al)
    ax.scatter(px(VX), py(VY), s=110, facecolors="none", edgecolors=C.OKC,
               linewidths=1.8, zorder=7, alpha=al)
    ax.text(PX0, PY1 + 8.0, "次数 %d" % deg, ha="left", va="bottom",
            fontsize=16, color=C.HOT if deg >= 8 else C.INK,
            fontproperties=C.FPB, alpha=al, zorder=6)
    ax.text(PX1, PY1 + 8.5, "● 訓練データ    ○ 検証データ", ha="right",
            va="bottom", fontsize=11, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)


def panel_err(deg, al=1.0, mark_best=False):
    ax.plot([GX0, GX1], [GY0, GY0], color=C.GRAY, lw=1.4, zorder=3, alpha=al)
    ax.plot([GX0, GX0], [GY0, GY1], color=C.GRAY, lw=1.4, zorder=3, alpha=al)
    ex = lambda d: GX0 + (GX1 - GX0) * (d - 1) / (DEG_MAX - 1)
    ey = lambda e: GY0 + (GY1 - GY0) * min(e / E_MAX, 1.0)
    shown = [r for r in ERR if r[0] <= deg]
    if len(shown) >= 2:
        ax.plot([ex(d) for d, _, _ in shown], [ey(a) for _, a, _ in shown],
                color=C.EL, lw=2.6, zorder=6, alpha=al)
        ax.plot([ex(d) for d, _, _ in shown], [ey(b) for _, _, b in shown],
                color=C.OKC, lw=2.6, zorder=6, alpha=al)
    # ラベルはパネルの中に収める。線に合わせて外へ出すと軸ラベルと重なる
    cur = ERR[min(deg, DEG_MAX) - 1]
    for e, lab, col in ((cur[1], "訓練誤差", C.EL), (cur[2], "検証誤差", C.OKC)):
        yy = float(np.clip(ey(e) + 2.6, GY0 + 3.0, GY1 - 4.0))
        ax.text(GX1 - 1.0, yy, lab, ha="right", va="bottom", fontsize=12,
                color=col, fontproperties=C.FPB, alpha=al, zorder=7,
                bbox=dict(facecolor=C.BG, edgecolor="none", pad=0.8,
                          alpha=al * 0.85))
    ax.text(GX0 - 2.5, GY1, "誤差", ha="right", va="center", fontsize=12,
            color=C.MUTED, fontproperties=C.FP, alpha=al, zorder=5)
    ax.text(GX1, GY0 - 3.5, "次数（複雑さ）→", ha="right", va="top",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)
    if mark_best:
        best = min(ERR, key=lambda r: r[2])[0]
        ax.plot([ex(best), ex(best)], [GY0, GY1], color=C.HOT, lw=1.6,
                ls=(0, (4, 3)), zorder=7, alpha=al)
        ax.text(ex(best), GY1 + 3.0, "ここで止める", ha="center",
                va="bottom", fontsize=13, color=C.HOT,
                fontproperties=C.FPB, alpha=al, zorder=8)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "過学習",
                     sub="G検定② ── 丸暗記した優等生は、初見に弱い")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "訓練データでの成績は、実力ではない",
                     main2="見たことのないデータで測る",
                     sub="だから手元のデータを訓練用と検証用に分けておく")
        SC.caption(ax, t)
        return []

    deg = deg_at(t)
    panel_fit(deg, al, show_true=(k == 1))
    if k >= 2:
        panel_err(deg, al, mark_best=(k == 4))

    notes = [
        ("観測できるのは点だけ。線は引く側が決める",
         "ノイズまで拾いにいくと、本当の形から離れる"),
        ("点は全部通った。誤差はほぼゼロ",
         "でも点と点の間で、曲線が大きくうねりはじめている"),
        ("訓練誤差↓ なのに 検証誤差↑",
         "この開きが過学習。複雑にするほど広がる"),
        ("いちばん外側に強いのは、真ん中あたり",
         "複雑さに罰を与えるのが正則化、途中で打ち切るのが早期終了"),
    ]
    main, sub = notes[k - 1]
    ax.text(80, 22, main, ha="center", va="center", fontsize=21,
            color=C.HOT if k == 3 else (C.OKC if k == 4 else C.INK),
            fontproperties=C.FPB, alpha=al)
    ax.text(80, 14, sub, ha="center", va="center", fontsize=14,
            color=C.MUTED, fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g02_overfitting.mp4")
