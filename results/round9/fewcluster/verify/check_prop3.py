import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd, math
from frontier_common import *
from scipy.optimize import minimize
rng=np.random.default_rng(3)
# validate min_kappa_partition against random numerical optimisation on a few partitions
def num_min(part,restarts=60):
    G=sum(part); lab=np.repeat(np.arange(len(part)),part); best=9
    for _ in range(restarts):
        v0=rng.normal(size=len(part))
        f=lambda v: kappa(v[lab]) if np.ptp(v)>1e-9 else 9
        r=minimize(f,v0,method='Nelder-Mead',options={'xatol':1e-10,'fatol':1e-12,'maxiter':4000})
        best=min(best,r.fun)
    return best
dev=0
for part in [(5,4,3),(6,3,2,1),(4,4,2,1,1),(7,5),(3,3,3,2,1),(6,6),(5,5,2)]:
    a=min_kappa_partition(part)[0]; b=num_min(part); dev=max(dev,abs(a-b)); 
    assert b>=a-1e-6, (part,a,b)
print('max |exact - numerical| (numerical never below exact):',dev)

rows=[]; viol=[]
def R_bound(G,n):
    best=0
    for m in range(1,G+1):
        if m<G/2:
            best=max(best,(G//m*C(m,n)+C(G%m,n))/C(G,n))
    return best
for G in range(6,17):
    parts=list(partitions(G))
    mk={}
    for p in parts:
        if len(p)>=2: mk[p]=min_kappa_partition(p)[0]
    for n in range(2,min(7,G)):
        cnt={p:sum(C(m,n) for m in p) for p in mk}
        Rb=R_bound(G,n)
        thresholds=sorted(set(round(v,12) for v in mk.values()))
        pts=[]
        for t in thresholds:
            pts+= [t, t*(1+1e-6)]
        for k0 in pts:
            beta=max([cnt[p] for p in mk if mk[p]<=k0+1e-12]+[0])/C(G,n)
            ks=[k for k in range(1,G//2+1) if kappa2(G,k)<=k0+1e-12]
            LB=max([pi_k(G,n,k) for k in ks]+[0])
            UB=max(LB,Rb)
            ok=(LB<=beta+1e-12) and (beta<=UB+1e-12)
            rows.append(dict(G=G,n=n,kappa0=k0,beta=beta,LB=LB,R=Rb,UB=UB,ok=ok,LB_tight=abs(beta-LB)<1e-12,UB_tight=abs(beta-UB)<1e-12))
            if not ok: viol.append(rows[-1])
df=pd.DataFrame(rows); df.to_csv('checks_prop3.csv',index=False)
print(len(df),'checked (G,n,kappa0) combos; violations:',len(viol))
print('LB tight in',df.LB_tight.mean().round(3),'; beta strictly above LB in',(~df.LB_tight).sum(),'cases; of those UB tight',df[~df.LB_tight].UB_tight.mean().round(3))
print(df[~df.LB_tight].head(8).to_string())
