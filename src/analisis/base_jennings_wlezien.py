import pandas as pd, numpy as np
import sys
# uso: python base_jennings_wlezien.py LONG_MI_NATURE_20180111.dta   (la base no se incluye en el repo)
d=pd.read_stata(sys.argv[1]) if len(sys.argv)>1 else pd.read_pickle("long.pkl")
p=d[(d.election=="Presidential")].copy()
f=p[(p.daysbeforeED>=1)&(p.daysbeforeED<=7)&p.poll_.notna()&p.vote_.notna()].copy()
key=["country","electionid","round"]
c=f.groupby(key+["partyid"]).agg(poll=("poll_","mean"),vote=("vote_","first"),gov=("gov_","first"),inc=("inc_","first"),
                                n=("poll_","size"),fecha=("elecdate","first"),yr=("yr","first")).reset_index()
rows=[]
LA=["Argentina","Brazil","Chile","Colombia","Ecuador","Mexico","Paraguay","Peru","Venezuela"]
for k,g in c.groupby(key):
    g=g.copy()
    if len(g)<2: continue
    S=g.vote.sum()
    g["pollN"]=g.poll/g.poll.sum()*S            # encuesta normalizada a los puntos de voto de los listados
    g["err"]=g.vote-g.pollN
    g["rank"]=g.pollN.rank(ascending=False,method="first").astype(int)
    top=g.sort_values("pollN",ascending=False).iloc[:2]
    pm=top.pollN.iloc[0]-top.pollN.iloc[1]; rm=top.vote.iloc[0]-top.vote.iloc[1]
    for _,r in g.iterrows():
        rows.append(dict(country=k[0],eid=k[1],round=k[2],yr=r.yr,ncand=len(g),cand=int(r.partyid),poll=r.pollN,vote=r.vote,err=r.err,rank=r["rank"],
                         gov=r.gov,inc=r.inc,lider_margen_enc=pm,lider_margen_real=rm,region="LatAm" if k[0] in LA else "Otros"))
D=pd.DataFrame(rows); D.to_pickle("pres_err.pkl")
E=D.groupby(["country","eid","round"]).first().reset_index()
E["err_margen"]=E.lider_margen_real-E.lider_margen_enc
E["lider_perdio"]=E.lider_margen_real<0
E.to_pickle("pres_elec.pkl")
print("elecciones-ronda presidenciales:",len(E),"| candidatos:",len(D))
print(E.groupby(["region"]).agg(n=("eid","size"),err_margen_medio=("err_margen","mean"),mediana=("err_margen","median"),sd=("err_margen","std"),lider_perdio=("lider_perdio","sum")).round(2).to_string())
print("\npor ronda:"); print(E.groupby(["region","round"]).agg(n=("eid","size"),err_margen=("err_margen","mean"),perdio=("lider_perdio","sum")).round(2).to_string())
print("\nPrimera vuelta con >=3 candidatos:")
E3=E[(E["round"]==1)&(E.ncand>=3)]
print(E3.groupby("region").agg(n=("eid","size"),err_margen=("err_margen","mean"),mediana=("err_margen","median"),sd=("err_margen","std"),perdio=("lider_perdio","sum")).round(2).to_string())
