from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, KeepTogether, ListFlowable, ListItem, HRFlowable)
D="/usr/share/fonts/truetype/dejavu/"
for n,f in [("Serif","DejaVuSerif.ttf"),("Serif-B","DejaVuSerif-Bold.ttf"),("Serif-I","DejaVuSerif-Italic.ttf"),
            ("Serif-BI","DejaVuSerif-BoldItalic.ttf"),("Sans","DejaVuSans.ttf"),("Sans-B","DejaVuSans-Bold.ttf"),
            ("Sans-I","DejaVuSans-Oblique.ttf")]:
    pdfmetrics.registerFont(TTFont(n,D+f))
pdfmetrics.registerFontFamily("Serif",normal="Serif",bold="Serif-B",italic="Serif-I",boldItalic="Serif-BI")
pdfmetrics.registerFontFamily("Sans",normal="Sans",bold="Sans-B",italic="Sans-I",boldItalic="Sans-B")

INK=colors.HexColor("#23272e"); TEAL=colors.HexColor("#1B6E8C"); GREY=colors.HexColor("#6b717b"); RULE=colors.HexColor("#c9cdd3")
PALE=colors.HexColor("#eef4f7")
W,H=A4; M=2.3*cm; CW=W-2*M

title=ParagraphStyle("t",fontName="Serif-B",fontSize=25,leading=30,textColor=INK,spaceAfter=14)
body=ParagraphStyle("b",fontName="Serif",fontSize=10,leading=15.6,textColor=INK,spaceAfter=8.5,alignment=TA_LEFT)
lead=ParagraphStyle("l",parent=body,fontSize=11.4,leading=17.5,spaceAfter=0)
h2=ParagraphStyle("h2",fontName="Sans-B",fontSize=14,leading=18,textColor=TEAL,spaceBefore=16,spaceAfter=7,keepWithNext=1)
cap=ParagraphStyle("cap",fontName="Sans-B",fontSize=8.6,leading=11.5,textColor=INK,spaceAfter=3,keepWithNext=1)
src=ParagraphStyle("s",fontName="Sans",fontSize=7.6,leading=10.5,textColor=GREY,spaceAfter=10)
cell=ParagraphStyle("c",fontName="Sans",fontSize=8.4,leading=11,textColor=INK)
cellh=ParagraphStyle("ch",parent=cell,fontName="Sans-B")
cellr=ParagraphStyle("cr",parent=cell,alignment=2)
cellhr=ParagraphStyle("chr",parent=cellh,alignment=2)
bul=ParagraphStyle("bu",parent=body,spaceAfter=3,leftIndent=0)

def P(t,s=body): return Paragraph(t,s)
def link(url,txt): return f'<a href="{url}" color="#1B6E8C"><u>{txt}</u></a>'
def fig(path,ratio,title_,source):
    w=CW*0.92; h=w*ratio
    im=Image(path,width=w,height=h); im.hAlign="CENTER"
    return KeepTogether([P(title_,cap),im,Spacer(1,3),P(source,src)])
def table(rows,cols,right=()):
    data=[]
    for i,r in enumerate(rows):
        data.append([Paragraph(c,(cellhr if j in right else cellh) if i==0 else (cellr if j in right else cell)) for j,c in enumerate(r)])
    t=Table(data,colWidths=cols,repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,0),0.9,INK),("LINEBELOW",(0,0),(-1,0),0.6,INK),
        ("LINEBELOW",(0,1),(-1,-2),0.25,RULE),("LINEBELOW",(0,-1),(-1,-1),0.9,INK),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),4.5),("BOTTOMPADDING",(0,0),(-1,-1),4.5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))
    return t

