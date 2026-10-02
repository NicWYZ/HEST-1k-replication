import subprocess, sys, os, time, json, resource, hashlib, platform, socket
D='/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts'
S=f'{D}/round4_ppi_q2_theorem_sim.py'
env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', OMP_NUM_THREADS='1', PYTHONPATH=D)
md5=lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
import numpy, pandas
for g in (6,12):
    out=f'{os.getcwd()}/theorem_v3/GL{g}'; os.makedirs(out,exist_ok=True)
    json.dump({"writer":"claude-science","project_id":"proj_3a4e23273fb6","frame_id":"ab674f84-25c3-4e5f-9a25-e0dbd7583e34","track":"ppi","plan":"","note":"Q2 theorem sim v3 (per-replicate lambda), local","host":socket.gethostname(),"created_at":time.strftime('%Y-%m-%dT%H:%M:%S+00:00',time.gmtime())},open(f'{out}/_provenance.json','w'))
    cmd=[sys.executable,S,'--G-L-grid',str(g),'--reps','2000','--out-dir',out]
    t=time.time(); r0=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    p=subprocess.run(cmd,env=env,stdout=open(f'{out}/stdout.txt','w'),stderr=open(f'{out}/stderr.txt','w'))
    w=time.time()-t; rss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    with open(f'{out}/PROVENANCE.txt','w') as f:
        f.write(f"host: {socket.gethostname()} local {platform.platform()}\nrepo: /Users/nicolaszhang/HEST-1k-replication-PPI, branch round4-ppi (lead states commit aa71028; read from .git/HEAD ref only)\n")
        for s in ('round4_ppi_q2_theorem_sim.py','round4_ppi_estimator.py','round4_ppi_q1_sim.py'): f.write(f"{md5(f'{D}/{s}')}  {s}\n")
        f.write(f"command: {' '.join(cmd)}\nenv: PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 OMP_NUM_THREADS=1 PYTHONPATH={D}\npython {sys.version.split()[0]} numpy {numpy.__version__} pandas {pandas.__version__}\nscript exit code: {p.returncode}\nwall_s: {w:.1f}\nmax_rss_children_bytes: {rss}\n")
    print(g,p.returncode,w,flush=True)
