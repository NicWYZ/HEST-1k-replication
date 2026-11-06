import sys,numpy as np,pandas as pd; sys.path.insert(0,'.')
from f_RRRIDGE_theory import Ridge,pca
LAM=0.1; THS=[0.3,0.5,0.8,1.2,2.0]; CS=[0.1,0.3]
REPS={500:20,1000:12,2000:4}
rows=[]
for n in (500,1000,2000):
  for gam in (0.5,1,2):
    res={}
    for rep in range(REPS[n]):
        rng=np.random.default_rng(1000*n+10*int(gam*10)+rep)
        p=int(gam*n); X=rng.standard_normal((n,p))
        u=rng.standard_normal(p);u/=np.linalg.norm(u)
        U,s,_=np.linalg.svd(X,full_matrices=False); h=s**2/(s**2+n*LAM)
        for c in CS:
            q=int(c*n); v=rng.standard_normal(q);v/=np.linalg.norm(v)
            N=rng.standard_normal((n,q))
            for th in THS:
                Y=np.sqrt(th)*np.outer(X@u,v)+N
                F=U@(h[:,None]*(U.T@Y))
                a=(np.linalg.svd(F,full_matrices=False)[2][0]@v)**2
                b=(np.linalg.svd(Y,full_matrices=False)[2][0]@v)**2
                res.setdefault((c,th),[]).append((a,b))
    for (c,th),L in res.items():
        L=np.array(L); R=Ridge(gam,c,LAM)
        rows.append(dict(n=n,gamma=gam,c=c,theta=th,lam=LAM,reps=len(L),sim_ridge=L[:,0].mean(),se_ridge=L[:,0].std(ddof=1)/np.sqrt(len(L)),
          sim_pca=L[:,1].mean(),se_pca=L[:,1].std(ddof=1)/np.sqrt(len(L)),th_ridge=R.align(th)[1],th_pca=pca(c,th),thr_ridge=R.threshold(),thr_pca=np.sqrt(c)))
    pd.DataFrame(rows).to_csv('f_RRRIDGE_sim_vs_theory.csv',index=False); print(n,gam,flush=True)
