import json, time, os, re, hashlib, unicodedata, html
import numpy as np
import pandas as pd
import requests
from urllib.parse import quote
from scipy.optimize import minimize

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
YT_SEARCH = "https://www.googleapis.com/youtube/v3/search"
HEADERS = {"User-Agent": "analisis-electoral/0.8"}
CACHE = "cache_modelo"
os.makedirs(CACHE, exist_ok=True)

DIAS_ANTES = 7       # corte principal: días antes de la primera vuelta
DIAS_TENDENCIA = 14  # el precio "anterior" se toma DIAS_TENDENCIA días antes del corte (t-21)
TOP_N = 8
MAX_STALE = 10       # días máximos de antigüedad aceptados para un precio
P_FALTANTE = 0.005   # precio asignado si no hay dato de mercado
P_PISO = 0.001       # piso para evitar log(0)
E_PISO = 0.5         # piso (en %) para encuestas y valor por defecto de candidatos sin encuesta

# Embeddings de titulares de YouTube (necesita una API key gratuita de YouTube Data API v3).
# Cada búsqueda cuesta 100 unidades de cuota; con 10.000 por día alcanzan ~100 búsquedas.
USAR_EMBEDDINGS = True
EMB_VENTANA_DIAS = 28
EMB_MIN_TITULOS = 5
MODELO_EMB = "paraphrase-multilingual-MiniLM-L12-v2"

# slug -> (fecha de la primera vuelta, idioma de Wikipedia/YouTube)  (VERIFICAR fechas)
ENTRENAMIENTO = {
    "argentina-presidential-election-who-will-win": ("2023-10-22", "es"),
    "mexican-presidential-election-who-will-win": ("2024-06-02", "es"),
    "ecuador-presidential-election": ("2025-02-09", "es"),
    "bolivia-presidential-election-1st-round-winner": ("2025-08-17", "es"),
    "chile-presidential-election-1st-round-winner": ("2025-11-16", "es"),
    "honduras-presidential-election": ("2025-11-30", "es"),
    "costa-rica-presidential-election": ("2026-02-01", "es"),
    "peru-presidential-election-first-round-winner": ("2026-04-12", "es"),
    "colombia-presidential-election-1st-round-winner": ("2026-05-31", "es"),
}
PREDICCION = ("brazil-presidential-election-first-round-winner", "2026-10-04", "pt")

# Correcciones manuales de artículos de Wikipedia (None = no usar Wikipedia para ese candidato)
TITULOS_MANUALES = {
    "Roberto Sánchez Palomino": "Roberto_Sánchez_Palomino",
    "Mario Rivera Callejas": None,
}

