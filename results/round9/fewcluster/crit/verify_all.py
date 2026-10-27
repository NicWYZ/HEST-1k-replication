
"""verify_all.py -- brute-force verification of every claimed identity/bound at small sizes. Run: python crit/verify_all.py"""
import sys, itertools, math, numpy as np
sys.path.insert(0,'crit')
from core import *
import moments, majorant, block, strat
from moments import moment_poly, eval_poly
rng=np.random.default_rng(0)
out={}
# 1. reduction: interval miss <=> (sum x)^2 > rho n sum x^2
for G,n in [(10,3),(12,4),(14,5)]:
    for _ in range(5):
        e=rng.standard_t(2,size=G)
        for c in [1.0,2.0,3.5,8]:
            assert direct_miss(e,n,c).sum()==(t_full(e,n)>rho_of_c(c,G,n)).sum()
out['reduction']='ok'
# 2. moment expander vs enumeration
for G,n in [(7,3),(8,4),(9,3)]:
    x=rng.standard_t(3,size=G); x-=x.mean(); S=np.array(list(itertools.combinations(range(G),n)))
    A=x[S].sum(1); Q=(x[S]**2).sum(1)
    for a,b in [(2,0),(0,1),(4,0),(2,1),(0,2),(6,0),(4,1),(2,2),(0,3),(3,0),(1,1)]:
        assert abs((A**a*Q**b).mean()-eval_poly(moment_poly(a,b,G,n),x))<1e-8
out['moments']='ok'
# 3. Lemma 1
v=0
for _ in range(3000):
    G=rng.integers(5,16); x=rng.standard_t(rng.choice([1,2,3,10]),size=G)*rng.choice([1,.2]); x-=x.mean(); k=kappa_of(x)
    pos=np.sort(x[x>0])
    for i in range(len(pos)):
        for j in range(i,len(pos)):
            m=j-i+1;R=pos[j]/pos[i];kk=G-m
            if kk>=1 and k<m/(kk*(m+R*R*kk))-1e-12: v+=1
assert v==0; out['lemma1']='ok'
# 4. counting (block) bound
bad=0;tests=0
for _ in range(400):
    G,n=10,3; kind=rng.integers(3)
    if kind==0: x=rng.standard_t(2,size=G)
    elif kind==1:
        k=rng.integers(2,6); x=np.where(np.arange(G)<k,1.0,0.0)+rng.normal(0,rng.choice([0,.01,.1]),size=G)
    else: x=np.round(rng.normal(size=G)*2)/2+rng.normal(0,.02,size=G)
    x=x-x.mean()
    if np.ptp(x)<1e-9: continue
    k0=kappa_of(x)*(1+1e-9); t=t_full(x,n)
    for c in [3,4,6,10,20]:
        nm=(t>rho_of_c(c,G,n)).sum()
        for s in (1,2):
            bb=block.block_bound(G,n,c,k0,s)
            tests+=1
            if bb is not None and nm>bb[0]*math.comb(G,n)+1e-9: bad+=1
assert bad==0; out['block_counting']=f'ok ({tests} tests)'
# 5. quadratic majorant: E L^2 formula and bound validity
G,n=12,4
for _ in range(4):
    e=rng.standard_t(3,size=G); x=e-e.mean(); x/=np.sqrt((x**2).sum())
    S=all_samples(G,n); xs=x[S]; A=xs.sum(1); Q=(xs**2).sum(1); s4=(x**4).sum()
    for a1,a2 in [(0.7,-1.5),(2.0,-3.0)]:
        assert abs(((1+a1*A*A+a2*Q)**2).mean()-majorant.EL2(a1,a2,G,n,s4))<1e-9
viol=0;tot=0
for _ in range(100):
    e=rng.standard_t(rng.choice([2,3,5,30]),size=G); x=e-e.mean(); k=kappa_of(x)
    for c in [1.5,2.5,4]:
        rho=rho_of_c(c,G,n); mp=(t_full(e,n)>rho).mean(); b=majorant.quad_bound(G,n,rho,k*(1+1e-7))
        tot+=1; viol+= mp>b+1e-9
assert viol==0; out['quad_bound']=f'ok ({tot} tests)'
print(out)

# 6. stratified: E L^2 formula (exact) and bound validity vs exact enumeration
from scipy.optimize import minimize
def strat_enum(pops,m,W):
    parts=[]
    for e,w in zip(pops,W):
        N=len(e); S=np.array(list(itertools.combinations(range(N),m))); es=e[S]
        parts.append((w*(es.mean(1)-e.mean()), w**2*(1-m/N)*es.var(1,ddof=1)/m))
    Dg=np.array(list(itertools.product(*[range(len(p[0])) for p in parts])))
    D=sum(parts[h][0][Dg[:,h]] for h in range(len(parts))); V=sum(parts[h][1][Dg[:,h]] for h in range(len(parts)))
    return D*D,V,parts
H,N,m=3,7,3
(r4a,r4b),(rda,rdb),(rva,rvb)=strat.stratum_ratios(N,m)
viol=0;tot=0
for _ in range(40):
    pops=[rng.standard_t(rng.choice([1.5,3,20]),size=N) for _ in range(H)]; W=list(rng.uniform(.3,2,size=H))
    u,q,parts=strat_enum(pops,m,W); Vh=np.array([pt[1].mean() for pt in parts]); V=Vh.sum()
    s=[((e-e.mean())**4).sum()/((e-e.mean())**2).sum()**2 for e in pops]
    a1,a2=0.3,-0.5
    form=1+2*(a1+a2)*V+a1*a1*(sum(Vh[h]**2*(r4a+r4b*s[h]) for h in range(H))+3*(V**2-(Vh**2).sum()))\
        +2*a1*a2*(sum(Vh[h]**2*(rda+rdb*s[h]) for h in range(H))+(V**2-(Vh**2).sum()))\
        +a2*a2*(sum(Vh[h]**2*(rva+rvb*s[h]) for h in range(H))+(V**2-(Vh**2).sum()))
    assert abs(((1+a1*u+a2*q)**2).mean()-form)<1e-8*max(1,form)
    v0=(Vh/V).max()
    for c in [1.5,2.5,4]:
        b,_=strat.strat_bound(c,(N,m,max(s),1/N),v0); miss=((u>c*c*q)&(u>0)).mean()
        tot+=1; viol+= miss>b+1e-9
assert viol==0; print('strat ok',tot)
