# Check of positioning note section 3.2.
# Round 5's cross-fitted estimator = T1 - T2; Williams (1961) k=2 estimator = T1 - (1-f) T2 (equal halves).
# Exact enumeration over all samples and all equal splits of a small finite population.
# Two coefficient rules: the unclipped least-squares slope of each half, and round 5's rule
# (slope clipped to [0, 1], coefficient 0 when n < 6).
import itertools, numpy as np
rng=np.random.default_rng(1)
G=10
f=rng.gamma(2,1,G); z=1.5*f+rng.normal(0,1,G)+0.4*f**2
theta=z.mean(); F=f.mean()
def slope(idx):
    ff=f[list(idx)]; zz=z[list(idx)]
    return np.cov(ff,zz,ddof=1)[0,1]/np.var(ff,ddof=1)
rules={'unclipped': lambda idx,n: slope(idx),
       'round5 (clip [0,1], 0 if n<6)': lambda idx,n: 0.0 if n<6 else min(1.0,max(0.0,slope(idx)))}
for name,lam in rules.items():
    print(name)
    for n in [4,6,8,10]:
        fr=n/G; r5=[]; wi=[]; covs=[]
        for S in itertools.combinations(range(G),n):
            S=list(S)
            for A in itertools.combinations(S,n//2):
                if S[0] not in A: continue   # each unordered split once
                B=[g for g in S if g not in A]; A=list(A)
                lA,lB=lam(A,n),lam(B,n)
                c=(lA+lB)/2
                est=c*F+(sum(z[g]-lB*f[g] for g in A)+sum(z[g]-lA*f[g] for g in B))/n
                T1=z[S].mean()-c*(f[S].mean()-F)
                T2=0.25*(lB-lA)*(f[A].mean()-f[B].mean())
                assert abs(est-(T1-T2))<1e-9
                W=T1+(1-fr)*0.5*((lA-c)*(f[A].mean()-f[S].mean())+(lB-c)*(f[B].mean()-f[S].mean()))
                assert abs(W-(T1-(1-fr)*T2))<1e-9
                r5.append(est); wi.append(W); covs.append((c, f[S].mean()))
        r5=np.array(r5); wi=np.array(wi); cv=np.array(covs)
        cov=np.mean((cv[:,0]-cv[:,0].mean())*(cv[:,1]-cv[:,1].mean()))
        pred = fr/(1-fr)*cov if fr<1 else float('nan')
        print(f"  n={n:2d} f={fr:.1f}  round5 bias={r5.mean()-theta:+.5f} (formula {pred:+.5f}) sd={r5.std():.5f} | Williams bias={wi.mean()-theta:+.1e} sd={wi.std():.5f}")
