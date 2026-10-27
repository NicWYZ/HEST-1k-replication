import sys, numpy as np, pandas as pd, itertools, time, pickle
sys.path.insert(0,'sim')
from boundary_sim import *
mode=sys.argv[1]; reps=int(sys.argv[2]); shard=int(sys.argv[3]); nshard=int(sys.argv[4])
cfgs=[]
hs=[2,3,5]
if mode=='null':
    for nu,rho,m,eps in itertools.product([0.5,1.5,2.5],[3,6,12],[2,20],[0.3,0.5,0.7]):
        cfgs.append(dict(nu=nu,rho=rho,m=m,eps=eps,sig=0.7,sig_s=2.0,hs=hs))
    for sig in (0.35,1.0):
        for m in (2,8,20): cfgs.append(dict(nu=1.5,rho=6,m=m,eps=0.5,sig=sig,sig_s=2.0,hs=hs))
    for m in (8,): 
        for nu,rho,eps in itertools.product([0.5,1.5,2.5],[3,6,12],[0.3,0.5,0.7]): cfgs.append(dict(nu=nu,rho=rho,m=m,eps=eps,sig=0.7,sig_s=2.0,hs=hs))
    for ss in (1.0,3.0): cfgs.append(dict(nu=1.5,rho=6,m=8,eps=0.5,sig=0.7,sig_s=ss,hs=hs))
elif mode=='power':
    for m,jump,eps in itertools.product([5,20],[0.0,0.4,0.8],[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]):
        cfgs.append(dict(nu=1.5,rho=4,m=m,eps=eps,sig=0.25,sig_s=2.0,hs=[2,3,5],jump=jump,curve=True))
# unique configs, dedupe
seen=set();u=[]
for c in cfgs:
    k=tuple(sorted((a,str(b)) for a,b in c.items()))
    if k not in seen: seen.add(k);u.append(c)
cfgs=u
blocks=[]; nb=10
for i,c in enumerate(cfgs):
    ss=np.random.SeedSequence([20261026,hash(mode)%1000,i]).spawn(nb)
    for b in range(nb): blocks.append((c,ss[b],reps//nb))
t0=time.time()
res=[run_block(b) for j,b in enumerate(blocks) if (j//nb)%nshard==shard]
print('time',time.time()-t0,flush=True)
pickle.dump(res,open(f'sim/raw_{mode}_{shard}.pkl','wb'))
