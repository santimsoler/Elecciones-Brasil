import numpy as np, pandas as pd
# (encuesta t7, encuesta t21 o None, resultado real votos validos) por candidato
D = {
"Argentina 2023": {
 "Milei": (34.6,37.2,29.99), "Massa": (30.4,30.5,36.78), "Bullrich": (26.1,26.2,23.81)},
"Mexico 2024": {
 "Sheinbaum": (51.0,50.8,61.18), "Galvez": (31.8,33.8,28.11), "Maynez": (11.3,9.5,10.57)},
"Ecuador 2025": {  # solo los dos con resultado
 "Noboa": (38.4,36.3,44.17), "Gonzalez": (33.9,38.3,44.00)},
"Bolivia 2025": {
 "Doria Medina": (22.2,23.0,19.69), "Quiroga": (21.5,21.5,26.70), "Reyes Villa": (8.7,8.0,6.75),
 "Rodriguez": (7.1,7.0,8.51), "Paz": (7.9,6.0,32.06), "Del Castillo": (2.0,2.0,3.17)},
"Chile 2025": {
 "Jara": (28.8,28.0,27), "Kast": (19.8,22.4,24), "Matthei": (14.3,14.8,12), "Kaiser": (15.8,13.6,14), "Parisi": (9.7,9.9,20)},
"Honduras 2025": {
 "Nasralla": (26.0,None,39.55), "Asfura": (20.0,None,40.26), "Moncada": (16.0,None,19.20)},
"Costa Rica 2026": {
 "Fernandez": (41.0,40.5,48.53), "Ramos": (6.9,7.5,33.65), "Dobles": (4.6,3.2,4.91),
 "Robles": (3.4,3.7,3.76), "Alvarado": (3.1,4.6,2.19)},
"Peru 2026": {
 "Fujimori": (14.8,11.0,17.19), "Lopez Aliaga": (8.5,10.0,11.91), "Sanchez": (5.0,5.0,12.04),
 "Nieto": (4.0,5.0,10.98), "Belmont": (6.0,2.0,10.15), "Alvarez": (9.5,5.0,7.93),
 "Lopez Chau": (4.9,5.0,7.30), "Perez Tello": (3.3,2.0,3.41)},
"Colombia 2026": {
 "Cepeda": (40.1,None,40.90), "De la Espriella": (32.1,None,43.75), "Valencia": (16.7,None,6.92)},
}
rows=[]
for el, c in D.items():
    p7=np.array([v[0] for v in c.values()]); r=np.array([v[2] for v in c.values()])
    sp=p7/p7.sum(); sr=r/r.sum()
    has21=all(v[1] is not None for v in c.values())
    p21=np.array([v[1] if v[1] is not None else np.nan for v in c.values()])
    tr = np.log(p7/p7.sum()) - np.log(p21/p21.sum()) if has21 else np.full(len(c),np.nan)
    rank=(-sp).argsort().argsort()+1
    for i,(n,v) in enumerate(c.items()):
        rows.append(dict(eleccion=el,cand=n,poll=sp[i]*100,real=sr[i]*100,err=(sr[i]-sp[i])*100,
                         rank=rank[i],trend=tr[i],logratio=np.log(sr[i]/sp[i])))
df=pd.DataFrame(rows)
pd.set_option("display.width",200)
print(df.round(2).to_string(index=False))
print()
# 1) lider de la encuesta vs resultado
lid=df[df["rank"]==1]
print("LIDER de la encuesta: error medio %.1f pts, ganó más que la encuesta en %d/%d"%(lid.err.mean(),(lid.err>0).sum(),len(lid)))
print(lid[["eleccion","cand","poll","real","err"]].round(1).to_string(index=False))
# 2) regresion log(real/poll) ~ log(poll): mean reversion
x=np.log(df.poll/100); y=df.logratio
b,a=np.polyfit(x,y,1); print("\nlogratio = %.2f + %.2f*log(poll)  (b<0: los chicos suben, los grandes bajan)"%(a,b))
# 3) tendencia
d2=df.dropna(subset=["trend"]); b2,a2=np.polyfit(d2.trend,d2.logratio,1)
print("logratio = %.2f + %.2f*tendencia (n=%d)"%(a2,b2,len(d2)))
# 4) mediana error segun rank
print("\nerror medio por puesto en la encuesta:")
print(df.groupby("rank").err.agg(["mean","count"]).round(1).to_string())
df.to_csv("errores.csv",index=False)
