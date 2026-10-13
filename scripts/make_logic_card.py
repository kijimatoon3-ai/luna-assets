"""ルナの「人気度マップ」カード。使い方: python3 scripts/make_logic_card.py <次回の回号>
過去全回の当せん者数から推定した、1〜43の人気度を色で表示し、ルナの6数字を金枠で示す。"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
N = int(sys.argv[1]); p = json.load(open(f"data/picks/{N}.json")); b = {int(k): v for k, v in p["b"].items()}
W, H = 1080, 1920; FD = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F = lambda w, s: ImageFont.truetype(FD.format(w), s)
BG = (10, 14, 30); GOLD = (240, 190, 90); WHITE = (245, 247, 252); GR = (150, 158, 180)
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
def ct(y, t, fn, fill):
    bb = d.textbbox((0, 0), t, font=fn); d.text((W/2-(bb[2]-bb[0])/2, y), t, font=fn, fill=fill)
ct(130, "ルナの人気度マップ", F("Bold", 68), WHITE)
ct(230, "過去%d回の当せん者数から、数字ごとの“選ばれやすさ”を推定" % p["draws"], F("Medium", 31), GR)
lo, hi = min(b.values()), max(b.values())
def col(v):   # 青(人気薄) → 暗い中間 → 赤(人気)
    t = (v-lo)/(hi-lo)
    return (int(40+215*t), int(110-50*abs(t-.5)*2+30), int(230-190*t))
cell, gap, x0, y0 = 128, 14, 60, 330
for n in range(1, 44):
    r, c = divmod(n-1, 7); x = x0+c*(cell+gap); y = y0+r*(cell+gap)
    d.rounded_rectangle([x, y, x+cell, y+cell], radius=20, fill=col(b[n]), outline=GOLD if n in p["luna"] else None, width=8 if n in p["luna"] else 0)
    t = str(n); bb = d.textbbox((0, 0), t, font=F("Bold", 54)); d.text((x+cell/2-(bb[2]-bb[0])/2, y+cell/2-(bb[3]-bb[1])/2-bb[1]), t, font=F("Bold", 54), fill=WHITE)
yb = y0+7*(cell+gap)+10
d.rectangle([80, yb, 320, yb+30], fill=col(lo)); d.rectangle([360, yb, 720, yb+30], fill=col((lo+hi)/2)); d.rectangle([760, yb, 1000, yb+30], fill=col(hi))
d.text((80, yb+40), "人気薄", font=F("Medium", 28), fill=GR); d.text((880, yb+40), "人気", font=F("Medium", 28), fill=GR)
pop = "・".join(map(str, p["popular"][:5])); unp = "・".join(map(str, p["unpopular"][:5]))
ct(yb+110, "人気ベスト5: " + pop, F("Bold", 40), (255, 150, 130)); ct(yb+175, "人気薄ベスト5: " + unp, F("Bold", 40), (140, 190, 255))
ct(yb+260, "金の枠 = 第%d回のルナの6数字" % N, F("Medium", 34), GOLD)
ct(1830, "AI×LOTTO LAB  ※当せん確率は、どの数字でも同じです", F("Regular", 26), GR)
im.save(f"cards/logic_{N}.png"); print("saved", f"cards/logic_{N}.png")