# Encuestas cargadas a mano (promedios aproximados de encuestas publicadas, en % de intención de voto).
# t21 = ~21 días antes de la primera vuelta, t7 = ~7 días antes. t21 = None si no hay dato confiable.
# Los nombres se emparejan por palabras en común con los de Polymarket.
ENCUESTAS = {
    # Promedios de ~10 encuestas (t21 es de ~29 días antes) y de encuestas del ~14-oct (t7)
    "argentina-presidential-election-who-will-win": {
        "t21": {"Javier Milei": 37.2, "Sergio Massa": 30.5, "Patricia Bullrich": 26.2},
        "t7": {"Javier Milei": 34.6, "Sergio Massa": 30.4, "Patricia Bullrich": 26.1},
    },
    "mexican-presidential-election-who-will-win": {
        "t21": {"Claudia Sheinbaum": 50.8, "Xóchitl Gálvez": 33.8, "Jorge Álvarez Máynez": 9.5},
        "t7": {"Claudia Sheinbaum": 51.0, "Xóchitl Gálvez": 31.8, "Jorge Álvarez Máynez": 11.3},
    },
    # Aproximado: la tabla fuente era confusa; Jalkh, Topić y Cucalón sin dato (0,3-0,5)
    "ecuador-presidential-election": {
        "t21": {"Daniel Noboa": 36.3, "Luisa González": 38.3, "Gustavo Jalkh": 0.3,
                "Jan Topić": 0.5, "Henry Cucalón": 0.5},
        "t7": {"Daniel Noboa": 38.4, "Luisa González": 33.9, "Gustavo Jalkh": 0.3,
               "Jan Topić": 0.5, "Henry Cucalón": 0.5},
    },
    "bolivia-presidential-election-1st-round-winner": {
        "t21": {"Samuel Doria Medina": 23.0, "Jorge Quiroga": 21.5, "Manfred Reyes Villa": 8.0,
                "Andrónico Rodríguez": 7.0, "Rodrigo Paz": 6.0, "Eduardo del Castillo": 2.0},
        "t7": {"Samuel Doria Medina": 22.2, "Jorge Quiroga": 21.5, "Manfred Reyes Villa": 8.7,
               "Andrónico Rodríguez": 7.1, "Rodrigo Paz": 7.9, "Eduardo del Castillo": 2.0},
    },
    "chile-presidential-election-1st-round-winner": {
        "t21": {"Jeannette Jara": 28.0, "José Antonio Kast": 22.4, "Evelyn Matthei": 14.8,
                "Johannes Kaiser": 13.6, "Franco Parisi": 9.9, "Marco Enríquez-Ominami": 1.0,
                "Eduardo Artés": 0.7, "Alberto Undurraga": 0.5},
        "t7": {"Jeannette Jara": 28.8, "José Antonio Kast": 19.8, "Evelyn Matthei": 14.3,
               "Johannes Kaiser": 15.8, "Franco Parisi": 9.7, "Marco Enríquez-Ominami": 1.4,
               "Eduardo Artés": 0.7, "Alberto Undurraga": 0.5},
    },
    # Poco confiable: encuestas contradictorias y solo hay la última de Le Vote (30-oct, ~31 días antes)
    "honduras-presidential-election": {
        "t21": None,
        "t7": {"Salvador Nasralla": 26.0, "Nasry Asfura": 20.0, "Rixi Moncada": 16.0,
               "Mario Rivera Callejas": 1.0, "Nelson Ávila": 1.0},
    },
    "costa-rica-presidential-election": {
        "t21": {"Laura Fernández": 40.5, "Álvaro Ramos": 7.5, "Claudia Dobles": 3.2,
                "Ariel Robles": 3.7, "Fabricio Alvarado": 4.6, "José Aguilar": 2.0,
                "Juan Carlos Hidalgo": 1.0, "Claudio Alpízar": 0.5},
        "t7": {"Laura Fernández": 41.0, "Álvaro Ramos": 6.9, "Claudia Dobles": 4.6,
               "Ariel Robles": 3.4, "Fabricio Alvarado": 3.1, "José Aguilar": 3.0,
               "Juan Carlos Hidalgo": 1.0, "Claudio Alpízar": 0.5},
    },
    "peru-presidential-election-first-round-winner": {
        "t21": {"Keiko Fujimori": 11.0, "Rafael López Aliaga": 10.0, "Roberto Sánchez": 5.0,
                "Jorge Nieto": 5.0, "Ricardo Belmont": 2.0, "Carlos Álvarez": 5.0,
                "Alfonso López Chau": 5.0, "Marisol Pérez Tello": 2.0},
        "t7": {"Keiko Fujimori": 14.8, "Rafael López Aliaga": 8.5, "Roberto Sánchez": 5.0,
               "Jorge Nieto": 4.0, "Ricardo Belmont": 6.0, "Carlos Álvarez": 9.5,
               "Alfonso López Chau": 4.9, "Marisol Pérez Tello": 3.3},
    },
    # t21 sin dato confiable (las encuestas de ~10-may no eran comparables)
    "colombia-presidential-election-1st-round-winner": {
        "t21": None,
        "t7": {"Iván Cepeda": 40.1, "Abelardo de la Espriella": 32.1, "Paloma Valencia": 16.7,
               "Claudia López": 1.6, "Vicky Dávila": 0.5, "Mauricio Cárdenas": 0.5,
               "Enrique Peñalosa": 0.5, "Luis Gilberto Murillo": 0.5},
    },
    # Quaest 10-13 sep (t21) y promedio Datafolha 22-24 sep + Quaest 17-20 sep (t7)
    "brazil-presidential-election-first-round-winner": {
        "t21": {"Lula": 36.0, "Flávio Bolsonaro": 31.0, "Ronaldo Caiado": 4.0, "Zema": 1.0,
                "Renan Santos": 4.0, "Augusto Cury": 7.0, "Pablo Marçal": 0.5,
                "Rui Costa Pimenta": 0.5},
        "t7": {"Lula": 38.5, "Flávio Bolsonaro": 34.5, "Ronaldo Caiado": 4.0, "Zema": 1.0,
               "Renan Santos": 3.0, "Augusto Cury": 5.5, "Pablo Marçal": 0.5,
               "Rui Costa Pimenta": 0.5},
    },
}

