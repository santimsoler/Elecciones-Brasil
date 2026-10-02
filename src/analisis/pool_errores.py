"""Error del margen del líder de las encuestas y probabilidad de que Lula quede primero.

Error = margen real - margen de las encuestas (puntos de votos válidos, última semana).
Negativo: el líder de las encuestas llegó a la elección con menos ventaja de la medida.

- 2023-2026: se calcula desde el diccionario D de errores_latam_2023_2026.py
  (se excluyen Costa Rica y Bolivia 2025: sorpresas de candidatos fragmentados).
- 2002-2014 y otras elecciones de la región: salidas de base_jennings_wlezien.py
  y errores_brasil_2014_2018.py (constantes abajo, con su origen).
- Brasil 2018 y 2022: errores_brasil_2014_2018.py y la tabla de encuestas 2022.
"""
import numpy as np
from math import erf, sqrt
exec(open("errores_latam_2023_2026.py").read().split("rows=[]")[0])   # trae el diccionario D

# --- 2023-2026 (sin Costa Rica ni Bolivia) ---
otros = {}
for el, c in D.items():
    if el in ("Costa Rica 2026", "Bolivia 2025"):
        continue
    names = list(c); p7 = np.array([c[n][0] for n in names]); r = np.array([c[n][2] for n in names])
    poll_valid = p7 / p7.sum() * r.sum()
    i = np.argsort(-p7)[:2]
    pm = poll_valid[i[0]] - poll_valid[i[1]]
    rm = r[i[0]] - r[i[1]]
    otros[el] = rm - pm

# --- otras elecciones de la región (base Jennings y Wlezien, primera vuelta, última semana) ---
otros.update({"Mexico 2012": -11.8, "Peru 2006": 2.3, "Peru 2011": -0.2,
              "Venezuela 2006": 6.0, "Venezuela 2013": -12.4, "Argentina 2011": 1.2})

# --- Brasil, primera vuelta: error del margen del PT (negativo = el PT terminó con menos ventaja) ---
brasil = {"2002": -10.4, "2006": -8.7, "2010": -10.8,   # base Jennings y Wlezien
          "2014": -10.3,                                # Dilma-Aécio, últimas 4 encuestas (errores_brasil_2014_2018.py)
          "2018": -2.6,                                 # Haddad-Bolsonaro, últimas 3 encuestas
          "2022": -3.3}                                 # Lula-Bolsonaro, promedio de la última semana

def resumen(nombre, e, base):
    e = np.array(e, dtype=float)
    emp = ((base + e) > 0).mean()
    normal = 0.5 * (1 + erf(((base + e.mean()) / e.std(ddof=1)) / sqrt(2)))
    print(f"{nombre:<28} n={len(e):>2}  media {e.mean():5.1f}  desvío {e.std(ddof=1):4.1f}  P(Lula primero): empírico {emp:.2f}, normal {normal:.2f}")

base = 3.7   # ventaja actual de Lula (promedio de las 12 consultoras, ver promedio_encuestas_2026.py)
o = list(otros.values()); b = list(brasil.values())
print(f"Ventaja actual de Lula: {base} puntos\n")
resumen("Resto de la región", o, base)
resumen("Brasil 2002-2022", b, base)
resumen("Brasil 2014-2022", [brasil["2014"], brasil["2018"], brasil["2022"]], base)
resumen("Brasil 2018 y 2022", [brasil["2018"], brasil["2022"]], base)
resumen("Región + Brasil", o + b, base)
print(f"\nEl líder perdió ventaja en {sum(v < 0 for v in o)} de {len(o)} elecciones del resto de la región")
