import openpyxl, numpy as np, json
from scipy import stats
wb=openpyxl.load_workbook('loto6_all.xlsx',data_only=True);ws=wb.active
rows=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
N=len(rows);print("draws",N)
nums=np.array([r[2:8] for r in rows]);bonus=np.array([r[8] for r in rows])
n3=np.array([r[11] for r in rows],float);n4=np.array([r[12] for r in rows],float);n5=np.array([r[13] for r in rows],float)
# 1) uniformity
cnt=np.bincount(nums.ravel(),minlength=44)[1:]
chi=stats.chisquare(cnt);print("freq chi2 p=",chi.pvalue,"min",cnt.min(),"max",cnt.max(),"expected",N*6/43)
# 2) walk-forward backtest
rng=np.random.default_rng(0)
start=300
def hits(pred,t):return len(set(pred)&set(nums[t]))
res={k:[] for k in["ランダム","ホット50回","ホット10回","コールド(通算少)","未出現期間長い","ホット3+コールド3"]}
for t in range(start,N):
    past=nums[:t]
    allc=np.bincount(past.ravel(),minlength=44)[1:]
    h50=np.bincount(past[-50:].ravel(),minlength=44)[1:]
    h10=np.bincount(past[-10:].ravel(),minlength=44)[1:]
    last=np.zeros(43)
    for n in range(1,44):
        idx=np.where((past==n).any(axis=1))[0];last[n-1]=t-(idx[-1] if len(idx) else 0)
    top=lambda a,k:list(np.argsort(-a,kind="stable")[:k]+1)
    res["ランダム"].append(hits(list(rng.choice(43,6,replace=False)+1),t))
    res["ホット50回"].append(hits(top(h50,6),t))
    res["ホット10回"].append(hits(top(h10,6),t))
    res["コールド(通算少)"].append(hits(top(-allc,6),t))
    res["未出現期間長い"].append(hits(top(last,6),t))
    res["ホット3+コールド3"].append(hits(top(h50,3)+[x for x in top(-allc,6) if x not in top(h50,3)][:3],t))
exp=36/43
out={}
for k,v in res.items():
    v=np.array(v);m=v.mean();se=v.std(ddof=1)/np.sqrt(len(v))
    out[k]={"mean":m,"se":se,"zero":float((v==0).mean()),"ge3":float((v>=3).mean())}
    print(f"{k:14s} 平均一致 {m:.3f} ±{se:.3f}  0個率 {100*(v==0).mean():.1f}%  3個以上 {100*(v>=3).mean():.2f}%")
print("理論値 平均",round(exp,3))
json.dump({"n":N-start,"exp":exp,"res":out},open("backtest.json","w"))
# 3) popularity analysis: detrended log winners
def detr(x):
    y=np.log(x);out=np.zeros_like(y)
    for t in range(len(y)):
        lo,hi=max(0,t-30),min(len(y),t+31);out[t]=y[t]-np.median(y[lo:hi])
    return out
m=(n4>0)&(n5>0)&(n3>0)
for name,arr in[("3等",n3),("4等",n4),("5等",n5)]:
    z=detr(np.maximum(arr,1))
    f_low=(nums<=31).sum(1);f_b12=(nums<=12).sum(1)
    cs=np.sort(nums,1);consec=(np.diff(cs,axis=1)==1).sum(1);ssum=nums.sum(1)
    sl=slice(100,N)
    for fn,f in[("31以下の個数",f_low),("12以下の個数",f_b12),("連番ペア数",consec),("合計値",ssum)]:
        r=stats.pearsonr(f[sl],z[sl]);print(name,fn,"相関",round(r[0],3),"p",round(r[1],4))
