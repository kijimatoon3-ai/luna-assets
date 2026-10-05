import json
from PIL import Image, ImageDraw, ImageFont
S=json.load(open("scores.json"));rank=S["rank"]
actual=[1,7,8,29,40,43];bonus=15;pred=[9,10,17,26,33,35]
pos={n:rank.index(n)+1 for n in actual}
print(pos, "hits", set(pred)&set(actual), "bonus in pred", bonus in pred)
FD="/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"
F=lambda w,s:ImageFont.truetype(FD.format(w),s)
# ---------- Scene A: answer check 2143 (light style like previous) ----------
W,H=1080,1920
BG=(250,248,242);CARD=(243,238,231);DARK=(40,38,34);GREY=(120,116,108);OR=(230,126,34)
im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
def ct(d,y,t,fn,fill,cx=W/2):
    b=d.textbbox((0,0),t,font=fn);d.text((cx-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
def row(d,nums,y,hl=(),fill=CARD):
    for i,n in enumerate(nums):
        x=70+i*160
        d.rounded_rectangle([x,y,x+140,y+140],radius=22,fill=fill)
        t="%d"%n;b=d.textbbox((0,0),t,font=F("Bold",64))
        d.text((x+70-(b[2]-b[0])/2,y+70-(b[3]-b[1])/2-b[1]),t,font=F("Bold",64),fill=DARK)
ct(d,200,"第2143回 ルナの予想",F("Bold",48),GREY)
row(d,pred,300)
ct(d,1330,"当せん番号(第2143回)",F("Bold",48),GREY)
row(d,actual,1430)
ct(d,1600,"ボーナス %d"%bonus,F("Bold",40),GREY)
ct(d,1680,"一致:0個",F("Bold",64),OR)
d.rounded_rectangle([W/2-170,1820,W/2+170,1876],radius=28,fill=CARD);ct(d,1832,"AI×LOTTO LAB",F("Bold",30),OR)
im.save("scene_A_answer_2143.png")
# ---------- Scene C: reflection + strategy (dark style) ----------
BGT=(10,14,30);BGB=(18,22,46);GOLD=(240,190,90);BLUE=(90,160,230);WHITE=(245,247,252)
GR=(150,158,180);CB=(26,32,58);CBD=(60,70,110)
im=Image.new("RGB",(W,H),BGT);d=ImageDraw.Draw(im)
for y in range(H):
    t=y/H;d.line([(0,y),(W,y)],fill=tuple(int(BGT[i]+(BGB[i]-BGT[i])*t) for i in range(3)))
m=60
def card(y0,y1,outline=CBD):d.rounded_rectangle([m,y0,W-m,y1],radius=26,fill=CB,outline=outline,width=3)
ct(d,170,"反省と次の作戦",F("Bold",70),WHITE)
ct(d,262,"2回連続ゼロ。ここから検証します",F("Medium",34),BLUE)
# reflection
y=340;card(y,y+640)
d.text((m+36,y+28),"① 反省:上位だけ見すぎた",font=F("Bold",42),fill=GOLD)
d.text((m+36,y+98),"当せん6数字の、ルナの統合ランキング順位",font=F("Regular",30),fill=GR)
for i,n in enumerate(actual):
    r=44;cx=m+36+r+i*((W-2*m-72-88)/5+0) if False else m+36+r+i*(( W-2*m-72-2*44)/5)
    cy=y+215
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(50,58,88))
    t="%d"%n;b=d.textbbox((0,0),t,font=F("Bold",44));d.text((cx-(b[2]-b[0])/2,cy-(b[3]-b[1])/2-b[1]),t,font=F("Bold",44),fill=WHITE)
    p=pos[n];lab="%d位"%p
    col=GOLD if p<=10 else GR
    ct(d,cy+62,lab,F("Bold",34),col,cx=cx)
d.text((m+36,y+400),"ルナが選んだ6つ(上位6位)は、1つも出ませんでした。",font=F("Regular",32),fill=WHITE)
d.text((m+36,y+458),"ただ、2回分では「手法がダメ」とも言えません。",font=F("Regular",32),fill=WHITE)
d.text((m+36,y+516),"抽せんは毎回独立。だから、検証が必要です。",font=F("Bold",32),fill=GOLD)
# strategy
y=1010;card(y,y+640,outline=GOLD)
d.text((m+36,y+28),"② 次の作戦:ルナ vs ランダム",font=F("Bold",42),fill=GOLD)
items=[("毎回、ランダム予想を同時に出す","ルナの予想と同じ6個を、くじ引きで作ります"),
       ("一致数をスコアボードに記録","毎回、どちらが何個当てたかを並べて公開"),
       ("10回続けて、AI予想の強さを判定","勝てなければ「AIでも当たらない」が結論です")]
yy=y+110
for i,(a,b) in enumerate(items,1):
    d.ellipse([m+36,yy+8,m+36+64,yy+72],fill=GOLD)
    t=str(i);bb=d.textbbox((0,0),t,font=F("Bold",40));d.text((m+68-(bb[2]-bb[0])/2,yy+40-(bb[3]-bb[1])/2-bb[1]),t,font=F("Bold",40),fill=(20,20,30))
    d.text((m+130,yy),a,font=F("Bold",36),fill=WHITE)
    d.text((m+130,yy+54),b,font=F("Regular",28),fill=GR)
    yy+=165
ct(d,1700,"第2144回は、木曜に予想を出します",F("Bold",36),WHITE)
d.rounded_rectangle([W/2-170,1800,W/2+170,1856],radius=28,fill=(30,38,68),outline=CBD,width=2);ct(d,1812,"AI×LOTTO LAB",F("Bold",30),GOLD)
im.save("scene_C_strategy.png")
