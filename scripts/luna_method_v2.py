"""ルナ・メソッド v2(逆張りなし): 出現回数・直近・相性・翌回・セット球の複合スコアで6数字を確率抽出。
使い方: python3 scripts/luna_method_v2.py <次回の回号> [--show]   リポジトリのルートから実行。"""
import sys, json, itertools, collections, numpy as np, openpyxl
NEXT=int(sys.argv[1]); SHOW="--show" in sys.argv
ws=openpyxl.load_workbook("data/loto6_all.xlsx",read_only=True).active
R=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
N=len(R); S=[set(r[2:8]) for r in R]
SB=json.load(open("data/setball.json"))["sets"]; sb=[SB.get(str(r[0])) for r in R]
def lift(cnt,tot,k):      # 期待との比の対数(少数データは0へ縮める)
    exp=tot*6/43; return np.log((cnt+k)/(exp+k))
# 1) 全期間の出現
c_all=np.array([sum(1 for s in S if n in s) for n in range(1,44)],float); f_all=lift(c_all,N,30)
# 2) 直近100回
c_rec=np.array([sum(1 for s in S[-100:] if n in s) for n in range(1,44)],float); f_rec=lift(c_rec,100,10)
last=S[-1]
# 3) 前回の数字との相性(同じ回に一緒に出た割合)
aff=np.zeros(43)
for n in last:
    idx=[t for t in range(N) if n in S[t]]
    for m in range(1,44):
        if m!=n: aff[m-1]+=sum(1 for t in idx if m in S[t])/len(idx)
aff=np.log((aff/len(last)+1e-9)/(6/43*(42/43)*0+6/43*1.0)); aff=(aff-aff.mean())
# 4) 前回の数字の翌回に出る確率
fol=np.zeros(43)
for n in last:
    idx=[t for t in range(N-1) if n in S[t]]
    for m in range(1,44): fol[m-1]+=sum(1 for t in idx if m in S[t+1])/len(idx)
fol=np.log((fol/len(last))/(6/43)); fol=fol-fol.mean()
# 5) セット球: 次回のセットの確率(最後に使われてからの間隔別の実績)×セット別の数字の偏り
ERA=648  # 第649回以降(インデックス)
sets="ABCDEFGHIJ"; gaps=collections.defaultdict(lambda:[0,0])
lastuse={}
for t in range(ERA,N):
    s=sb[t]
    if s is None: lastuse={}; continue
    for k in sets:
        if k in lastuse:
            g=min(t-lastuse[k],25); gaps[g][1]+=1; gaps[g][0]+= (k==s)
    lastuse[s]=t
# 直近の使用位置(傷んだ範囲より後)
lu={}
for t in range(1901,N):
    if sb[t]: lu[sb[t]]=t
cur={}
for k in sets:
    g=min(N-lu[k],25) if k in lu else 25
    h,n=gaps[g]; cur[k]=(h+1)/(n+10)
tot=sum(cur.values()); pset={k:v/tot for k,v in cur.items()}
setlift={}
for k in sets:
    idx=[t for t in range(ERA,N) if sb[t]==k]
    c=np.array([sum(1 for t in idx if n in S[t]) for n in range(1,44)],float)
    setlift[k]=lift(c,len(idx),15)
f_set=sum(pset[k]*setlift[k] for k in sets)
Z=lambda x:(x-x.mean())/x.std()
score=Z(f_all)+Z(f_rec)+Z(aff)+Z(fol)+Z(f_set)
# 組み合わせ: 形の条件(奇数3-4、合計95-170、連続ペア<=1、前回と同じ数字1-2個)で絞り、スコアに比例する確率で抽出
combos=np.array(list(itertools.combinations(range(1,44),6)),dtype=np.int8)
odd=(combos%2).sum(1); sm=combos.sum(1,dtype=np.int32)
cons=(np.diff(combos.astype(np.int16),axis=1)==1).sum(1)
carry=np.isin(combos,list(last)).sum(1)
ok=(odd>=3)&(odd<=4)&(sm>=95)&(sm<=170)&(cons<=1)&(carry>=1)&(carry<=2)
cs=score[combos[ok]-1].sum(1); BETA=0.5
p=np.exp(BETA*(cs-cs.max())); p/=p.sum()
rng=np.random.default_rng(NEXT)
pick=sorted(int(x) for x in combos[ok][rng.choice(ok.sum(),p=p)])
out={"next":NEXT,"draws":N,"luna":pick,"pset":{k:round(v,3) for k,v in pset.items()},
     "top":[int(i+1) for i in np.argsort(-score)[:10]],"score":{str(i+1):round(float(score[i]),2) for i in range(43)},"beta":BETA,"n_candidates":int(ok.sum())}
json.dump(out,open(f"data/picks_v2_{NEXT}.json","w"),ensure_ascii=False,indent=1)
if SHOW:
    print("次回セット球の確率:",dict(sorted(out["pset"].items(),key=lambda x:-x[1])))
    print("スコア上位:",out["top"]); print("抽出:",pick,"候補数",out["n_candidates"])
    for name,v in (("全期間",f_all),("直近",f_rec),("相性",aff),("翌回",fol),("セット球",f_set)):
        print(name,"上位",[int(i+1) for i in np.argsort(-v)[:6]])
