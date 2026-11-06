
import sys, json, multiprocessing as mp
sys.path.insert(0,'crit')
from core import *
import search_grouped as sg
cases=[(24,8),(24,12),(51,8),(51,16)]
fracs=[.25,.5,.75,.9,.95]
jobs=[]
for G,n in cases:
    fr=frontier(G,n,.1)
    for f in fracs:
        k0=f*fr
        if k0<1.0/G*(1+1e-9): continue
        for d in [2,3,4,5,6]:
            for seed in range(24):
                jobs.append((G,n,.1,k0,d,seed*100+d,8000))
if __name__=="__main__":
    with mp.Pool(9) as p:
        res=p.map(sg.run,jobs,chunksize=4)
    res=[r for r in res if r]
    json.dump(res,open('crit/search_grouped_results.json','w'))
    print(len(jobs),len(res))
