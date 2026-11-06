from fractions import Fraction as F
from math import comb, sqrt
import numpy as np
from scipy.optimize import minimize
ALPHA=F(1,10)
def frontier(G,n,alpha=ALPHA):
    for k in range(1,G//2+1):
        if F(comb(G-k,n)+comb(k,n),comb(G,n))<=alpha: ks=k;break
    else: raise
    return ks, F(G-(ks-1),G*(ks-1)) if False else (1-F(ks-1,G))/(ks-1)
# moments (own derivation, p1=0,p2=1) -- exact Fractions
def moms(G,n,p4):
    G=F(G);n=F(n);p4=F(p4)
    EA2=n*(G-n)/(G*(G-1)); EQ=n/G
    EA4=n*(G-n)*(G*G*p4-6*G*n*p4+3*G*n+G*p4-3*G+6*n*n*p4-3*n*n+3)/(G*(G-3)*(G-2)*(G-1))
    EA2Q=n*(n-G)*(-G*p4+2*n*p4-n+1)/(G*(G-2)*(G-1))
    EQ2=-n*(-G*p4+n*p4-n+1)/(G*(G-1))
    return EA2,EQ,EA4,EA2Q,EQ2
def EL2(G,n,p4,a1,a2):
    m=moms(G,n,p4); return 1+2*a1*m[0]+2*a2*m[1]+a1*a1*m[2]+2*a1*a2*m[3]+a2*a2*m[4]
def rho_of(G,n,c):
    g=c*c*(1-F(n,G))/(n-1); return g/(1+g)
def feasible(G,n,c,a1,a2):
    r=rho_of(G,n,c); return a1>=0 and a1+a2/n>=0 and a1+a2/(r*n)>=0
def bound_float(G,n,kap0,c):
    r=float(rho_of(G,n,F(c).limit_denominator(10**6)))
    mf=lambda p4: [float(v) for v in moms(G,n,p4)]
    M0=mf(F(1,G)); M1=mf(kap0)
    def el(M,a):
        return 1+2*a[0]*M[0]+2*a[1]*M[1]+a[0]**2*M[2]+2*a[0]*a[1]*M[3]+a[1]**2*M[4]
    best=(9,None)
    for x0 in [(0.5,-1.0),(1,-3),(2,-10),(0.1,-0.3),(5,-30)]:
        z0=list(x0)+[1.0]
        cons=[{'type':'ineq','fun':lambda z:z[0]},
              {'type':'ineq','fun':lambda z:z[0]+z[1]/n},
              {'type':'ineq','fun':lambda z:z[0]+z[1]/(r*n)},
              {'type':'ineq','fun':lambda z:z[2]-el(M0,z[:2])},
              {'type':'ineq','fun':lambda z:z[2]-el(M1,z[:2])}]
        res=minimize(lambda z:z[2],z0,constraints=cons,method='SLSQP',options={'maxiter':500,'ftol':1e-14})
        if res.success and res.fun<best[0]: best=(res.fun,res.x[:2])
    return best
def exact_cert(G,n,kap0,c,a1,a2):
    """exact Fraction check of validity + bound; returns max over p4 endpoints"""
    ok=feasible(G,n,c,a1,a2)
    return ok, max(EL2(G,n,F(1,G),a1,a2),EL2(G,n,kap0,a1,a2))
