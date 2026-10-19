# Check: round 5's cross-fitted estimator = T1 - T2, Williams (1961) k=2 estimator = T1 - (1-f) T2.
# Exact enumeration over all samples and all equal splits for a small finite population.
import itertools, numpy as np
rng=np.random.default_rng(1)
G=10
f=rng.gamma(2,1,G); z=1.5*f+rng.normal(0,1,G)+0.4*f**2
theta=z.mean(); F=f.mean()
def lam(idx):
    ff=f[list(idx)]; zz=z[list(idx)]
    return np.cov(ff,zz,ddof=1)[0,1]/np.var(ff,ddof=1)
for n in [4,6,8,10]:
    fr=n/G; r5=[]; wi=[]; t1s=[]; t2s=[]
    for S in itertools.combinations(range(G),n):
        S=list(S)
        for A in itertools.combinations(S,n//2):
            if S[0] not in A: continue   # each unordered split once
            B=[g for g in S if g not in A]; A=list(A)
            lA,lB=lam(A),lam(B)
            c=(lA+lB)/2
            est=c*F+(sum(z[g]-lB*f[g] for g in A)+sum(z[g]-lA*f[g] for g in B))/n
            T1=z[S].mean()-c*(f[S].mean()-F)
            kap=0.25
            T2=kap*(lB-lA)*(f[A].mean()-f[B].mean())
            assert abs(est-(T1-T2))<1e-9
            W=T1+(1-fr)*(1/(2*1))*((lA-c)*(f[A].mean()-f[S].mean())+(lB-c)*(f[B].mean()-f[S].mean()))
            assert abs(W-(T1-(1-fr)*T2))<1e-9
            r5.append(est); wi.append(W)
    r5=np.array(r5); wi=np.array(wi)
    print(f"n={n:2d} f={fr:.1f}  R5 bias={r5.mean()-theta:+.5f} sd={r5.std():.5f} | Williams bias={wi.mean()-theta:+.2e} sd={wi.std():.5f}")
