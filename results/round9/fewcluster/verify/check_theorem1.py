import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from frontier_common import *
rng=np.random.default_rng(7)
rows=[]
cs=[1,2,5,10,100,1e3,1e5]
for (G,n) in [(8,3),(10,4),(12,4)]:
    idx=samples(G,n); N=len(idx)
    for k in range(1,G//2+1):
        pk=pi_k(G,n,k); k2=kappa2(G,k)
        # kappa0 slightly above kappa2(k)
        kappa0=k2*1.02 if k2*1.02<=1 else 1.0
        for utype in ['gauss','heavy','constB1B2','gauss_big']:
            if utype=='gauss': u=rng.normal(size=G)
            elif utype=='heavy': u=rng.standard_cauchy(size=G)
            elif utype=='gauss_big': u=rng.normal(size=G)*1e3+50
            else: u=np.zeros(G)   # u constant => S inside B1 or B2 have s=0
            B2=rng.choice(G,k,replace=False); ind=np.zeros(G); ind[B2]=1
            # smallest eps at which e_eps is in K(kappa0): scan
            for c in cs:
                covs=[]; inK=[]
                for eps in [1e-1,1e-2,1e-3,1e-4,1e-6,1e-8]:
                    e=ind+eps*u
                    kv=kappa(e); inK.append(kv<=kappa0)
                    miss=miss_mask(e,c,G,n,idx)
                    covs.append(1-miss.mean())
                # restrict to eps where e_eps in K
                covK=[cv for cv,ok in zip(covs,inK) if ok]
                rows.append(dict(G=G,n=n,k=k,kappa0=kappa0,pi_k=pk,u=utype,c=c,
                                 cov_eps1e8=covs[-1],cov_eps1e6=covs[-2],limit_bound_1_minus_pi=1-pk,
                                 in_K_at_all_eps=all(inK),
                                 ok=(covs[-1]<=1-pk+1e-12)))
df=pd.DataFrame(rows); df.to_csv('checks_theorem1.csv',index=False)
print(len(df), df.ok.mean(), (df.in_K_at_all_eps).mean())
# how tight: coverage at eps=1e-8 minus (1-pi)
df['gap']=df.cov_eps1e8-(1-df.pi_k)
print(df.groupby(['G','n','c']).gap.agg(['min','max']).round(4).to_string())
print(df[~df.ok].head())
# OLS-tuned PPI interval (satisfies (E) by construction) on z_eps
def ols_cov(G,n,k,c,eps,u,lam=0.7):
    f=rng.normal(size=G)+1.0
    B2=np.arange(k); ind=np.zeros(G); ind[B2]=1
    z=lam*f+ind+eps*u
    idx=samples(G,n); miss=0
    theta=z.mean()
    for S in idx:
        X=np.c_[np.ones(n),f[S]]; lh=np.linalg.lstsq(X,z[S],rcond=None)[0][1]
        r=z[S]-lh*f[S]; est=lh*f.mean()+r.mean(); se=np.sqrt((1-n/G)*r.var(ddof=1)/n)
        if abs(est-theta)>c*se: miss+=1
    return 1-miss/len(idx)
orow=[]
for (G,n,k) in [(10,4,3),(10,4,5),(12,4,4)]:
    u=rng.normal(size=G)
    for c in [2,10,100]:
        for eps in [1e-3,1e-6]:
            cv=ols_cov(G,n,k,c,eps,u); orow.append(dict(G=G,n=n,k=k,c=c,eps=eps,cov_ols=cv,one_minus_pi=1-pi_k(G,n,k)))
od=pd.DataFrame(orow); od.to_csv('checks_theorem1_ols.csv',index=False); print(od.round(4).to_string())
