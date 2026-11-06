
import numpy as np, math
from fractions import Fraction
from scipy.optimize import minimize
import sys; sys.path.insert(0,'crit')
from core import *
from moments import moment_poly
from functools import lru_cache

@lru_cache(None)
def coeffs(G,n):
    """E[A^a Q^b] for p2=1 as (const, coef_p4): value = const + coef_p4 * p4  (p3-free for degree 4)."""
    out={}
    for ab in [(2,0),(0,1),(4,0),(2,1),(0,2)]:
        pol=moment_poly(*ab,G,n)
        c0=Fraction(0); c4=Fraction(0)
        for key,cf in pol.items():
            if key==(2,): c0+=cf
            elif key==(2,2): c0+=cf
            elif key==(4,): c4+=cf
            else: raise ValueError(key)
        out[ab]=(c0,c4)
    return out

def EL2(a1,a2,G,n,s):
    C=coeffs(G,n); f=lambda ab: float(C[ab][0])+float(C[ab][1])*s
    return 1+2*a1*f((2,0))+2*a2*f((0,1))+a1*a1*f((4,0))+2*a1*a2*f((2,1))+a2*a2*f((0,2))

def quad_bound(G,n,rho,k0,return_a=False):
    """min over (a1,a2) feasible of max_{s in [1/G,k0]} E L^2."""
    best=None
    # parametrize: a1 = lam >=0 ; a2 = -lam*n*rho*theta, theta in [~1/rho.. ] constraints a1+a2/n>=0, a1+a2/(rho n)>=0
    # => -a1*n <= a2 <= -a1*rho*n  *or* a2 >= -a1*n*rho (second) ; first: a2>=-a1*n. So a2>=-a1*rho*n (stronger since rho<1).
    # (a2 >= -a1 n rho  and a2 >= -a1 n).  upper unbounded.
    from scipy.optimize import minimize
    def obj(p):
        lam,th=p   # a1=lam, a2=-lam*n*rho*th, th<=1
        a1=lam; a2=-lam*n*rho*th
        return max(EL2(a1,a2,G,n,1.0/G),EL2(a1,a2,G,n,k0))
    bestv=2;bp=None
    for lam0 in [0.01,0.1,1,10]:
        for th0 in [1.0,0.9,0.5,0.0,-0.5]:
            r=minimize(obj,[lam0,th0],bounds=[(0,None),(None,1.0)],method='L-BFGS-B')
            r2=minimize(obj,r.x,bounds=[(0,None),(None,1.0)],method='Nelder-Mead')
            for rr in (r,r2):
                if rr.fun<bestv: bestv=rr.fun;bp=rr.x
    return (bestv,bp) if return_a else bestv

if __name__=="__main__":
    for G,n in [(24,8)]:
        k0=.5*frontier(G,n,.1)
        for c in [1.645,2,2.5,3,3.5,4,5,6,8]:
            print(c,quad_bound(G,n,rho_of_c(c,G,n),k0))
