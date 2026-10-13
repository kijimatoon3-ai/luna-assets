"""理論を図で見せるカード2枚。python3 scripts/make_explain_cards.py <次回の回号>
 cards/flow_<N>.png    : ルナ式ロジックの流れ(4ステップ)
 cards/evidence_<N>.png: 人気度の推定が当たっている証拠(検証データの散布図)"""
import sys, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image, ImageDraw, ImageFont
N = int(sys.argv[1]); p = json.load(open(f"data/picks/{N}.json")); sc = json.load(open("data/oos_scatter.json"))
FD = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F = lambda w, s: ImageFont.truetype(FD.format(w), s)
W, H = 1080, 1920; BG = (10, 14, 30); GOLD = (240, 190, 90); BLUE = (90, 160, 230); WHITE = (245, 247, 252); GR = (150, 158, 180); CB = (26, 32, 58); CBD = (60, 70, 110)
def ct(d, y, t, fn, fill):
    bb = d.textbbox((0, 0), t, font=fn); d.text((W/2-(bb[2]-bb[0])/2, y), t, font=fn, fill=fill)
# ---- 流れカード
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
ct(d, 120, "ルナ式ロジック", F("Bold", 70), WHITE); ct(d, 215, "4ステップで6数字を決める", F("Medium", 34), GR)
steps = [("1", "過去%d回ぶんを読み込む" % p["draws"], "当せん数字 と 3〜5等の当せん者の数"),
         ("2", "数字ごとの『被り度』を推定", "当せん者が多い回 = みんなが選びがちな数字が出た回"),
         ("3", "全6,096,454通りを採点", "組み合わせごとに『被りやすさ』を計算"),
         ("4", "被りにくい組から1組を抽せん", "上位固定にしないので、毎回ちがう6数字")]
y = 300
for i, (n, t, sub) in enumerate(steps):
    d.rounded_rectangle([60, y, W-60, y+300], radius=28, fill=CB, outline=GOLD if i == 3 else CBD, width=4 if i == 3 else 3)
    d.ellipse([90, y+30, 170, y+110], fill=GOLD); bb = d.textbbox((0, 0), n, font=F("Bold", 52)); d.text((130-(bb[2]-bb[0])/2, 70+y-(bb[3]-bb[1])/2-bb[1]+0), n, font=F("Bold", 52), fill=(20, 20, 30))
    d.text((200, y+36), t, font=F("Bold", 44), fill=WHITE); d.text((200, y+110), sub, font=F("Regular", 30), fill=GR)
    # 各ステップのミニ図
    if i == 0:
        for k in range(24): h = 20+((k*37)%60); d.rectangle([200+k*34, y+270-h, 200+k*34+22, y+270], fill=BLUE)
    if i == 1:
        for k in range(14):
            v = p["b"][str(k*3+1)]; c = (230, 110, 60) if v > 0.05 else (90, 130, 220) if v < -0.04 else (140, 140, 150)
            d.rounded_rectangle([200+k*54, y+200, 200+k*54+44, y+264], radius=8, fill=c)
    if i == 2:
        ct(d, y+190, "6,096,454", F("Bold", 70), GOLD)
    if i == 3:
        ct(d, y+190, "  →   " + "・".join(map(str, p["luna"])), F("Bold", 56), GOLD)
    y += 330
    if i < 3: d.polygon([(W/2-30, y-28), (W/2+30, y-28), (W/2, y)], fill=GR)
ct(d, 1780, "※当せん確率は、どの数字でも同じです", F("Regular", 28), GR)
im.save(f"cards/flow_{N}.png")
# ---- 証拠カード(散布図)
fp = fm.FontProperties(fname=FD.format("Bold").replace("{}", "Bold"), size=1)
plt.rcParams["font.family"] = ["Noto Sans CJK JP"]
fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor="#0a0e1e"); ax = fig.add_axes([0.14, 0.30, 0.78, 0.42], facecolor="#121832")
x = np.array(sc["pred"]); yv = np.array(sc["actual"]); m, c = np.polyfit(x, yv, 1)
ax.scatter(x, yv, s=26, color="#5aa0e6", alpha=.7, edgecolors="none"); xs = np.linspace(x.min(), x.max(), 10); ax.plot(xs, m*xs+c, color="#f0be5a", lw=5)
ax.tick_params(colors="#9aa2b8", labelsize=18); [s.set_color("#3c4670") for s in ax.spines.values()]
ax.set_xlabel("ルナの予測(その回の“被りやすさ”)", color="#f5f7fc", fontsize=26, labelpad=18); ax.set_ylabel("実際の当せん者の多さ", color="#f5f7fc", fontsize=26, labelpad=18)
fig.text(0.5, 0.90, "この人気度推定、合ってる?", color="#f5f7fc", fontsize=54, ha="center", weight="bold")
fig.text(0.5, 0.855, "学習に使っていない %d回で、予測と実際を比べた" % sc["n"], color="#9aa2b8", fontsize=28, ha="center")
fig.text(0.5, 0.78, "相関 %.2f" % sc["corr"], color="#f0be5a", fontsize=80, ha="center", weight="bold")
fig.text(0.5, 0.74, "(1.0が満点 / 0なら当てずっぽう)", color="#9aa2b8", fontsize=26, ha="center")
fig.text(0.5, 0.22, "右上がり = 予測が当たっている", color="#f5f7fc", fontsize=34, ha="center", weight="bold")
fig.text(0.5, 0.17, "ただし当せん確率そのものは変わりません", color="#9aa2b8", fontsize=26, ha="center")
fig.savefig(f"cards/evidence_{N}.png", facecolor=fig.get_facecolor()); print("saved")
