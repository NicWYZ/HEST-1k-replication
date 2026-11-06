import sys; sys.path.insert(0,'.')
import numpy as np, itertools, csv
from scipy.optimize import minimize
from frontier_common import *
rng=np.random.default_rng(1)
rows=[]

# ---------- Lemma 1: numerical minimisation of kappa over e constant (=0) on B, free on A (|A|=k)
def min_kappa_free(G,k,restarts=40):
    best=(9,None)
    for _ in range(restarts):
        x0=np.concatenate([rng.normal(size=k),[0.5]])
        def cons_ineq(v):
            x,t=v[:k],v[k]
            e=np.concatenate([x,np.zeros(G-k)]); d=e-e.mean()
            return t-d**2          # d_g^2 <= t   (with SS=1)
        def cons_eq(v):
            x=v[:k]; e=np.concatenate([x,np.zeros(G-k)]); d=e-e.mean()
            return (d**2).sum()-1
        r=minimize(lambda v:v[k],x0,constraints=[{'type':'ineq','fun':cons_ineq},{'type':'eq','fun':cons_eq}],method='SLSQP',options={'maxiter':500,'ftol':1e-14})
        if r.success:
            e=np.concatenate([r.x[:k],np.zeros(G-k)])
            kv=kappa(e)
            if kv<best[0]: best=(kv,e)
    return best
for G in (8,10,12):
    for k in range(1,G):
        kv,e=min_kappa_free(G,k)
        bound=kappa2(G,k)
        # two-point value (all x equal)
        e2=np.concatenate([np.ones(k),np.zeros(G-k)])
        rows.append(dict(check='Lemma1',G=G,n='',k=k,quantity='min kappa over e const on G-k clusters',value=kv,reference=bound,
            note=f'k<=G/2={k<=G/2}; two-point kappa={kappa(e2):.6f}; min>=bound:{kv>=bound-1e-8}; min==bound:{abs(kv-bound)<1e-6}'))
# random sampling check of the inequality
viol=0
for _ in range(200000):
    G=int(rng.integers(4,14)); k=int(rng.integers(1,G)); 
    e=np.zeros(G); e[:k]=rng.normal(size=k)*rng.choice([1e-3,1,10])
    if rng.random()<.3: e[:k]=rng.integers(-2,3,size=k)
    kv=kappa(e)
    if np.isnan(kv): continue
    if kv<kappa2(G,k)-1e-12: viol+=1
rows.append(dict(check='Lemma1',G='4-13',n='',k='1..G-1',quantity='random violations of kappa>=kappa2(k) in 200000 draws',value=viol,reference=0,note=''))

# ---------- Lemma 0
# procedure: C(D)=R if S in S0 else fpc-t interval (c=2) around est ; coverage >= P(S0) for every population.
G,n=8,3
S=samples(G,n); N=len(S)
res=[]
for trial in range(300):
    S0=rng.random(N)<rng.uniform(.5,.95)
    one_minus_alpha=S0.mean(); alpha=1-one_minus_alpha
    z=rng.normal(size=G)*rng.choice([1,10]); M=rng.choice([-1e4,-50,-1,0.3,7,1e5])
    def covered_point(z,point_shift):
        # does theta(z)+shift in C(D)?  C=R on S0, t-interval(c=2) elsewhere
        eS=z[S]; mean=eS.mean(1); se=np.sqrt((1-n/G)*eS.var(1,ddof=1)/n)
        theta=z.mean()+point_shift
        return S0 | (np.abs(mean-theta)<=2*se)
    cov0=covered_point(z,0).mean()
    A=covered_point(z,M/G)
    uncond=A.mean()
    bound=(one_minus_alpha-n/G)/(1-n/G)
    # key identity: sum_j P(j notin S, A)=(G-n)P(A)
    notin=np.stack([~(S==j).any(1) for j in range(G)])   # (G,N)
    lhs=sum((notin[j]&A).mean() for j in range(G)); rhs=(G-n)*uncond
    # per-j: P(j notin S, theta+M/G in C(D)) at z equals P(j notin S, theta' in C) at z'=z+M e_j
    perj=[]
    for j in range(G):
        zp=z.copy(); zp[j]+=M
        Ap=covered_point(zp,0)
        perj.append(np.isclose((notin[j]&Ap).mean(),(notin[j]&A).mean()))
    res.append((uncond>=bound-1e-12, abs(lhs-rhs)<1e-12, all(perj), uncond-bound, cov0>=one_minus_alpha-1e-12))
