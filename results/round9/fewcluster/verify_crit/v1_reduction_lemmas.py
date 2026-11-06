# Checks (1) reduction, (2) Lemma 1 and Lemma 2 -- independent code
import itertools, math, random
import numpy as np
random.seed(1); np.random.seed(1)

def raw_miss(x, S, G, c):
    """direct interval test: x centred pop (mean 0 so target is 0). interval xbar +- c sqrt((1-f) s^2/n)"""
    n=len(S); xs=[x[i] for i in S]; xb=sum(xs)/n
    s2=sum((v-xb)**2 for v in xs)/(n-1); f=n/G
    hw=c*math.sqrt((1-f)*s2/n)
    return abs(xb-0.0)>hw+1e-13      # miss = target outside closed interval
def t_miss(x,S,G,c):
    n=len(S); A=sum(x[i] for i in S); Q=sum(x[i]**2 for i in S)
    g=c*c*(1-n/G)/(n-1); rho=g/(1+g)
    t=0.0 if Q==0 else A*A/(n*Q)
    return t>rho+1e-13
bad=0; tot=0; near=0
for (G,n) in [(10,3),(12,4),(14,5)]:
    for rep in range(6):
        e=np.random.standard_cauchy(G) if rep%2 else np.random.lognormal(0,1.5,G)
        if rep==4: e=np.round(e)  # ties / constant samples
        x=list(e-e.mean())
        for c in [1,2,3.5,8]:
            for S in itertools.combinations(range(G),n):
                tot+=1
                if raw_miss(x,S,G,c)!=t_miss(x,S,G,c): bad+=1
print("reduction: samples",tot,"discrepancies",bad)
# constant-sample edge case
x=[3,3,3,-1,-1,-1,-1,-1,-1,-1,-1,-1]; m=np.mean(x); x=[v-m for v in x]
print("const-sample edge: raw",raw_miss(x,(0,1,2),12,2.0),"t-form",t_miss(x,(0,1,2),12,2.0))

# Lemma 1: min kappa given m same sign values in [a,Ra], k=G-m others; random + adversarial
def L1(G,m,R): k=G-m; return m/(k*(m+R*R*k))
viol=0; cnt=0; minratio=9
for _ in range(20000):
    G=random.randint(4,30); m=random.randint(1,G-1); k=G-m; R=1+random.random()*random.choice([0.01,0.3,3,10])
    a=random.random()*3+0.01
    pos=np.sort(a*np.random.uniform(1,R,m)) if random.random()<.7 else a*np.array([1]*(m//2)+[R]*(m-m//2))
    # others: sum -sum(pos); random split (any signs) with sum fixed
    tgt=-pos.sum(); w=np.random.randn(k)*random.choice([0.01,1,10]); oth=w-w.mean()+tgt/k
    x=np.concatenate([pos,oth]); kap=(x**2).max()/(x**2).sum(); cnt+=1
    if kap<L1(G,m,pos.max()/pos.min())-1e-12: viol+=1
    minratio=min(minratio,kap/L1(G,m,pos.max()/pos.min()))
print("Lemma1: trials",cnt,"violations",viol,"min kappa/bound",minratio)
# tightness R=1: m equal a, others equal -ma/k
G,m=24,18;k=G-m;x=np.array([k]*m+[-m]*k,float);x=x-x.mean();print("L1 tight R=1:",(x**2).max()/(x**2).sum(),L1(G,m,1))

# Lemma 2: every missed sample is one-signed with max/min ratio < r
for (G,n) in [(10,3),(12,4),(14,5)]:
    bad=0;nm=0
    for rep in range(5):
        e=np.random.standard_cauchy(G); x=list(e-e.mean())
        for c in [2.0,4.0,6.0,10.0,30.0]:
            f=n/G; delta=(n-1)/(c*math.sqrt(1-f))
            if delta>=1: continue
            r=(1+delta)/(1-delta)
            for S in itertools.combinations(range(G),n):
                if t_miss(x,S,G,c):
                    nm+=1; v=[x[i] for i in S]
                    if not (all(a>0 for a in v) or all(a<0 for a in v)) or max(map(abs,v))/min(map(abs,v))>=r: bad+=1
    print("Lemma2",(G,n),"missed samples tested",nm,"violations",bad)
# tightness of Lemma 2: one outlier sample
n=5;G=14;c=10.0;f=n/G;delta=(n-1)/(c*math.sqrt(1-f));print("delta",delta)
