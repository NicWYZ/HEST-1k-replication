"""theta*(lam) on a realized X (c=0.1, n=2000, gamma from argv): root of eta_1(theta)=0
(Liu et al. distant-spike condition), compared with PCA-of-Y threshold sqrt(c)
(BBP for Y = sqrt(theta) Xu v' + E, ||Xu||^2 ~ n).  Single realization of X: finite-n error ~ +-0.005."""
import numpy as np, pandas as pd, sys
from scipy.optimize import brentq
n=2000; gam=float(sys.argv[1]); c=0.1; p=int(gam*n); q=int(c*n)
rng=np.random.default_rng(3); X=rng.standard_normal((n,p))
Uf,s,Vt=np.linalg.svd(X,full_matrices=True)   # Uf n x n; s has min(n,p) entries
m=len(s); Xu=X[:,0]
rows=[]
for lam in [0.0,0.05,0.1,0.3,1.0,3.0]:
    h=np.zeros(n); h[:m]=s**2/(s**2+n*lam) if lam>0 else 1.0
    w=Uf.T@(Uf[:,:m]@(h[:m]*(Uf[:,:m].T@Xu)))   # H X u in eigenbasis of H
    S2=h**2
    def eta(theta):
        a=np.sqrt(theta/q)*w
        g=np.linalg.eigvalsh(np.diag(S2)+np.outer(a,a))[::-1]
        return 1-np.sum(g[1:]**2/(g[0]-g[1:])**2)/q
    try: ts=brentq(eta,0.02,3.0,xtol=1e-3)
    except Exception as e: ts=np.nan
    rows.append(dict(gamma=gam,lam=lam,theta_star_realized=ts,theta_PCA=np.sqrt(c)))
df=pd.DataFrame(rows); df.to_csv(f'threshold_vs_lambda_gamma{gam}.csv',index=False); print(df.round(4))
