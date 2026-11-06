# Own derivation of exact SRSWOR moments in power sums (Moebius inversion over set partitions)
from fractions import Fraction as F
import itertools, sympy as sp
from sympy.utilities.iterables import multiset_partitions
G,n=sp.symbols('G n')
p=sp.symbols('p1:9')  # p1..p8
def P(e): return p[e-1]
def falling(z,j):
    r=1
    for i in range(j): r*= (z-i)
    return r
def setparts(lst):
    return [ [list(b) for b in part] for part in multiset_partitions(lst)]
def E_product(exps):
    """E[ prod_i ( sum_g I_g x_g^{e_i} ) ] as polynomial in p's, G, n"""
    r=len(exps); tot=0
    for pi in setparts(list(range(r))):         # which factors share the same index
        E=[sum(exps[i] for i in blk) for blk in pi]; b=len(E)
        # sum over DISTINCT indices h_1..h_b of prod x_h^{E_j} = sum over partitions sigma of blocks mu * prod p
        s=0
        for sg in setparts(list(range(b))):
            mu=1
            for C in sg: mu*= (-1)**(len(C)-1)*sp.factorial(len(C)-1)
            term=1
            for C in sg: term*=P(sum(E[j] for j in C))
            s+=mu*term
        tot+= s*falling(n,b)/falling(G,b)
    return sp.simplify(tot)
# A=sum I x (exp 1), Q = sum I x^2 (exp 2)
mom={'EA2':[1,1],'EQ':[2],'EA4':[1,1,1,1],'EA2Q':[1,1,2],'EQ2':[2,2]}
res={k:sp.factor(E_product(v)) for k,v in mom.items()}
sub={p[0]:0,p[1]:1}
P4=sp.Symbol('p4')
red={}
for k,v in res.items():
    r=sp.simplify(sp.expand(v.subs(sub)))
    red[k]=sp.factor(sp.simplify(r.subs(p[3],P4)))  # p4 symbol
    print(k,"=",red[k]," | free symbols:",sorted(map(str,red[k].free_symbols)))
import pickle; pickle.dump({k:str(v) for k,v in red.items()},open('moments_red.pkl','wb'))
# brute force check on exact rational populations
def brute(xs,nn):
    GG=len(xs); out={k:F(0) for k in mom}; cnt=0
    for S in itertools.combinations(range(GG),nn):
        A=sum(xs[i] for i in S);Q=sum(xs[i]**2 for i in S);cnt+=1
        out['EA2']+=A*A;out['EQ']+=Q;out['EA4']+=A**4;out['EA2Q']+=A*A*Q;out['EQ2']+=Q*Q
    return {k:v/cnt for k,v in out.items()}
import random
random.seed(3)
maxerr=0
for (GG,nn) in [(7,3),(8,4),(9,3),(10,5),(9,2),(8,8-1)]:
    xs=[F(random.randint(-9,9)) for _ in range(GG)]
    # arbitrary (NOT centred) population to test the full general formula
    pv={p[i]:sum(v**(i+1) for v in xs) for i in range(8)}
    b=brute(xs,nn)
    for k in mom:
        val=res[k].subs(pv).subs({G:GG,n:nn})
        err=abs(sp.Rational(val)-sp.Rational(b[k].numerator,b[k].denominator)); maxerr=max(maxerr,err)
print("max abs err general formula vs enumeration (exact):",maxerr)
open('moments_general.txt','w').write("\n".join(f"{k} = {v}" for k,v in res.items()))