PLACEHOLDER = re.compile(r"^(Person|Candidate|Other)\b", re.I)
STOP = {"de", "la", "del", "los", "las", "da", "do", "dos", "el", "escritor"}


# ---------- utilidades de red con caché ----------
def _sin_clave(params):
    return {k: v for k, v in (params or {}).items() if k != "key"}


def get(url, params=None, reintentos=6, quiet=False):
    clave = hashlib.md5((url + json.dumps(_sin_clave(params), sort_keys=True)).encode()).hexdigest()
    ruta = os.path.join(CACHE, clave + ".json")
    if os.path.exists(ruta):
        with open(ruta) as f:
            return json.load(f)
    espera = 2
    for _ in range(reintentos):
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            with open(ruta, "w") as f:
                json.dump(data, f)
            time.sleep(0.3)
            return data
        if r.status_code == 429:
            espera = int(r.headers.get("Retry-After", espera))
            print(f"  429, espero {espera}s")
            time.sleep(espera)
            espera = min(espera * 2, 60)
            continue
        if not quiet:
            print(f"  HTTP {r.status_code} en {url} {_sin_clave(params)}")
        return None
    return None


def parsear(x):
    return json.loads(x) if isinstance(x, str) else x


# ---------- Polymarket ----------
def historial(token, corte):
    def a_df(data):
        h = (data or {}).get("history") or []
        if not h:
            return pd.DataFrame(columns=["t", "p"])
        d = pd.DataFrame(h)
        d["t"] = pd.to_datetime(d["t"], unit="s", utc=True)
        return d.sort_values("t")

    df = a_df(get(f"{CLOB}/prices-history", {"market": token, "interval": "max", "fidelity": 1440}, quiet=True))
    cerca = df[(df["t"] <= corte) & (df["t"] >= corte - pd.Timedelta(days=MAX_STALE))]
    if cerca.empty:  # respaldo: ventana angosta alrededor del corte
        ts0 = int((corte - pd.Timedelta(days=12)).timestamp())
        ts1 = int((corte + pd.Timedelta(days=1)).timestamp())
        df = a_df(get(f"{CLOB}/prices-history",
                      {"market": token, "startTs": ts0, "endTs": ts1, "fidelity": 60}, quiet=True))
    return df


def precio_en_corte(token, corte):
    h = historial(token, corte)
    previo = h[h["t"] <= corte]
    if previo.empty:
        return None
    if (corte - previo["t"].iloc[-1]).days > MAX_STALE:
        return None
    return float(previo["p"].iloc[-1])


