"""F3 SCALE data check. Usage: python f_SCALE_data_check.py <R> <outdir>. Aggregates only."""
import sys, json, glob, numpy as np, pandas as pd, anndata as ad, scipy.sparse as sp
from scipy.spatial import cKDTree
PQ={"CCRCC":"results/round3/B1_ppi","INDIANA_KIDNEY":"results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY","LUNG_XENIUM":"results/round4/ppi/Q2_theory/predictions"}
ENC="uni_v2"; rng=np.random.default_rng(20261026)
def main(R,out):
    gl=[]; tl=[]
    for t,pqd in PQ.items():
        tds=[p for p in glob.glob(R+"/results/**/"+t+".json",recursive=True) if "pre_P8" not in p and "paths" in json.load(open(p))]
        tmpl=json.load(open(tds[0]))["paths"]["adata"]
        df=pd.read_parquet(f"{R}/{pqd}/b1_predictions__{t}__{ENC}.parquet").set_index(["sample_id","barcode"])
        genes=[c[3:] for c in df.columns if c.startswith("y__")]
        cells=[]
        for sid in sorted(set(df.index.get_level_values(0))):
            m=df.index.get_level_values(0)==sid
            bcs=df.index.get_level_values(1)[m].astype(str)
            a=ad.read_h5ad(R+"/"+tmpl.format(sample_id=sid))
            pos=pd.Index(a.obs_names.astype(str)).get_indexer(bcs)
            if (pos<0).any(): continue
            xy=np.asarray(a.obsm["spatial"])[pos].astype(float)
            Y=np.rint(np.expm1(df.loc[m,["y__"+g for g in genes]].values.astype(float)))
            P=np.clip(np.expm1(df.loc[m,["f__"+g for g in genes]].values.astype(float)),0,None)
            ok=np.isfinite(Y).all(1)&np.isfinite(P).all(1)
            Y=Y[ok];P=P[ok];xy=xy[ok]; n=len(Y)
            if n<100: continue
            nbr=cKDTree(xy).query(xy,k=7)[1][:,1:]
            donor=str(df.loc[m,"donor_id"].iloc[0])
            yb=Y.mean(0); V=Y.var(0,ddof=1); Z=Y-yb
            cnn=np.mean([(Z*Z[nbr[:,k]]).mean(0) for k in range(6)],axis=0)
            y1=rng.binomial(Y.astype(int),0.5).astype(float); y2=Y-y1
            with np.errstate(all="ignore"):
                r=np.array([np.corrcoef(y1[:,j],y2[:,j])[0,1] for j in range(Y.shape[1])])
                T=2*r/(1+r)
                U=1-yb/V; L=cnn/V
                cov=((P-P.mean(0))*Z).sum(0)/(n-1); vp=P.var(0,ddof=1)
                sk_lo=cov/np.sqrt(vp*np.clip(U,1e-9,None)*V); sk_hi=cov/np.sqrt(vp*np.where(L>0,L,np.nan)*V)
            for j,g in enumerate(genes):
                if yb[j]>0 and V[j]>0: cells.append((t,donor,sid,g,n,yb[j],V[j],U[j],L[j],T[j],cov[j],sk_lo[j],sk_hi[j]))
        c=pd.DataFrame(cells,columns="task donor sample gene n ybar V U L T cov sk_lo sk_hi".split())
        d=c.groupby(["gene","donor"]).mean(numeric_only=True).reset_index()   # donor-level (mean over slides)
        d["width"]=d.U-d.L
        g=d.groupby("gene").agg(n_donors=("donor","nunique"),ybar=("ybar","mean"),U=("U","mean"),L=("L","mean"),T=("T","mean"),
            cov=("cov","mean"),cov_se=("cov",lambda x:x.std(ddof=1)/np.sqrt(len(x))),sk_lo=("sk_lo","mean"),sk_hi=("sk_hi","mean")).reset_index()
        g.insert(0,"task",t); gl.append(g)
        top=g.sort_values("cov",ascending=False).head(20)
        tl.append(dict(task=t,n_donors=d.donor.nunique(),n_genes=g.shape[0],n_donor_gene_cells=len(d),
            frac_L_le_U=float((d.L<=d.U).mean()),median_width=float(d.width.median()),median_U=float(d.U.median()),median_L=float(d.L.median()),
            median_abs_T_minus_U=float((d["T"]-d.U).abs().median()),frac_sk_hi_le_1=float((d.sk_hi<=1).mean()),
            top20_n_se_lt_half=int((top.cov_se<0.5*top["cov"].abs()).sum()),top20_median_se_over_est=float((top.cov_se/top["cov"].abs()).median()),
            median_sk_lo=float(g.sk_lo.median()),median_sk_hi=float(g.sk_hi.median())))
        print(t,"done",flush=True)
    pd.concat(gl).to_csv(out+"/f_SCALE_gene_summary.csv.gz",index=False)
    pd.DataFrame(tl).to_csv(out+"/f_SCALE_task_summary.csv",index=False)
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
