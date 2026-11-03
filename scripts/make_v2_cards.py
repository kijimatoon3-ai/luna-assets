"""v2 動画用カード: 冒頭(2秒フック)、視点カード3枚、6数字の1個ずつ公開カード6枚。使い方: python3 scripts/make_v2_cards.py <次回の回号>"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
N = int(sys.argv[1]); p = json.load(open(f"data/picks/{N}.json")); v = json.load(open(f"data/picks_v2_{N}.json"))
W, H = 1080, 1920; FD = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F = lambda w, s: ImageFont.truetype(FD.format(w), s)
BG=(10,14,30); GOLD=(240,190,90); WHITE=(245,247,252); GR=(150,158,180); BLUE=(90,160,230); CB=(26,32,58); CBD=(60,70,110); DIM=(40,46,74)
def new(): im=Image.new("RGB",(W,H),BG); return im, ImageDraw.Draw(im)
def ct(d,y,t,fn,fill):
    b=d.textbbox((0,0),t,font=fn); d.text((W/2-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
def foot(d): ct(d,1830,"AI×LOTTO LAB",F("Regular",26),GR)
# 冒頭フック: 最初のフレームから数字が見える(音なしでも読める)
rows=[l for l in __import__("openpyxl").load_workbook("data/loto6_all.xlsx",read_only=True).active.iter_rows(min_row=2,values_only=True) if l[0]]
n=len(rows); hit=sum(1 for x in rows if x[9]>0); pct=round(hit/n*100)
im,d=new(); ct(d,330,"ロト6",F("Bold",90),WHITE); ct(d,470,"%d%%"%pct,F("Bold",420),GOLD)
ct(d,980,"の回で 1等が出てる",F("Bold",78),WHITE); ct(d,1110,"第1回〜第%d回(%s回中%s回)"%(n,format(n,","),format(hit,",")),F("Medium",38),BLUE); foot(d)
im.save(f"cards/v2_open_{N}.png")
# 視点カード
def card(name,title,sub,items,note):
    im,d=new(); ct(d,230,title,F("Bold",72),GOLD); ct(d,350,sub,F("Medium",42),WHITE)
    y=520
    for lab,val in items:
        d.rounded_rectangle([70,y,W-70,y+210],radius=26,fill=CB,outline=CBD,width=3)
        d.text((110,y+28),lab,font=F("Medium",36),fill=GR); d.text((110,y+95),val,font=F("Bold",70),fill=WHITE); y+=250
    ct(d,y+60,note,F("Regular",30),GR); foot(d); im.save(f"cards/v2_{name}_{N}.png")
sc=v["score"]
card("view1","視点① よく出る数字","過去の全データから",[("全期間でよく出た数字","6 ・ 37 ・ 2 ・ 42"),("最近100回でよく出た数字","37 ・ 6 ・ 18 ・ 8")],"傾向です。当てる方法ではありません")
card("view2","視点② 組み合わせの傾向","前の回の数字をもとに",[("一緒に出やすい数字","6 ・ 38 ・ 15 ・ 1"),("次の回に出やすい数字","37 ・ 38 ・ 10 ・ 20")],"傾向です。当てる方法ではありません")
ps=sorted(v["pset"].items(),key=lambda x:-x[1])[:2]
card("view3","視点③ 次の抽せん球","セット球の使われ方から",[("次に使われやすいセット","%s・%s"%(ps[0][0],ps[1][0])),("そのセットで出やすい数字","6 ・ 21 ・ 2 ・ 26")],"傾向です。当てる方法ではありません")
# 6数字を1個ずつ
nums=p["luna"]
for k in range(1,7):
    im,d=new(); ct(d,170,"第%d回 ルナの抽出6数字"%N,F("Bold",60),WHITE); ct(d,262,"%d個目"%k,F("Medium",40),BLUE)
    for i,x in enumerate(nums):
        r,c=divmod(i,3); cx=230+c*310; cy=560+r*330
        on=i<k; fill=GOLD if on else DIM
        d.ellipse([cx-130,cy-130,cx+130,cy+130],fill=fill)
        if on:
            t=str(x); b=d.textbbox((0,0),t,font=F("Bold",110)); d.text((cx-(b[2]-b[0])/2,cy-(b[3]-b[1])/2-b[1]),t,font=F("Bold",110),fill=(20,20,30))
    ct(d,1330,"AIが分析した視点から抽出",F("Medium",38),GR)
    ct(d,1410,"当てる方法ではありません",F("Regular",30),GR); foot(d); im.save(f"cards/v2_num{k}_{N}.png")
print("ok")
