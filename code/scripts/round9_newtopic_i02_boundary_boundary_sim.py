"""F2 BOUNDARY simulation. Poisson counts from a log-Matern field on 64x64 lattice, thin into Y1,Y2,
estimate boundary on Y1 (Gaussian smooth + 2-means), test continuity at the boundary on Y2.
Tests: diff-in-means (Welch), local-linear (HC1), RBC (local quadratic, same h, HC1), and cluster-robust (8x8 blocks) versions.
Control: boundary taken from an INDEPENDENT field replicate (not selected on this lambda)."""
import numpy as np, sys, json, time
from scipy import ndimage, stats
from multiprocessing import Pool
N=64; NT=128
def matern_field(rng, nu, rho, cache={}):
    key=(nu,rho)
    if key not in cache:
        k=2*np.pi*np.fft.fftfreq(NT); kk=k[:,None]**2+k[None,:]**2
        kap=np.sqrt(2*nu)/rho
        S=(kap**2+kk)**(-(nu+1.0)); S=S/ (S.sum()/NT**2)
        cache[key]=np.sqrt(S)
    A=cache[key]
    W=rng.standard_normal((NT,NT))
    F=np.fft.ifft2(A*np.fft.fft2(W)).real
    return F[:N,:N]
def two_means(v):
    a,b=np.percentile(v,25),np.percentile(v,75)
    for _ in range(30):
        t=(a+b)/2; lo=v[v<=t]; hi=v[v>t]
        if len(lo)==0 or len(hi)==0: return None
        a2,b2=lo.mean(),hi.mean()
        if abs(a2-a)+abs(b2-b)<1e-9: break
        a,b=a2,b2
    return (a+b)/2
def boundary(y1,eps,sig_s):
    sm=ndimage.gaussian_filter(y1/eps,sig_s,mode='nearest')
    t=two_means(sm.ravel())
    if t is None: return None
    mask=sm>t
    if mask.all() or (~mask).all(): return None
    d=np.where(mask,ndimage.distance_transform_edt(mask)-0.5,-(ndimage.distance_transform_edt(~mask)-0.5))
    return d,mask
