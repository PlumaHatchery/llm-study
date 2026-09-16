"""第36回 デーモンとcron ── 出発点が、いちばん上に立っていた。

  cron は「寝て、起きて、表を見て、時刻が合えば起動する」だけのループ。
  使っているシステムコールは、ほかのアプリと同じ。
  そのループが、ここまでの35回すべての上に乗っている。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 22, 38, 56, 67],
    caps=[
        "",                                            # 0 タイトル
        "寝て、起きて、表を見て、合えば起動する",         # 1
        "使っているのは、ごく普通のシステムコール",        # 2
        "その下に、35回ぶんが積んである",                # 3
        "",                                            # 4 まとめ
    ],
)

fig, ax = C.new_axes()

STEPS = ["寝る", "起きる", "表を見る", "時刻が合えば起動"]
CALLS = ["nanosleep", "（タイマ割り込み）", "read", "fork + exec"]
SX = [24.0, 60.0, 96.0, 132.0]
SW, SH, SY = 30.0, 13.0, 68.0
CRON = [("毎日 4:00", "backup.sh"),
        ("5分ごと", "check-health.sh")]
STACK = ["第1部 電気そのもの", "第2部 半導体", "第3部 時間をつくる",
         "第4部 論理", "第5部 コンピュータになる", "第6部 OS"]


def loop(step, al=1.0, calls=False):
    for j, (x, name) in enumerate(zip(SX, STEPS)):
        on = (j == step)
        C.rrect(ax, x - SW / 2, SY - SH / 2, SW, SH,
                C.FILL if on else C.BG, C.OKC if on else C.EDGE, r=1.2,
                lw=1.8 if on else 1.1, al=al, z=4)
        # 呼び出し名は箱の中に入れる。下に出すと表とぶつかる
        ax.text(x, SY + (2.6 if calls else 0.0), name, ha="center",
                va="center", fontsize=13,
                color=C.OKC if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        if calls:
            ax.text(x, SY - 3.4, CALLS[j], ha="center", va="center",
                    fontsize=11, color=C.HOT, fontproperties=C.FPB,
                    alpha=al, zorder=5)
        if j < 3:
            ax.annotate("", xy=(SX[j + 1] - SW / 2 - 1, SY),
                        xytext=(x + SW / 2 + 1, SY),
                        arrowprops=dict(arrowstyle="-|>", color=C.GRAY,
                                        lw=1.4, alpha=al), zorder=5)
    y = SY + SH / 2 + 6.0
    ax.plot([SX[-1], SX[-1], SX[0], SX[0]],
            [SY + SH / 2, y, y, SY + SH / 2], color=C.GRAY, lw=1.4,
            zorder=3, alpha=al)
    ax.text((SX[0] + SX[-1]) / 2, y + 1.5, "また寝る", ha="center",
            va="bottom", fontsize=12, color=C.MUTED, fontproperties=C.FP,
            alpha=al, zorder=5)


def crontab(hit, al=1.0):
    x, y0, w = 34.0, 48.0, 92.0
    C.rrect(ax, x, y0 - 3.0 - len(CRON) * 7.5, w,
            len(CRON) * 7.5 + 9.0, C.BG, C.EDGE, r=1.2, lw=1.2, al=al, z=3)
    ax.text(x + w / 2, y0 + 2.0, "表（crontab）", ha="center", va="center",
            fontsize=13, color=C.INK, fontproperties=C.FPB, alpha=al,
            zorder=5)
    ax.plot([x + 3, x + w - 3], [y0 - 2.0, y0 - 2.0], color=C.GRAY, lw=0.9,
            zorder=4, alpha=al)
    for j, (when, what) in enumerate(CRON):
        yy = y0 - 6.5 - j * 7.5
        on = (j == hit)
        ax.text(x + 5.0, yy, when, ha="left", va="center", fontsize=12,
                color=C.HOT if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)
        ax.text(x + w - 5.0, yy, what, ha="right", va="center", fontsize=12,
                color=C.OKC if on else C.MUTED, fontproperties=C.FPB,
                alpha=al, zorder=5)


def stack(upto, al=1.0):
    for j, name in enumerate(STACK):
        y = 26.0 + j * 8.0
        shown = j <= upto
        C.rrect(ax, 30.0, y, 100.0, 7.0, C.FILL if shown else C.BG,
                C.EDGE if shown else "#E4E2DA", r=0.8, lw=1.1,
                al=al * (1.0 if shown else 0.25), z=3)
        ax.text(80.0, y + 3.5, name, ha="center", va="center", fontsize=13,
                color=C.MUTED, fontproperties=C.FPB,
                alpha=al * (1.0 if shown else 0.25), zorder=5)
    top = (upto >= len(STACK) - 1)
    C.rrect(ax, 30.0, 74.0, 100.0, 8.0, C.FILL if top else C.BG,
            C.OKC if top else "#E4E2DA", r=0.8, lw=1.8,
            al=al * (1.0 if top else 0.25), z=4)
    ax.text(80.0, 78.0, "cron（寝て、起きて、表を見るだけ）", ha="center",
            va="center", fontsize=14, color=C.OKC, fontproperties=C.FPB,
            alpha=al * (1.0 if top else 0.25), zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "デーモンとcron",
                     sub="第36回 ── 出発点に戻ってくる")
        SC.caption(ax, t)
        return []

    if k == 4:
        C.title_card(ax, SC, t, "いちばん単純なループが、",
                     main2="いちばん高いところに立っていた",
                     sub="電子のドリフトから、ここまで。全36回、了")
        SC.caption(ax, t)
        return []

    if k == 3:
        upto = min(int(max(lo - 1.0, 0) / 1.9), len(STACK) - 1)
        stack(upto, al)
        ax.text(80, 20, "どれが欠けても、この行は動かない", ha="center",
                va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 13, "時刻を数えているのは、第13回の水晶振動子",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    step = int(max(lo - 0.8, 0) / 1.9) % 4
    hit = 1 if step == 3 else None
    loop(step, al, calls=(k == 2))
    crontab(hit, al)

    if k == 1:
        ax.text(80, 20, "それだけ。ほかには何もしていない", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 13, "常駐プロセス（デーモン）は、たいていこの形",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 20, "特別な権限も、特別な命令も使っていない",
                ha="center", va="center", fontsize=21, color=C.OKC,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 13, "第32回の扉を、ほかのアプリと同じように通っている",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep36_cron.mp4")
