"""Simulation: LLG lower bound (Chen-Kelly-Malamud) under group-level shifts. Seeds fixed per cell/rep."""
import numpy as np, pandas as pd, itertools, sys
import multiprocessing as mp, os

FSH=0.2          # variance share of f(z)=z'beta (within-group predictable part), relative to var(z'beta)+tau2+sig_e2 =1
def sizes(rng,G,nbar,unequal):
    if not unequal: return np.full(G,nbar)
    return 2+rng.multinomial(nbar*G-2*G,rng.dirichlet(np.ones(G)))

def llg(S,Soos,z_ref=0.1):
    T=S.shape[0]; U,s,Vt=np.linalg.svd(S,full_matrices=False)
    lam=s**2/T; z=z_ref*lam.sum()/min(S.shape)
    D=lam/(z+lam)**2
    Toos=Soos.shape[0]
    q=((Soos@Vt.T)**2).sum(0)/Toos          # v_i' Psi_oos v_i
    L=(D*q).sum()/T
    # ridge predictor f = Soos (zI+Psi)^-1 S'y/T = Soos V diag(1/(z+lam)) (s) U' y / T
    return L,(U,s,Vt,z,lam)
def ridge_pred(parts,Soos,y):
    U,s,Vt,z,lam=parts; T=len(y)
    coef=Vt.T@((s/(z+lam))*(U.T@y)/T)
    return Soos@coef

def draw(rng,sz,p,beta,s,kappa,mu_shift,iid_twin,sig2e):
    n=int(sz.sum()); gid=np.repeat(np.arange(len(sz)),sz)
    Z=rng.standard_normal((n,p))
    if mu_shift: X=Z+np.sqrt(kappa)*rng.standard_normal((len(sz),p))[gid]
    else: X=Z
    f=X@beta
    tau2=s
    eta=np.sqrt(tau2)*(rng.standard_normal(n) if iid_twin else rng.standard_normal(len(sz))[gid])
    y=f+eta+np.sqrt(sig2e)*rng.standard_normal(n)
    return X,y,gid,Z@beta

def one(seed,G,nbar,s,unequal,variant,p_ratio=1.5):
    rng=np.random.default_rng(seed)
    N=nbar*G; p=int(p_ratio*N)
    sig2e=1-FSH-s
    kappa=0.5 if variant.endswith("B") else 0.0
    u=rng.standard_normal(p); beta=np.sqrt(FSH)*u/np.linalg.norm(u)
    twin=variant.startswith("twin"); shift=variant.endswith("B")
    sz=sizes(rng,G,nbar,unequal); szo=sizes(rng,G,nbar,unequal)
    X,y,g,fz=draw(rng,sz,p,beta,s,kappa,shift,twin,sig2e)
    Xo,yo,go,fzo=draw(rng,szo,p,beta,s,kappa,shift,twin,sig2e)
    out={}
    varf=FSH*(1+kappa)  # Var(x'beta)
    tot=varf+s+sig2e
    R2tot=varf/tot; R2within=FSH/(FSH+sig2e)
    # pooled, no demeaning (the claim)
    L,parts=llg(X,Xo); fh=ridge_pred(parts,Xo,y)
    R2=1-((yo-fh)**2).mean()/(yo**2).mean()
    out.update(R2oos=R2,L=L,B=(R2+L)/(1+L),R2tot=R2tot,R2within=R2within)
    if variant=="clusA" or variant=="clusB":
        # within-demeaned fit and bound (equal-size reduction)
        def dm(A,gid,k):
            m=np.zeros((k,)+A.shape[1:]); np.add.at(m,gid,A); m/= np.bincount(gid,minlength=k).reshape((-1,)+(1,)*(A.ndim-1)); return A-m[gid]
        Xd,yd,Xod,yod=dm(X,g,G),dm(y,g,G),dm(Xo,go,G),dm(yo,go,G)
        Ld,pd_=llg(Xd,Xod); fhd=ridge_pred(pd_,Xod,yd)
        R2d=1-((yod-fhd)**2).mean()/(yod**2).mean()
        out.update(R2oos_dm=R2d,L_dm=Ld,B_dm=(R2d+Ld)/(1+Ld))
    return out

def one_means(seed,G,nbar,s,unequal,whiten,p_ratio=1.5):
    """group-mean regression: features are group means of x, outcome group mean of y."""
    rng=np.random.default_rng(seed); N=nbar*G; p=int(p_ratio*N); sig2e=1-FSH-s
    u=rng.standard_normal(p); beta=np.sqrt(FSH)*u/np.linalg.norm(u)
    def mk(sz):
        Xb=rng.standard_normal((len(sz),p))/np.sqrt(sz)[:,None]
        sd=np.sqrt(s+sig2e/sz)
        yb=Xb@beta+sd*rng.standard_normal(len(sz))
        return Xb,yb,sd
    sz=sizes(rng,G,nbar,unequal); szo=sizes(rng,G,nbar,unequal)
    X,y,sd=mk(sz); Xo,yo,sdo=mk(szo)
    if whiten: X,y,Xo,yo=X/sd[:,None],y/sd,Xo/sdo[:,None],yo/sdo
    # target: 1 - E[noise var]/E[y^2] on the scale used (E over the size distribution, estimated by large draw)
    big=np.random.default_rng(999).choice(sizes(np.random.default_rng(1),2000,nbar,unequal),20000)
    nv=s+sig2e/big
    if whiten: tgt=1-1/(1+ (FSH/(nv)).mean())
    else: tgt=1-nv.mean()/(FSH/big+nv).mean()  # E[f^2]=FSH*E[|xbar|^2 ... ] f=xbar'beta has var FSH/n
    L,parts=llg(X,Xo); fh=ridge_pred(parts,Xo,y)
    R2=1-((yo-fh)**2).mean()/(yo**2).mean()
    return dict(R2oos=R2,L=L,B=(R2+L)/(1+L),tgt=tgt)


CODE={'clusA':1,'twinA':2,'clusB':3,'twinB':4,'raw':5,'whit':6}
def run(j):
    kind,var,G,s,un,r=j
    seed=(abs(int(1e6*s))*7919+G*104729+r*1299709+int(un)*15485863+CODE[var]*32452843)%(2**31)
    o=one(seed,G,10,s,un,var) if kind=="pooled" else one_means(seed,G,10,s,un,var=="whit")
    o.update(kind=kind,variant=var,G=G,s=s,unequal=un,rep=r); return o

if __name__=="__main__":
    reps=int(sys.argv[1]) if len(sys.argv)>1 else 300
    jobs=[]
    for variant in ["clusA","twinA","clusB","twinB"]:
        for G in [10,25,50]:
            for s in [0.0,0.1,0.3,0.6]:
                for un in [False,True]:
                    for r in range(reps): jobs.append(("pooled",variant,G,s,un,r))
    for G in [10,25,50]:
        for s in [0.1,0.3,0.6]:
            for un in [False,True]:
                for wh in [False,True]:
                    for r in range(reps): jobs.append(("means","whit" if wh else "raw",G,s,un,r))
    with mp.Pool(int(os.environ.get('NPROC','4'))) as pool_: res=pool_.map(run,jobs,chunksize=20)
    pd.DataFrame(res).to_parquet("f_LLGCLUSTER_sim_raw.parquet"); print(len(res))