BLK=(np.arange(N)[:,None]//8)*8+(np.arange(N)[None,:]//8)
def fit(d,y,h,p,cl=None,y_or=None):
    """joint WLS with side-specific polynomials of order p; returns jump, se, oracle jump. cl=cluster ids or None (HC1)."""
    sel=np.abs(d)<h
    dd=d[sel]; w=1-np.abs(dd)/h; yy=y[sel]
    R=(dd>0)
    nR,nL=R.sum(),(~R).sum()
    if nR<p+3 or nL<p+3: return None
    cols=[]
    for s in (R,~R):
        for j in range(p+1): cols.append(np.where(s,dd**j,0.0))
    X=np.stack(cols,1)
    Xw=X*w[:,None]
    A=Xw.T@X
    try: Ai=np.linalg.inv(A)
    except np.linalg.LinAlgError: return None
    beta=Ai@(Xw.T@yy); e=yy-X@beta
    c=np.zeros(X.shape[1]); c[0]=1; c[p+1]=-1   # intercept_R - intercept_L
    # note first block is R, second is L
    sc=Xw*e[:,None]
    if cl is None:
        meat=sc.T@sc; G=None; adj=len(yy)/(len(yy)-X.shape[1])
    else:
        g=cl[sel]; u,inv=np.unique(g,return_inverse=True); G=len(u)
        S=np.zeros((G,X.shape[1])); np.add.at(S,inv,sc); meat=S.T@S
        adj=G/(G-1)*(len(yy)-1)/(len(yy)-X.shape[1]) if G>1 else np.nan
    V=Ai@meat@Ai*adj
    se=np.sqrt(max(c@V@c,1e-12))
    jump=c@beta
    bo=None
    if y_or is not None:
        bo=c@(Ai@(Xw.T@y_or[sel]))
    return jump,se,bo,G,nR,nL
def analyse(d,y2,mu2,hs):
    out={}
    for h in hs:
        for nm,p,cl in (('ll',1,None),('rbc',2,None),('llcr',1,BLK),('rbccr',2,BLK),('cub',3,None),('cubcr',3,BLK)):
            r=fit(d,y2,h,p,cl,mu2)
            if r is None: out[(nm,h)]=None; continue
            j,se,bo,G,nR,nL=r
            if cl is None: rej=abs(j/se)>1.96
            else: rej=abs(j/se)>stats.t.ppf(0.975,max(G-1,1))
            out[(nm,h)]=(j,se,bo,rej,nR+nL)
    return out
def one_rep(rng,nu,rho,m,eps,sig,sig_s,hs,jump=0.0,curve=False):
    g=matern_field(rng,nu,rho)
    lam_log=sig*g-sig**2/2
    if jump>0:
        yy,xx=np.mgrid[0:N,0:N]
        dom=(yy>32+8*np.sin(2*np.pi*xx/64)) if curve else (yy>32)
        lam_log=lam_log+jump*dom
        truedom=dom
    else: truedom=None
    lam=m*np.exp(lam_log)
    Y=rng.poisson(lam); Y1=rng.binomial(Y,eps); Y2=Y-Y1
    bd=boundary(Y1,eps,sig_s)
    # control boundary: independent replicate, same law (no jump)
    g2=matern_field(rng,nu,rho); lam2=m*np.exp(sig*g2-sig**2/2); Yc=rng.poisson(lam2); Y1c=rng.binomial(Yc,eps)
    bc=boundary(Y1c,eps,sig_s)
    if bd is None or bc is None: return None
    mu2=(1-eps)*lam
    res={'own':analyse(bd[0],Y2.astype(float),mu2,hs),'ctl':analyse(bc[0],Y2.astype(float),mu2,hs)}
    # difference in means between estimated domains
    mk=bd[1]; a,b=Y2[mk],Y2[~mk]
    t=stats.ttest_ind(a,b,equal_var=False); res['dim_p']=t.pvalue
    res['dim_d']=a.mean()-b.mean()
    if truedom is not None:
        res['mis']=(mk!=truedom).mean(); res['mis']=min(res['mis'],1-res['mis'])
        # mean absolute true-boundary-distance of estimated boundary pixels
        dt=np.where(truedom,ndimage.distance_transform_edt(truedom),-ndimage.distance_transform_edt(~truedom))
        eb=(ndimage.binary_dilation(mk)&~mk)|(ndimage.binary_dilation(~mk)&mk)
        res['bderr']=np.abs(dt[eb]).mean()
        # oracle-aligned test at TRUE boundary
        dtr=np.where(truedom,ndimage.distance_transform_edt(truedom)-0.5,-(ndimage.distance_transform_edt(~truedom)-0.5))
        res['true']=analyse(dtr,Y2.astype(float),mu2,hs)
    # mean profile of lambda for own boundary (sign: high side positive): accumulate sums by integer-ish bins
    dd=bd[0]; bins=np.clip(np.round(dd).astype(int),-8,8)
    pr=np.zeros(17); pc=np.zeros(17)
    np.add.at(pr,bins+8,mu2/(1-eps)/m); np.add.at(pc,bins+8,1)
    res['prof']=(pr,pc)
    return res
def run_block(args):
    cfg,seed,nrep=args
    rng=np.random.default_rng(seed)
    hs=cfg['hs']
    keys=[(nm,h) for h in hs for nm in ('ll','rbc','llcr','rbccr','cub','cubcr')]
    acc={w:{k:{'rej':[],'z':[],'b':[],'bz':[],'n':[]} for k in keys} for w in (['own','ctl']+(['true'] if cfg.get('jump',0)>0 else []))}
    dimp=[];dimd=[];mis=[];bde=[];fails=0
    PR=np.zeros(17);PC=np.zeros(17)
    for _ in range(nrep):
        r=one_rep(rng,cfg['nu'],cfg['rho'],cfg['m'],cfg['eps'],cfg['sig'],cfg['sig_s'],hs,cfg.get('jump',0.0),cfg.get('curve',False))
        if r is None: fails+=1; continue
        for w in acc:
            for k in keys:
                v=r[w][k]
                if v is None: continue
                j,se,bo,rej,n=v
                a=acc[w][k]; a['rej'].append(rej); a['z'].append(j/se); a['b'].append(bo); a['bz'].append(bo/se); a['n'].append(n)
        dimp.append(r['dim_p']); dimd.append(r['dim_d'])
        if 'mis' in r: mis.append(r['mis']); bde.append(r['bderr'])
        PR+=r['prof'][0]; PC+=r['prof'][1]
    return cfg,acc,dimp,dimd,mis,bde,fails,PR,PC
