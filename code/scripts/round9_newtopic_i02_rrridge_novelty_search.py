import requests, time, csv, re, urllib.parse, xml.etree.ElementTree as ET
UA={"User-Agent":"research-lit-check/1.0"}
Q=[
 ("arxiv",'all:"reduced rank regression" AND all:ridge AND all:"high-dimensional"'),
 ("arxiv",'all:"reduced-rank ridge" AND all:asymptotic'),
 ("arxiv",'all:"reduced rank" AND all:"random matrix" AND all:"singular vector"'),
 ("arxiv",'all:"multi-output ridge" AND all:"deterministic equivalent"'),
 ("arxiv",'all:"ridge regression" AND all:"multiple responses" AND all:"proportional asymptotics"'),
 ("arxiv",'all:"spiked" AND all:"separable covariance" AND all:"singular vectors"'),
 ("arxiv",'all:"signal-plus-noise" AND all:"general noise covariance" AND all:"outlier singular"'),
 ("arxiv",'all:"reduced-rank regression" AND all:"phase transition"'),
 ("arxiv",'all:"canonical correlation" AND all:ridge AND all:"high-dimensional" AND all:"phase transition"'),
 ("arxiv",'all:"partial least squares" AND all:"high-dimensional" AND all:"spiked" AND all:"overlap"'),
 ("arxiv",'all:"principal component regression" AND all:"eigenvector overlap"'),
 ("arxiv",'all:"reduced rank regression" AND all:"hidden" AND all:"nuisance" AND all:factor'),
 ("arxiv",'all:"reduced rank regression" AND all:"group" AND all:"random effects" AND all:"high-dimensional"'),
 ("arxiv",'all:"ridge" AND all:"singular value" AND all:"fitted values" AND all:"spike" AND all:"multivariate regression"'),
 ("arxiv",'all:"regularized reduced rank regression" AND all:"random matrix"'),
 ("arxiv",'all:"matrix denoising" AND all:"ridge" AND all:"hat matrix"'),
 ("crossref","ridge reduced-rank regression proportional asymptotics subspace alignment"),
 ("crossref","spiked separable covariance matrices principal components"),
 ("crossref","reduced rank regression phase transition singular vectors high dimension"),
 ("crossref","multivariate ridge regression random matrix theory risk many responses"),
 ("s2","reduced rank ridge regression high-dimensional asymptotics"),
 ("s2","ridge regression low-rank coefficient matrix random matrix theory alignment"),
]
rows=[];cands=[]
def arx(q):
    u="http://export.arxiv.org/api/query?search_query="+urllib.parse.quote(q)+"&max_results=8"
    for k in range(4):
        r=requests.get(u,headers=UA,timeout=40)
        if r.status_code==429: time.sleep(10*2**k); continue
        r.raise_for_status(); break
    ns={"a":"http://www.w3.org/2005/Atom"}
    root=ET.fromstring(r.text); out=[]
    for e in root.findall("a:entry",ns):
        out.append((re.sub(r"\s+"," ",e.find("a:title",ns).text.strip()),e.find("a:id",ns).text,e.find("a:published",ns).text[:4],re.sub(r"\s+"," ",e.find("a:summary",ns).text.strip())[:300]))
    return out
def cr(q):
    r=requests.get("https://api.crossref.org/works",params={"query":q,"rows":8},headers=UA,timeout=40); r.raise_for_status()
    return [((i.get("title") or [""])[0],i.get("DOI",""),str((i.get("issued",{}).get("date-parts",[[""]])[0] or [""])[0]),"") for i in r.json()["message"]["items"]]
def s2(q):
    for k in range(3):
        r=requests.get("https://api.semanticscholar.org/graph/v1/paper/search",params={"query":q,"limit":8,"fields":"title,year,externalIds,abstract"},headers=UA,timeout=40)
        if r.status_code==429: time.sleep(15*2**k); continue
        r.raise_for_status(); d=r.json().get("data",[])
        return [(p["title"],str(p.get("externalIds",{}).get("DOI") or p.get("externalIds",{}).get("ArXiv","")),str(p.get("year")),(p.get("abstract") or "")[:300]) for p in d]
    raise RuntimeError("429")
for src,q in Q:
    try:
        res={"arxiv":arx,"crossref":cr,"s2":s2}[src](q); st="ok"
    except Exception as e:
        res=[];st="FAIL "+str(e)[:60]
    rows.append([src,q,st,len(res)])
    for t in res: cands.append([src,q,t[0],t[1],t[2],t[3]])
    print(src,st,len(res),flush=True)
    time.sleep(6)
csv.writer(open("f_RRRIDGE_novelty_queries.csv","w")).writerows([["source","query","status","n_results"]]+rows)
csv.writer(open("f_RRRIDGE_novelty_raw_hits.csv","w")).writerows([["source","query","title","id","year","abstract_snip"]]+cands)
