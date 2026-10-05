import openpyxl, numpy as np, json, itertools
from scipy import stats
wb=openpyxl.load_workbook('loto6_all.xlsx',data_only=True);ws=wb.active
rows=[r for r in ws.iter_rows(min_row=2,values_only=True) if r[0]]
N=len(rows);nums=np.array([r[2:8] for r in rows])
n3,n4,n5=[np.array([r[i] for r in rows],float) for i in(11,12,13)]
def detr(x):
    y=np.log(np.maximum(x,1));o=np.zeros_like(y)
    for t in range(len(y)):
        lo,hi=max(0,t-30),min(len(y),t+31);o[t]=y[t]-np.median(y[lo:hi])
    return o
z=(detr(n3)+detr(n4)+detr(n5))/3
X=np.zeros((N,43))
for t in range(N):
    for n in nums[t]:X[t,n-1]=1
def fit(idx,lam=5.0):
    A=X[idx]-X[idx].mean(0);y=z[idx]-z[idx].mean()
    return np.linalg.solve(A.T@A+lam*np.eye(43),A.T@y)
tr=np.arange(100,1700);te=np.arange(1700,N)
b=fit(tr)
pred=(X[te]-X[tr].mean(0))@b
r=stats.pearsonr(pred,z[te]);print("out-of-sample corr",round(r[0],3),"p",r[1])
b=fit(np.arange(100,N))
pop=-b  # larger = more popular? b positive => more winners => popular
print("most popular:",[ (i+1,round(b[i],3)) for i in np.argsort(-b)[:8]])
print("least popular:",[ (i+1,round(b[i],3)) for i in np.argsort(b)[:8]])
def mult(c):return float(np.exp(sum(b[n-1] for n in c)))
# typical draw multiplier distribution
mm=np.array([np.exp((X[t]*b).sum()-(X.mean(0)*b).sum()*1) for t in range(N)])
print("multiplier over draws: 5%,50%,95%:",np.percentile(mm,[5,50,95]).round(2))
# candidate sets
best=None
rng=np.random.default_rng(1)
cands=[]
for c in itertools.combinations(range(1,44),6):
    pass
# ---- outputs
f31=(nums<=31).sum(1)
print("\nby count<=31: n draws, mean multiplier of winners (exp z)")
by={}
for k in range(0,7):
    m=f31==k
    if m.sum()>=5: by[k]=(int(m.sum()),float(np.exp(z[m]).mean()));print(k,by[k])
sm=nums.sum(1)
q=np.quantile(sm,[0,.25,.5,.75,1])
print("sum quartiles",q)
# least popular combo search with constraints
order=np.argsort(b)
best=sorted(itertools.combinations(range(1,44),6),key=lambda c:sum(b[n-1] for n in c))[:5]
for c in best:print("candidate",c,round(mult(c),3))
luna=sorted(best[0])
rng=np.random.default_rng(2144);rand=sorted((rng.choice(43,6,replace=False)+1).tolist())
print("LUNA",luna,mult(luna),"RANDOM",rand,mult(rand))
print("prev luna 2143",mult([9,10,17,26,33,35]),"2142",mult([7,9,13,17,29,34]))
# typical random set average
allr=[mult(sorted((rng.choice(43,6,replace=False)+1).tolist())) for _ in range(5000)]
print("random avg mult",np.mean(allr),np.percentile(allr,[5,50,95]))
json.dump({"b":{str(i+1):float(b[i]) for i in range(43)},"luna":luna,"rand":rand,"mult_luna":mult(luna),"mult_rand":mult(rand),"by31":by,"oos":float(r[0]),
 "prev2143":mult([9,10,17,26,33,35]),"avg_rand":float(np.mean(allr))},open("pop.json","w"))
