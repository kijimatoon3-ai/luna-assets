"""月曜 vs 木曜の比較カード(第543回=月曜開催開始以降)。使い方: python3 scripts/make_weekday_card.py <次回の回号>"""
import sys
from PIL import Image, ImageDraw, ImageFont
N=int(sys.argv[1]); W,H=1080,1920; FD="/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F=lambda w,s:ImageFont.truetype(FD.format(w),s)
BG=(10,14,30);GOLD=(240,190,90);WHITE=(245,247,252);GR=(150,158,180);BLUE=(90,160,230);CB=(26,32,58);CBD=(60,70,110)
im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
def ct(y,t,fn,fill):
    b=d.textbbox((0,0),t,font=fn);d.text((W/2-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
ct(180,"月曜 と 木曜",F("Bold",84),WHITE); ct(300,"出る数字に違いはある?",F("Bold",52),BLUE)
ct(390,"第543回〜(月曜806回・木曜805回)で比較",F("Medium",34),GR)
rows=[("合計","131.7","132.8"),("奇数の個数","3.02","2.97"),("21以下の個数","2.89","2.94"),("連番の組","0.68","0.72")]
d.rounded_rectangle([60,480,W-60,1090],radius=26,fill=CB,outline=CBD,width=3)
d.text((330,505),"月曜",font=F("Bold",40),fill=GOLD); d.text((560,505),"木曜",font=F("Bold",40),fill=GOLD)
for i,(n,a,b) in enumerate(rows):
    y=590+i*115; d.text((100,y),n,font=F("Medium",36),fill=WHITE); d.text((330,y),a,font=F("Bold",44),fill=WHITE); d.text((560,y),b,font=F("Bold",44),fill=WHITE)
d.text((100,1050),"セット球の使われ方も、ほぼ同じ(月曜と木曜で差なし)",font=F("Regular",28),fill=GR)
ct(1190,"結論",F("Medium",40),GR); ct(1260,"差は偶然の範囲",F("Bold",100),GOLD)
d.rounded_rectangle([60,1480,W-60,1700],radius=26,fill=(30,24,20),outline=(120,90,50),width=2)
d.text((100,1510),"⚠ 当てる方法ではありません",font=F("Bold",38),fill=(240,180,120))
d.text((100,1580),"抽せんは毎回独立。当せん確率は、どの6数字でも同じです。",font=F("Regular",28),fill=WHITE)
ct(1830,"AI×LOTTO LAB",F("Regular",26),GR)
im.save(f"cards/weekday_{N}.png")
