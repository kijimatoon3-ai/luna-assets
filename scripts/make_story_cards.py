import json
from PIL import Image, ImageDraw, ImageFont
bt=json.load(open("backtest.json"));pp=json.load(open("pop.json"));lp=json.load(open("luna_pick.json"));pp["luna"]=lp["luna"];pp["rand"]=lp["random"];pp["mult_luna"]=lp["mult_luna"];PCT=lp["percentile_luna"]
W,H=1080,1920
BGT=(10,14,30);BGB=(18,22,46);GOLD=(240,190,90);BLUE=(90,160,230);WHITE=(245,247,252)
GR=(150,158,180);CB=(26,32,58);CBD=(60,70,110);RED=(235,120,100)
FD="/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"
F=lambda w,s:ImageFont.truetype(FD.format(w),s)
def base():
    im=Image.new("RGB",(W,H),BGT);d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H;d.line([(0,y),(W,y)],fill=tuple(int(BGT[i]+(BGB[i]-BGT[i])*t) for i in range(3)))
    return im,d
def ct(d,y,t,fn,fill,cx=W/2):
    b=d.textbbox((0,0),t,font=fn);d.text((cx-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
def chip(d):
    d.rounded_rectangle([W/2-170,1800,W/2+170,1856],radius=28,fill=(30,38,68),outline=CBD,width=2);ct(d,1810,"AI×LOTTO LAB",F("Bold",30),GOLD)
m=60
# ---- D: backtest
im,d=base()
ct(d,170,"全2143回のデータで検証",F("Bold",64),WHITE)
ct(d,255,"どの手法も、ランダムと同じ(1843回分を比較)",F("Medium",36),BLUE)
d.rounded_rectangle([m,340,W-m,1500],radius=26,fill=CB,outline=CBD,width=3)
d.text((m+36,368),"1回あたりの平均一致数(理論値0.84)",font=F("Bold",34),fill=GOLD)
order=["ランダム","ホット50回","ホット10回","コールド(通算少)","未出現期間長い","ホット3+コールド3"]
lab={"ランダム":"ランダム","ホット50回":"ホット(直近50回)","ホット10回":"ホット(直近10回)","コールド(通算少)":"コールド(通算)","未出現期間長い":"未出現が長い数字","ホット3+コールド3":"ホット3+コールド3"}
y=450;x0=m+36;bw=W-2*m-72-260;sc=bw/1.2
for k in order:
    v=bt["res"][k]["mean"]
    d.text((x0,y),lab[k],font=F("Medium",30),fill=WHITE)
    d.rounded_rectangle([x0,y+48,x0+bw,y+48+44],radius=10,fill=(40,48,80))
    d.rounded_rectangle([x0,y+48,x0+v*sc,y+48+44],radius=10,fill=BLUE if k!="ランダム" else GR)
    d.text((x0+bw+24,y+46),"%.2f"%v,font=F("Bold",40),fill=WHITE)
    y+=150
tx=x0+bt["exp"]*sc
d.line([(tx,440),(tx,y-10)],fill=GOLD,width=4)
d.text((tx-80,y-6),"理論値 0.84",font=F("Bold",28),fill=GOLD)
d.text((m+36,y+50),"差は誤差の範囲。過去データで未来は当てられません。",font=F("Regular",30),fill=WHITE)
ct(d,1560,"ルナの今までの予想法も、同じでした",F("Bold",40),GOLD)
ct(d,1630,"だから、やり方を変えます",F("Bold",40),WHITE)
chip(d);im.save("scene_D_backtest.png")
# ---- E: popularity
im,d=base()
ct(d,170,"発見:人気の数字がある",F("Bold",64),WHITE)
ct(d,255,"当せん者の数に、はっきり差が出ていた",F("Medium",34),BLUE)
d.rounded_rectangle([m,340,W-m,1180],radius=26,fill=CB,outline=CBD,width=3)
d.text((m+36,368),"当せん数字のうち「31以下」の個数",font=F("Bold",34),fill=GOLD)
d.text((m+36,418),"当せん者数の多さ(平均を1.0とした比)",font=F("Regular",28),fill=GR)
by=pp["by31"];groups=[("2個以下",[1,2]),("3個",[3]),("4個",[4]),("5個",[5]),("6個",[6])]
vals=[]
for name,ks in groups:
    n=sum(by[str(k)][0] for k in ks if str(k) in by);v=sum(by[str(k)][0]*by[str(k)][1] for k in ks if str(k) in by)/n;vals.append((name,v))
cw=(W-2*m-72)/5;base_y=1090;sc=420/1.3
for i,(name,v) in enumerate(vals):
    cx=m+36+cw*i+cw/2;h=v*sc
    col=RED if v>1.05 else (BLUE if v<0.95 else GR)
    d.rounded_rectangle([cx-48,base_y-h,cx+48,base_y],radius=12,fill=col)
    ct(d,base_y-h-52,"%.2f"%v,F("Bold",36),WHITE,cx=cx)
    ct(d,base_y+14,name,F("Medium",28),WHITE,cx=cx)
ly=base_y-1.0*sc;d.line([(m+36,ly),(W-m-36,ly)],fill=GOLD,width=3)
d.rounded_rectangle([m,1210,W-m,1650],radius=26,fill=CB,outline=GOLD,width=3)
d.text((m+36,1236),"人気が高い数字(推定)",font=F("Bold",32),fill=RED)
d.text((m+36,1288),"11・8・3・7・12・5・6",font=F("Bold",44),fill=WHITE)
d.text((m+36,1388),"人気が低い数字(推定)",font=F("Bold",32),fill=BLUE)
d.text((m+36,1440),"43・40・34・41・35・20・42",font=F("Bold",44),fill=WHITE)
d.text((m+36,1540),"誕生日の数字(1〜31)に、みんな偏っている",font=F("Regular",30),fill=GR)
d.text((m+36,1584),"※当せん者数の統計から、私が推定した値です",font=F("Regular",24),fill=GR)
ct(d,1690,"人気を避ければ、当たったとき取り分が増える",F("Bold",34),GOLD)
chip(d);im.save("scene_E_popularity.png")
# ---- F: prediction 2144
im,d=base()
ct(d,170,"第2144回(10/8木)の予想",F("Bold",60),WHITE)
ct(d,252,"ルナ「逆張り」 vs ランダム",F("Medium",36),BLUE)
def balls(nums,y,fill,tc):
    for i,n in enumerate(nums):
        cx=m+36+70+i*((W-2*m-72-140)/5);r=62
        d.ellipse([cx-r,y-r,cx+r,y+r],fill=fill)
        t="%d"%n;b=d.textbbox((0,0),t,font=F("Bold",56));d.text((cx-(b[2]-b[0])/2,y-(b[3]-b[1])/2-b[1]),t,font=F("Bold",56),fill=tc)
d.rounded_rectangle([m,340,W-m,800],radius=26,fill=CB,outline=GOLD,width=4)
d.text((m+36,370),"ルナ(人気の低い数字)",font=F("Bold",38),fill=GOLD)
balls(pp["luna"],560,GOLD,(20,20,30))
d.text((m+36,670),"全613万通りのうち、人気の低さ上位%.1f%%"%PCT,font=F("Medium",32),fill=WHITE)
d.text((m+36,722),"※当せん確率は他と同じ。狙うのは、当たったときの取り分",font=F("Regular",26),fill=GR)
d.rounded_rectangle([m,840,W-m,1240],radius=26,fill=CB,outline=CBD,width=3)
d.text((m+36,870),"ランダム(くじ引き)",font=F("Bold",38),fill=GR)
balls(pp["rand"],1050,(60,68,100),WHITE)
d.text((m+36,1160),"比べるための基準です",font=F("Regular",30),fill=GR)
d.rounded_rectangle([m,1290,W-m,1600],radius=26,fill=(30,24,20),outline=(120,90,50),width=2)
d.text((m+36,1320),"⚠ 当てる方法ではありません",font=F("Bold",36),fill=(240,180,120))
d.text((m+36,1384),"抽せんは毎回独立。当選確率は、どの6数字でも同じです。",font=F("Regular",28),fill=WHITE)
d.text((m+36,1432),"エンタメとして、結果を毎回検証して見せます。",font=F("Regular",28),fill=WHITE)
chip(d);im.save("scene_F_pred_2144.png")
print(pp["luna"],pp["rand"],pp["mult_luna"])
