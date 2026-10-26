import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from frontier_common import *
df=pd.read_csv('checks_theorem1.csv')
print(df[~df.ok].c.value_counts().to_dict(), df[~df.ok].u.value_counts().to_dict())
# for c=1e5 and each failing config, use eps 1e-12 (u scale up to 1e3)
rng=np.random.default_rng(11)
bad=0;tot=0;rows=[]
for (G,n) in [(8,3),(10,4),(12,4)]:
    idx=samples(G,n)
    for k in range(1,G//2+1):
        for ut in ['gauss','heavy','gauss_big','const']:
            u={'gauss':rng.normal(size=G),'heavy':rng.standard_cauchy(size=G),'gauss_big':rng.normal(size=G)*1e3+50,'const':np.zeros(G)}[ut]
            ind=np.zeros(G); ind[rng.choice(G,k,replace=False)]=1
            for c in [1e5]:
                for eps in [1e-9,1e-12]:
                    cov=1-miss_mask(ind+eps*u,c,G,n,idx).mean()
                    ok=cov<=1-pi_k(G,n,k)+1e-12; tot+=1; bad+= (not ok)
                    rows.append(dict(G=G,n=n,k=k,u=ut,c=c,eps=eps,cov=cov,one_minus_pi=1-pi_k(G,n,k),ok=ok))
print('failures at c=1e5 with eps<=1e-9:',bad,'of',tot)
pd.DataFrame(rows).to_csv('checks_theorem1_smalleps.csv',index=False)
