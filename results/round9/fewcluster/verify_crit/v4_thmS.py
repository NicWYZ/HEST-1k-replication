from fractions import Fraction as F
import itertools, numpy as np
from scipy.optimize import minimize
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qlib import moms
def rs(N,m,s):
    """r4, rDV, rVV for stratum of size N, sample m, with p1=0,p2=1,p4=s (exact Fractions). W=1."""
    N=F(N);m=F(m);s=F(s)
    EA2,EQ,EA4,EA2Q,EQ2=moms(N,m,s)
    c1=(1-m/N)/(m*(m-1))
    V=EA2/m**2                               # E D^2
    EV=c1*(EQ-EA2/m)                          # E Vhat
    ED4=EA4/m**4
    EDV=c1*(EA2Q-EA4/m)/m**2                  # E D^2 Vhat
    EVV=c1**2*(EQ2-2*EA2Q/m+EA4/m**2)         # E Vhat^2
    return EV/V, ED4/V**2, EDV/V**2, EVV/V**2
# unbiasedness
print("E Vhat/V =",rs(20,5,F(1,20))[0], rs(7,3,F(1,3))[0])
# full enumeration test: 3 strata (N=7,m=3), independent, V normalised by direct computation
import random
random.seed(5)
def stratum_dist(xs,m,W):
    N=len(xs); mu=F(sum(xs),N); out=[]
    for S in itertools.combinations(range(N),m):
        d=W*(F(sum(xs[i] for i in S),m)-mu)
        xb=F(sum(xs[i] for i in S),m); s2=sum((xs[i]-xb)**2 for i in S)/(m-1)
        vh=W*W*(1-F(m,N))*s2/m
        out.append((d,vh))
    return out
N,m=7,3
strata=[[F(random.randint(-6,6)) for _ in range(N)] for _ in range(3)]
Ws=[F(1),F(2),F(1,2)]
dists=[stratum_dist(x,m,W) for x,W in zip(strata,Ws)]
Vh=[sum(d*d for d,_ in ds)/len(ds) for ds in dists]; V=sum(Vh)
a1,a2=F(3,10),F(-1,2)
tot=F(0);cnt=0
for combo in itertools.product(*dists):
    u=sum(d for d,_ in combo)**2; q=sum(v for _,v in combo)
    L=1+a1*u/V+a2*q/V; tot+=L*L; cnt+=1
direct=tot/cnt
# formula
vh=[v/V for v in Vh]
form=1+2*(a1+a2)+3*a1**2+2*a1*a2+a2**2
for x,v in zip(strata,vh):
    mu=F(sum(x),N); xc=[t-mu for t in x]; p2=sum(t**2 for t in xc); p4=sum(t**4 for t in xc)
    s=p4/p2**2
    _,r4,rDV,rVV=rs(N,m,s)
    form+=v*v*(a1**2*(r4-3)+2*a1*a2*(rDV-1)+a2**2*(rVV-1))
print("3-stratum enumeration:",float(direct)," formula:",float(form)," equal exactly:",direct==form)

# ---- certified c for requested settings
def bound(a,c,N,m,Lam0,v0):
    a1,a2=a
    base=1+2*(a1+a2)+3*a1**2+2*a1*a2+a2**2
    best=0
    for s in [1/N, Lam0**2/(N-1)]:
        _,r4,rDV,rVV=[float(t) for t in rs(N,m,F(s).limit_denominator(10**12))]
        K=a1**2*(r4-3)+2*a1*a2*(rDV-1)+a2**2*(rVV-1); best=max(best,K)
    return base+v0*best
def opt(c,N,m,Lam0,v0):
    bst=(9,None)
    for x0 in [(0.3,-0.5),(0.1,-0.2),(0.5,-1),(0.05,-0.1),(1,-2),(0.02,-0.03)]:
        r=minimize(lambda a:bound(a,c,N,m,Lam0,v0),x0,method='SLSQP',
          constraints=[{'type':'ineq','fun':lambda a:a[0]},{'type':'ineq','fun':lambda a:a[1]+a[0]*c*c}],options={'ftol':1e-13,'maxiter':400})
        if r.fun<bst[0]: bst=(r.fun,r.x)
    return bst
for (N,m,Lam0,v0) in [(20000,5,9,0.025),(20000,10,9,0.025),(2000,10,6,0.1),(2000,20,6,0.1)]:
    print("plateau (c=60) N,m,Lam0,v0=",(N,m,Lam0,v0),":",opt(60.0,N,m,Lam0,v0)[0])
for (N,m,Lam0,v0,cr) in [(20000,5,9,0.005,3.029),(2000,20,6,0.05,3.222),(20000,5,3,0.025,2.57)]:
    b=opt(cr,N,m,Lam0,v0)[0]
    lo,hi=1.0,60.0
    for _ in range(30):
        mid=(lo+hi)/2
        if opt(mid,N,m,Lam0,v0)[0]<=0.1: hi=mid
        else: lo=mid
    print((N,m,Lam0,v0),"bound at reported c",cr,"=",b,"; my min c:",round(hi,4))
