import sys,numpy as np,pandas as pd; sys.path.insert(0,'.')
from f_RRRIDGE_theory import Ridge
from scipy.optimize import brentq
def zeta_signal(R,S2):  # signal with weights s h^2 (predictable spike), energy S2 = theta*ma already in D
    z0=R.edge()*(1+1e-7); f=lambda z:S2*R.Dprod(z)[0]-1
    if f(z0)<=0: return None
    hi=z0*2
    while f(hi)>0: hi*=2
    return brentq(f,z0,hi,xtol=1e-12)
def zeta_nuis(R,psi):   # nuisance spike left vector H b, b independent of X: weights t
    mb=np.sum(R.nuw*R.t)
    def f(z):
        d=R.delta(z);k=1/(1+d)
        A=np.sum(R.nuw*R.t/(z-R.c*R.t*k))/mb
        B=(np.sum(R.nuw/(z-R.c*R.t*k))+R.nu0/z+(R.c-1)/z)/R.c
        return psi*mb*z*A*B-1
    z0=R.edge()*(1+1e-7)
    if f(z0)<=0: return None
    hi=z0*2
    while f(hi)>0: hi*=2
    return brentq(f,z0,hi,xtol=1e-12)
def sim(n,gam,c,th,psi,K,lam,seed):
    rng=np.random.default_rng(seed);p=int(gam*n);q=int(c*n)
    X=rng.standard_normal((n,p));u=rng.standard_normal(p);u/=np.linalg.norm(u)
    v=rng.standard_normal(q);v/=np.linalg.norm(v);xi=rng.standard_normal(q);xi/=np.linalg.norm(xi)
    g=np.repeat(np.arange(K),n//K); f=rng.standard_normal(K)[g]; f*=np.sqrt(n/np.sum(f**2))  # |Gf|^2=n
    Y=np.sqrt(th)*np.outer(X@u,v)+np.sqrt(psi)*np.outer(f,xi)+rng.standard_normal((n,q))
    U,s,_=np.linalg.svd(X,full_matrices=False);h=s**2/(s**2+n*lam)
    F=U@(h[:,None]*(U.T@Y))
    out=[]
    for M in (F,Y):
        vh=np.linalg.svd(M,full_matrices=False)[2][0]; out+= [(vh@v)**2,(vh@xi)**2]
    return out
rows=[]
for gam,c,th,psi in [(0.5,0.2,1.0,1.5),(0.5,0.2,1.0,0.5),(1.0,0.2,1.0,1.4),(1.0,0.2,0.8,1.0)]:
    R=Ridge(gam,c,0.1)
    zv=zeta_signal(R,th*R.ma); zn=zeta_nuis(R,psi)
    # PCA (H=I): outlier zeta=(1+l)(l+c)/l
    zp=lambda l:(1+l)*(l+c)/l if l>np.sqrt(c) else 0
    r=np.array([sim(1000,gam,c,th,psi,20,0.1,s) for s in range(10)])
    rows.append(dict(gamma=gam,c=c,theta=th,psi=psi,zeta_v_ridge=zv,zeta_nuis_ridge=zn,zeta_v_pca=zp(th),zeta_nuis_pca=zp(psi),
      ridge_top_overlap_v=r[:,0].mean(),ridge_top_overlap_xi=r[:,1].mean(),pca_top_overlap_v=r[:,2].mean(),pca_top_overlap_xi=r[:,3].mean(),reps=10))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('f_RRRIDGE_nuisance_sim.csv',index=False)
