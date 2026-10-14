"""冒頭フック(1等が出た回の割合)と、ルナの6数字だけのカード。使い方: python3 scripts/make_hook_cards.py <次回の回号>"""
import sys, json, openpyxl
from PIL import Image, ImageDraw, ImageFont
N = int(sys.argv[1]); p = json.load(open(f"data/picks/{N}.json"))
rows = [x for x in openpyxl.load_workbook("data/loto6_all.xlsx", read_only=True).active.iter_rows(values_only=True)][1:]
n = len(rows); hit = sum(1 for x in rows if x[9] > 0); pct = round(hit/n*100)
W, H = 1080, 1920; FD = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F = lambda w, s: ImageFont.truetype(FD.format(w), s)
BG = (10, 14, 30); GOLD = (240, 190, 90); WHITE = (245, 247, 252); GR = (150, 158, 180); BLUE = (90, 160, 230); CB = (26, 32, 58)
def new():
    im = Image.new("RGB", (W, H), BG); return im, ImageDraw.Draw(im)
def ct(d, y, t, fn, fill):
    b = d.textbbox((0, 0), t, font=fn); d.text((W/2-(b[2]-b[0])/2, y), t, font=fn, fill=fill)
# フック
im, d = new()
ct(d, 200, "第1回〜第%d回のデータ" % p["draws"], F("Medium", 40), GR)
ct(d, 330, "1等が出た回", F("Bold", 72), WHITE)
ct(d, 470, "%d%%" % pct, F("Bold", 300), GOLD)
ct(d, 860, "%s回中 %s回" % (format(n, ","), format(hit, ",")), F("Bold", 56), WHITE)
ct(d, 960, "日本のだれかが当てている", F("Medium", 44), BLUE)
d.rounded_rectangle([60, 1160, W-60, 1560], radius=30, fill=CB, outline=(60, 70, 110), width=3)
ct(d, 1210, "でも、自分が1等を当てる確率は", F("Bold", 42), WHITE)
ct(d, 1310, "1 / 6,096,454", F("Bold", 96), (255, 150, 130))
ct(d, 1450, "どの6数字でも同じ", F("Medium", 38), GR)
ct(d, 1830, "AI×LOTTO LAB", F("Regular", 26), GR)
im.save(f"cards/hook_{N}.png")
# 6数字
im, d = new()
ct(d, 170, "第%d回 ルナの6数字" % N, F("Bold", 64), WHITE)
ct(d, 262, "全%d回のデータを分析して選びました" % p["draws"], F("Medium", 34), BLUE)
for i, v in enumerate(p["luna"]):
    r, c = divmod(i, 3); cx = 230+c*310; cy = 560+r*330
    d.ellipse([cx-130, cy-130, cx+130, cy+130], fill=GOLD)
    t = str(v); b = d.textbbox((0, 0), t, font=F("Bold", 130)); d.text((cx-(b[2]-b[0])/2, cy-(b[3]-b[1])/2-b[1]), t, font=F("Bold", 130), fill=(20, 20, 30))
d.rounded_rectangle([60, 1260, W-60, 1560], radius=26, fill=(30, 24, 20), outline=(120, 90, 50), width=2)
d.text((100, 1290), "⚠ 当てる方法ではありません", font=F("Bold", 38), fill=(240, 180, 120))
d.text((100, 1360), "抽せんは毎回独立。当せん確率は、どの6数字でも同じです。", font=F("Regular", 28), fill=WHITE)
d.text((100, 1410), "エンタメとして、結果を毎回公開して検証します。", font=F("Regular", 28), fill=WHITE)
ct(d, 1640, "答え合わせは、金曜の朝", F("Bold", 50), GOLD)
ct(d, 1830, "AI×LOTTO LAB", F("Regular", 26), GR)
im.save(f"cards/numbers_{N}.png"); print(pct, hit, n)
