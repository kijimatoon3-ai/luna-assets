"""ルナ・メソッド v1: 全履歴から「人気度」を学習し、人気の低い組み合わせを確率的に抽出する。
使い方: python3 luna_method.py <次回の回号>   (loto6_all.xlsx に最新回を追記済みであること)
出力: luna_pick.json (予想・ランダム比較・根拠の数値)"""
import sys, json, itertools, numpy as np, openpyxl
from scipy import stats
NEXT=int(sys.argv[1]) if len(sys.argv)>1 else 2144
BETA=12.0     # 人気度への逆張りの強さ(大きいほど極端)
wb=openpyxl.load_workbook('loto6_all.xlsx',data_only=True);ws=wb.active
rows=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
N=len(rows);nums=np.array([r[2:8] for r in rows])
w3,w4,w5=[np.array([r[i] for r in rows],float) for i in(11,12,13)]
def detr(x):
    y=np.log(np.maximum(x,1));o=np.zeros_like(y)
    for t in range(N):
        lo,hi=max(0,t-30),min(N,t+31);o[t]=y[t]-np.median(y[lo:hi])
    return o
z=(detr(w3)+detr(w4)+detr(w5))/3          # 売上の増減を除いた「当せん者の多さ」
X=np.zeros((N,43))
for t in range(N):
    for n in nums[t]:X[t,n-1]=1
def fit(idx,lam=5.0):
    A=X[idx]-X[idx].mean(0);y=z[idx]-z[idx].mean()
    return np.linalg.solve(A.T@A+lam*np.eye(43),A.T@y)
# 精度確認(前半で学習→後半で検証)
cut=int(N*0.8);b_tr=fit(np.arange(100,cut))
oos=float(stats.pearsonr((X[cut:]-X[100:cut].mean(0))@b_tr,z[cut:])[0])
b=fit(np.arange(100,N))                    # 本番は全データで学習
# 全 C(43,6) を列挙して、人気度スコアに応じた確率で1組を抽出
combos=np.array(list(itertools.combinations(range(43),6)),dtype=np.int8)
s=b[combos].sum(1)
p=np.exp(-BETA*(s-s.min()));p/=p.sum()
rng=np.random.default_rng(NEXT)
pick=sorted((combos[rng.choice(len(combos),p=p)]+1).tolist())
rand=sorted((np.random.default_rng(NEXT*7+1).choice(43,6,replace=False)+1).tolist())
mult=lambda c:float(np.exp(sum(b[n-1] for n in c)))
pct=float((s<sum(b[n-1] for n in pick)).mean()*100)   # 全組合せ中の人気度の順位(低いほど人気薄)
out={"next":NEXT,"draws":N,"oos_corr":oos,"luna":pick,"random":rand,"mult_luna":mult(pick),"mult_rand":mult(rand),
 "percentile_luna":pct,"popular":[int(i+1) for i in np.argsort(-b)[:7]],"unpopular":[int(i+1) for i in np.argsort(b)[:7]],
 "b":{str(i+1):float(b[i]) for i in range(43)},"beta":BETA}
json.dump(out,open("luna_pick.json","w"),ensure_ascii=False,indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="b"},ensure_ascii=False))
