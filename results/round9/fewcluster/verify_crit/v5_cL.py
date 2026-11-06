import numpy as np, itertools, math
from math import comb
ALPHA=0.1
def all_cS(x,n):
    """c_S = |xbar| / sqrt((1-f) s^2/n) for every n-subset (raw interval, independent of t-reduction)"""
    G=len(x); x=np.asarray(x,float); x=x-x.mean()
    combos=np.array(list(itertools.combinations(range(G),n)),dtype=np.int16)
    v=x[combos]; xb=v.mean(1); s2=v.var(1,ddof=1); f=n/G
    se=np.sqrt((1-f)*s2/n)
    with np.errstate(divide='ignore',invalid='ignore'):
        cS=np.where(se>1e-14*np.maximum(1,np.abs(xb)), np.abs(xb)/se, np.where(np.abs(xb)>1e-12,np.inf,0.0))
    return cS,x
def c_pop(cS,alpha=ALPHA):
    # miss iff c < c_S ; coverage(c)=P(c_S<=c); smallest c with miss prob <= alpha
    s=np.sort(cS)[::-1]; N=len(s); kmax=int(math.floor(alpha*N+1e-12))  # at most kmax samples may be missed
    return s[kmax]  # c must be >= (kmax+1)-th largest c_S
def raw_cov(cS,c): return np.mean(cS<=c)
def report(name,vals,mult,G,n,reported):
    x=np.repeat(vals,mult).astype(float)
    cS,xc=all_cS(x,n); cp=c_pop(cS)
    sd=xc.std(ddof=1); kap=(xc**2).max()/(xc**2).sum()
    print(f"{name}: G={G} n={n} kappa={kap:.6f} (max|x|/SD={np.abs(xc).max()/sd:.4f}) c_pop={cp:.5f} reported={reported}")
    print("    coverage at c_pop:",raw_cov(cS,cp+1e-9)," coverage just below:",raw_cov(cS,cp-1e-6)," (need >=0.9 / <0.9)")
    return cp,kap
# two-point (24,8): exact shape from counts 9,15: values -5,3 (sum zero)
report("2pt exact (-5,3)x(9,15)",[-5,3],[9,15],24,8,2.449)
report("2pt rounded [-1.264,0.758]",[-1.264,0.758],[9,15],24,8,2.449)
print("   sqrt6 =",math.sqrt(6))
# 3-valued at 0.4 frontier, (24,8): kappa0=19/300
cp,k=report("3val rounded [-1.024,1.207,-0.274]x[9,9,6]",[-1.024,1.207,-0.274],[9,9,6],24,8,2.086)
print("   kappa0 = 19/300 =",19/300)
# sensitivity: perturb within rounding box
rng=np.random.default_rng(0); outs=[]
for _ in range(30):
    v=np.array([-1.024,1.207,-0.274])+rng.uniform(-5e-4,5e-4,3)
    cS,xc=all_cS(np.repeat(v,[9,9,6]),8); outs.append(c_pop(cS))
print("   c_pop under +-0.0005 value jitter: min %.5f max %.5f"%(min(outs),max(outs)))
# a solved version: keep shape ratio but enforce kappa=kappa0 exactly by choosing middle value then centring
from scipy.optimize import brentq
def shape(d):  # values (-1.024,1.207,d) with counts 9,9,6 -> need sum 0: d=-(9*(-1.024)+9*1.207)/6
    pass
# also (24,12) 0.25: [0.806,1.198,-0.893] x [4,7,13], reported 1.914
report("3val (24,12)",[0.806,1.198,-0.893],[4,7,13],24,12,1.914)
# 2pt (24,12) 0.5 : [-0.692,1.384]x[16,8] reported 2.098
report("2pt (24,12)",[-0.692,1.384],[16,8],24,12,2.098)
