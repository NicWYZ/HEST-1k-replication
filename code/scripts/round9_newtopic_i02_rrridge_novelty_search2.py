import requests,time,csv,re,urllib.parse,xml.etree.ElementTree as ET
Q=["reduced rank ridge regression asymptotics","reduced rank regression random matrix singular vector high-dimensional","ridge regression multiple responses low rank coefficient phase transition","principal component regression eigenvector overlap","hidden variable multivariate regression nuisance factor","spiked separable covariance outlier singular vectors","canonical correlation analysis high-dimensional singular vectors random matrix","signal plus noise matrix general covariance outlier singular value ridge"]
rows=[];c=[]
for q in Q:
    u="http://export.arxiv.org/api/query?search_query="+urllib.parse.quote("all:"+q)+"&max_results=8"
    try:
        r=requests.get(u,headers={"User-Agent":"lit-check/1.0"},timeout=40)
        if r.status_code==429: time.sleep(20); r=requests.get(u,timeout=40)
        root=ET.fromstring(r.text);ns={"a":"http://www.w3.org/2005/Atom"}
        es=root.findall("a:entry",ns); st="ok"
        for e in es: c.append(["arxiv",q,re.sub(r"\s+"," ",e.find("a:title",ns).text.strip()),e.find("a:id",ns).text,e.find("a:published",ns).text[:4]])
    except Exception as e: es=[];st="FAIL"
    rows.append(["arxiv",q,st,len(es)]);print(q,st,len(es),flush=True);time.sleep(6)
csv.writer(open("q2.csv","w")).writerows(rows);csv.writer(open("c2.csv","w")).writerows(c)
