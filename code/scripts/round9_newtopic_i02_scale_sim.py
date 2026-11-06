import numpy as np, pandas as pd
rng=np.random.default_rng(20261026)
L=50
ii,jj=np.meshgrid(np.arange(L),np.arange(L),indexing='ij'); ii=ii.ravel(); jj=jj.ravel()
xy=np.c_[ii+jj/2,jj*np.sqrt(3)/2]
D=np.sqrt(((xy[:,None]-xy[None])**2).sum(-1))
idx={(a,b):k for k,(a,b) in enumerate(zip(ii,jj))}
nb=[(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
pools=[]
for k,(a,b) in enumerate(zip(ii,jj)):
    m=[idx.get((a+da,b+db)) for da,db in nb]
    if all(v is not None for v in m): pools.append([k]+m)
pools=np.array(pools)
S2=0.5
def sumrho(phi,shape='LN'):
    p=pools[0]; d=D[np.ix_(p,p)]; r=np.exp(-d/phi)
    if shape=='LN': r=(np.exp(S2*r)-1)/(np.exp(S2)-1)
    return r.sum()-7
def run(mu,phi,s2,v,R=1000,phi_assumed=None,rho=0.6,shape='LN'):
    phi_assumed=phi_assumed or phi
    C=s2*np.exp(-D/phi); Lc=np.linalg.cholesky(C+1e-9*np.eye(len(C)))
    VarL=mu**2*(np.exp(s2)-1); EL2=mu**2*np.exp(s2)
    VarY=mu+v*EL2+VarL; ceil=VarL/VarY
    out=[]
    for r in range(R):
        g=Lc@rng.standard_normal(len(C)); lam=mu*np.exp(g-s2/2)
        lam_n=lam*(rng.gamma(1/v,v,len(lam)) if v>0 else 1)
        y=rng.poisson(lam_n)
        z=(lam-lam.mean())/lam.std()
        P=rho*z+np.sqrt(1-rho**2)*rng.standard_normal(len(z))
        ybar=y.mean(); V1=y.var(ddof=1)
        c1=1-ybar/V1
        S7=y[pools].sum(1); V7=S7.var(ddof=1)
        sr=sumrho(phi_assumed,shape); sig2=(V7-7*V1)/sr   # two-scale, known shape
        c2=sig2/V1
        cPY=np.cov(P,y)[0,1]
        sk1=cPY/np.sqrt(P.var(ddof=1)*max(V1-ybar,1e-9))
        sk2=cPY/np.sqrt(P.var(ddof=1)*max(sig2,1e-9))
        # block jackknife SE of c2 and c1: 5x5 tiles over the lattice
        tile=(ii//10)*5+(jj//10); ptile=tile[pools[:,0]]
        j1=[];j2=[]
        for t in range(25):
            k=tile!=t; kp=ptile!=t
            yv=y[k]; v1=yv.var(ddof=1); a=1-yv.mean()/v1
            v7=S7[kp].var(ddof=1); b=(v7-7*v1)/sr/v1
            j1.append(a); j2.append(b)
        se1=np.sqrt(24/25*np.sum((np.array(j1)-np.mean(j1))**2)); se2=np.sqrt(24/25*np.sum((np.array(j2)-np.mean(j2))**2))
        out.append((c1,c2,sk1,sk2,ceil,rho,se1,se2))
    o=np.array(out)
    return o,ceil
rows=[]
for mu in (0.5,3.0):
  for phi in (1.0,2.5):
    for v,lab in ((0.0,'Poisson'),(0.5,'overdisp')):
      for fac,shp,labm in ((1,'LN','shape_right'),(1,'EX','expshape_for_lognormal'),(1.3,'LN','phi_x1.3'),(0.7,'LN','phi_x0.7')):
        pa=fac*phi
        o,ceil=run(mu,phi,0.5,v,R=300,phi_assumed=pa,shape=shp)
        R=len(o)
        for name,j in (('ceil_poisson_1scale',0),('ceil_2scale',1),('skill_poisson_1scale',2),('skill_2scale',3)):
            tru=ceil if j<2 else 0.6
            x=o[:,j]
            rows.append(dict(mu=mu,phi=phi,noise=lab,assumed=labm,est=name,truth=tru,mean=x.mean(),mc_se_mean=x.std(ddof=1)/np.sqrt(R),
              rel_bias=(x.mean()-tru)/tru,sd=x.std(ddof=1),R=R,jk_se_mean=(o[:,6].mean() if j==0 else o[:,7].mean() if j==1 else np.nan)))
df=pd.DataFrame(rows); df.to_csv('f_SCALE_sim_results.csv',index=False)
pd.set_option('display.width',200)
print(df[df.assumed=='shape_right'].round(3).to_string())
print(df[(df.assumed!='shape_right')&df.est.isin(['ceil_2scale'])].round(3).to_string())