# ---------- nombres ----------
def limpiar(label):
    s = re.sub(r"\(.*?\)", "", label)
    s = re.sub(r"[“”\"].*?[“”\"]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalizar(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def tokens(s):
    return {t for t in normalizar(s).split() if len(t) >= 3 and t not in STOP}


def titulo_valido(label, titulo):
    tl, tt = tokens(limpiar(label)), tokens(titulo.replace("_", " "))
    if not tl:
        return True
    return len(tl & tt) >= min(2, len(tl))


def buscar_encuesta(label, dic, default=E_PISO):
    """Busca en dic el candidato con más palabras en común con label."""
    if not dic:
        return default
    tl = tokens(limpiar(label))
    mejor, mejor_n = None, 0
    for k, v in dic.items():
        n = len(tl & tokens(k))
        if n > mejor_n:
            mejor, mejor_n = v, n
    necesario = min(2, len(tl)) if tl else 1
    return mejor if (mejor is not None and mejor_n >= necesario) else default


# ---------- Wikipedia ----------
def resolver_titulo(label, lang):
    if label in TITULOS_MANUALES:
        return TITULOS_MANUALES[label]
    data = get(f"https://{lang}.wikipedia.org/w/api.php",
               {"action": "query", "list": "search", "srsearch": limpiar(label),
                "srlimit": 1, "format": "json"})
    res = ((data or {}).get("query") or {}).get("search") or []
    if not res:
        return None
    titulo = res[0]["title"].replace(" ", "_")
    if not titulo_valido(label, titulo):
        print(f"  [aviso] artículo descartado por no coincidir: {label} -> {titulo}")
        return None
    return titulo


def wiki_serie(titulo, lang, ini, fin):
    if not titulo:
        return {}
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"{lang}.wikipedia/all-access/user/{quote(titulo, safe='')}/daily/"
           f"{ini:%Y%m%d}/{fin:%Y%m%d}")
    data = get(url, quiet=True)
    if not data:
        return {}
    return {pd.to_datetime(x["timestamp"][:8]).date(): x["views"] for x in data["items"]}


# ---------- embeddings de titulares de YouTube ----------
def api_key_youtube():
    k = os.environ.get("YOUTUBE_API_KEY")
    if k:
        return k
    try:
        from google.colab import userdata  # en Colab: Secretos -> YOUTUBE_API_KEY
        return userdata.get("YOUTUBE_API_KEY")
    except Exception:
        return None


def titulos_youtube(label, lang, ini, fin, key):
    nombre = limpiar(label)
    params = {"part": "snippet", "q": f'"{nombre}"', "type": "video", "maxResults": 50,
              "publishedAfter": f"{ini}T00:00:00Z", "publishedBefore": f"{fin}T23:59:59Z",
              "order": "relevance", "relevanceLanguage": lang, "key": key}
    data = get(YT_SEARCH, params)
    items = (data or {}).get("items") or []
    toks = tokens(nombre)
    clave = max(toks, key=len) if toks else None
    out = []
    for it in items:
        t = html.unescape(it["snippet"]["title"])
        if clave is None or clave in normalizar(t):
            out.append(t)
    return out


_MODELO = None
ANCLAS_POS = [
    "el candidato lidera las encuestas y gana apoyo",
    "el candidato es el favorito y crece en intención de voto",
    "o candidato lidera as pesquisas e ganha apoio",
]
ANCLAS_NEG = [
    "escándalo y denuncia de corrupción contra el candidato",
    "el candidato cae en las encuestas y pierde apoyo",
    "o candidato perde apoio e enfrenta escândalo",
]


def modelo_emb():
    global _MODELO
    if _MODELO is None:
        from sentence_transformers import SentenceTransformer
        _MODELO = SentenceTransformer(MODELO_EMB)
    return _MODELO


def puntaje_emb(titulos):
    """Puntaje zero-shot: cercanía a 'gana apoyo' menos cercanía a 'escándalo/pierde apoyo'."""
    if len(titulos) < EMB_MIN_TITULOS:
        return np.nan
    m = modelo_emb()
    E = m.encode(titulos, normalize_embeddings=True, show_progress_bar=False)
    P = m.encode(ANCLAS_POS, normalize_embeddings=True, show_progress_bar=False)
    N = m.encode(ANCLAS_NEG, normalize_embeddings=True, show_progress_bar=False)
    s = (E @ P.T).max(axis=1) - (E @ N.T).max(axis=1)
    return float(s.mean())


