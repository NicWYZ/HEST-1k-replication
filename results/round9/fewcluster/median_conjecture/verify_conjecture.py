"""Numerical check of the three-cluster argument against the HulC-median conjecture.
P_{eta,D}: mass (1-eta)/2 uniform on [-1,1] (A), (1-eta)/2 on [2D-1,2D+1] (B), eta uniform on [D-w,D+w] (C).
Continuous, symmetric about D, unique median D (eta>0).  Forced misses: all-in-A and all-in-B.
Candidate shift-invariant intervals: order-statistic intervals [X_(i),X_(j)] and mean +- c*range; plus non-invariant (5)-type interval."""
import numpy as np, itertools
rng=np.random.default_rng(1)
def sample(n,N,eta,D,w):
    u=rng.random((N,n)); x=np.empty((N,n))
    comp=rng.choice(3,size=(N,n),p=[(1-eta)/2,(1-eta)/2,eta])
    x=np.where(comp==0,rng.uniform(-1,1,(N,n)),np.where(comp==1,rng.uniform(2*D-1,2*D+1,(N,n)),rng.uniform(D-w,D+w,(N,n))))
    return x
def miss_rates(n,eta,D=1e4,w=0.01,N=400000):
    x=sample(n,N,eta,D,w); th=D; xs=np.sort(x,1); out={}
    for i in range(n):
        for j in range(i,n):
            out[f"[X({i+1}),X({j+1})]"]=np.mean(~((xs[:,i]<=th)&(th<=xs[:,j])))
    rg=xs[:,-1]-xs[:,0]; m=x.mean(1)
    for c in (0.5,1,2,5):
        out[f"mean+-{c}*range"]=np.mean(~(np.abs(m-th)<=c*rg))
    # non-shift-invariant (5)-type interval, a=0: [min(a,Xi)<=th<=max(a,Xi)] counts >= k ; here k=n (all) -> th in all segments
    cnt=((np.minimum(0,x)<=th)&(th<=np.maximum(0,x))).sum(1)
    out["nonInv a=0, count>=ceil(n/2)"]=np.mean(~(cnt>=int(np.ceil(n/2))))
    return out
for n in (3,4,5):
    r=miss_rates(n,eta=1e-3)
    best=min(v for k,v in r.items() if 'nonInv' not in k)
    print(f"n={n}: 2^(1-n)={2**(1-n):.4f}  2^-n={2**-n:.4f}  forced 2((1-eta)/2)^n={2*((1-1e-3)/2)**n:.4f}")
    print(f"   min miss over shift-invariant candidates = {best:.4f}")
    print(f"   non-invariant (5)-type miss = {r['nonInv a=0, count>=ceil(n/2)']:.4f}")
    for k,v in r.items():
        if v<2*((1-1e-3)/2)**n-0.004 and 'nonInv' not in k: print("   VIOLATION",k,v)
# analyst's two-cluster (eps>0) variant: only far cluster forced
for eps in (0.0,0.05):
    n=3;D=1e4;N=400000
    x=np.where(rng.random((N,n))<0.5+eps,rng.uniform(-1,1,(N,n)),rng.uniform(2*D-1,2*D+1,(N,n)))
    xs=np.sort(x,1); m=-2*eps/(1+2*eps)  # median in near cluster
    miss=np.mean(~((xs[:,0]<=m)&(m<=xs[:,-1])))
    print(f"two-cluster eps={eps}: median={m:.3f}, miss of [X(1),X(n)] = {miss:.4f}; (1/2-eps)^n={(0.5-eps)**n:.4f}; 2^(1-n)={2**(1-n):.4f}")

# --- Proper eq.(5) interval of Paul & Kuchibhotla, a=0 (NOT shift-invariant), n=3, alpha=0.2 (log2(1/alpha)=2.32<n<log2(2/alpha)=3.32)
from scipy.stats import binom
def c_n_alpha(n,alpha):
    x=0
    while binom.sf(n//2-x-1,n,0.5)<1-alpha/2: x+=1   # P(Y>=floor(n/2)-x)>=1-alpha/2
    return x
n,alpha=3,0.2
k=n//2-c_n_alpha(n,2*alpha)
print("eq.(5) threshold k =",k)
N=400000; D=1e4
for eta in (1e-3,0.2):
    x=sample(n,N,eta,D,0.01); cnt=((np.minimum(0,x)<=D)&(D<=np.maximum(0,x))).sum(1)
    print(f"eq.(5), a=0: three-cluster eta={eta}: miss={np.mean(cnt<k):.4f} (<= alpha={alpha}); shift-invariant forced bound 2((1-eta)/2)^n={2*((1-eta)/2)**n:.4f}")
# worst-case over D of eq.(5) interval for median at D over a few distributions: point mass-like two-point checks
for D in (0.0,1.0,1e4):
    for p in (0.5,):
        x=np.where(rng.random((N,n))<p,-1.0,1.0)+D  # median set [D-1,D+1]; check theta=D (a median)
        cnt=((np.minimum(0,x)<=D)&(D<=np.maximum(0,x))).sum(1)
        print(f"two-point D={D}: miss at theta=D {np.mean(cnt<k):.4f}")
