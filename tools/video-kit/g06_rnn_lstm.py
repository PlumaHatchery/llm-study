"""G検定③ RNN → LSTM ── 昔の情報が薄れる。だからゲートで守る。

  RNNを時間方向に展開し、隠れ状態が右へ渡っていくのを見せる。
  長い系列では昔の情報が褪せる（BPTTでも勾配が掛け算されるため）。
  LSTMは記憶セルと3つのゲートで「何を覚え、何を忘れ、何を出すか」を制御する。
  ノート「③ ディープラーニング」の「RNN → LSTM」に対応。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 18, 33, 49, 63, 73],
    caps=[
        "",                                            # 0 タイトル
        "前の時刻の状態を、次の時刻へ渡していく",        # 1
        "離れるほど、昔の情報は薄れていく",              # 2
        "記憶セルと、3つのゲートを足す",                # 3
        "守られた記憶の通り道が、勾配の通り道になる",     # 4
        "",                                            # 5 まとめ
    ],
)

fig, ax = C.new_axes()

WORDS = ["昨日", "私", "は", "寿司", "を", "食べた"]
NT = len(WORDS)
TX = [20.0 + j * 24.0 for j in range(NT)]
TY, TW, TH = 62.0, 17.0, 14.0
CELL_X, CELL_Y, CW, CH = 44.0, 44.0, 64.0, 26.0     # LSTMセルの拡大図


def unrolled(fade, al=1.0, upto=None):
    """展開したRNN。fade=True で古い時刻ほど薄くする"""
    n = NT if upto is None else min(upto + 1, NT)
    for j in range(NT):
        on = j < n
        a = al * (1.0 if on else 0.15)
        if fade and on:
            a = al * (0.22 + 0.78 * (j / (NT - 1)))
        C.rrect(ax, TX[j] - TW / 2, TY - TH / 2, TW, TH, C.FILL, C.EDGE,
                r=1.2, lw=1.2, al=a, z=4)
        ax.text(TX[j], TY + 2.5, "RNN", ha="center", va="center",
                fontsize=11, color=C.MUTED, fontproperties=C.FPB, alpha=a,
                zorder=5)
        ax.text(TX[j], TY - 3.5, WORDS[j], ha="center", va="center",
                fontsize=13, color=C.INK, fontproperties=C.FPB, alpha=a,
                zorder=5)
        if j < NT - 1 and j < n - 1:
            aa = al
            if fade:
                aa = al * (0.22 + 0.78 * (j / (NT - 1)))
            ax.annotate("", xy=(TX[j + 1] - TW / 2 - 1, TY),
                        xytext=(TX[j] + TW / 2 + 1, TY),
                        arrowprops=dict(arrowstyle="-|>", color=C.EL,
                                        lw=2.2, alpha=aa), zorder=6)
    ax.text(TX[0] - TW / 2 - 3.0, TY, "時刻 →", ha="right", va="center",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def memory_bar(vals, y, col, lab, al=1.0):
    """各時刻で「昨日」がどれだけ残っているか"""
    for j, v in enumerate(vals):
        h = max(0.6, 13.0 * v)
        C.rrect(ax, TX[j] - 4.0, y, 8.0, h, col, "none", r=0.6,
                al=al * 0.9, z=4)
        ax.text(TX[j], y - 3.0, "%.2f" % v, ha="center", va="top",
                fontsize=11, color=col if v > 0.15 else C.NGC,
                fontproperties=C.FPB, alpha=al, zorder=5)
    ax.text(TX[0] - TW / 2 - 2.0, y + 7.0, lab, ha="right", va="center",
            fontsize=12, color=C.MUTED, fontproperties=C.FP, alpha=al,
            zorder=5)


def lstm_cell(lo, al=1.0):
    """記憶セルと3つのゲート。周期的に開閉する"""
    C.rrect(ax, CELL_X, CELL_Y, CW, CH, C.BG, C.EDGE, r=1.6, lw=1.4,
            al=al, z=3)
    ax.text(CELL_X + CW / 2, CELL_Y + CH + 2.5, "LSTM セル", ha="center",
            va="bottom", fontsize=14, color=C.INK, fontproperties=C.FPB,
            alpha=al, zorder=5)
    # 記憶の通り道（セルの上を素通りする線）
    ax.plot([CELL_X - 8.0, CELL_X + CW + 8.0],
            [CELL_Y + CH - 5.0, CELL_Y + CH - 5.0], color=C.OKC, lw=3.4,
            solid_capstyle="round", zorder=6, alpha=al)
    ax.text(CELL_X + CW + 9.0, CELL_Y + CH - 5.0, "記憶", ha="left",
            va="center", fontsize=13, color=C.OKC, fontproperties=C.FPB,
            alpha=al, zorder=6)
    gates = [("入力", 0.0), ("忘却", 0.33), ("出力", 0.66)]
    for j, (name, ph) in enumerate(gates):
        x = CELL_X + 11.0 + j * 21.0
        openness = 0.5 + 0.5 * np.sin(2 * np.pi * (lo * 0.35 + ph))
        C.rrect(ax, x - 7.0, CELL_Y + 5.0, 14.0, 9.0, C.FILL, C.EDGE,
                r=0.9, lw=1.2, al=al, z=5)
        C.rrect(ax, x - 7.0, CELL_Y + 5.0, 14.0 * openness, 9.0,
                C.HOT if openness > 0.5 else C.NGC, "none", r=0.9,
                al=al * 0.85, z=6)
        ax.text(x, CELL_Y + 9.5, name, ha="center", va="center",
                fontsize=12, color=C.INK, fontproperties=C.FPB, alpha=al,
                zorder=7)
        ax.text(x, CELL_Y + 1.5, "%d%%" % int(openness * 100), ha="center",
                va="center", fontsize=11, color=C.MUTED,
                fontproperties=C.FPB, alpha=al, zorder=7)
        ax.plot([x, x], [CELL_Y + 14.0, CELL_Y + CH - 5.0], color=C.GRAY,
                lw=1.2, ls=(0, (2, 2)), zorder=5, alpha=al * 0.8)
    ax.text(CELL_X + CW / 2, CELL_Y - 4.0,
            "何を覚え、何を忘れ、何を出すかを、学習で決める",
            ha="center", va="top", fontsize=13, color=C.MUTED,
            fontproperties=C.FP, alpha=al, zorder=5)


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    lo = SC.local(t)
    al = C.ease(lo / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "RNN と LSTM",
                     sub="G検定③ ── 覚えていられる距離の話")
        SC.caption(ax, t)
        return []

    if k == 5:
        C.title_card(ax, SC, t, "同じ箱を、時刻の数だけ並べたもの",
                     main2="だから時間方向にも、勾配の掛け算が起きる",
                     sub="ゲートで通り道を守る。GRU はその簡略版")
        SC.caption(ax, t)
        return []

    if k == 1:
        upto = int(np.clip((lo - 0.8) / 1.5, 0, NT - 1))
        unrolled(False, al, upto)
        ax.text(80, 24, "同じ箱を、時刻の数だけ横に並べたもの", ha="center",
                va="center", fontsize=22, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "重みは全時刻で共通。渡していくのは隠れ状態だけ",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    if k == 2:
        unrolled(True, al)
        memory_bar([0.62 ** j for j in range(NT)], 38.0, C.HOT, "残り", al)
        ax.text(80, 24, "6語さきでは、もう 0.09 しか残っていない",
                ha="center", va="center", fontsize=21, color=C.HOT,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "時間方向の逆伝播でも、勾配が掛け算される（長期依存の問題）",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
        SC.caption(ax, t)
        return []

    lstm_cell(lo, al)
    if k == 4:
        memory_bar([0.94 ** j for j in range(NT)], 22.0, C.OKC, "残り", al)
        ax.text(80, 12, "6語さきでも 0.73。掛け算ではなく、足し引きで更新するから",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)
    else:
        ax.text(80, 24, "ゲートは 0〜1 の蛇口。開き具合も学習する",
                ha="center", va="center", fontsize=21, color=C.INK,
                fontproperties=C.FPB, alpha=al)
        ax.text(80, 15, "忘却ゲートが閉じれば、その記憶はそのまま保たれる",
                ha="center", va="center", fontsize=14, color=C.MUTED,
                fontproperties=C.FP, alpha=al)

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/g06_rnn_lstm.mp4")
