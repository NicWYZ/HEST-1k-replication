
import sys, json, math, numpy as np, multiprocessing as mp
sys.path.insert(0,'crit')
from core import *
import search_grouped as sg

def full_search(args):
    G,n,alpha,k0,start_vals,start_mult,seed,iters=args
    rng=np.random.default_rng(seed)
    x=np.repeat(np.array(start_vals,float),np.array(start_mult,int))
    x=x+rng.normal(0,1e-3,size=G)*np.std(x)   # break ties slightly
    x=x-x.mean()
    if kappa_of(x)>k0: 
        return None
    S=all_samples(G,n)
    def tstat(x):
        xs=x[S]; A=xs.sum(1); Q=(xs**2).sum(1)
        return np.where(Q>1e-300,A*A/(n*np.maximum(Q,1e-300)),0.0)
    def cpop(x):
        t=tstat(x); w=np.full(len(t),1/len(t)); rho,const=quantile_rho(t,w,alpha)
        return c_of_rho(rho,G,n)
    cur=cpop(x); best=(cur,x.copy())
    cref=cur*0.995; 
    t=tstat(x); J=(t>rho_of_c(cref,G,n)).mean()
    for it in range(iters):
        y=x.copy()
        r=rng.random()
        kk=rng.integers(1,4)
        idx=rng.choice(G,size=kk,replace=False)
        if r<0.7: y[idx]+=rng.normal(0,rng.choice([0.005,0.03,0.15]),size=kk)*np.std(x)
        else: y[idx[0]]=y[rng.integers(G)]+rng.normal(0,0.01)*np.std(x)
        y=y-y.mean()
        if kappa_of(y)>k0*(1-1e-12): continue
        ty=tstat(y); Jy=(ty>rho_of_c(cref,G,n)).mean()
        if Jy>=J:
            x,J=y,Jy
            if J>alpha+1e-9:
                c=cpop(x)
                if c>best[0]: best=(c,x.copy())
                cref=max(cref,best[0]*0.998)
                J=(tstat(x)>rho_of_c(cref,G,n)).mean()
    return dict(G=G,n=n,k0=k0,seed=seed,c=float(best[0]),x=(best[1]/np.std(best[1],ddof=1)).tolist())

if __name__=="__main__":
    res=json.load(open('crit/search_grouped_results.json'))
    best={}
    for r in res:
        key=(r['G'],r['n'],round(r['k0'],6))
        if key not in best or r['c']>best[key]['c']: best[key]=r
    jobs=[]
    for k,v in best.items():
        if k[0]==24:
            for seed in range(3):
                jobs.append((k[0],k[1],.1,v['k0'],v['vals'],v['mult'],seed,2500 if k[1]==8 else 900))
    with mp.Pool(9) as pool: out=pool.map(full_search,jobs)
    out=[o for o in out if o]
    json.dump(out,open('crit/full_search_results.json','w'))
    # extra grouped d=3,4,5 for G=51 and 24 high fractions
    jobs2=[]
    for k,v in best.items():
        for d in [3,4,5]:
            for seed in range(30):
                jobs2.append((k[0],k[1],.1,v['k0'],d,10000+seed*7+d,15000))
    with mp.Pool(9) as pool: out2=pool.map(sg.run,jobs2,chunksize=4)
    json.dump([o for o in out2 if o],open('crit/search_grouped_results2.json','w'))
    print('done')
