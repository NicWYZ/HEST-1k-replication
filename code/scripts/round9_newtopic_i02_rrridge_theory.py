"""Rank-one isotropic ridge-RRR: deterministic-equivalent limits. sigma=1 (theta = signal/noise variance)."""
import numpy as np
from scipy.optimize import brentq
NQ=4000
def mp_nodes(g):
    a,b=(1-np.sqrt(g))**2,(1+np.sqrt(g))**2
    ph=(np.arange(NQ)+.5)*np.pi/NQ
    x=(a+b)/2+(b-a)/2*np.cos(ph)
    w=((b-a)/2)**2*np.sin(ph)**2/(2*np.pi*g*x)*(np.pi/NQ)
    return x,w     # mass of continuous part (1 if g<=1 else 1/g)
class Ridge:
    def __init__(s,g,c,lam):
        s.g,s.c,s.lam=g,c,lam
        s.x,s.w=mp_nodes(g)
        s.h=s.x/(s.x+lam); s.t=s.h**2
        s.nuw=g*s.w; s.nu0=max(1-g,0.0)           # nu = g*mu|_{s>0} + (1-g)_+ delta_0
        s.ma=np.sum(s.w*s.x*s.t)                  # int s h^2 dmu
        s.wa=s.w*s.x*s.t/s.ma
        s.tmax=s.t.max()
    def Gfun(s,d,z):
        return d-np.sum(s.nuw*s.t/(s.c*s.t/(1+d)-z))
    def delta(s,z):
        dmin=s.c*s.tmax/z-1+1e-12
        ds=np.linspace(max(dmin,-1+1e-9),0,4000)
        G=np.array([s.Gfun(d,z) for d in ds])
        i=np.where(G<0)[0]
        if len(i)==0: return None
        j=i[-1]
        if j==len(ds)-1: return None
        return brentq(lambda d:s.Gfun(d,z),ds[j],ds[j+1])
    def edge(s):
        lo=s.c*s.tmax*1.0000001+1e-9; hi=50.0
        if s.delta(hi) is None: hi=500
        for _ in range(60):
            mid=(lo+hi)/2
            if s.delta(mid) is None: lo=mid
            else: hi=mid
        return hi
    def D(s,z):
        d=s.delta(z); k=1/(1+d)
        A=np.sum(s.wa/(z-s.c*s.t*k))
        B=(np.sum(s.nuw/(z-s.c*s.t*k))+s.nu0/z+(s.c-1)/z)/s.c
        return z*A*B/ s.c * 1.0, z*A, B   # theta*ma*[z A B/c]=1 ; (zA, B) ~ (phi_a, phi_v) pieces
    def Dprod(s,z):
        d=s.delta(z); k=1/(1+d)
        A=np.sum(s.wa/(z-s.c*s.t*k))
        B=(np.sum(s.nuw/(z-s.c*s.t*k))+s.nu0/z+(s.c-1)/z)/s.c
        return z*A*B, A, B
    def threshold(s):
        z=s.edge()*(1+1e-6)
        return 1/(s.ma*s.Dprod(z)[0])
    def align(s,th):
        """returns (rho_zeta, |<v_hat,v>|^2, |<a_hat,a>|^2) or (None,0,0) below threshold"""
        z0=s.edge()*(1+1e-7)
        f=lambda z: th*s.ma*s.Dprod(z)[0]-1
        if f(z0)<=0: return None,0.0,0.0
        hi=z0*2
        while f(hi)>0: hi*=2
        z=brentq(f,z0,hi,xtol=1e-12)
        e=1e-5*z; 
        P=lambda z:s.Dprod(z)[0]; dP=(P(z+e)-P(z-e))/(2*e)
        # outlier eq: S2 * P(z) =1 with S2=th*ma ; overlaps by BGN-type formula in z=x^2 variable
        S2=th*s.ma
        # x=sqrt(z); phi_a = x g_a(x^2) ; D=phi_a phi_v ; D'(x)=2x P'(z)/(n-scale) ; use ratio forms
        Dx=2*np.sqrt(z)*dP  # derivative wrt x (x scaled by sqrt(n) cancels with s scaling)
        phi_v=np.sqrt(z)*s.Dprod(z)[2]/s.c*0+np.sqrt(z)*s.Dprod(z)[2]/s.c  # placeholder, rescaled below
        # use coordinates: x=sqrt(z), s_sig=sqrt(S2); phi_a=x*A, phi_v=x*B/c  (so D=phi_a*phi_v = z A B / c)
        x=np.sqrt(z); A,B=s.Dprod(z)[1],s.Dprod(z)[2]
        pa=x*A; pv=x*B/s.c
        Dp=(lambda zz:(np.sqrt(zz)**2*s.Dprod(zz)[1]*s.Dprod(zz)[2]/s.c))
        dD=(Dp(z+e)-Dp(z-e))/(2*e)*2*x
        sig2=1.0/ (pa*pv)   # = S2*? ; equals S2 up to the c factor
        ov_v=s.c*(-2*pv/(sig2*dD))  # factor c verified against iid/PCA closed form
        ov_a=-2*pa/(sig2*dD)
        return z,ov_v,ov_a
def pca(c,th):
    """PCA of Y alone, Sigma=I, spike th/sigma^2: right-vector alignment^2"""
    return 0.0 if th<=np.sqrt(c) else (1-c/th**2)/(1+c/th)
