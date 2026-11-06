
"""core.py: exact coverage machinery for the fixed-coefficient finite-population interval.
Miss(S) <=> (sum_S x)^2 > rho * n * sum_S x^2, x = e - ebar, rho = g/(1+g), g = c^2 (1-f)/(n-1).
Statistic t_S = (sum_S x)^2 / (n sum_S x^2) in [0,1]  (t=1 <=> x constant on S, nonzero; t:=0 if x_S==0).
"""
import numpy as np, math, itertools
from math import comb

def pi_k(G,n,k): return (comb(G-k,n)+comb(k,n))/comb(G,n)
def kappa2(G,k): return (1-k/G)/k
def kstar(G,n,alpha):
    for k in range(1,G//2+1):
        if pi_k(G,n,k)<=alpha: return k
    return None
def frontier(G,n,alpha):
    ks=kstar(G,n,alpha); return kappa2(G,ks-1)
def kappa_of(x):
    x=np.asarray(x,float); x=x-x.mean(); return (x**2).max()/(x**2).sum()
def c_of_rho(rho,G,n):
    if rho>=1: return np.inf
    g=rho/(1-rho); return math.sqrt(g*(n-1)/(1-n/G))
def rho_of_c(c,G,n):
    g=c*c*(1-n/G)/(n-1); return g/(1+g)

def quantile_rho(t,w,alpha,tol=1e-9):
    """smallest rho with sum w[t>rho] <= alpha (w normalized). Returns (rho, constant_mass)."""
    t=np.asarray(t); w=np.asarray(w)
    const=w[t>1-tol].sum()
    if const>alpha+1e-15: return 1.0,const
    o=np.argsort(-t); ts=t[o]; cw=np.cumsum(w[o])
    # first index where cumulative weight > alpha (+tiny)
    idx=np.searchsorted(cw,alpha*(1+1e-12),side='right')
    if idx>=len(ts): return 0.0,const
    return float(ts[idx]),const

def grouped_stats(vals,mult,n):
    """exact distribution of t over SRSWOR for population with values vals (distinct groups) and multiplicities mult."""
    vals=np.asarray(vals,float); mult=np.asarray(mult,int); G=int(mult.sum()); d=len(vals)
    x=vals-(vals*mult).sum()/G
    # enumerate count vectors
    J=[]
    def rec(i,rem,cur):
        if i==d-1:
            if rem<=mult[i]: J.append(cur+[rem])
            return
        for j in range(min(rem,mult[i])+1): rec(i+1,rem-j,cur+[j])
    rec(0,n,[])
    J=np.array(J,int)
    logw=np.zeros(len(J))
    from scipy.special import gammaln
    lc=lambda a,b: gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1)
    for i in range(d): logw+=lc(mult[i],J[:,i])
    logw-=lc(G,n)
    w=np.exp(logw)
    A=J@x; Q=J@(x**2)
    t=np.where(Q>1e-300, A*A/(n*np.maximum(Q,1e-300)),0.0)
    # exact constant detection: sample entirely within one group (nonzero x)
    const=(J.max(axis=1)==n)&(np.abs(x[np.argmax(J,axis=1)])>1e-12*np.abs(x).max())
    t=np.where(const,1.0,t)
    return t,w,x

def c_pop_grouped(vals,mult,n,alpha):
    t,w,x=grouped_stats(vals,mult,n)
    G=int(np.sum(mult)); rho,const=quantile_rho(t,w,alpha)
    return c_of_rho(rho,G,n),const

def miss_prob_grouped(vals,mult,n,c):
    t,w,x=grouped_stats(vals,mult,n); G=int(np.sum(mult))
    return float(w[t>rho_of_c(c,G,n)].sum())

_idx_cache={}
def all_samples(G,n):
    key=(G,n)
    if key not in _idx_cache:
        _idx_cache[key]=np.array(list(itertools.combinations(range(G),n)),dtype=np.int8)
    return _idx_cache[key]

def t_full(e,n):
    e=np.asarray(e,float); G=len(e); x=e-e.mean(); S=all_samples(G,n)
    xs=x[S]; A=xs.sum(1); Q=(xs**2).sum(1)
    t=np.where(Q>1e-300,A*A/(n*np.maximum(Q,1e-300)),0.0)
    return t

def c_pop_full(e,n,alpha):
    t=t_full(e,n); G=len(e)
    w=np.full(len(t),1/len(t))
    # constant samples: tolerance
    rho,const=quantile_rho(t,w,alpha,tol=1e-9)
    return c_of_rho(rho,G,n),const

def direct_miss(e,n,c):
    """direct interval check, for validation"""
    e=np.asarray(e,float); G=len(e); S=all_samples(G,n); es=e[S]
    m=es.mean(1); s2=es.var(1,ddof=1); f=n/G
    half=c*np.sqrt((1-f)*s2/n)
    ebar=e.mean()
    return (np.abs(m-ebar)>half+0.0) # miss (point interval: half=0, miss iff m!=ebar)
