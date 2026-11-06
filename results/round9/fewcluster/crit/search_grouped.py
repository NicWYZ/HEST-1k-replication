
import sys, json, math, numpy as np
sys.path.insert(0,'crit')
from core import *

def feas(vals,mult,k0):
    G=mult.sum(); m=(vals*mult).sum()/G; x=vals-m; T=(mult*x*x).sum()
    if T<=1e-12: return False
    return (x*x).max()/T<=k0*(1-1e-12)

def score(vals,mult,n,alpha):
    c,const=c_pop_grouped(vals,mult,n,alpha)
    return c

def init(G,k0,d,rng):
    for _ in range(2000):
        mult=np.ones(d,int)+rng.multinomial(G-d,np.ones(d)/d)
        base=rng.choice([-1.0,1.0],size=d)+rng.normal(0,rng.uniform(0.05,1.0),size=d)
        if feas(base,mult,k0): return base,mult
    return None

def anneal(G,n,alpha,k0,d,seed,iters=4000):
    rng=np.random.default_rng(seed)
    st=init(G,k0,d,rng)
    if st is None: return None
    vals,mult=st; cur=score(vals,mult,n,alpha); best=(cur,vals.copy(),mult.copy())
    T0=0.3
    for it in range(iters):
        temp=T0*(1-it/iters)+1e-3
        v2=vals.copy(); m2=mult.copy()
        r=rng.random()
        if r<0.35:
            i=rng.integers(len(vals)); v2[i]+=rng.normal(0,rng.choice([0.01,0.05,0.2]))
        elif r<0.7:
            i,j=rng.integers(len(vals),size=2)
            if i!=j and m2[i]>1: m2[i]-=1; m2[j]+=1
            else: continue
        elif r<0.85:
            # move value to boundary-ish: set value equal another group's value perturbed
            i,j=rng.integers(len(vals),size=2); v2[i]=v2[j]+rng.normal(0,0.02)
        else:
            i=rng.integers(len(vals)); v2*=1.0; v2[i]=rng.normal(0,1.5)
        if not feas(v2,m2,k0): continue
        s=score(v2,m2,n,alpha)
        if not np.isfinite(s): continue
        if s>=cur or rng.random()<math.exp((s-cur)/temp):
            vals,mult,cur=v2,m2,s
            if cur>best[0]: best=(cur,vals.copy(),mult.copy())
    return best

def run(args):
    G,n,alpha,k0,d,seed,iters=args
    b=anneal(G,n,alpha,k0,d,seed,iters)
    if b is None: return None
    x=b[1]-(b[1]*b[2]).sum()/G
    return dict(G=G,n=n,k0=k0,d=d,seed=seed,c=float(b[0]),vals=b[1].tolist(),mult=b[2].tolist(),kappa=float((x*x).max()/(b[2]*x*x).sum()))