s=[]
s.append(P("Con un final de foto finish, Brasil elige presidente",title))
s.append(P("Por Lic. Santiago Martínez Soler",ParagraphStyle("by",fontName="Sans",fontSize=9.5,leading=13,textColor=GREY,spaceAfter=12)))
callout=Table([[P("<b>Nuestra predicción para el domingo 4 de octubre:</b> Lula tiene alrededor de <b>45%</b> de probabilidad de terminar primero en la primera vuelta, Flávio Bolsonaro alrededor de <b>53%</b> y los demás candidatos 2%. No es una estimación de cuántos votos sacará cada uno: es la probabilidad de que cada uno gane la primera vuelta, es decir, de que termine con más votos que el resto.",lead)]],colWidths=[CW])
callout.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PALE),("LINEBEFORE",(0,0),(0,-1),3,TEAL),
    ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),("TOPPADDING",(0,0),(-1,-1),11),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
s+= [callout,Spacer(1,12)]
s.append(P("Es una carrera pareja: dentro de lo razonable, la probabilidad de Lula va de 35 a 55%. Las encuestas, el mercado y el historial de errores de las encuestas describen lo mismo: pareja hasta el final."))
s.append(P("Una vez más, como en 2018 y en 2022, un Bolsonaro es el principal rival de Lula y del PT. En 2018 Jair Bolsonaro ganó la primera vuelta con 46,0% de los votos válidos contra 29,3% de Fernando Haddad, el candidato que reemplazó a un Lula preso e inhabilitado, y luego ganó el balotaje. En 2022 Lula lo superó en primera vuelta por 48,4% a 43,2% y ganó el balotaje por 50,9% a 49,1%."))
s.append(P("En 2026 el rival es Flávio, senador e hijo de Jair, porque el expresidente está inhabilitado para competir."))

s.append(P("Qué dicen las encuestas",h2))
s.append(P("Lula lidera por unos 3 o 4 puntos, pero las consultoras (los institutos de encuestas, como se los llama en Brasil) muestran resultados muy distintos entre sí. Si se toma la última encuesta de cada una de las 12 consultoras que midieron en septiembre y se deja de lado a los indecisos, Lula promedia 44,4% y Flávio 40,8%, una ventaja de 3,7 puntos. Según la consultora, la ventaja de Lula va de −2,1 (Flávio arriba) a 11,7 puntos."))
s.append(P("Gerp y Futura tienen a Flávio adelante y Palver lo tiene empatado. En el otro extremo, CNT/MDA (11,7 puntos a favor de Lula) y Alfa (7,9) son las que más lo favorecen. Los sitios que promedian encuestas daban a fines de septiembre una ventaja de Lula de entre 0,7 y 5 puntos: UOL 4,2, PollingData 2,6, Plano Político 2,4, BBC y CartaCapital 2, Poll+Trend 0,7 y ABC Dados 5."))
s.append(fig("figuras/c1_consultoras.png",3.3/6.6,"La ventaja de Lula depende de a quién se le pregunte","Última encuesta de septiembre de cada consultora, sin contar indecisos. Fuente: encuestas registradas en Wikipedia; cálculo propio."))
s.append(P("Datos: "+link("https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026","Wikipedia, encuestas de la elección presidencial 2026")+".",src))

s.append(P("Qué dice el mercado",h2))
s.append(P("<b>Polymarket</b> es una plataforma de internet donde la gente apuesta dinero real sobre hechos futuros. Cada apuesta cuesta entre 0 y 100 centavos de dólar y paga un dólar si el hecho ocurre, así que su precio se lee como la probabilidad que el público le asigna. Sobre Brasil hay dos apuestas distintas y a fines de septiembre daban señales opuestas: Lula era favorito para ganar la primera vuelta y Flávio era favorito para ganar la presidencia."))
s.append(KeepTogether([table([["Mercado","Lula","Flávio","Dinero apostado"],
  [link("https://polymarket.com/event/brazil-presidential-election-first-round-winner","Primera vuelta: quién obtiene más votos"),"70%","31%","US$ 560 mil"],
  [link("https://polymarket.com/event/brazil-presidential-election","Presidencia (incluye balotaje)"),"41,5%","58%","US$ 157 millones"]],
  [CW*0.46,CW*0.14,CW*0.14,CW*0.26],right=(1,2,3)),Spacer(1,9)]))
