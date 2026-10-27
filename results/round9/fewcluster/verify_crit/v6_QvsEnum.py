import numpy as np, itertools, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qlib import *
G,n=24,8
combos=np.array(list(itertools.combinations(range(G),n)),dtype=np.int16)
rng=np.random.default_rng(2)
kap0=F(19,300)
for c in [F(3775,1000),F(3,1)]:
    b,a=bound_float(G,n,kap0,float(c))
    rho=float(rho_of(G,n,c)); 
    a1,a2=float(a[0]),float(a[1])
    for trial in range(5):
        while True:
            x=rng.standard_t(2,G) if trial%2 else rng.normal(size=G)*(1+rng.integers(0,2,G)*2)
            x=x-x.mean(); x=x/np.sqrt((x**2).sum())
            if (x**2).max()<=float(kap0): break
            # shrink spikes
            x=np.clip(x,-0.5*np.sqrt(float(kap0))*1.0,0.5*np.sqrt(float(kap0))); x=x-x.mean(); x/=np.sqrt((x**2).sum())
            if (x**2).max()<=float(kap0): break
        v=x[combos]; A=v.sum(1); Q=(v**2).sum(1); u=A*A
        L=1+a1*u+a2*Q
        miss=(u>rho*n*Q)
        p4=(x**4).sum()
        formula=1+2*a1*moms(G,n,0)[0].__float__()+0  # placeholder
        m=[float(t) for t in moms(G,n,F(p4).limit_denominator(10**12))]
        EL2f=1+2*a1*m[0]+2*a2*m[1]+a1*a1*m[2]+2*a1*a2*m[3]+a2*a2*m[4]
        print(f"c={float(c):.3f} trial{trial} kappa={(x**2).max():.4f} p4={p4:.4f} P(miss)={miss.mean():.5f}  E L^2 enum={np.mean(L*L):.6f} formula={EL2f:.6f}  L>=1 on miss: {bool(np.all(L[miss]>=1-1e-12)) if miss.any() else True}")
