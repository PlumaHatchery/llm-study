import json
import numpy as np
import pyopenjtalk
import scipy.io.wavfile as wav

LINES = [
    "トランジスタは、どうやって電気を通したり、止めたりしているのか。順番に見ていきます。",
    "まず、電気が流れるというのは、電子という小さな粒が、ぞろぞろと移動することです。",
    "左と右には、この粒がたくさんいます。でも真ん中は空き地で、粒がほとんどいません。だから左の粒は、右へ渡れません。これがオフの状態です。",
    "そこで、空き地の上にフタをして、その上に金属の板を置きます。これをゲートと呼びます。",
    "この板に、プラスの電気をためます。",
    "プラスはマイナスを引き寄せます。下敷きをこすると髪が逆立つ、あれと同じ力です。空き地に散らばっていたわずかな粒が、板に引っぱられて、表面に集まってきます。",
    "集まった粒がつながって、橋になりました。左から右へ、電気が流れます。これがオンの状態です。",
    "板の電気を抜けば、粒は散って、橋は消えます。",
    "つまりこれは、電気で入り切りできるスイッチです。これがたった一個。シーピーユーの中には、これが何百億個も入っています。",
]

SR = 48000
durs = []
clips = []
for i, s in enumerate(LINES):
    x, sr = pyopenjtalk.tts(s)
    x = x / max(np.max(np.abs(x)), 1e-9) * 0.85
    clips.append(x.astype(np.float32))
    durs.append(len(x) / sr)
    print(i, round(len(x) / sr, 2), s[:18])

np.save("/home/claude/clips.npy", np.array(clips, dtype=object),
        allow_pickle=True)
json.dump(durs, open("/home/claude/durs.json", "w"))
print("total speech", round(sum(durs), 1))
