"""ルナ毎週パイプライン(カード・予想・戦績の生成)。リポジトリのルートから実行する。

使い方:
  python3 scripts/weekly.py --result data/result.json --next 2145
    result.json 例(直前に終わった回の公式結果):
      {"draw":2144,"date":"2026-10-08","nums":[..6..],"bonus":0,
       "counts":[1等,2等,3等,4等,5等の口数],"prizes":[1等〜5等の賞金],"carry":0}
  1) data/loto6_all.xlsx に結果を追記(すでにあれば何もしない)
  2) data/picks/<draw>.json に保存済みの「ルナ・ランダムの予想」と照合し、戦績 data/scoreboard.json を更新
  3) luna_method.py で次回(--next)の予想を計算し data/picks/<next>.json に保存
  4) カード2枚を cards/ に出力: answer_<draw>.png(答え合わせ)、pred_<next>.png(予想)
"""
import argparse, json, os, shutil, subprocess, sys, datetime
import openpyxl
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--result", required=True)
ap.add_argument("--next", type=int, required=True)
ap.add_argument("--next-date", default="")          # 例 "10/12(月)"
a = ap.parse_args()
R = json.load(open(a.result))
if not a.next_date:   # 次回の抽せん日(月・木)を自動で出す
    d0 = datetime.date.fromisoformat(R["date"]); n = d0 + datetime.timedelta(days=1)
    while n.weekday() not in (0, 3): n += datetime.timedelta(days=1)
    a.next_date = "%d/%d %s" % (n.month, n.day, "月火水木金土日"[n.weekday()])
    print("next-date auto:", a.next_date)
D, NEXT = R["draw"], a.next
os.makedirs("data/picks", exist_ok=True); os.makedirs("cards", exist_ok=True)

# 1) データ追記
wb = openpyxl.load_workbook("data/loto6_all.xlsx"); ws = wb.active
have = {r[0] for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}
if D not in have:
    ws.append([D, datetime.datetime.fromisoformat(R["date"]), *R["nums"], R["bonus"], *R["counts"], *R["prizes"], R.get("carry", 0)])
    wb.save("data/loto6_all.xlsx"); print("appended", D)
else:
    print("already in data:", D)

# 2) 戦績
pk = json.load(open(f"data/picks/{D}.json"))
hit = lambda p: len(set(p) & set(R["nums"]))
sb = json.load(open("data/scoreboard.json")) if os.path.exists("data/scoreboard.json") else {"rows": []}
sb["rows"] = [x for x in sb["rows"] if x["draw"] != D]
sb["rows"].append({"draw": D, "luna": pk["luna"], "random": pk["random"], "luna_hit": hit(pk["luna"]), "random_hit": hit(pk["random"]),
                   "luna_bonus": R["bonus"] in pk["luna"], "random_bonus": R["bonus"] in pk["random"],
                   "nums": R["nums"], "bonus": R["bonus"], "counts": R["counts"]})
sb["rows"].sort(key=lambda x: x["draw"])
json.dump(sb, open("data/scoreboard.json", "w"), ensure_ascii=False, indent=1)
tl = sum(x["luna_hit"] for x in sb["rows"]); tr = sum(x["random_hit"] for x in sb["rows"]); n = len(sb["rows"])

# 3) 次回予想(luna_method.py は data/ で実行)
subprocess.run([sys.executable, "../scripts/luna_method.py", str(NEXT)], cwd="data", check=True)
shutil.copy("data/luna_pick.json", f"data/picks/{NEXT}.json")
nx = json.load(open(f"data/picks/{NEXT}.json"))

# 4) カード
W, H = 1080, 1920
FD = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"
F = lambda w, s: ImageFont.truetype(FD.format(w), s)
def ct(d, y, t, fn, fill, cx=W/2):
    b = d.textbbox((0, 0), t, font=fn); d.text((cx-(b[2]-b[0])/2, y), t, font=fn, fill=fill)

# 答え合わせカード(明るい配色)
BG=(250,248,242);CARD=(243,238,231);DARK=(40,38,34);GREY=(120,116,108);OR=(230,126,34);HL=(255,214,150)
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
def row(nums, y, hl=()):
    for i, n in enumerate(nums):
        x = 70 + i*160
        d.rounded_rectangle([x, y, x+140, y+140], radius=22, fill=HL if n in hl else CARD)
        t = "%d" % n; b = d.textbbox((0, 0), t, font=F("Bold", 64))
        d.text((x+70-(b[2]-b[0])/2, y+70-(b[3]-b[1])/2-b[1]), t, font=F("Bold", 64), fill=DARK)