s.append(P("Precios leídos el 1 de octubre (primera vuelta) y el 29 de septiembre (presidencia). Para que ambas cosas sean ciertas, Flávio tendría que ganar cerca de la mitad de los balotajes en los que llegue segundo. Además, el mercado de la primera vuelta mueve poco dinero, así que su precio es el menos confiable de los dos."))

s.append(P("El voto por región",h2))
s.append(P("La ventaja de Lula depende del Nordeste, pero el resultado lo define el Sudeste. En la primera vuelta de 2022 Lula sacó 67,2% de los votos válidos (sin contar blancos ni nulos) en el Nordeste, una región que reúne al 27,7% de los votantes. Eso le dio 11,1 puntos de ventaja, y el resto del país se los descontó casi por la mitad: 5,8 puntos en contra, hasta quedar en la ventaja nacional de 5,3."))
s.append(KeepTogether([table([["Región (2022, primera vuelta)","Lula","Bolsonaro","Peso en el total de votos","Puntos de ventaja (o desventaja) para Lula"],
  ["Nordeste","67,2%","27,0%","27,7%","+11,1"],["Sudeste","42,9%","47,9%","41,8%","−2,1"],["Sur","36,9%","55,2%","14,8%","−2,7"],
  ["Centro-Oeste","37,9%","54,1%","7,5%","−1,2"],["Norte","47,3%","45,5%","8,3%","+0,1"]],
  [CW*0.25,CW*0.13,CW*0.15,CW*0.2,CW*0.27],right=(1,2,3,4)),Spacer(1,4),
  P("Datos de 2022: "+link("https://dadosabertos.tse.jus.br","TSE, resultados por municipio y zona")+".",src)]))
s.append(P("Las encuestas regionales de 2026 muestran un patrón parecido, con un Nordeste algo menos favorable a Lula: le suma entre 8,1 y 8,6 puntos (contra 11,1 en 2022) y el resto del país le resta entre 3,6 y 4,8 (contra 5,8). Son cortes de Datafolha y Quaest de la segunda quincena de septiembre."))
s.append(fig("figuras/c2_regiones.png",2.7/6.6,"El Nordeste le da a Lula menos ventaja que en 2022","Puntos que cada zona aporta a la ventaja nacional de Lula. Fuentes: TSE (2022); Datafolha y Quaest, septiembre de 2026."))
s.append(P("El Sudeste, con 42 de cada 100 votantes, es donde más pesa un error de las encuestas: si se equivocan 5 puntos ahí, la ventaja nacional cambia 2,1 puntos; en el Nordeste cambia 1,35, en el Sur 0,7 y en el Norte y el Centro-Oeste 0,4."))

