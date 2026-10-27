"""Round 9 newtopic interval 3: F1 (ridge-then-PCA reduced-rank) derivation and corollary check.

G2: deterministic-equivalent threshold and overlap for top right singular vector of F = H Y,
H = X (X'X + n lam I)^{-1} X', conditional on X (class RRR).
S1: comparison with Liu, Liu, Pan, Zhang, Zhang arXiv:2310.13939 Theorem 1 (A + Sigma^{1/2} W),
applied conditionally on X with Sigma = H^2, A = sqrt(theta) H X u v'/sqrt(q) (liu_overlap).
Outputs: results/round9/newtopic/i03/*.csv
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
import numpy as np
from scipy.optimize import brentq, minimize_scalar
def mp_quad(g, NQ=6000):
    a,b=(1-np.sqrt(g))**2,(1+np.sqrt(g))**2
    ph=(np.arange(NQ)+.5)*np.pi/NQ
    x=(a+b)/2+(b-a)/2*np.cos(ph)
    dens=np.sqrt((b-x)*(x-a))/(2*np.pi*g*x)
    w=dens*((b-a)/2)*np.sin(ph)*(np.pi/NQ)
    return x,w   # continuous part of MP_g; total mass min(1,1/g)
class RRR:
    """Conditional-on-X theory, my own normalisation. nu = law of the n eigen-directions of H."""
    def __init__(s,g,c,lam):
        s.g,s.c,s.lam=g,c,lam
        x,w=mp_quad(g)              # eigenvalues s of X'X/n (nonzero part), weights over p
        h=x/(x+lam) if lam>0 else np.ones_like(x)
        s.t=h**2
        s.nu=g*w                    # weights over n directions (nonzero part)
        s.nu0=max(1-g,0.0)          # zero directions (t=0)
        s.ma=np.sum(w*x*s.t)        # int s h^2 dmu_g  = beta^2/theta
        al=s.nu*s.t*x; s.al=al/al.sum()
    def zeta(s,m):   # inverse of m~(zeta) on the real branch
        return -1/m + np.sum(s.nu*s.t/(1+s.c*s.t*m))
    def dzeta(s,m):
        return 1/m**2 - np.sum(s.nu*s.c*s.t**2/(1+s.c*s.t*m)**2)
    def P(s,m): return -m*np.sum(s.al/(1+s.c*s.t*m))
    def dP(s,m): return -np.sum(s.al/(1+s.c*s.t*m)) + m*np.sum(s.al*s.c*s.t/(1+s.c*s.t*m)**2)
    def mstar(s):
        lo=-1/(s.c*s.t.max())*(1-1e-12); hi=-1e-12
        # dzeta>0 near 0-, find root of dzeta in (lo,hi)
        return brentq(s.dzeta, lo*(1-1e-9) if s.dzeta(lo)<0 else lo, hi) if s.dzeta(lo)<0 else lo
    def threshold(s):
        m=s.mstar(); return 1/(s.ma*s.P(m))
    def overlap(s,theta):
        ms=s.mstar(); b2=theta*s.ma
        if b2*s.P(ms)<=1: return 0.0, None
        m=brentq(lambda m: b2*s.P(m)-1, ms, -1e-14)
        ov=m*s.P(m)*s.dzeta(m)/s.dP(m)
        return ov, s.zeta(m)
def pca_thr(c): return np.sqrt(c)
def pca_ov(c,th): return 0.0 if th<=np.sqrt(c) else (1-c/th**2)/(1+c/th)

def liu_overlap(n,g,c,lam,theta,seed=0):
    rng=np.random.default_rng(seed); p=int(g*n); q=int(c*n)
    X=rng.standard_normal((n,p)); u=np.zeros(p); u[0]=1
    G=X.T@X; H=X@np.linalg.solve(G+n*lam*np.eye(p),X.T)
    a=H@(X@u)
    R=H@H + theta/q*np.outer(a,a)
    w,V=np.linalg.eigh(R); gk=w[-1]; xi=V[:,-1]; others=w[:-1]
    eta=1-np.sum(others**2/(gk-others)**2)/q
    Av_sq=theta/q*(xi@a)**2
    return eta*Av_sq/gk, gk, w[-2]

if __name__=="__main__":
    import pandas as pd
    rows=[]
    for (g,c,lam) in [(0.5,0.1,0.3),(2,0.25,3),(2,0.1,0.3),(0.5,0.25,3)]:
        M=RRR(g,c,lam); th0=M.threshold()
        for f in [1.5,2.5,4]:
            th=f*th0
            los=[liu_overlap(1500,g,c,lam,th,seed=s)[0] for s in range(3)]
            rows.append((g,c,lam,th,np.mean(los),float(M.overlap(th)[0])))
    L=pd.DataFrame(rows,columns=['gamma','c','lam','theta','liu_thm1_n1500_mean3','mine_limit'])
    L['diff']=L.liu_thm1_n1500_mean3-L.mine_limit
    L.to_csv('results/round9/newtopic/i03/s1_liu2310_13939_vs_mine.csv',index=False)
    print(L.round(4).to_string())
