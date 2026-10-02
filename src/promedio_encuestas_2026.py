"""Promedio de las encuestas de septiembre de 2026 por consultora (Lula vs Flávio).

Toma la última encuesta de cada consultora, deja de lado a los indecisos
(normaliza a los candidatos listados) y calcula la ventaja de Lula.
"""
import pandas as pd
from math import erf, sqrt

d = pd.read_csv("../data/encuestas_brasil_2026_septiembre.csv")
d["consultora"] = d.consultora.str.lower()
total = 100 - d.indecisos_abstenciones
d["lula_sin_indecisos"] = d.lula / total * 100
d["flavio_sin_indecisos"] = d.flavio / total * 100
d["ventaja_lula"] = d.lula_sin_indecisos - d.flavio_sin_indecisos

ultima = d.drop_duplicates("consultora", keep="first")  # el archivo viene ordenado de más reciente a más antigua
print(ultima[["consultora", "fechas_2026", "lula_sin_indecisos", "flavio_sin_indecisos", "ventaja_lula"]].round(1).to_string(index=False))
print(f"\nConsultoras: {len(ultima)}")
print(f"Lula {ultima.lula_sin_indecisos.mean():.1f}%  Flávio {ultima.flavio_sin_indecisos.mean():.1f}%  ventaja {ultima.ventaja_lula.mean():.1f} puntos")

# Probabilidad de que Lula quede primero si la ventaja actual se achica en `sesgo` puntos,
# con un error residual normal de desvío `sd` (ver el artículo para los supuestos de sesgo).
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
base = ultima.ventaja_lula.mean()
print("\nP(Lula primero) según sesgo restado y desvío del error:")
for sesgo in (0, 3, 3.3, 4.4):
    print(f"sesgo {sesgo:>4}: " + "  ".join(f"sd={sd}: {Phi((base - sesgo) / sd):.0%}" for sd in (4, 5, 6)))
