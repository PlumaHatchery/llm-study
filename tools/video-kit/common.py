"""共通モジュール。各話のスクリプトはこれを import して書く。

使い方は README.md を参照。設計意図は3つ:
  1. 見た目(色・フォント・字幕位置)を全話で固定する
  2. シーン境界を秒で宣言し、そこから逆算して描く
  3. draw(frame) を「その時刻の画を全部描き直す関数」に保つ(状態を持たない)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
from matplotlib.animation import FuncAnimation, FFMpegWriter

# --- フォント: 環境依存。上から順に探して最初に見つかった組を使う。
#     増やすときは fc-list :lang=ja の結果から (通常, 太め) の対で足す ---
import os

_CANDIDATES = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
     "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"),
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
     "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"),
]


def _pick_font():
    for reg, bold in _CANDIDATES:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold
    raise RuntimeError(
        "日本語フォントが見つからない。fc-list :lang=ja の結果を "
        "common.py の _CANDIDATES に足すこと")


_REG, _BOLD = _pick_font()
FP = FontProperties(fname=_REG)
FPB = FontProperties(fname=_BOLD)

# --- 配色。勝手に増やさない。増やすと全話でバラける ---
BG = "#FAF9F5"        # 背景
INK = "#2C2C2A"       # 本文
MUTED = "#5F5E5A"     # 補助ラベル
EL = "#185FA5"        # 電子・信号(青)
ELL = "#378ADD"       # 青の明るいほう
HOT = "#D85A30"       # 注目・熱・だめな方(橙)
DEEP = "#A32D2D"      # プラス電荷・強調(赤)
OKC = "#0F6E56"       # 通った・ON(緑)
NGC = "#993C1D"       # 通らない・OFF(茶)
GRAY = "#B4B2A9"      # 導線・原子
FILL = "#E8E6DE"      # 部品の塗り
EDGE = "#888780"      # 部品の枠

FPS = 20
FIGSIZE = (12.8, 7.2)   # 1280x720
XLIM, YLIM = 160, 90    # 描画座標系。実ピクセルの1/8

# 字幕は必ずこの位置・このサイズ。全話で揃えるため触らない
CAP_Y, CAP_SIZE = 7, 21


def ease(u):
    """0..1 に丸めた上で滑らかに補間(フェードにも移動にも使う)"""
    u = min(max(float(u), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def plen(pts):
    p = np.array(pts, dtype=float)
    d = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    return p, np.concatenate([[0], np.cumsum(d)])


def ppt(pts, u):
    """折れ線 pts を弧長で正規化し、u(0..1、はみ出しは巻き戻し)の座標を返す"""
    p, cs = plen(pts)
    s = (u % 1.0) * cs[-1]
    j = int(np.clip(np.searchsorted(cs, s) - 1, 0, len(cs) - 2))
    f = (s - cs[j]) / max(cs[j + 1] - cs[j], 1e-9)
    return p[j] + (p[j + 1] - p[j]) * f


def rrect(ax, x, y, w, h, fc, ec, r=1.2, lw=1.2, al=1.0, z=2):
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2 * r, h - 2 * r,
                                boxstyle="round,pad=%f" % r, fc=fc, ec=ec,
                                lw=lw, alpha=al, zorder=z))


class Scenes:
    """シーン境界(秒)と字幕のまとめ。bounds は要素数 = 字幕数 + 1"""

    def __init__(self, bounds, caps):
        assert len(bounds) == len(caps) + 1, "bounds は caps より1個多い"
        self.b = bounds
        self.caps = caps
        self.dur = bounds[-1]
        self.nframes = int(FPS * self.dur)

    def idx(self, t):
        for i in range(len(self.caps)):
            if self.b[i] <= t < self.b[i + 1]:
                return i
        return len(self.caps) - 1

    def local(self, t):
        """そのシーンに入ってからの経過秒"""
        return t - self.b[self.idx(t)]

    def fade(self, t, up=0.5, down=0.4):
        """シーン頭で明け、終わりで暮れる 0..1"""
        i = self.idx(t)
        return max(0.0, min(1.0, (t - self.b[i]) / up,
                            (self.b[i + 1] - t) / down))

    def caption(self, ax, t):
        c = self.caps[self.idx(t)]
        if not c:
            return
        ax.text(XLIM / 2, CAP_Y, c, ha="center", va="center", fontsize=CAP_SIZE,
                color=INK, fontproperties=FPB, alpha=self.fade(t), zorder=12)


def new_axes():
    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    return fig, ax


def reset(ax):
    """draw() の先頭で必ず呼ぶ。毎フレーム全消し全描きが前提"""
    ax.clear()
    ax.set_xlim(0, XLIM)
    ax.set_ylim(0, YLIM)
    ax.axis("off")


def title_card(ax, sc, t, main, sub=None, main2=None):
    a = ease(sc.local(t) / 0.5)
    y = 55 if main2 is None else 60
    ax.text(80, y, main, ha="center", va="center", fontsize=32, color=INK,
            fontproperties=FPB, alpha=a)
    if main2:
        ax.text(80, 47, main2, ha="center", va="center", fontsize=32,
                color=INK, fontproperties=FPB, alpha=a)
    if sub:
        ax.text(80, 33 if main2 else 38, sub, ha="center", va="center",
                fontsize=18, color=MUTED, fontproperties=FP, alpha=a)


def render(fig, draw, sc, out):
    ani = FuncAnimation(fig, draw, frames=sc.nframes,
                        interval=1000 / FPS, blit=False)
    w = FFMpegWriter(fps=FPS, bitrate=2600,
                     extra_args=["-pix_fmt", "yuv420p", "-vcodec", "libx264"])
    ani.save(out, writer=w, dpi=100, savefig_kwargs={"facecolor": BG})
    print("rendered", out, round(sc.dur, 1), "sec")
