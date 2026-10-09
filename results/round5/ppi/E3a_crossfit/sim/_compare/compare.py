import pandas as pd, numpy as np, glob, json
B='/Users/nicolaszhang/hest-1k/HEST-1k-replication-PPI/results/round5/ppi/E3a_crossfit'
fs=sorted(glob.glob(B+'/sim/G*/e3a_sim_grid__*.csv'))
n=pd.concat([pd.read_csv(f) for f in fs],ignore_index=True); n.to_csv(B+'/e3a_sim_grid.csv',index=False)
e=pd.read_csv(B+'/../E1_interval/e1_sim_grid.csv')
K=['G','n_L','R2','lambda_star','kappa','law','rule','interval']
out={'files':len(fs),'rows':len(n),'intervals':sorted(n.interval.unique()),'laws':sorted(n.law.unique())}
acc=[]
# A
na=n[n.interval.isin(['textbook_t|fpc|lin','textbook_t|fpc'])]
m=na.merge(e,on=K,suffixes=('','_e1'),how='left',indicator=True)
out['A_unmatched']=int((m._merge!='both').sum())
cols=[c for c in n.columns if c not in K and pd.api.types.is_numeric_dtype(n[c]) and c+'_e1' in m.columns]
eq=np.ones(len(m),bool); worst={}
for c in cols:
    a=m[c].values.astype(float); b=m[c+'_e1'].values.astype(float)
    same=(a==b)|(np.isnan(a)&np.isnan(b)); eq&=same
    d=np.abs(a-b); d=np.where(same,0,d); r=np.where(same,0,d/np.maximum(np.abs(b),1e-300))
    worst[c]=(float(np.nanmax(d)),float(np.nanmax(r)))
out['A_rows']=len(m); out['A_exact']=int(eq.sum()); out['A_cols']=len(cols)
out['A_worst_nonzero']={c:v for c,v in worst.items() if v[0]>0}
cov=[c for c in cols if c.startswith('coverage')]
acc.append(dict(check='A_reproduction_exact_rows',n=len(m),n_pass=int(eq.sum()),worst=max(v[0] for v in worst.values()),tolerance='exact (E0: 0.005 abs coverage, 1e-5 rel variance)'))
# B
ids=[c for c in n.columns if c not in K+['interval']]
def pair(sub,lab):
    a=sub[sub.interval=='textbook_t|fpc|lin'].set_index(K[:-1]); b=sub[sub.interval=='textbook_t|fpc|lin|xf'].set_index(K[:-1])
    j=a.join(b,lsuffix='_a',rsuffix='_b',how='inner')
    ok=np.ones(len(j),bool); w=0.
    for c in n.columns:
        if c in K or c in('source_file',): continue
        if not pd.api.types.is_numeric_dtype(n[c]): continue
        x=j[c+'_a'].values.astype(float); y=j[c+'_b'].values.astype(float)
        s=(x==y)|(np.isnan(x)&np.isnan(y)); ok&=s
        if (~s).any(): w=max(w,float(np.nanmax(np.abs(x-y)[~s])))
    acc.append(dict(check=lab,n=len(j),n_pass=int(ok.sum()),worst=w,tolerance='exact'))
    out[lab+'_nonident_cols']=[c for c in n.columns if c not in K and c!='source_file' and pd.api.types.is_numeric_dtype(n[c]) and not ((j[c+'_a']==j[c+'_b'])|(j[c+'_a'].isna()&j[c+'_b'].isna())).all()]
