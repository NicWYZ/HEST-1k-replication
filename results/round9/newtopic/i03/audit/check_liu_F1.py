"""Check Liu et al. (arXiv:2310.13939) Thm 1(2)/2 on the conditional F1 model against direct Monte Carlo.
Model: X n x p iid N(0,1), Y = X B + E, B = sqrt(theta) e1 e1', H = X (X'X + n lam I)^-1 X', F = H Y.
Liu notation: Xliu = F/sqrt(q) = A + Sigma^{1/2} W, Sigma=H^2, A = sqrt(theta/q) H X u v', W = E/sqrt(q), p_L=n, n_L=q.
Prediction (my own implementation): R = AA' + Sigma, gamma_1 top eig, Xi top eigvec,
 eta = 1 - (1/q) sum_{i!=1} g_i^2/(g_1-g_i)^2,  overlap = eta * (Xi'a)^2 / g_1,   a = sqrt(theta/q) H X u.
 top eigenvalue prediction phi(g_1) = g_1 + (g_1/q) sum_{i!=1} g_i/(g_1-g_i).
"""
import numpy as np, pandas as pd, sys
def one(n,gam,c,lam,theta,rng):
    p=int(gam*n); q=int(c*n)
    X=rng.standard_normal((n,p)); E=rng.standard_normal((n,q))
    Hm=X@np.linalg.solve(X.T@X+n*lam*np.eye(p),X.T); Hm=(Hm+Hm.T)/2
    u=np.zeros(p);u[0]=1; v=np.zeros(q);v[0]=1
    Y=np.sqrt(theta)*np.outer(X@u,v)+E
    F=Hm@Y
    U,s,Vt=np.linalg.svd(F,full_matrices=False)
    mc_overlap=(Vt[0]@v)**2; mc_lam=s[0]**2/q
    a=np.sqrt(theta/q)*Hm@(X@u)
    R=np.outer(a,a)+Hm@Hm
    g,Xi=np.linalg.eigh(R); g=g[::-1]; Xi=Xi[:,::-1]
    g1=g[0]; rest=g[1:]
    eta=1-np.sum(rest**2/(g1-rest)**2)/q
    pred=eta*(Xi[:,0]@a)**2/g1
    phi=g1+g1*np.sum(rest/(g1-rest))/q
    return dict(n=n,gamma=gam,c=c,lam=lam,theta=theta,mc_overlap=mc_overlap,pred_overlap=pred,eta=eta,
                gamma1=g1,gamma2=g[1],mc_top_eig=mc_lam,pred_top_eig=phi)
if __name__=="__main__":
    rng=np.random.default_rng(1); rows=[]
    n=int(sys.argv[1]) if len(sys.argv)>1 else 1500
    for theta in [0.4,0.7,1.1,2.0]:
        for rep in range(8):
            rows.append(one(n,2.0,0.1,0.3,theta,rng))
    df=pd.DataFrame(rows); df.to_csv(f'liu_check_n{n}.csv',index=False)
    g=df.groupby('theta').agg(['mean','std'])[['mc_overlap','pred_overlap','eta','mc_top_eig','pred_top_eig','gamma1','gamma2']]
    pd.set_option('display.width',250); print(g.round(4))
