import pandas as pd, numpy as np
from math import erf,sqrt
# 2018
c18=['B','H','C','A','M','Am','Me','Al','Bo']
p18=[('Datafolha','05-06/10',[35,22,11,8,4,3,2,2,1]),('Ibope','03-05/10',[35,22,11,8,5,3,2,2,1]),
('Ipespe','03-04/10',[34,23,10,8,5,3,2,1,1]),('CNT/MDA','29-30/09',[31.1,23.8,9.4,5.6,4.8,2.5,1.8,1.4,0.9]),
('Datafolha','27-28/09',[28,22,11,10,7,3,2,3,1]),('Ibope','26-28/09',[31,24,11,8,6,3,2,2,1]),('XP/Ipespe','24-26/09',[29,22,11,8,7,3,2,2,1])]
a18=dict(zip(c18,[46.03,29.28,12.47,4.76,1.00,2.50,1.20,0.80,0.58]))
# 2014
c14=['D','M','A','E','G']
p14=[('Ibope','03-04/10',[40,21,24,1,1]),('Datafolha','03-04/10',[40,22,24,1,1]),('Vox Populi','03-04/10',[41,20,23,1,2]),
('CNT/MDA','02-03/10',[40.6,21.4,24,.8,1.1]),('Datafolha','01-02/10',[40,24,21,1,1]),('Ibope','29/9-01/10',[40,24,19,1,1]),
('Datafolha','29-30/09',[40,25,20,1,1]),('Ibope','27-29/09',[39,25,19,1,1]),('Vox Populi','27-28/09',[40,24,18,1,1]),('CNT/MDA','27-28/09',[40.4,25.2,19.8,.6,1.2])]
a14=dict(zip(c14,[41.59,21.32,33.55,0.75,1.55]))
def run(name,cols,pl,act,pt,rival):
    sa=sum(act.values()); A={k:v/sa*100 for k,v in act.items()}
    am=A[pt]-A[rival]
    print(f'== {name}: real (norm listed) PT {A[pt]:.1f} rival {A[rival]:.1f} margin PT-rival {am:.1f}')
    rows=[]
    for inst,f,v in pl:
        s=sum(v); d={k:x/s*100 for k,x in zip(cols,v)}
        rows.append((inst,f,d[pt],d[rival],d[pt]-d[rival]-am, d[pt]-A[pt], d[rival]-A[rival]))
    df=pd.DataFrame(rows,columns=['inst','f','PT','rival','err_margen','err_PT','err_rival'])
    print(df.round(1).to_string()); 
    print('media todas: err_margen %.1f err_PT %.1f err_rival %.1f'%(df.err_margen.mean(),df.err_PT.mean(),df.err_rival.mean()))
    top=df.head(4 if name=='2018' else 4); print('media 4 ultimas: %.1f'%top.err_margen.mean())
    return df
d18=run('2018',c18,p18,a18,'H','B')
d14=run('2014',c14,p14,a14,'D','A')
print('2022 (previo): err margen medio ult7d +3.3 (media), +4.4 (mediana)')