res=np.array(res)
rows.append(dict(check='Lemma0',G=8,n=3,k='',quantity='trials with unconditional P>=bound / identity holds / per-j transfer holds (of 300)',value=f'{res[:,0].sum()}/{res[:,1].sum()}/{res[:,2].sum()}',reference=300,note=f'min slack uncond-bound={res[:,3].min():.4f}; procedure covers>=1-alpha at all tested z: {res[:,4].all()}'))
# hand-built small example where conditional-on-j and unconditional differ: conditional prob P(A | j notin S) is NOT what is bounded; show both
ex=[]
for trial in range(300):
    S0=rng.random(N)<.85; one_minus_alpha=S0.mean()
    z=rng.normal(size=G); M=5.0
    eS=z[S]; mean=eS.mean(1); se=np.sqrt((1-n/G)*eS.var(1,ddof=1)/n)
    A=S0|(np.abs(mean-(z.mean()+M/G))<=2*se)
    notin=np.stack([~(S==j).any(1) for j in range(G)])
    cond=np.array([A[notin[j]].mean() for j in range(G)])
    ex.append((A.mean(),cond.mean(),cond.min()))
ex=np.array(ex)
rows.append(dict(check='Lemma0',G=8,n=3,k='',quantity='average over j of P(A|j notin S) equals P(A) (SRSWOR symmetry): max abs diff',value=float(np.abs(ex[:,0]-ex[:,1]).max()),reference=0,note='unconditional P(A)=avg_j P(A | j not in S) since exactly G-n clusters are unsampled in every sample'))

# ---------- Corollary 4: random designs
maxerr=0; minmax=9; cnt=0
for trial in range(200):
    G=int(rng.integers(6,13)); n=int(rng.integers(2,min(5,G-1))); k=int(rng.integers(1,G//2+1))
    S=samples(G,n); N=len(S)
    kind=rng.integers(3)
    if kind==0: p=rng.dirichlet(np.ones(N)*0.2)
    elif kind==1: p=np.zeros(N); p[rng.integers(N)]=1
    else: p=rng.dirichlet(np.ones(N))
    tot=0; best=0; nB=0
    for B2 in itertools.combinations(range(G),k):
        m=np.zeros(G,bool); m[list(B2)]=True
        inB2=m[S].all(1); inB1=(~m[S]).all(1)
        val=p[inB1|inB2].sum(); tot+=val; nB+=1; best=max(best,val)
    avg=tot/nB; pk=pi_k(G,n,k)
    maxerr=max(maxerr,abs(avg-pk)); minmax=min(minmax,best-pk); cnt+=1
rows.append(dict(check='Cor4',G='6-12',n='2-4',k='1..G/2',quantity='max |avg_B P_p(S in B1 or B2) - pi(k)| over 200 random designs',value=maxerr,reference=0,note=f'min over designs of (max_B P_p - pi(k))={minmax:.3e} (>=0 required)'))
# variable-size design caveat
G,n,k=10,4,3
rows.append(dict(check='Cor4',G=10,n='4 and 2',k=3,quantity='pi_n(k) for n=4 vs n=2 (design mixing sizes breaks the fixed-size average)',value=f'{pi_k(G,4,k):.4f} vs {pi_k(G,2,k):.4f}',reference='',note='pi_n(k) decreasing in n: a design that sometimes takes larger samples can fall below pi(k) for the nominal n'))

# ---------- (E) for OLS-tuned lambda (with / without intercept)
def interval(zS,fS,Fbar,G,n,c,intercept=True):
    if intercept:
        X=np.c_[np.ones(n),fS]; lam=np.linalg.lstsq(X,zS,rcond=None)[0][1]
    else:
        lam=(fS@zS)/(fS@fS)
    r=zS-lam*fS; est=lam*Fbar+r.mean(); se=np.sqrt((1-n/G)*r.var(ddof=1)/n)
    return est-c*se, est+c*se
errs={True:0,False:0}
for _ in range(2000):
    G,n=12,5; f=rng.normal(size=G)+1; lam=rng.normal(); z=rng.normal(size=G)*3+f*rng.normal()
    S=rng.choice(G,n,replace=False); a=rng.normal()*5; b=rng.uniform(.1,5)
    z2=lam*f+a+b*(z-lam*f)
    for ic in (True,False):
        lo,hi=interval(z[S],f[S],f.mean(),G,n,2.3,ic); lo2,hi2=interval(z2[S],f[S],f.mean(),G,n,2.3,ic)
        exp_lo=lam*f.mean()+a+b*(lo-lam*f.mean()); exp_hi=lam*f.mean()+a+b*(hi-lam*f.mean())
        errs[ic]=max(errs[ic],abs(lo2-exp_lo),abs(hi2-exp_hi))
rows.append(dict(check='Equivariance(E)',G=12,n=5,k='',quantity='max |C(z\')-transform(C(z))| for OLS-tuned PPI interval WITH intercept',value=errs[True],reference=0,note='satisfies (E)'))
rows.append(dict(check='Equivariance(E)',G=12,n=5,k='',quantity='same, OLS WITHOUT intercept (slope = sum fz/sum f^2)',value=errs[False],reference=0,note='violates (E) in the shift a'))
import pandas as pd
pd.DataFrame(rows).to_csv('checks_lemmas.csv',index=False)
pd.set_option('display.width',250,'display.max_colwidth',120)
print(pd.DataFrame(rows).drop(columns=['note']).to_string())
print(pd.DataFrame(rows)[pd.DataFrame(rows).check=='Lemma1'].note.head(30).tolist())
