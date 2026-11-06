import sys, json, glob, numpy as np, pandas as pd, anndata as ad, scipy.sparse as sp, pyarrow.parquet as pq
from scipy.spatial import cKDTree
from scipy import stats
sys.path.insert(0,'.')
from boundary_sim import fit, two_means
R="/work/users/w/e/weiyang/hest_replication"
rng=np.random.default_rng(20261027)
rows=[]
for task in ("CCRCC","INDIANA_KIDNEY"):
    pf=glob.glob(R+f"/results/**/*predictions*{task}*resnet50.parquet",recursive=True)+glob.glob(R+f"/results/**/b1_predictions__{task}__resnet50.parquet",recursive=True)
    pf=sorted(set(pf)); print(task,pf[:2],flush=True)
    sch=pq.read_schema(pf[0]); genes=[n[3:] for n in sch.names if n.startswith("y__")]
    sids=pd.read_parquet(pf[0],columns=["sample_id"]).sample_id.unique()
    tds=[p for p in glob.glob(R+"/results/**/"+task+".json",recursive=True) if "pre_P8" not in p and "paths" in json.load(open(p))]
    tmpl=json.load(open(tds[0]))["paths"]["adata"]
    for si,sid in enumerate(sids[:3]):
        a=ad.read_h5ad(R+"/"+tmpl.format(sample_id=sid))
        xy=np.asarray(a.obsm["spatial"]).astype(float)
        tree=cKDTree(xy); nn=tree.query(xy,k=2)[0][:,1]; s=np.median(nn)
        X=a.X; X=X.tocsc() if sp.issparse(X) else X
        gi=[(g,list(a.var_names).index(g)) for g in genes if g in set(a.var_names)]
        mu=[(g,i,float(np.asarray(X[:,i].todense() if sp.issparse(X) else X[:,i]).mean())) for g,i in gi]
        mu=sorted(mu,key=lambda t:-t[2])
        pick=mu[:3]+mu[len(mu)//2:len(mu)//2+3]+mu[-2:]
        cl=((xy[:,0]//(8*s)).astype(int)*1000+(xy[:,1]//(8*s)).astype(int))
        pairs=tree.query_ball_tree(tree,6*2*s)
        # smoothing weights (Gaussian sigma = 2 spacings)
        idx=np.concatenate([np.full(len(p),i) for i,p in enumerate(pairs)]); jdx=np.concatenate([np.array(p) for p in pairs])
        w=np.exp(-((xy[idx]-xy[jdx])**2).sum(1)/(2*(2*s)**2))
        for g,i,m in pick:
            y=np.asarray(X[:,i].todense() if sp.issparse(X) else X[:,i]).ravel().astype(float)
            for eps in (0.5,):
                res={}
                for rep in range(20):
                    y1=rng.binomial(y.astype(int),eps).astype(float); y2=y-y1
                    num=np.bincount(idx,w*y1[jdx]/eps,minlength=len(y)); den=np.bincount(idx,w,minlength=len(y))
                    sm=num/den; t=two_means(sm)
                    if t is None: continue
                    mk=sm>t
                    if mk.sum()<20 or (~mk).sum()<20: continue
                    dh=cKDTree(xy[mk]).query(xy)[0]; dl=cKDTree(xy[~mk]).query(xy)[0]
                    d=np.where(mk,dl-s/2,-(dh-s/2))/s
                    tt=stats.ttest_ind(y2[mk],y2[~mk],equal_var=False)
                    res.setdefault(('dim',0),[]).append(tt.pvalue<0.05)
                    for h in (2,3,5):
                        for nm,p,c in (('ll',1,None),('rbc',2,None),('llcr',1,cl),('rbccr',2,cl)):
                            r=fit(d,y2,h,p,c,None)
                            if r is None: continue
                            j,se,bo,G,nR,nL=r
                            rej=abs(j/se)>(1.96 if c is None else stats.t.ppf(.975,max(G-1,1)))
                            res.setdefault((nm,h),[]).append(rej)
                for (nm,h),v in res.items():
                    rows.append(dict(task=task,slide=si,gene=g,mean_count=m,eps=eps,test=nm,h=h,n_thin=len(v),reject_frac=float(np.mean(v)),n_spots=len(y)))
        print(task,si,flush=True)
import os; os.makedirs("out",exist_ok=True)
pd.DataFrame(rows).to_csv("out/data_check.csv",index=False)
