import numpy as np, pandas as pd, sys
sys.path.insert(0,'.')
from check_liu_F1 import one
rng=np.random.default_rng(7); rows=[]
n=int(sys.argv[1]); reps=int(sys.argv[2])
for theta in [0.1,0.2,0.3,0.4,0.5,0.7,1.1]:
    for r in range(reps): rows.append(one(n,2.0,0.1,0.3,theta,rng))
df=pd.DataFrame(rows); df.to_csv(f'liu_scan_n{n}.csv',index=False)
pd.set_option('display.width',250)
print(df.groupby('theta')[['mc_overlap','pred_overlap','eta','mc_top_eig','pred_top_eig','gamma1']].mean().round(4))
