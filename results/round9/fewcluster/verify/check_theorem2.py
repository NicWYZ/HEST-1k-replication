import sys, time; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from frontier_common import *
rng=np.random.default_rng(5)
CS=[1,2,3,5,10,30,100,1e3,1e4,1e5,1e6]
def norm(e):
    e=e-e.mean(); return e/np.sqrt((e**2).sum())
def search(G,n,kappa0,c,starts,steps,idx,mk,beta_cnt):
    best=0; bestE=None
    for si in range(starts):
        # starting point
        if si%3==2 or not mk:
            e=np.zeros(G); e[:G//2]=1; e+=rng.normal(size=G)*0.3
        else:
            p=list(mk)[rng.integers(len(mk))]; e=mk[p].copy()
            e=e+rng.normal(size=G)*10**rng.uniform(-6,-1)
        e=norm(e)
        if not (kappa(e)<=kappa0): continue
        cur=int(miss_mask(e,c,G,n,idx).sum())
        for t in range(steps):
            e2=e.copy()
            r=rng.random()
            if r<0.4:
                j=rng.integers(G); e2[j]+=rng.normal()*10**rng.uniform(-7,0)
            elif r<0.7:
                j,l=rng.choice(G,2,replace=False); e2[j]=e2[l]+rng.normal()*10**rng.uniform(-9,-1)
            elif r<0.85:
                e2+=rng.normal(size=G)*10**rng.uniform(-7,-1)
            else:
                m=rng.random(G)<0.5; e2[m]=e2[m].mean()+rng.normal(size=m.sum())*10**rng.uniform(-9,-2)
            e2=norm(e2)
            if not (kappa(e2)<=kappa0): continue
            v=int(miss_mask(e2,c,G,n,idx).sum())
            if v>=cur:
                e,cur=e2,v
        if cur>best: best,bestE=cur,e
    return best,bestE
rows=[]
t0=time.time()
for (G,n) in [(8,3),(10,4),(12,4)]:
    idx=samples(G,n); N=len(idx)
    parts=[p for p in partitions(G) if len(p)>=2]
    mkd={p:min_kappa_partition(p) for p in parts}
    thr=sorted(set(round(v[0],12) for v in mkd.values()))
    # intervals with distinct beta
    def beta_at(k0): return max([sum(C(m,n) for m in p) for p in parts if mkd[p][0]<=k0+1e-12]+[0])
    intervals=[(thr[i],thr[i+1]) for i in range(len(thr)-1)]
    # keep intervals where beta changes info: pick up to 4 spread, with beta>0
    cand=[(a,b) for a,b in intervals if beta_at((a+b)/2)>0 and (a+b)/2<0.6]
    pick=[cand[int(i)] for i in np.linspace(0,len(cand)-1,min(4,len(cand)))]
    for a,b in pick:
        k0=(a+b)/2; bcnt=beta_at(k0); beta=bcnt/N
        # starting points: minimizers of all partitions feasible, mixed with balanced population for slack
        mk={}
        for p in parts:
            if mkd[p][0]<=k0-1e-9:
                mk[p]=mkd[p][1]
        for c in CS:
            found,_=search(G,n,k0,c,starts=24,steps=600,idx=idx,mk=mk,beta_cnt=bcnt)
            rows.append(dict(G=G,n=n,kappa0=k0,beta=beta,beta_count=bcnt,N=N,c=c,worst_miss_count_found=found,
                             worst_cov_found=1-found/N,one_minus_beta=1-beta,exceeds_beta=found>bcnt))
        print(G,n,round(k0,4),'beta',round(beta,4),round(time.time()-t0),'s',flush=True)
df=pd.DataFrame(rows); df.to_csv('checks_theorem2.csv',index=False)
pd.set_option('display.width',250)
for key,g in df.groupby(['G','n','kappa0']):
    print(key, 'beta_count',g.beta_count.iloc[0],'of',g.N.iloc[0]); print(g[['c','worst_miss_count_found','worst_cov_found','one_minus_beta','exceeds_beta']].to_string(index=False))
