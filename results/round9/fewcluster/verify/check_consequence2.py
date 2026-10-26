import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd, math, time
from frontier_common import *
rng=np.random.default_rng(21)
print('pi(k) nonincreasing for k<=G/2 (G 4..60, 2<=n<=min(12,G)):',all(pi_k(G,n,k)>=pi_k(G,n,k+1)-1e-15 for G in range(4,61) for n in range(2,min(12,G)+1) for k in range(1,G//2)))
alpha=0.1
print('threshold 1+log2(1/alpha)=',1+math.log2(1/alpha))
for n in (3,4,5):
    print('n',n,'2^(1-n)=',2**(1-n),'pi(floor(G/2)) at G=20,50,200,1000,10000:',[round(pi_k(G,n,G//2),5) for G in (20,50,200,1000,10000)])
# smallest G with pi(floor(G/2))>alpha for n=3,4
for n in (3,4):
    print('n',n,'smallest G with pi(G//2)>0.1:',next(G for G in range(2*n,5000) if pi_k(G,n,G//2)>alpha))
# direct G=24,n=8 tests
G,n=24,8; idx=samples(G,n); N=len(idx); print('N',N)
rows=[]
# (a) kappa0=0.14 in (kappa2(6),kappa2(5)): hill-climb worst coverage for several c
kappa0=0.14
def norm(e): e=e-e.mean(); return e/np.sqrt((e**2).sum())
for c in [3,5,10,30,100]:
    best=0
    for st in range(4):
        e=np.zeros(G); e[:6]=1; e=norm(e+rng.normal(size=G)*10**rng.uniform(-6,-2))
        assert kappa(e)<=kappa0
        cur=miss_mask(e,c,G,n,idx).sum()
        for t in range(150):
            e2=e.copy(); j=rng.integers(G); e2[j]+=rng.normal()*10**rng.uniform(-7,0); 
            if rng.random()<.3: e2[rng.integers(G)]=e2[rng.integers(G)]+rng.normal()*1e-6
            e2=norm(e2)
            if kappa(e2)>kappa0: continue
            v=miss_mask(e2,c,G,n,idx).sum()
            if v>=cur: e,cur=e2,v
        best=max(best,cur)
    rows.append(dict(G=G,n=n,kappa0=kappa0,c=c,worst_cov_found=1-best/N,one_minus_pi6=1-pi_k(G,n,6),alpha=alpha))
    print(rows[-1],flush=True)
# (b) kappa0=0.17>kappa2(5): z_eps with k=5 -> coverage <= 1-pi(5)=0.8972 for any c
k=5; ind=np.zeros(G); ind[:k]=1; u=rng.normal(size=G)
for c in [3,100,1e3]:
    for eps in [1e-6,1e-9]:
        e=ind+eps*u; cov=1-miss_mask(e,c,G,n,idx).mean()
        rows.append(dict(G=G,n=n,kappa0=0.17,c=c,eps=eps,kappa_e=kappa(e),worst_cov_found=cov,one_minus_pi5=1-pi_k(G,n,5),alpha=alpha))
        print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('checks_consequence_G24.csv',index=False)
