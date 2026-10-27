
"""moments.py: exact E[A^a Q^b] for SRSWOR, A=sum_S x, Q=sum_S x^2, as polynomial in power sums p_j=sum_g x_g^j of a
population with p_1=0.  Polynomial = dict {tuple(sorted powers): Fraction}."""
from fractions import Fraction
from functools import lru_cache
from math import factorial
import itertools

def set_partitions(lst):
    if not lst:
        yield []
        return
    first=lst[0]
    for part in set_partitions(lst[1:]):
        # put first in its own block or into an existing block
        yield [[first]]+part
        for i in range(len(part)):
            yield part[:i]+[[first]+part[i]]+part[i+1:]

def ff(x,r):
    out=1
    for i in range(r): out*=(x-i)
    return out

@lru_cache(None)
def distinct_sum_poly(exps):
    """sum over distinct index tuples of prod x_{g_i}^{exps_i} as polynomial in p (p1=0 -> terms with p_1 dropped)."""
    res={}
    idx=list(range(len(exps)))
    for sp in set_partitions(idx):
        coef=1
        for P in sp: coef*=(-1)**(len(P)-1)*factorial(len(P)-1)
        powers=tuple(sorted(sum(exps[i] for i in P) for P in sp))
        if 1 in powers: continue
        res[powers]=res.get(powers,0)+coef
    return res

def moment_poly(a,b,G,n):
    slots=[1]*a+[2]*b
    res={}
    for sp in set_partitions(list(range(len(slots)))):
        r=len(sp)
        pr=Fraction(ff(n,r),ff(G,r))
        if pr==0: continue
        E=tuple(sorted(sum(slots[i] for i in B) for B in sp))
        for key,cf in distinct_sum_poly(E).items():
            res[key]=res.get(key,0)+pr*cf
    return {k:v for k,v in res.items() if v!=0}

def eval_poly(poly,x):
    import numpy as np
    x=np.asarray(x,float); ps={}
    tot=0.0
    for key,cf in poly.items():
        t=float(cf)
        for j in key:
            if j not in ps: ps[j]=(x**j).sum()
            t*=ps[j]
        tot+=t
    return tot
