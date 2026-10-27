
import numpy as np, math
from math import comb
import sys; sys.path.insert(0,'crit')
from core import *

def Mmax(R,k0,G):
    """largest m<=G-1 with m/(k(m+R^2 k))<=k0, k=G-m  (Lemma 1)."""
    best=0
    for m in range(1,G):
        k=G-m
        if m/(k*(m+R*R*k))<=k0*(1+1e-12): best=m
        else: break
    return best

def F_star(G,n,Pmax,s,M):
    """max over block-size sequences (m_t>=0), sum<=P, every window of s+1 consecutive blocks has total <= M of
    sum_t [C(S_t,n)-C(S_t-m_t,n)], S_t=m_t+...+m_{t+s}.  Returns array F[P] for P=0..Pmax (monotone)."""
    # DP over t; state=(last s block sizes tuple), value[budget]
    from collections import defaultdict
    NEG=-1
    T=2*Pmax+s+2
    # state: tuple of previous s sizes (m_{t-s},..,m_{t-1}); we add m_t and collect term for index t-s (needs m_{t-s..t})
    init=tuple([0]*s)
    cur={init:np.zeros(Pmax+1)}   # value[b]=best value using budget exactly <= b (monotone)
    for t in range(T):
        nxt={}
        for st,val in cur.items():
            ssum=sum(st)
            for m in range(0,M-ssum+1):
                # window blocks (t-s .. t): total S = ssum + m; term for block t-s = C(S,n)-C(S-m_{t-s},n)
                S=ssum+m
                first=st[0] if s>0 else m
                if s==0: term=comb(S,n)
                else: term=comb(S,n)-comb(S-first,n)
                ns=st[1:]+(m,) if s>0 else ()
                # budget shift
                if m==0: nv=val+term
                else:
                    nv=np.full(Pmax+1,-1e18); nv[m:]=val[:Pmax+1-m]+term
                if ns in nxt: nxt[ns]=np.maximum(nxt[ns],nv)
                else: nxt[ns]=nv
        cur=nxt
    # flush: remaining terms for blocks in last s positions (as if followed by zeros)
    best=np.full(Pmax+1,-1e18)
    for st,val in cur.items():
        # state st = last s sizes; blocks followed by zeros: remaining terms
        extra=0; arr=list(st)
        for i in range(len(arr)):
            S=sum(arr[i:]); extra+=comb(S,n)-comb(S-arr[i],n)
        best=np.maximum(best,val+extra)
    return np.maximum.accumulate(best)

def block_bound(G,n,c,k0,s=1,cache={}):
    f=n/G; delta=(n-1)/(c*math.sqrt(1-f))
    if delta>=1: return None
    r=(1+delta)/(1-delta)
    R=r**((s+1)/s)
    M=Mmax(R,k0,G)
    key=(G,n,s,M)
    if key not in cache: cache[key]=F_star(G,n,G-1,s,M)
    F=cache[key]
    tot=max(F[a]+F[min(G-a,G-1)] for a in range(0,G))
    return tot/comb(G,n), M, r

def cU_block(G,n,k0,alpha=.1,s_list=(1,2)):
    f=n/G; c0=(n-1)/math.sqrt(1-f)
    best=None
    for s in s_list:
        lo=c0*1.0001; hi=c0*400
        b=block_bound(G,n,hi,k0,s)
        if b is None or b[0]>alpha: continue
        for _ in range(40):
            mid=math.sqrt(lo*hi)
            bb=block_bound(G,n,mid,k0,s)
            if bb is not None and bb[0]<=alpha: hi=mid
            else: lo=mid
        if best is None or hi<best[0]: best=(hi,s)
    return best
