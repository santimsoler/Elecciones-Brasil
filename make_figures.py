import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ["DejaVuSans.ttf","DejaVuSans-Bold.ttf"]:
    fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/"+f)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.edgecolor":"#8a8f98","axes.labelcolor":"#3a3f47","xtick.color":"#3a3f47","ytick.color":"#3a3f47"})
TEAL="#1B6E8C"; ORNG="#D9822B"; GREY="#8a8f98"; INK="#23272e"

# 1) ventaja de Lula por consultora (ult. encuesta de septiembre, sin indecisos)
d=[("CNT/MDA",11.7),("Alfa",7.9),("Quaest",5.9),("Nexus/BTG",5.3),("Datafolha",4.3),("Real Time Big Data",4.3),
   ("Vox Brasil",3.5),("AtlasIntel",3.2),("PoderData/Aya",2.1),("Palver",0.0),("Gerp",-2.1),("Futura",-2.1)]
d=d[::-1]
fig,ax=plt.subplots(figsize=(6.6,3.3),dpi=200)
cols=[TEAL if v>0 else (GREY if v==0 else ORNG) for _,v in d]
ax.barh([n for n,_ in d],[v for _,v in d],color=cols,height=0.62)
for i,(n,v) in enumerate(d):
    ax.text(v+(0.25 if v>=0 else -0.25),i,f"{v:+.1f}".replace(".",",").replace("+0,0","0,0").replace("-","\u2212"),va="center",ha="left" if v>=0 else "right",fontsize=8,color=INK,bbox=dict(fc="white",ec="none",pad=0.6),zorder=5)
ax.axvline(0,color=INK,lw=0.8)
ax.axvline(3.7,color=INK,lw=0.8,ls=(0,(3,3)),zorder=1)
ax.text(3.85,-0.95,"promedio: 3,7",fontsize=7.5,color=INK,va="top")
ax.set_xlim(-4.5,13.5); ax.set_ylim(-1.5,len(d)-0.4)
ax.set_xlabel("Ventaja de Lula sobre Flávio (puntos, sin contar indecisos)")
ax.tick_params(length=0); ax.grid(axis="x",color="#e4e6ea",lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("figuras/c1_consultoras.png"); plt.close(fig)

# 2) aporte regional a la ventaja de Lula: 2022 real vs encuestas 2026
fig,ax=plt.subplots(figsize=(6.6,2.7),dpi=200)
import numpy as np
x=np.arange(2); w=0.34
r22=[11.1,-5.8]; lo=[8.1,-4.8]; hi=[8.6,-3.6]; mid=[(a+b)/2 for a,b in zip(lo,hi)]
b1=ax.bar(x-w/2,r22,w,color=GREY,label="Resultado real 2022")
b2=ax.bar(x+w/2,mid,w,color=TEAL,label="Encuestas 2026")
ax.errorbar(x+w/2,mid,yerr=[[m-l for m,l in zip(mid,lo)],[h-m for m,h in zip(mid,hi)]],fmt="none",ecolor=INK,capsize=3,lw=1)
for xi,v in zip(x-w/2,r22): ax.text(xi,v+(0.5 if v>0 else -0.5),f"{v:+.1f}".replace(".",",").replace("-","\u2212"),ha="center",va="bottom" if v>0 else "top",fontsize=8,color=INK)
for xi,v,l,h in zip(x+w/2,mid,lo,hi):
    top=max(l,h) if v>0 else min(l,h)
    ax.text(xi,top+(0.55 if v>0 else -0.55),(f"{l:+.1f} a {h:+.1f}" if v>0 else f"{h:+.1f} a {l:+.1f}").replace(".",",").replace("-","\u2212"),ha="center",va="bottom" if v>0 else "top",fontsize=8,color=INK)
ax.axhline(0,color=INK,lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(["Nordeste","Resto del país"])
ax.set_ylim(-9,14.5); ax.set_ylabel("Puntos que aporta a la ventaja nacional")
ax.legend(frameon=False,loc="upper right",fontsize=8); ax.tick_params(axis="x",length=0)
ax.grid(axis="y",color="#e4e6ea",lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("figuras/c2_regiones.png"); plt.close(fig)

# 3) cuanto mejor le iba al PT en las encuestas que en las urnas
yrs=["2002","2006","2010","2014","2018","2022"]; v=[10.4,8.7,10.8,10.3,2.6,3.3]
fig,ax=plt.subplots(figsize=(6.6,2.5),dpi=200)
ax.bar(yrs,v,color=[ORNG]*4+[TEAL]*2,width=0.6)
for i,val in enumerate(v): ax.text(i,val+0.3,f"{val:.1f}".replace(".",","),ha="center",fontsize=8,color=INK)
ax.set_ylim(0,13); ax.set_ylabel("Puntos"); ax.tick_params(axis="x",length=0)
ax.grid(axis="y",color="#e4e6ea",lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("figuras/c3_sesgo_brasil.png"); plt.close(fig)

# 4) probabilidad de que Lula quede primero segun supuesto de error
esc=[("Las encuestas no se equivocan",77,77),("Error de Brasil 2018 y 2022",55,55),("Error promedio de América Latina",42,51),("Error de Brasil 2002-2022",14,33)]
esc=esc[::-1]
fig,ax=plt.subplots(figsize=(6.6,2.5),dpi=200)
for i,(n,a,b) in enumerate(esc):
    if a==b: ax.plot([a],[i],"o",color=TEAL,ms=7); lab=f"~{a}%"
    else: ax.plot([a,b],[i,i],"-",color=TEAL,lw=6,solid_capstyle="round"); lab=f"{a} a {b}%"
    ax.text(max(a,b)+2.5,i,lab,va="center",fontsize=8,color=INK,bbox=dict(fc="white",ec="none",pad=0.8),zorder=5)
ax.axvline(45,color=INK,lw=0.9,ls=(0,(3,3))); ax.text(45.6,3.55,"nuestra estimación: 45%",fontsize=7.5,color=INK,va="bottom")
ax.set_yticks(range(len(esc))); ax.set_yticklabels([n for n,_,_ in esc]); ax.set_xlim(0,100); ax.set_ylim(-0.6,4.1)
ax.set_xlabel("Probabilidad de que Lula termine primero (%)"); ax.tick_params(axis="y",length=0)
ax.grid(axis="x",color="#e4e6ea",lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("figuras/c4_escenarios.png"); plt.close(fig)
print("ok")