# ---------- dataset por elección ----------
def cargar_eleccion(slug, fecha, lang, yt_key=None):
    ev = get(f"{GAMMA}/events", {"slug": slug})
    if not ev:
        print(f"No se encontró {slug}")
        return None
    ev = ev[0] if isinstance(ev, list) else ev
    corte = pd.Timestamp(fecha, tz="UTC") - pd.Timedelta(days=DIAS_ANTES)
    corte_prev = corte - pd.Timedelta(days=DIAS_TENDENCIA)
    c = corte.date()
    b0, b1 = c - pd.Timedelta(days=34), c - pd.Timedelta(days=7)
    r0 = c - pd.Timedelta(days=6)
    e0 = c - pd.Timedelta(days=EMB_VENTANA_DIAS - 1)

    mercados = [m for m in ev.get("markets", [])
                if float(m.get("volume") or 0) > 0
                and not PLACEHOLDER.match(m.get("groupItemTitle") or "")]
    mercados = sorted(mercados, key=lambda m: float(m.get("volume") or 0), reverse=True)[:TOP_N]

    filas = []
    for m in mercados:
        try:
            outcomes, tokens_id, precios = parsear(m["outcomes"]), parsear(m["clobTokenIds"]), parsear(m["outcomePrices"])
        except Exception:
            continue
        if "Yes" not in outcomes:
            continue
        i = outcomes.index("Yes")
        label = m.get("groupItemTitle") or m.get("question")
        p7 = precio_en_corte(tokens_id[i], corte)
        p21 = precio_en_corte(tokens_id[i], corte_prev)
        if p7 is None:
            print(f"  [aviso] {slug[:30]} | sin precio válido a t-7 para {label}")
        titulo = resolver_titulo(label, lang)
        serie = wiki_serie(titulo, lang, b0, c)
        if serie:
            v_base = sum(v for d, v in serie.items() if b0 <= d <= b1)
            v_rec = sum(v for d, v in serie.items() if r0 <= d <= c)
        else:
            print(f"  [aviso] sin vistas de Wikipedia para {label} -> {titulo}")
            v_base, v_rec = np.nan, np.nan
        emb = np.nan
        if yt_key:
            tit = titulos_youtube(label, lang, e0, c, yt_key)
            emb = puntaje_emb(tit)
            if np.isnan(emb):
                print(f"  [aviso] pocos titulares de YouTube para {label} ({len(tit)})")
        filas.append({
            "eleccion": slug, "candidato": label, "articulo": titulo,
            "p_mkt": p7, "p_mkt21": p21,
            "v_base": v_base, "v_rec": v_rec, "emb_raw": emb,
            "gano": float(precios[i]) > 0.99,
        })
    return pd.DataFrame(filas)


def log_share(x):
    x = pd.Series(x).astype(float).clip(lower=E_PISO)
    return np.log(x / x.sum())


