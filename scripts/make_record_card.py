"""検証用の事前記録カード(「予想」「当たる」を使わない表現)。使い方: python3 scripts/make_record_card.py <回号> <6数字をカンマ区切り> <答え合わせの曜日>"""
import sys
from PIL import Image, ImageDraw, ImageFont
N=int(sys.argv[1]); nums=[int(x) for x in sys.argv[2].split(",")]; day=sys.argv[3]
W,H=1080,1920; FD="/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F=lambda w,s:ImageFont.truetype(FD.format(w),s)
BG=(10,14,30);GOLD=(240,190,90);WHITE=(245,247,252);GR=(150,158,180);BLUE=(90,160,230)
im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
def ct(y,t,fn,fill):
    b=d.textbbox((0,0),t,font=fn);d.text((W/2-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
ct(170,"第%d回 検証用の記録"%N,F("Bold",62),WHITE); ct(262,"結果と照らし合わせるために、先に記録します",F("Medium",34),BLUE)
for i,v in enumerate(nums):
    r,c=divmod(i,3);cx=230+c*310;cy=560+r*330
    d.ellipse([cx-130,cy-130,cx+130,cy+130],fill=GOLD)
    t=str(v);b=d.textbbox((0,0),t,font=F("Bold",130));d.text((cx-(b[2]-b[0])/2,cy-(b[3]-b[1])/2-b[1]),t,font=F("Bold",130),fill=(20,20,30))
d.rounded_rectangle([60,1260,W-60,1580],radius=26,fill=(30,24,20),outline=(120,90,50),width=2)
d.text((100,1290),"⚠ 購入をすすめるものではありません",font=F("Bold",36),fill=(240,180,120))
d.text((100,1360),"当てる方法ではありません。確率はどの6数字でも同じ。",font=F("Regular",28),fill=WHITE)
d.text((100,1410),"抽せんは毎回独立。仮説の検証と、エンタメとしての記録です。",font=F("Regular",28),fill=WHITE)
d.text((100,1460),"※AI生成のキャラクターです",font=F("Regular",28),fill=GR)
ct(1650,"答え合わせは、%sの朝"%day,F("Bold",50),GOLD); ct(1830,"AI×LOTTO LAB",F("Regular",26),GR)
im.save(f"cards/record_{N}.png")
