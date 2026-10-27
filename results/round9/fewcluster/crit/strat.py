
import numpy as np, sys
from fractions import Fraction
sys.path.insert(0,'crit')
from moments import moment_poly
from functools import lru_cache
from scipy.optimize import minimize, minimize_scalar

@lru_cache(None)
def stratum_ratios(N,m):
    """Return functions of s=p4/p2^2 for ratios (units of V_h^2 where V_h=E Vhat_h):
    r4(s)=E D^4/V^2, rDV(s)=E[D^2 Vhat]/V^2, rVV(s)=E Vhat^2/V^2. All linear in s.  W-free: D=(W/m)A, Vhat=W^2(1-f)/m * s2,
    s2=(Q-A^2/m)/(m-1)."""
    P={ab:moment_poly(*ab,N,m) for ab in [(2,0),(4,0),(2,1),(0,1),(0,2)]}
    def lin(pol):
        c0=Fraction(0);c4=Fraction(0)
        for key,cf in pol.items():
            if key in [(2,),(2,2)]: c0+=cf
            elif key==(4,): c4+=cf
            else: raise ValueError(key)
        return c0,c4
    f=m/N
    # per unit p2=1:  A2=E A^2 ; A4; A2Q; Q; Q2
    A2=lin(P[(2,0)]);A4=lin(P[(4,0)]);A2Q=lin(P[(2,1)]);Q1=lin(P[(0,1)]);Q2=lin(P[(0,2)])
    def comb(*terms):
        c0=sum(t[0]*t[1] for t in terms) ; c4=sum(t[0]*t[2] for t in terms); return c0,c4
    # D = k_D * A ; Vhat = k_V*(Q - A^2/m)/(m-1);  k_D=W/m, k_V=W^2(1-f)/m.  Set W=1.
    kD=Fraction(1,m); kV=Fraction(1-f)/m if False else (1-Fraction(m,N))/m
    # V = E Vhat = kV*(E Q - E A^2/m)/(m-1)
    V0=kV*(Q1[0]-A2[0]/m)/(m-1)      # p4 coefficient zero in both
    assert Q1[1]==0 and A2[1]==0
    # E D^4 = kD^4 E A^4
    ED4=(kD**4*A4[0],kD**4*A4[1])
    # E D^2 Vhat = kD^2 kV/(m-1) * (E A^2 Q - E A^4/m)
    EDV=(kD**2*kV/(m-1)*(A2Q[0]-A4[0]/m), kD**2*kV/(m-1)*(A2Q[1]-A4[1]/m))
    # E Vhat^2 = (kV/(m-1))^2 * (E Q^2 - 2/m E A^2 Q + 1/m^2 E A^4)
    EVV=((kV/(m-1))**2*(Q2[0]-2*A2Q[0]/m+A4[0]/m**2),(kV/(m-1))**2*(Q2[1]-2*A2Q[1]/m+A4[1]/m**2))
    # check E D^2 = V
    assert kD**2*A2[0]==V0
    r=lambda t:(float(t[0]/V0**2),float(t[1]/V0**2))
    return r(ED4),r(EDV),r(EVV)

def strat_EL2(a1,a2,H_terms):
    pass

def strat_bound(c,strata,v0,Lam0=None):
    """strata: (N,m,s_max,s_min) assumed identical for all strata. Returns certified bound on sup P(miss) via
    min_{a1>=0,a2>=-a1 c^2} E L^2, worst case over shares (sum v_h^2 <= v0) and kurtosis s_h in [s_min,s_max]."""
    N,m,smax,smin=strata
    (r4a,r4b),(rda,rdb),(rva,rvb)=stratum_ratios(N,m)
    def coefK(a1,a2,s):
        return a1*a1*((r4a+r4b*s)-3)+2*a1*a2*((rda+rdb*s)-1)+a2*a2*((rva+rvb*s)-1)
    def obj(p):
        a1,a2=p
        base=1+2*(a1+a2)+3*a1*a1+2*a1*a2+a2*a2
        Kmax=max(coefK(a1,a2,smin),coefK(a1,a2,smax))
        return base+v0*max(Kmax,0)   # Sum v^2 in [?,v0]; if Kmax<=0 worst case is sum v^2->0 (many tiny strata)
    best=9;bp=None
    for l0 in [0.01,0.1,1]:
        for th in [0,0.5,1,2]:
            cons=[{'type':'ineq','fun':lambda p: p[0]},{'type':'ineq','fun':lambda p: p[1]+p[0]*c*c}]
            r=minimize(obj,[l0,-l0*c*c*th/2],constraints=cons,method='SLSQP',options=dict(maxiter=300,ftol=1e-12))
            if r.fun<best and r.x[0]>=-1e-9 and r.x[1]+r.x[0]*c*c>=-1e-9: best=r.fun;bp=r.x
    return best,bp
