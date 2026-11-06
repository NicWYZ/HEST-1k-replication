import numpy as np, pandas as pd, sys
sys.path.insert(0,'.')
from check_liu_F1 import one
rng=np.random.default_rng(11); rows=[]
for n in [750,1500,3000]:
    for theta in [0.4,0.7]:
        for r in range({750:12,1500:6,3000:3}[n]): rows.append(one(n,2.0,0.1,0.3,theta,rng))
df=pd.DataFrame(rows); df.to_csv('liu_scale_check.csv',index=False)
df['abs_err']=(df.mc_overlap-df.pred_overlap).abs()
print(df.groupby(['theta','n'])[['mc_overlap','pred_overlap','abs_err']].mean().round(4))
