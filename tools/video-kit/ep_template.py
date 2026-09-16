"""各話のひな形。これをコピーして中身を差し替える。

  python3 ep_template.py            → out/ep_template.mp4
  python3 check.py out/ep_template.mp4 2 8 14   → 指定秒のフレームをPNGに

必ず check.py で静止画を目で見てから次へ進む。ffmpeg が成功しても
ラベルが重なっていたり画面外に出ていたりは普通に起きる。
"""
import numpy as np
import common as C

SC = C.Scenes(
    bounds=[0, 5, 12, 18],
    caps=[
        "",                                  # 0: タイトル
        "ここに、この回の中心になる動きを置く",   # 1: 本編
        "",                                  # 2: まとめ
    ],
)

fig, ax = C.new_axes()


def draw(i):
    t = i / C.FPS
    C.reset(ax)
    k = SC.idx(t)
    al = C.ease(SC.local(t) / 0.5)

    if k == 0:
        C.title_card(ax, SC, t, "この回の題", sub="第N回 ── 副題")

    elif k == 1:
        # --- 本編。座標は 160 x 90 の系で考える ---
        C.rrect(ax, 40, 44, 80, 14, C.FILL, C.EDGE, al=al, z=3)
        u = C.ease(SC.local(t) / 4.0)          # 0→1 でゆっくり動かす
        x = 46 + 68 * u
        ax.scatter([x], [51], s=200, c=C.EL, zorder=6, linewidths=0)
        ax.text(80, 66, "補助ラベル", ha="center", va="bottom", fontsize=15,
                color=C.MUTED, fontproperties=C.FP, alpha=al)
        # 数値や式はこの高さに置くと字幕とぶつからない
        ax.text(80, 25, "式や数値はこのあたり", ha="center", va="center",
                fontsize=23, color=C.INK, fontproperties=C.FPB, alpha=al)

    else:
        C.title_card(ax, SC, t, "この回の結論を一行で",
                     sub="次につながる一言")

    SC.caption(ax, t)
    return []


if __name__ == "__main__":
    C.render(fig, draw, SC, "out/ep_template.mp4")