def armar_features(d, usar_enc):
    d = d.copy()
    n = len(d)

    # mercado: nivel y tendencia
    p7 = d["p_mkt"].fillna(P_FALTANTE).clip(lower=P_PISO)
    pn7 = p7 / p7.sum()
    d["f_mkt"] = np.log(pn7)
    if d["p_mkt21"].notna().sum() >= max(2, n // 2):
        p21 = d["p_mkt21"].fillna(P_FALTANTE).clip(lower=P_PISO)
        pn21 = p21 / p21.sum()
        d["f_mkt_mom"] = np.clip(np.log(pn7) - np.log(pn21), -3, 3)
    else:
        d["f_mkt_mom"] = 0.0

    # Wikipedia: nivel y tendencia (los sin dato reciben la mediana de la elección)
    med_b = d["v_base"].median()
    med_r = d["v_rec"].median()
    sb = d["v_base"].fillna(med_b if pd.notna(med_b) else 0) + 1
    sr = d["v_rec"].fillna(med_r if pd.notna(med_r) else 0) + 1
    d["f_wiki"] = np.log(sb / sb.sum())
    d["f_wiki_mom"] = np.clip(np.log(sr / sr.sum()) - d["f_wiki"], -3, 3)

    # encuestas: nivel y tendencia
    if usar_enc:
        cfg = ENCUESTAS.get(d["eleccion"].iloc[0], {})
        e7 = d["candidato"].map(lambda c: buscar_encuesta(c, cfg.get("t7")))
        l7 = log_share(e7.values)
        d["f_enc"] = l7.values
        if cfg.get("t21"):
            e21 = d["candidato"].map(lambda c: buscar_encuesta(c, cfg["t21"]))
            d["f_enc_mom"] = np.clip(l7.values - log_share(e21.values).values, -3, 3)
        else:
            d["f_enc_mom"] = 0.0

    # embeddings: puntaje estandarizado dentro de la elección
    v = d["emb_raw"].astype(float)
    if v.notna().sum() >= 2 and v.std(skipna=True) > 0:
        z = (v - v.mean(skipna=True)) / v.std(skipna=True)
        d["f_emb"] = z.fillna(0.0).clip(-2, 2)
    else:
        d["f_emb"] = 0.0
    return d


# ---------- modelo: elección discreta penalizada hacia "confiar en el mercado" ----------
def nll(beta, grupos, lam, prior):
    total = 0.0
    for X, y in grupos:
        s = X @ beta
        s = s - s.max()
        total -= s[y] - np.log(np.exp(s).sum())
    return total + lam * np.sum((beta - prior) ** 2)


def ajustar(grupos, lam, prior):
    return minimize(nll, prior.copy(), args=(grupos, lam, prior), method="BFGS").x


def probs(X, beta):
    s = X @ beta
    e = np.exp(s - s.max())
    return e / e.sum()


def metricas(p, y):
    onehot = np.zeros(len(p))
    onehot[y] = 1
    return {"p_ganador": p[y], "logloss": -np.log(max(p[y], 1e-3)),
            "brier": float(((p - onehot) ** 2).sum()), "acierta": int(np.argmax(p) == y)}


def resumen(filas):
    r = pd.DataFrame(filas)
    return {"logloss": r["logloss"].mean(), "brier": r["brier"].mean(),
            "aciertos": int(r["acierta"].sum()), "p_ganador_medio": r["p_ganador"].mean()}


def prior_de(cols):
    return np.array([1.0 if c == "f_mkt" else 0.0 for c in cols])


def loo(claves, dfs, y_idx, cols, lam):
    prior = prior_de(cols)
    filas = []
    for k in claves:
        train = [(dfs[j][cols].values, y_idx[j]) for j in claves if j != k]
        beta = ajustar(train, lam, prior)
        filas.append(metricas(probs(dfs[k][cols].values, beta), y_idx[k]))
    return resumen(filas)


def main():
    yt_key = api_key_youtube() if USAR_EMBEDDINGS else None
    if USAR_EMBEDDINGS and not yt_key:
        print("[aviso] no hay YOUTUBE_API_KEY: se omiten los embeddings")

    # 1) datos
    data = {}
    for slug, (fecha, lang) in ENTRENAMIENTO.items():
        df = cargar_eleccion(slug, fecha, lang, yt_key)
        if df is not None and not df.empty:
            data[slug] = df
    slug_p, fecha_p, lang_p = PREDICCION
    df_pred = cargar_eleccion(slug_p, fecha_p, lang_p, yt_key)

    print("\n--- Artículos de Wikipedia y encuestas emparejadas (revisar) ---")
    for slug, df in list(data.items()) + [(slug_p, df_pred)]:
        print(f"\n{slug}")
        cfg = ENCUESTAS.get(slug, {})
        tmp = df[["candidato", "articulo"]].copy()
        tmp["enc_t7"] = df["candidato"].map(lambda c: buscar_encuesta(c, cfg.get("t7")))
        print(tmp.to_string(index=False))

    usar_enc = all(s in ENCUESTAS for s in list(ENTRENAMIENTO) + [slug_p])
    usar_emb = bool(yt_key) and all(df["emb_raw"].notna().mean() >= 0.5
                                    for df in list(data.values()) + [df_pred])
    print(f"\nEncuestas incluidas: {usar_enc} | Embeddings incluidos: {usar_emb}")

    dfs, y_idx = {}, {}
    for slug, df in data.items():
        if df["gano"].sum() != 1:
            print(f"[aviso] {slug}: sin ganador único en el top {TOP_N}, se excluye")
            continue
        d = armar_features(df, usar_enc)
        dfs[slug] = d.reset_index(drop=True)
        y_idx[slug] = int(np.where(d["gano"].values)[0][0])
    claves = list(dfs)
    print(f"Elecciones de entrenamiento: {len(claves)}")

    # 2) referencias
    refs = {"uniforme": None, "mercado puro": ["f_mkt"], "wikipedia pura": ["f_wiki"]}
    if usar_enc:
        refs["encuestas puras"] = ["f_enc"]
    if usar_emb:
        refs["embeddings puros"] = ["f_emb"]
    tabla = []
    for nombre, cols in refs.items():
        filas = []
        for k in claves:
            d, y = dfs[k], y_idx[k]
            p = np.ones(len(d)) / len(d) if cols is None else probs(d[cols].values, np.array([1.0]))
            filas.append(metricas(p, y))
        tabla.append({"modelo": nombre, "lambda": "-", **resumen(filas)})

    # 3) ablación: qué agrega cada variable al mercado (una elección afuera)
    conjuntos = {
        "mercado + tendencia mercado": ["f_mkt", "f_mkt_mom"],
        "mercado + wikipedia": ["f_mkt", "f_wiki", "f_wiki_mom"],
    }
    if usar_enc:
        conjuntos["mercado + encuestas"] = ["f_mkt", "f_enc"]
        conjuntos["mercado + tendencia encuestas"] = ["f_mkt", "f_enc_mom"]
        conjuntos["mercado + enc + tend. enc"] = ["f_mkt", "f_enc", "f_enc_mom"]
    if usar_emb:
        conjuntos["mercado + embeddings"] = ["f_mkt", "f_emb"]
    if usar_enc and usar_emb:
        conjuntos["mercado + enc + embeddings"] = ["f_mkt", "f_enc", "f_emb"]
    todo = ["f_mkt", "f_mkt_mom", "f_wiki", "f_wiki_mom"]
    if usar_enc:
        todo += ["f_enc", "f_enc_mom"]
    if usar_emb:
        todo += ["f_emb"]
    conjuntos["todo"] = todo

    mejor = None
    for nombre, cols in conjuntos.items():
        for lam in [2, 10, 20, 50]:
            r = loo(claves, dfs, y_idx, cols, lam)
            tabla.append({"modelo": nombre, "lambda": lam, **r})
            if mejor is None or r["logloss"] < mejor[2]:
                mejor = (nombre, lam, r["logloss"], cols)

    pd.set_option("display.width", 220, "display.max_colwidth", 45)
    print("\n===== VALIDACIÓN (una elección afuera) =====")
    print(pd.DataFrame(tabla).round(3).to_string(index=False))
    base = next(t for t in tabla if t["modelo"] == "mercado puro")
    print(f"\nReferencia mercado puro: logloss {base['logloss']:.3f}, brier {base['brier']:.3f}")
    print(f"Mejor especificación: {mejor[0]} (lambda={mejor[1]}, logloss {mejor[2]:.3f})")
    print("Ojo: elegir la mejor con los mismos datos es optimista.")
    print("Si la mejora contra 'mercado puro' es chica, la variable probablemente no aporta.")

    # 4) ajuste final y predicción
    nombre_m, lam_m, _, cols_m = mejor
    beta = ajustar([(dfs[k][cols_m].values, y_idx[k]) for k in claves], lam_m, prior_de(cols_m))
    print("\nCoeficientes finales:", dict(zip(cols_m, beta.round(3))))

    dp = armar_features(df_pred, usar_enc)
    out = pd.DataFrame({"candidato": dp["candidato"],
                        "mercado": probs(dp[["f_mkt"]].values, np.array([1.0]))})
    if usar_enc:
        out["encuestas"] = probs(dp[["f_enc"]].values, np.array([1.0]))
        cols_me = ["f_mkt", "f_enc"]
        b_me = ajustar([(dfs[k][cols_me].values, y_idx[k]) for k in claves], 10, prior_de(cols_me))
        out["mkt+enc"] = probs(dp[cols_me].values, b_me)
        print("Coeficientes mercado+encuestas (lambda=10):", dict(zip(cols_me, b_me.round(3))))
    out["wikipedia"] = probs(dp[["f_wiki"]].values, np.array([1.0]))
    out["mejor"] = probs(dp[cols_m].values, beta)
    out = out.sort_values("mercado", ascending=False)
    print(f"\n===== {slug_p} | probabilidad de ganar la primera vuelta =====")
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