win = set(R["nums"])
ct(d, 170, "第%d回 答え合わせ" % D, F("Bold", 52), GREY)
ct(d, 270, "当せん番号", F("Bold", 40), GREY); row(R["nums"], 340)
ct(d, 500, "ボーナス %d" % R["bonus"], F("Bold", 40), GREY)
ct(d, 640, "ルナ(人気薄の逆張り)", F("Bold", 44), OR); row(pk["luna"], 720, win)
ct(d, 890, "一致 %d個" % hit(pk["luna"]), F("Bold", 64), OR)
ct(d, 1080, "ランダム(くじ引き)", F("Bold", 44), GREY); row(pk["random"], 1160, win)
ct(d, 1330, "一致 %d個" % hit(pk["random"]), F("Bold", 64), GREY)
verdict = "ルナの勝ち" if hit(pk["luna"]) > hit(pk["random"]) else ("ランダムの勝ち" if hit(pk["luna"]) < hit(pk["random"]) else "引き分け")
ct(d, 1470, verdict, F("Bold", 72), DARK)
ct(d, 1580, "通算(%d回) ルナ %d個 / ランダム %d個" % (n, tl, tr), F("Medium", 38), GREY)
d.rounded_rectangle([W/2-170, 1820, W/2+170, 1876], radius=28, fill=CARD); ct(d, 1832, "AI×LOTTO LAB", F("Bold", 30), OR)
im.save(f"cards/answer_{D}.png")

# 予想カード(暗い配色)
BGT=(10,14,30);BGB=(18,22,46);GOLD=(240,190,90);BLUE=(90,160,230);WHITE=(245,247,252);GR=(150,158,180);CB=(26,32,58);CBD=(60,70,110)
im = Image.new("RGB", (W, H), BGT); d = ImageDraw.Draw(im)
for y in range(H):
    t = y/H; d.line([(0, y), (W, y)], fill=tuple(int(BGT[i]+(BGB[i]-BGT[i])*t) for i in range(3)))
m = 60
title = "第%d回%sの予想" % (NEXT, (" %s" % a.next_date) if a.next_date else "")
ct(d, 170, title, F("Bold", 60), WHITE); ct(d, 252, "ルナ「逆張り」 vs ランダム", F("Medium", 36), BLUE)
def balls(nums, y, fill, tc):
    for i, v in enumerate(nums):
        cx = m+36+70+i*((W-2*m-72-140)/5); r = 62
        d.ellipse([cx-r, y-r, cx+r, y+r], fill=fill)
        t = "%d" % v; b = d.textbbox((0, 0), t, font=F("Bold", 56)); d.text((cx-(b[2]-b[0])/2, y-(b[3]-b[1])/2-b[1]), t, font=F("Bold", 56), fill=tc)
d.rounded_rectangle([m, 340, W-m, 800], radius=26, fill=CB, outline=GOLD, width=4)
d.text((m+36, 370), "ルナ(人気の低い数字)", font=F("Bold", 38), fill=GOLD); balls(nx["luna"], 560, GOLD, (20, 20, 30))
d.text((m+36, 670), "全613万通りのうち、人気の低さ上位%.1f%%" % nx["percentile_luna"], font=F("Medium", 32), fill=WHITE)
d.text((m+36, 722), "※当せん確率は他と同じ。狙うのは、当たったときの取り分", font=F("Regular", 26), fill=GR)
d.rounded_rectangle([m, 840, W-m, 1240], radius=26, fill=CB, outline=CBD, width=3)
d.text((m+36, 870), "ランダム(くじ引き)", font=F("Bold", 38), fill=GR); balls(nx["random"], 1050, (60, 68, 100), WHITE)
d.text((m+36, 1160), "比べるための基準です", font=F("Regular", 30), fill=GR)
d.rounded_rectangle([m, 1290, W-m, 1600], radius=26, fill=(30, 24, 20), outline=(120, 90, 50), width=2)
d.text((m+36, 1320), "⚠ 当てる方法ではありません", font=F("Bold", 36), fill=(240, 180, 120))
d.text((m+36, 1384), "抽せんは毎回独立。当選確率は、どの6数字でも同じです。", font=F("Regular", 28), fill=WHITE)
d.text((m+36, 1432), "エンタメとして、結果を毎回検証して見せます。", font=F("Regular", 28), fill=WHITE)
d.rounded_rectangle([W/2-170, 1800, W/2+170, 1856], radius=28, fill=(30, 38, 68), outline=CBD, width=2); ct(d, 1810, "AI×LOTTO LAB", F("Bold", 30), GOLD)
im.save(f"cards/pred_{NEXT}.png")

json.dump({"answer_draw": D, "luna_hit": hit(pk["luna"]), "random_hit": hit(pk["random"]), "verdict": verdict,
           "total": {"draws": n, "luna": tl, "random": tr}, "next": NEXT, "luna": nx["luna"], "random": nx["random"],
           "percentile": nx["percentile_luna"], "nums": R["nums"], "bonus": R["bonus"]},
          open("data/week_summary.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, "scripts/build_history.py"], check=True)
print(open("data/week_summary.json").read())