pair(n[n.rule.isin(['none','oracle'])],'B_rules_none_oracle_lin_vs_xf')
pair(n[(n.rule=='c_crossfit_design')&(n.n_L==4)],'B_c_crossfit_nL4_lin_vs_xf')
pd.DataFrame(acc).to_csv(B+'/e3a_sim_acceptance.csv',index=False)
# predictions
cd=n[n.rule=='c_crossfit_design']
L=cd[cd.interval=='textbook_t|fpc|lin'].set_index(['G','n_L','R2','lambda_star','kappa','law'])
X=cd[cd.interval=='textbook_t|fpc|lin|xf'].set_index(['G','n_L','R2','lambda_star','kappa','law'])
j=L[['coverage_mean','est_over_emp_mean']].join(X[['coverage_mean','est_over_emp_mean']],lsuffix='_lin',rsuffix='_xf').reset_index()
c1=j[(j.law=='normal')&(j.lambda_star==0.6)&(j.G==15)&(j.n_L==12)].copy()
c1['in_ratio_band']=c1.est_over_emp_mean_xf.between(0.90,1.05); c1['cov_ok']=c1.coverage_mean_xf>=0.88
c1.to_csv(B+'/e3a_sim_prediction_cells.csv',index=False)
out['E31']=dict(cells=len(c1),ratio_in_band=int(c1.in_ratio_band.sum()),cov_ok=int(c1.cov_ok.sum()),both=int((c1.in_ratio_band&c1.cov_ok).sum()),
 xf_ratio_range=[float(c1.est_over_emp_mean_xf.min()),float(c1.est_over_emp_mean_xf.max())],lin_ratio_range=[float(c1.est_over_emp_mean_lin.min()),float(c1.est_over_emp_mean_lin.max())],
 cov_xf_min=float(c1.coverage_mean_xf.min()),cov_xf_range_med=float(c1.coverage_mean_xf.median()),
 worst=c1.sort_values('est_over_emp_mean_xf').iloc[[0,-1]][['R2','kappa','est_over_emp_mean_xf','coverage_mean_xf']].to_dict('records'),
 worst_cov=c1.sort_values('coverage_mean_xf').iloc[0][['R2','kappa','coverage_mean_xf']].to_dict())
j['absdiff']=(j.coverage_mean_xf-j.coverage_mean_lin).abs()
c2=j[j.G==51].copy(); c2['ok_001']=c2.absdiff<0.01; c2['ok_0005']=c2.absdiff<0.005
c2['applies_0005']=c2.lambda_star==1.2
c2.to_csv(B+'/e3a_sim_prediction_cells_E3a2.csv',index=False)
l12=c2[c2.lambda_star==1.2]
out['E32']=dict(cells=len(c2),lt001=int(c2.ok_001.sum()),max_diff=float(c2.absdiff.max()),signed_range=[float((c2.coverage_mean_xf-c2.coverage_mean_lin).min()),float((c2.coverage_mean_xf-c2.coverage_mean_lin).max())],
 lam12_cells=len(l12),lam12_lt0005=int(l12.ok_0005.sum()),lam12_max=float(l12.absdiff.max()),
 worst=c2.sort_values('absdiff',ascending=False).head(5)[['law','n_L','R2','lambda_star','kappa','absdiff']].to_dict('records'),
 worst_lam12=l12.sort_values('absdiff',ascending=False).head(3)[['law','n_L','R2','kappa','absdiff']].to_dict('records'),
 laws_in_E32=sorted(c2.law.unique()))
# tabulation
t=j.copy(); t['skew']=np.where(t.law=='normal','normal','skewed')
rows=[]
for (G,nl,lw),g in t.groupby(['G','n_L','law']):
    r=dict(G=G,n_L=nl,law=lw,n_cells=len(g))
    for s in('lin','xf'):
        r[f'cov_median_{s}']=g['coverage_mean_'+s].median(); r[f'cov_min_{s}']=g['coverage_mean_'+s].min()
        r[f'ratio_median_{s}']=g['est_over_emp_mean_'+s].median(); r[f'ratio_min_{s}']=g['est_over_emp_mean_'+s].min()
    rows.append(r)
T=pd.DataFrame(rows); T.to_csv(B+'/e3a_sim_tabulation.csv',index=False)
out['tab_G15_nL12']=T[(T.G==15)&(T.n_L==12)].round(3).to_dict('records')
out['tab_G51_nL12']=T[(T.G==51)&(T.n_L==12)].round(3).to_dict('records')
out['tab_global']=T.groupby('G')[['cov_min_lin','cov_min_xf','ratio_min_lin','ratio_min_xf']].min().round(3).to_dict()
json.dump(out,open(B+'/sim/_compare/summary.json','w'),default=str,indent=1)
print(json.dumps(out,default=str,indent=1))
