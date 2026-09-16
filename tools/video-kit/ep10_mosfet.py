"""第10回 MOSFET ── 電気で、橋を架ける。

  n-p-n の三領域。真ん中は空き地で渡れない。
  ゲートに電圧をかけると、空き地の電子が表面に集まって橋になる。

  ep10_mosfet_narrated.py の字幕のみ版。音声の尺（durs.json）に頼らず、
  シーン境界を秒で固定し、色は common.py の定数だけを使う。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 14, 24, 32, 40, 50, 60, 69, 78],
    caps=[
        "",                                            # 0 タイトル
        "左と右は粒だらけ。でも真ん中は空き地",          # 1
        "空き地は渡れない。だから流れない",              # 2
        "空き地の上にフタをして、金属の板を置く",         # 3
        "板にプラスの電気をためる",                     # 4
        "プラスが、マイナスの粒を引き寄せる",            # 5
        "集まった粒が橋になった。左から右へ流れる",       # 6
        "板の電気を抜くと、橋は散って消える",            # 7
        "",                                            # 8 まとめ
    ],
)

fig, ax = C.new_axes()

SUB = (20.0, 34.0, 120.0, 28.0)      # p基板
LN = (26.0, 50.0, 32.0, 12.0)        # 左の n領域
RN = (102.0, 50.0, 32.0, 12.0)       # 右の n領域
SURF = 62.0                          # 表面（橋ができる高さ）
GAPL, GAPR = 58.0, 102.0             # 空き地の左右
OX = (62.0, 63.0, 36.0, 2.6)         # 酸化膜(フタ)
GT = (62.0, 66.5, 36.0, 7.0)         # ゲート(板)
CHAN_Y = SURF - 1.8

_rng = np.random.default_rng(7)
SRC = np.column_stack([_rng.uniform(29, 55, 9), _rng.uniform(52.5, 59.5, 9)])
DRN = np.column_stack([_rng.uniform(105, 131, 9),
                       _rng.uniform(52.5, 59.5, 9)])
NS = 7
STRAY = np.column_stack([_rng.uniform(61, 99, NS), _rng.uniform(38, 47, NS)])
CHAN = np.column_stack([np.linspace(60.5, 99.5, NS), np.full(NS, CHAN_Y)])


def device(al=1.0):
    C.rrect(ax, *SUB, C.BG, C.NGC, r=1.6, lw=1.4, al=al, z=2)
    ax.text(SUB[0] + 3.0, SUB[1] + 3.0, "p", ha="left", va="bottom",
            fontsize=14, color=C.NGC, fontproperties=C.FPB, alpha=al * 0.8,
            zorder=3)
    for x, y, w, h in (LN, RN):
        C.rrect(ax, x, y, w, h, C.FILL, C.EL, r=1.2, lw=1.4, al=al, z=3)
        ax.text(x + 3.0, y + h - 3.0, "n", ha="left", va="top", fontsize=14,
                color=C.EL, fontproperties=C.FPB, alpha=al * 0.8, zorder=4)


def gate(dy, al=1.0):
    C.rrect(ax, OX[0], OX[1] + dy, OX[2], OX[3], C.GRAY, C.EDGE, r=0.6,
            lw=1.0, al=al, z=7)
    C.rrect(ax, GT[0], GT[1] + dy, GT[2], GT[3], C.FILL, C.EDGE, r=0.8,
            lw=1.4, al=al, z=7)
    ax.text(80.0, GT[1] + GT[3] + 2.0 + dy, "板（ゲート）", ha="center",
            va="bottom", fontsize=14, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=7)


def plus(al=1.0):
    if al <= 0.01:
        return
    for px in (68.0, 76.0, 84.0, 92.0):
        ax.text(px, GT[1] + GT[3] / 2, "＋", ha="center", va="center",
                fontsize=17, color=C.DEEP, fontproperties=C.FPB, alpha=al,
                zorder=8)


def carriers(t, al=1.0):
    j = 0.35 * np.sin(t * 2.0 + np.arange(9))
    ax.scatter(SRC[:, 0], SRC[:, 1] + j, s=90, c=C.EL, zorder=5,
               linewidths=0, alpha=al)
    ax.scatter(DRN[:, 0], DRN[:, 1] - j, s=90, c=C.EL, zorder=5,
               linewidths=0, alpha=al)


def stray_pos(k, lo, t):
    """空き地の電子。第5場面で表面へ集まり、第7場面で散る"""
    if k == 5:
        u = C.ease((lo - 1.5) / 4.5)
        return STRAY + (CHAN - STRAY) * u
    if k == 6:
        p = CHAN.copy()
        p[:, 1] += 0.18 * np.sin(t * 3.0 + np.arange(NS))
        return p
    if k == 7:
        u = C.ease((lo - 1.5) / 2.5)
        return CHAN + (STRAY - CHAN) * u
    p = STRAY.copy()
    p[:, 1] += 0.3 * np.sin(t * 1.6 + np.arange(NS))
    return p


def blocked(lo, al=1.0):
    """空き地の手前で跳ね返される粒"""
    ph = (lo % 2.6) / 2.6
    if ph < 0.55:
        x = 31.0 + (GAPL - 2.0 - 31.0) * C.ease(ph / 0.55)
    else:
        x = (GAPL - 2.0) - (GAPL - 2.0 - 31.0) * C.ease((ph - 0.55) / 0.45)
    ax.scatter([x], [56.0], s=150, c=C.HOT, zorder=9, linewidths=0, alpha=al)
    if ph > 0.45:
        ax.text(GAPL + 1.5, 56.0, "×", ha="left", va="center", fontsize=22,
                color=C.HOT, fontproperties=C.FPB, alpha=al, zorder=9)


def flowing(lo, al=1.0):
    for m in range(3):
        x = 30.0 + (lo * 26.0 + m * 33.0) % 100.0
        ax.scatter([x], [CHAN_Y], s=150, c=C.EL, zorder=9, linewidths=0,
                   alpha=al)
    ax.annotate("", xy=(112.0, 82.0), xytext=(48.0, 82.0),
                arrowprops=dict(arrowstyle="-|>", color=C.EL, lw=2.2,
                                alpha=al), zorder=9)
    ax.text(80.0, 84.0, "電気が流れている", ha="center", va="bottom",
            fontsize=14, color=C.EL, fontproperties=C.FP, alpha=al, zorder=9)


def badge(text, col, al=1.0):
    ax.text(150.0, 82.0, text, ha="right", va="center", fontsize=26,
            color=col, fontproperties=C.FPB, alpha=al, zorder=12)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "MOSFET", sub="第10回 ── 電気で、橋を架ける")
        SC.caption(ax, t)
        return []

    if k == 8:
        C.title_card(ax, SC, t, "触らずに、電気だけで入り切りする",
                     main2="動く部品がないから、いくらでも小さくできる",
                     sub="CPU1個に、これが何百億個ならんでいる")
        SC.caption(ax, t)
        return []

    device(al)
    carriers(t, al)

    # 板は第3場面で上から降りてくる
    if k >= 3:
        dy = (1 - C.ease(lo / 1.2)) * 14.0 if k == 3 else 0.0
        gate(dy, al)

    # プラスの電気は第4場面でたまり、第7場面で抜ける
    pa = 0.0
    if k in (4, 5, 6):
        pa = C.ease(lo / 0.7) if k == 4 else 1.0
    elif k == 7:
        pa = max(0.0, 1 - C.ease((lo - 0.8) / 0.8))
    plus(al * pa)

    pos = stray_pos(k, lo, t)
    ax.scatter(pos[:, 0], pos[:, 1], s=70, c=C.EL, zorder=6,
               linewidths=0, alpha=al * 0.85)

    if k <= 2:
        a2 = C.ease(lo / 0.8) if k == 1 else 1.0
        for x in (42.0, 118.0):
            ax.text(x, 64.5, "粒がいる", ha="center", va="bottom",
                    fontsize=14, color=C.MUTED, fontproperties=C.FP,
                    alpha=al * a2, zorder=6)
        # n領域と n領域のあいだ。散らばった電子の帯(y 38〜47)は避ける
        ax.text(80.0, 56.0, "空き地", ha="center", va="center", fontsize=15,
                color=C.NGC, fontproperties=C.FPB, alpha=al * a2, zorder=6)

    if k == 2:
        blocked(lo, al)
        badge("OFF", C.NGC, al)
    if k == 6:
        flowing(lo, al)
        badge("ON", C.OKC, al)
    if k == 7 and lo > 3.5:
        badge("OFF", C.NGC, al * C.ease((lo - 3.5) / 0.8))

    notes = [
        ("両側は電子が多い n。真ん中は電子の少ない p",
         "つないだだけでは、まだただの3層"),
        ("渡る道がない  →  流れない", "電圧をかけても、粒は空き地を越えられない"),
        ("触れてはいない。間にフタがある", "板と半導体は、直接つながっていない"),
        ("板と半導体で、コンデンサになっている", "第3回の2枚の板と同じ形"),
        ("散らばっていた粒が、表面に集まる", "呼ばれてくるのは、p の中にわずかにいる電子"),
        ("橋ができた  →  流れる", "板の電圧ひとつで、道が現れる"),
        ("橋が消える  →  また流れない", "電圧を戻せば、もとの空き地に戻る"),
    ]
    main, sub = notes[k - 1]
    ax.text(80, 24, main, ha="center", va="center", fontsize=23,
            color=C.OKC if k == 6 else (C.NGC if k in (2, 7) else C.INK),
            fontproperties=C.FPB, alpha=al)
    ax.text(80, 15, sub, ha="center", va="center", fontsize=15,
            color=C.MUTED, fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep10_mosfet.mp4")
