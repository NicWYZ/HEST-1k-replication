import pickle,glob,numpy as np,pandas as pd
def agg(mode):
    rows=[];prof={}
    blocks=[]
    for f in sorted(glob.glob(f'sim/raw_{mode}_*.pkl')): blocks+=pickle.load(open(f,'rb'))
    groups={}
    for b in blocks:
        cfg=b[0]; k=tuple(sorted((a,str(v)) for a,v in cfg.items())); groups.setdefault(k,[]).append(b)
    for k,bl in groups.items():
        cfg=bl[0][0]; fails=sum(b[6] for b in bl)
        dimp=np.concatenate([b[2] for b in bl]); dimd=np.concatenate([b[3] for b in bl])
        mis=np.concatenate([b[4] for b in bl]) if bl[0][4] else np.array([]); bde=np.concatenate([b[5] for b in bl]) if bl[0][5] else np.array([])
        base={a:v for a,v in cfg.items() if a!='hs'}
        PR=sum(b[7] for b in bl);PC=sum(b[8] for b in bl)
        prof[k]=(base,PR/np.maximum(PC,1))
        for w in bl[0][1]:
            for key in bl[0][1][w]:
                cat=lambda f: np.concatenate([np.array(b[1][w][key][f],float) for b in bl])
                rej=cat('rej');z=cat('z');bz=cat('bz');b_=cat('b');n=cat('n')
                r=dict(base);r.update(which=w,test=key[0],h=key[1],nrep=len(rej),fails=fails,
                  reject=rej.mean(),mc_se=np.sqrt(rej.mean()*(1-rej.mean())/max(len(rej),1)),
                  mean_z=z.mean(),sd_z=z.std(),mean_bias_over_se=bz.mean(),rms_bias_over_se=np.sqrt((bz**2).mean()),
                  mean_bias=b_.mean(),sd_bias=b_.std(),mean_npts=n.mean(),
                  dim_reject=(dimp<0.05).mean(),dim_mean_diff=dimd.mean(),
                  mis=mis.mean() if len(mis) else np.nan,bderr=bde.mean() if len(bde) else np.nan)
                rows.append(r)
    return pd.DataFrame(rows),prof
if __name__=='__main__':
    for m in ('null','power'):
        df,prof=agg(m); df.to_csv(f'f_BOUNDARY_sim_{m}.csv',index=False); pickle.dump(prof,open(f'sim/prof_{m}.pkl','wb'))
        print(m,df.shape)
