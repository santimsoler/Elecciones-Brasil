"""Resultados reales por región de la primera vuelta 2018 y 2022 (TSE, datos abiertos).

Descarga los CSV de votación por candidato, municipio y zona, suma los votos por región y
calcula el margen de la izquierda (Lula / Haddad) contra Bolsonaro y cuánto aporta cada región
al margen nacional. Imprime un chequeo contra los totales oficiales: el voto en el exterior
(UF 'ZZ') no está en ninguna región, por eso hay una diferencia de ~0,6%.
"""
import io, zipfile, requests
import pandas as pd

URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{}.zip"

REGION = {}
for uf in "MA PI CE RN PB PE AL SE BA".split(): REGION[uf] = "Nordeste"
for uf in "AC AP AM PA RO RR TO".split():       REGION[uf] = "Norte"
for uf in "DF GO MT MS".split():                REGION[uf] = "Centro-Oeste"
for uf in "ES MG RJ SP".split():                REGION[uf] = "Sudeste"
for uf in "PR RS SC".split():                   REGION[uf] = "Sul"

# totales oficiales (votos válidos, 1ª vuelta) para chequear la descarga
CHEQUEO = {
    2022: {"LULA": 57_259_504, "BOLSONARO": 51_072_345},
    2018: {"BOLSONARO": 49_277_010, "HADDAD": 31_342_051},
}

def bajar(anio):
    print(f"Descargando {anio}...")
    r = requests.get(URL.format(anio), timeout=300, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    partes = []
    for nombre in z.namelist():
        if not nombre.lower().endswith(".csv"):
            continue
        with z.open(nombre) as f:
            df = pd.read_csv(
                f, sep=";", encoding="latin-1", dtype=str,
                usecols=lambda c: c in {"NR_TURNO", "DS_CARGO", "SG_UF",
                                        "NM_URNA_CANDIDATO", "QT_VOTOS_NOMINAIS"},
            )
        df = df[(df["DS_CARGO"].str.upper() == "PRESIDENTE") & (df["NR_TURNO"] == "1")]
        if len(df):
            partes.append(df)
    if not partes:
        raise RuntimeError("No encontré filas de Presidente en el zip; revisar estructura del archivo.")
    d = pd.concat(partes, ignore_index=True)
    d["votos"] = pd.to_numeric(d["QT_VOTOS_NOMINAIS"], errors="coerce").fillna(0)
    return d.drop_duplicates()

def por_region(d):
    d = d[d["SG_UF"].isin(REGION)].copy()
    d["region"] = d["SG_UF"].map(REGION)
    return d.pivot_table(index="NM_URNA_CANDIDATO", columns="region",
                         values="votos", aggfunc="sum", fill_value=0)

resultados = {}
for anio in (2022, 2018):
    try:
        d = bajar(anio)
    except Exception as e:
        print(f"[{anio}] falló la descarga: {e}")
        continue

    tot = d.groupby("NM_URNA_CANDIDATO")["votos"].sum()
    print(f"\n--- Chequeo {anio} (total nacional, votos válidos) ---")
    for k, oficial in CHEQUEO[anio].items():
        m = tot[tot.index.str.upper().str.contains(k)]
        if len(m):
            print(f"{m.index[0]}: {int(m.iloc[0]):,} vs oficial {oficial:,}  (dif {int(m.iloc[0]) - oficial:+,})")
        else:
            print(f"{k}: no encontrado en NM_URNA_CANDIDATO")

    t = por_region(d)
    t["Total"] = t.sum(axis=1)
    t = t.sort_values("Total", ascending=False)
    top = t.head(4)
    validos_region = t.drop(columns="Total").sum()
    pct = (t.drop(columns="Total") / validos_region * 100).loc[top.index]
    peso = validos_region / validos_region.sum() * 100

    print(f"\n=== {anio}: % de votos válidos por región (top 4 candidatos) ===")
    print(pct.round(1).to_string())
    print("\nPeso de cada región en el total de votos válidos (%):")
    print(peso.round(1).to_string())

    izq = [i for i in t.index if any(k in i.upper() for k in ("LULA", "HADDAD"))]
    der = [i for i in t.index if "BOLSONARO" in i.upper()]
    if izq and der:
        margen = (t.loc[izq[0], validos_region.index] - t.loc[der[0], validos_region.index]) / validos_region * 100
        contrib = margen * peso / 100
        out = pd.DataFrame({"margen_pts": margen.round(1),
                            "peso_%": peso.round(1),
                            "aporte_al_margen_nac": contrib.round(2)})
        print(f"\nMargen {izq[0]} - {der[0]} por región (puntos de válidos) y aporte al margen nacional:")
        print(out.to_string())
        print(f"Margen nacional (sin exterior): {contrib.sum():.2f} pts")

    resultados[anio] = {"tabla": t, "pct": pct, "peso": peso}
