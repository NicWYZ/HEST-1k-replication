import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from frontier_common import *
p="/Users/nicolaszhang/.claude-science/orgs/c42040b3-6d87-451b-9b93-c94218d0c812/artifacts/proj_cdb12919c7d7/ec42003d-cf85-42f6-8065-112864d130ca/vbf739906_s3_frontier_exact.csv"
tab=pd.read_csv(p); tab=tab[np.isclose(tab.alpha,0.10)].reset_index(drop=True)
def R_bound(G,n):
    return max([(G//m*C(m,n)+C(G%m,n))/C(G,n) for m in range(1,G+1) if m<G/2]+[0])
def exact_frontier(G,n,alpha):
    """smallest kappa0 at which beta(kappa0) > alpha, over ALL partitions (DFS over blocks >= n, rest free singletons).
    beta(kappa0)<=alpha  <=>  kappa0 < this value."""
    tot=C(G,n); thr=alpha*tot
    best=[np.inf,None]; seen=0
    def dfs(blocks,rem,maxp,cnt):
        nonlocal seen
        if cnt>thr+1e-9:
            part=tuple(blocks)+(1,)*rem
            if len(part)>=2:
                seen+=1
                k,_=min_kappa_partition(part)
                if k<best[0]: best[0]=k; best[1]=tuple(blocks)
            # adding more blocks only increases count and constraint -> minkappa not smaller necessarily; still continue? supersets of constraints => minkappa can only increase
            return
        for m in range(min(maxp,rem),n-1,-1):
            if cnt+C(rem,n)<=thr+1e-9: return   # even one block of everything remaining cannot exceed
            dfs(blocks+[m],rem-m,m,cnt+C(m,n))
    dfs([],G,G,0)
    return best[0],best[1]
rows=[]
for _,r in tab.iterrows():
    G,n,a=int(r.G),int(r.n),r.alpha
    ks=[k for k in range(1,G//2+1) if pi_k(G,n,k)<=a+1e-15]
    ks_=ks[0] if ks else np.nan
    kst=kappa2(G,int(ks_)) if ks else np.nan
    pik=pi_k(G,n,int(ks_)) if ks else np.nan
    pik1=pi_k(G,n,int(ks_)-1) if ks and ks_>1 else np.nan
    Rb=R_bound(G,n)
    kex,blk=exact_frontier(G,n,a)
    ksup=kappa2(G,int(ks_)-1) if ks and ks_>1 else np.nan
    rows.append(dict(G=G,n=n,alpha=a,k_star_mine=ks_,k_star_table=r.k_star,kappa_star_mine=kst,kappa_star_table=r.kappa_star,
        pi_k_star=pik,pi_k_star_table=r.pi_at_k_star,pi_k_star_m1=pik1,pi_k_star_m1_table=r.pi_at_k_star_minus1,
        rest_bound_mine=Rb,rest_bound_table=r.rest_bound,
        kappa2_kstar_minus1=ksup,exact_frontier_kappa=kex,exact_frontier_blocks=str(blk),
        match_k=(np.isnan(ks_) and np.isnan(r.k_star)) or ks_==r.k_star,
        match_kappa=(np.isnan(kst) and np.isnan(r.kappa_star)) or np.isclose(kst,r.kappa_star,atol=1e-6),
        match_R=np.isclose(Rb,r.rest_bound,atol=1e-6)))
df=pd.DataFrame(rows); df.to_csv('checks_consequence_table.csv',index=False)
pd.set_option('display.width',300,'display.max_columns',30)
print(df[['G','n','k_star_mine','k_star_table','kappa_star_mine','kappa_star_table','rest_bound_mine','rest_bound_table','kappa2_kstar_minus1','exact_frontier_kappa','match_k','match_kappa','match_R']].round(5).to_string())
print(df[['match_k','match_kappa','match_R']].all())
# explicit CONSEQUENCE numbers
print('G=24,n=8: kappa2(6)=',kappa2(24,6),' pi(6)=',pi_k(24,8,6),' pi(5)=',pi_k(24,8,5),' kappa2(5)=',kappa2(24,5),' R=',R_bound(24,8))
print('G=51,n=8: kappa2(12)=',kappa2(51,12),'pi(12)=',pi_k(51,8,12),'pi(11)=',pi_k(51,8,11),'kappa2(11)=',kappa2(51,11),'R=',R_bound(51,8))
print('G=51,n=4: min over k<=25 of pi:',min(pi_k(51,4,k) for k in range(1,26)),' at k=25:',pi_k(51,4,25),' R=',R_bound(51,4), 'kappa2(25)=',kappa2(51,25))
print('pi(k) nonincreasing for k<=G/2 (all G<=60,n<=12)?',all(pi_k(G,n,k)>=pi_k(G,n,k+1)-1e-15 for G in range(4,61) for n in range(2,13) for k in range(1,G//2)))
# asymptotics
alpha=0.1; import math
print('n < 1+log2(1/alpha) =',1+math.log2(1/alpha))
for n in (3,4,5):
    print(n,'2^(1-n)=',2**(1-n),[ (G,round(pi_k(G,n,G//2),5)) for G in (20,50,200,1000,10000)])
