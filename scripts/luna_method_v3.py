"""ルナ v3: ユーザー指定の7視点(2026-11-16, 上位6個=2026-11-19)を同じ重みで合成。逆張り・形の絞り込み・前回引っ張りは使わない。
使い方: python3 scripts/luna_method_v3.py <次回の回号> <次回の曜日 0=月/3=木>  リポジトリのルートから。
①よく出る数字(全回・直近100回) ②前回の当せん6数字それぞれの次回に出やすい数字 ③②の上位6個と一緒によく出る数字
④次のセット球の確率 ⑤④の重みで、そのセット球で出ている回数の多い数字 ⑥⑤の上位6個と一緒によく出る数字 ⑦次回と同じ曜日(月/木)の回の出現傾向
各視点を標準化(Z)して単純合計(重みなし)→ softmax(温度1)で6個を非復元抽出(乱数シード=回号)。"""
import sys, json, collections, numpy as np, openpyxl
NEXT=int(sys.argv[1]); WD=int(sys.argv[2])
ws=openpyxl.load_workbook("data/loto6_all.xlsx",read_only=True).active
R=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
N=len(R); assert R[-1][0]==NEXT-1, (R[-1][0],NEXT)
S=[set(r[2:8]) for r in R]; DT=[r[1] for r in R]
SB=json.load(open("data/setball.json"))["sets"]; sb=[SB.get(str(r[0])) for r in R]
Z=lambda x:(x-x.mean())/x.std()
lift=lambda c,t,k:np.log((c+k)/(t*6/43+k))
cnt=lambda idx:np.array([sum(1 for t in idx if n in S[t]) for n in range(1,44)],float)
f_all=lift(cnt(range(N)),N,30); f_rec=lift(cnt(range(N-100,N)),100,10)
v1=Z(Z(f_all)+Z(f_rec))
last=S[-1]
fol=np.zeros(43)
for n in last:
    idx=[t for t in range(N-1) if n in S[t]]
    for m in range(1,44): fol[m-1]+=sum(1 for t in idx if m in S[t+1])/len(idx)
fol/=len(last); v2=Z(np.log(fol/(6/43)))
def cooc(base):   # base: 数字(1始まり)のリスト。各数字と同じ回に出た割合の平均
    a=np.zeros(43)
    for n in base:
        idx=[t for t in range(N) if n in S[t]]
        for m in range(1,44):
            if m!=n: a[m-1]+=sum(1 for t in idx if m in S[t])/len(idx)
    a/=len(base); a[[n-1 for n in base]]=np.nan; a[np.isnan(a)]=np.nanmean(a); return Z(np.log(a/(6/43)))
top2=[int(i+1) for i in np.argsort(-v2)[:6]]; v3=cooc(top2)
# ④ セット球(v2と同じ: 最後に使われてからの間隔別の実績)
ERA=648; sets="ABCDEFGHIJ"; gaps=collections.defaultdict(lambda:[0,0]); lastuse={}
for t in range(ERA,N):
    s=sb[t]
    if s is None: lastuse={}; continue
    for k in sets:
        if k in lastuse: g=min(t-lastuse[k],25); gaps[g][1]+=1; gaps[g][0]+=(k==s)
    lastuse[s]=t
lu={}
for t in range(1901,N):
    if sb[t]: lu[sb[t]]=t
cur={}
for k in sets:
    g=min(N-lu[k],25) if k in lu else 25; h,n=gaps[g]; cur[k]=(h+1)/(n+10)
tt=sum(cur.values()); pset={k:v/tt for k,v in cur.items()}
f_set=sum(pset[k]*lift(cnt([t for t in range(ERA,N) if sb[t]==k]),len([t for t in range(ERA,N) if sb[t]==k]),15) for k in sets)
v5=Z(f_set); top5=[int(i+1) for i in np.argsort(-v5)[:6]]; v6=cooc(top5)
# ⑦ 同じ曜日の回
widx=[t for t in range(N) if DT[t].weekday()==WD]; v7=Z(lift(cnt(widx),len(widx),15))
V={"1":v1,"2":v2,"3":v3,"5":v5,"6":v6,"7":v7}
score=sum(V.values())/len(V)
p=np.exp(score-score.max()); p/=p.sum()
rng=np.random.default_rng(NEXT)
pick=sorted(int(x)+1 for x in rng.choice(43,size=6,replace=False,p=p))
out={"next":NEXT,"draws":N,"luna":pick,"method":"v3 seven viewpoints equal weight, softmax T=1","weekday_draws":len(widx),
     "top2":top2,"top5":top5,"pset":{k:round(v,3) for k,v in sorted(pset.items(),key=lambda x:-x[1])},
     "top_by_view":{k:[int(i+1) for i in np.argsort(-v)[:6]] for k,v in V.items()},"top_score":[int(i+1) for i in np.argsort(-score)[:10]]}
json.dump(out,open(f"data/picks_v3_{NEXT}.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
