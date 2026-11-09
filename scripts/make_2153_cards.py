"""v3 動画カード(全データ・前回振り返り・材料・似た回)。使い方: python3 scripts/make_2153_cards.py <次回の回号> <v2出力txt>"""
import sys, json, re, openpyxl
from PIL import Image, ImageDraw, ImageFont
N=int(sys.argv[1]); D=N-1; out=open(sys.argv[2]).read()
W,H=1080,1920; FD="/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"; F=lambda w,s: ImageFont.truetype(FD.format(w),s)
BG=(10,14,30); GOLD=(240,190,90); WHITE=(245,247,252); GR=(150,158,180); BLUE=(90,160,230); CB=(26,32,58); CBD=(60,70,110)
def new(): im=Image.new("RGB",(W,H),BG); return im,ImageDraw.Draw(im)
def ct(d,y,t,fn,fill):
    b=d.textbbox((0,0),t,font=fn); d.text((W/2-(b[2]-b[0])/2,y),t,font=fn,fill=fill)
def foot(d): ct(d,1830,"AI×LOTTO LAB",F("Regular",26),GR)
def box(d,y,h): d.rounded_rectangle([70,y,W-70,y+h],radius=26,fill=CB,outline=CBD,width=3)
ws=openpyxl.load_workbook("data/loto6_all.xlsx",read_only=True).active
R=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
n=len(R); hit=sum(1 for x in R if x[9]>0); pct=round(hit/n*100)
assert R[-1][0]==D
pk=json.load(open(f"data/picks/{D}.json")); sb=json.load(open("data/scoreboard.json"))["rows"]
SB=json.load(open("data/setball.json"))["sets"]
J=lambda xs:" ・ ".join(str(x) for x in xs)
# 1 冒頭
im,d=new(); ct(d,330,"ロト6",F("Bold",90),WHITE); ct(d,470,"%d%%"%pct,F("Bold",420),GOLD)
ct(d,980,"の回で 1等が出てる",F("Bold",78),WHITE); ct(d,1110,"第1回〜第%d回(%s回中%s回)"%(n,format(n,","),format(hit,",")),F("Medium",38),BLUE); foot(d); im.save(f"cards/v3_open_{N}.png")
# 2 全データ
im,d=new(); ct(d,220,"全%s回の当選結果を"%format(n,","),F("Bold",76),GOLD); ct(d,340,"すべて集めて分析",F("Bold",76),GOLD)
items=[("当せん数字",format(n*6,",")+"個"),("ボーナス数字",format(n,",")+"個"),("等級別の口数・賞金","1等〜5等 すべて"),("使われた抽せん球(セット球)","回ごとに記録")]
y=520
for lab,val in items:
    box(d,y,230); d.text((110,y+30),lab,font=F("Medium",38),fill=GR); d.text((110,y+100),val,font=F("Bold",78),fill=WHITE); y+=265
ct(d,y+30,"第1回 〜 第%d回"%D,F("Medium",40),BLUE); foot(d); im.save(f"cards/v3_data_{N}.png")
# 3 前回の振り返り
r=sb[-1]; assert r["draw"]==D
tl=sum(x["luna_hit"] for x in sb); tr=sum(x["random_hit"] for x in sb)
im,d=new(); ct(d,200,"前回の振り返り",F("Bold",76),GOLD); ct(d,320,"第%d回"%D,F("Medium",48),WHITE)
box(d,430,330); d.text((110,460),"当せん番号",font=F("Medium",38),fill=GR); d.text((110,540),J(r["nums"]),font=F("Bold",54),fill=WHITE); d.text((110,650),"ボーナス %d"%r["bonus"],font=F("Medium",44),fill=BLUE)
box(d,800,330); d.text((110,830),"ルナの抽出6数字",font=F("Medium",38),fill=GR); d.text((110,910),J(r["luna"]),font=F("Bold",54),fill=WHITE); d.text((110,1020),"一致 %d個"%r["luna_hit"],font=F("Bold",56),fill=GOLD)
box(d,1170,230); d.text((110,1200),"使われたセット球",font=F("Medium",38),fill=GR); d.text((110,1270),SB[str(D)]+" セット",font=F("Bold",80),fill=WHITE)
ct(d,1450,"ルナの通算 %d個一致(%d回中)"%(tl,len(sb)),F("Medium",40),WHITE); ct(d,1520,"ランダムの通算は %d個"%tr,F("Regular",32),GR); foot(d); im.save(f"cards/v3_review_{N}.png")
# 4 材料
g=lambda k: re.search(k+r" 上位 \[([^\]]*)\]",out).group(1).split(", ")
ps=re.search(r"次回セット球の確率: (\{.*\})",out).group(1); ps=eval(ps); top=[k for k,_ in sorted(ps.items(),key=lambda x:-x[1])[:3]]
im,d=new(); ct(d,200,"今回の材料",F("Bold",76),GOLD); ct(d,320,"全データから見えたこと",F("Medium",42),WHITE)
items=[("全期間でよく出る数字",J(g("全期間")[:4])),("最近100回でよく出る数字",J(g("直近")[:4])),("前回の次に出やすい数字",J(g("翌回")[:4])),("次に使われやすいセット球",J(top)+" の順")]
y=450
for lab,val in items:
    box(d,y,250); d.text((110,y+30),lab,font=F("Medium",38),fill=GR); d.text((110,y+105),val,font=F("Bold",76),fill=WHITE); y+=285
ct(d,y+20,"傾向です。当てる方法ではありません",F("Regular",32),GR); foot(d); im.save(f"cards/v3_material_{N}.png")
# 5 似た回
last=set(R[-1][2:8]); sim=[]
for i,x in enumerate(R[:-1]):
    k=len(set(x[2:8])&last)
    if k>=3: sim.append((k,x[0],sorted(x[2:8]),R[i+1][0],sorted(R[i+1][2:8])))
sim.sort(key=lambda t:(-t[0],-t[1])); json.dump(sim[:6],open(f"data/similar_{N}.json","w"))
im,d=new(); ct(d,200,"似た過去の回",F("Bold",76),GOLD); ct(d,320,"前回の数字が3個以上同じ回は %d回"%len(sim),F("Medium",40),WHITE)
d.text((110,430),"前回(第%d回)"%D,font=F("Medium",36),fill=GR); d.text((110,490),J(sorted(last)),font=F("Bold",58),fill=BLUE)
y=640
for k,a,s,b,t in sim[:2]:
    box(d,y,430); d.text((110,y+25),"第%d回(%d個一致)"%(a,k),font=F("Medium",36),fill=GR); d.text((110,y+85),J(s),font=F("Bold",52),fill=WHITE)
    d.text((110,y+190),"その次の第%d回"%b,font=F("Medium",36),fill=GR); d.text((110,y+250),J(t),font=F("Bold",58),fill=GOLD); y+=480
ct(d,y+20,"参考のひとつです。当てる方法ではありません",F("Regular",32),GR); foot(d); im.save(f"cards/v3_similar_{N}.png")
print("ok",sim[:2],g("全期間"),top)