s.append(P("Cómo se hizo el estudio y qué encontramos",h2))
s.append(P("Lo más importante que encontramos no salió de un modelo sofisticado, sino de mirar cuánto se equivocaron las encuestas en el pasado: en Brasil y en el resto de la región, el que lidera las encuestas suele llegar a la elección con menos ventaja de la que tenía."))
s.append(P("Para llegar a esa conclusión hicimos tres cosas. Primero, comparamos las encuestas de la última semana con los resultados reales de 19 elecciones presidenciales: seis primeras vueltas de Brasil (2002, 2006, 2010, 2014, 2018 y 2022) y trece de otros países latinoamericanos, entre ellos Argentina, México, Ecuador, Chile, Honduras, Perú, Colombia y Venezuela. Los datos vienen de una base académica internacional (Jennings y Wlezien, <i>Nature Human Behaviour</i>, 2018) y de las tablas de encuestas de Wikipedia. Dejamos afuera Costa Rica y Bolivia 2025, donde candidatos poco conocidos dieron sorpresas que no se parecen al caso brasileño."))
s.append(P("Segundo, probamos si sumar otras señales mejoraba la predicción: el precio de las apuestas, las visitas a Wikipedia y lo que se dice en YouTube. Evaluamos cada método en nueve elecciones recientes de la región (2023 a 2026), sacando una por vez para ver cómo le habría ido a predecirla sin conocerla. El precio de las apuestas combinado con las encuestas funcionó mejor que cada uno por separado; Wikipedia y YouTube no aportaron nada útil."))
s.append(P("Tercero, medimos los sesgos de las encuestas:",ParagraphStyle("x",parent=body,spaceAfter=4,keepWithNext=1)))
items=["En la región, el líder de las encuestas perdió ventaja en 8 de 13 elecciones, en promedio unos 3,5 puntos.",
"En Brasil, las encuestas le dieron al PT más ventaja de la que tuvo en las seis primeras vueltas. Hasta 2014 la diferencia fue de unos 10 puntos; en 2018 y 2022, de unos 3.",
"En 2022 Lula estuvo bien medido, pero Bolsonaro salió unos 4 puntos por encima de lo que decían las encuestas. La última de Ipec le daba a Lula 14 puntos de ventaja; la real fue de 5,2.",
"No encontramos que las encuestas subestimen sistemáticamente al candidato que viene creciendo al final."]
s.append(ListFlowable([ListItem(P(t,bul),leftIndent=14,bulletColor=TEAL) for t in items],bulletType="bullet",start="•",leftIndent=14,bulletFontSize=10))
s.append(Spacer(1,8))
s.append(fig("figuras/c3_sesgo_brasil.png",2.5/6.6,"Hasta 2014 las encuestas le daban al PT unos 10 puntos de más","Cuánto mejor le iba al PT en las encuestas que en las urnas, en la primera vuelta (puntos). Fuentes: base Jennings y Wlezien (2002 a 2010); Wikipedia (2014, 2018, 2022); TSE."))
s.append(P("Son pocas elecciones y las consultoras pueden haber cambiado sus métodos desde entonces, así que estos sesgos indican un riesgo, no una regla."))

s.append(P("La predicción",h2))
s.append(P("La predicción final: Lula tiene alrededor de 45% de probabilidad de terminar primero, Flávio Bolsonaro alrededor de 53% y los demás candidatos 2%. El rango razonable para Lula va de 35 a 55%. No es un porcentaje de votos: es la probabilidad de que cada uno gane la primera vuelta."))
s.append(P("Hoy las encuestas le dan a Lula una ventaja de unos 3,7 puntos. Cuánto vale esa ventaja depende de si las encuestas se equivocan como en el pasado:",ParagraphStyle("y",parent=body,keepWithNext=1)))
s.append(fig("figuras/c4_escenarios.png",2.5/6.6,"Con el error de otras elecciones, la ventaja de Lula se achica o se da vuelta","Probabilidad de que Lula quede primero según cuánto se equivoquen las encuestas. Cálculo propio."))
s.append(P("La cifra de 45% queda por debajo del 70% que da Polymarket para Lula en el mercado de primera vuelta. Todavía no pudimos medir cuánto se equivocan las encuestas en cada región, así que la predicción no ajusta por región. Con una ventaja de 3 o 4 puntos, un error como los del pasado alcanza para dar vuelta el resultado en cualquiera de los dos sentidos."))

def footer(c,doc):
    c.saveState(); c.setFont("Sans",7.5); c.setFillColor(GREY)
    c.drawString(M,1.3*cm,"Con un final de foto finish, Brasil elige presidente")
    c.drawRightString(W-M,1.3*cm,f"{doc.page}")
    c.setStrokeColor(RULE); c.setLineWidth(0.4); c.line(M,1.75*cm,W-M,1.75*cm); c.restoreState()
doc=BaseDocTemplate("articulo_brasil_2026.pdf",pagesize=A4,leftMargin=M,rightMargin=M,topMargin=2.1*cm,bottomMargin=2.3*cm,
                    title="Con un final de foto finish, Brasil elige presidente",author="Lic. Santiago Martínez Soler",subject="Brasil 2026: predicción de la primera vuelta")
doc.addPageTemplates([PageTemplate(id="p",frames=[Frame(M,2.3*cm,CW,H-4.4*cm,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer)])
doc.build(s)
print("pdf ok")
