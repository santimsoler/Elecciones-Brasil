# Brasil 2026: predicción de la primera vuelta

Análisis y artículo sobre la primera vuelta de las elecciones presidenciales de Brasil (4 de octubre de 2026):
qué dicen las encuestas, qué dice el mercado (Polymarket), cómo se reparte el voto por región y cuánto suelen
equivocarse las encuestas en Brasil y en América Latina.

**Predicción:** Lula ~45% de probabilidad de terminar primero en la primera vuelta, Flávio Bolsonaro ~53%, otros ~2%
(rango razonable para Lula: 35 a 55%). Es la probabilidad de ganar la primera vuelta, no un porcentaje de votos.

El artículo completo está en [`articulo/articulo_brasil_2026.pdf`](articulo/articulo_brasil_2026.pdf).

## Qué se encontró

- Promedio de la última encuesta de cada una de las 12 consultoras de septiembre: Lula 44,4%, Flávio 40,8% (sin indecisos), ventaja de 3,7 puntos.
- En las 6 primeras vueltas de Brasil analizadas (2002 a 2022) las encuestas le dieron al PT más ventaja de la que tuvo: unos 10 puntos hasta 2014 y unos 3 en 2018 y 2022.
- En 13 elecciones del resto de la región, el líder de las encuestas perdió ventaja en 8, en promedio 3,5 puntos.
- Sumar Wikipedia o YouTube (embeddings de titulares) no mejoró las predicciones; el precio del mercado combinado con las encuestas funcionó mejor que cada uno por separado.
- La ventaja de Lula depende del Nordeste; el Sudeste (42% de los votantes) es donde más pesa un error de las encuestas.

## Estructura

```
articulo/                 PDF del artículo, scripts de gráficos y de armado del PDF, figuras
data/                     encuestas 2014, 2018, 2022 y 2026, agregadores, mercado, resultados por región, errores por elección
src/modelo_electoral.py   modelo (logit condicional) con Polymarket, encuestas, Wikipedia y embeddings, validado dejando una elección afuera
src/promedio_encuestas_2026.py   promedio por consultora y probabilidad según el sesgo supuesto
src/regional_tse.py       resultados reales por región 2018 y 2022 (TSE, datos abiertos)
src/analisis/             errores de las encuestas: 2023-2026, Brasil 2014-2018, base Jennings y Wlezien, y el análisis conjunto
```

## Cómo correrlo

```bash
pip install -r requirements.txt

# promedio de encuestas 2026 y probabilidades según el sesgo
cd src && python promedio_encuestas_2026.py

# errores de las encuestas y análisis conjunto (región + Brasil)
cd analisis && python pool_errores.py

# resultados reales por región (descarga ~ decenas de MB del TSE)
cd .. && python regional_tse.py

# regenerar gráficos y PDF
cd ../articulo && python make_figures.py && python build_pdf.py
```

El modelo (`src/modelo_electoral.py`) usa la API de Polymarket y Wikipedia. Para los embeddings de YouTube hace falta una
clave de la YouTube Data API v3 en la variable de entorno `YOUTUBE_API_KEY` (el repo no incluye ninguna clave).
Si no está, corre sin embeddings.

## Datos y límites

- Las encuestas 2014, 2018, 2022 y 2026 vienen de las tablas de Wikipedia (pt), 2014 y 2018 cargadas a mano.
- Los resultados reales por región 2018 y 2022 vienen del TSE (`regional_tse.py`). El voto en el exterior no está en ninguna región.
- La base de Jennings y Wlezien (*Nature Human Behaviour*, 2018) no se incluye por tamaño; `src/analisis/base_jennings_wlezien.py` la procesa si se la descarga aparte.
- Los precios de Polymarket son una lectura del 29 de septiembre y del 1 de octubre de 2026 (`data/mercado_polymarket_2026-09-29.csv`).
- Son pocas elecciones: los sesgos históricos indican un riesgo, no una regla. No se pudo medir el error de las encuestas por región, así que la predicción no ajusta por región.
- En `modelo_electoral.py`, la elección de Argentina 2023 se entrena con la primera vuelta y el favorito de Polymarket para "ganar la presidencia" (Milei) difiere del ganador de la primera vuelta (Massa); conviene revisar esa etiqueta antes de reusar el modelo.
