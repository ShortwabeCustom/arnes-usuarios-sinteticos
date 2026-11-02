"""Build offline reading pages from the report's real, local evidence.
Run with the repository .venv Python after updating fuente-editorial.html or sources.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import re
import yaml
import runpy

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT.parent
ASSETS = ROOT / 'assets/report-reader'
PAGES = ROOT / 'lecturas'
PAGES.mkdir(exist_ok=True)
(ASSETS / 'data').mkdir(exist_ok=True)
MAIN = 'oupwa-pdu-originacion-unica-2-0-pwa-sintetico_2026-10-28-v1.html'
manifest = {}

class CleanHTML(HTMLParser):
    """Keep document semantics, without embedded executable markup or original CSS."""
    allowed = set('div section article aside header footer main h1 h2 h3 h4 h5 h6 p a ul ol li table thead tbody tr td th blockquote strong b em i small span details summary pre code br hr figure figcaption img dl dt dd'.split())
    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'svg', 'canvas', 'nav'):
            self.skip += 1; return
        if self.skip or tag not in self.allowed: return
        safe = []
        for k, v in attrs:
            if k == 'id': safe.append(('data-source-id', v))
            elif k in ('href','src') and not re.match(r'\s*(javascript|data|vbscript):', v, re.I): safe.append((k,v))
            elif k in ('alt','colspan','rowspan','open'): safe.append((k,v or ''))
        self.out.append('<' + tag + ''.join(f' {k}="{escape(v, quote=True)}"' for k,v in safe) + '>')
    def handle_endtag(self, tag):
        if tag in ('script','style','svg','canvas','nav'):
            self.skip = max(0,self.skip-1); return
        if not self.skip and tag in self.allowed and tag not in ('img','br','hr'): self.out.append(f'</{tag}>')
    def handle_data(self, data):
        if not self.skip: self.out.append(escape(data))

def clean(raw):
    p=CleanHTML(); p.feed(raw); return ''.join(p.out)

def add(key,title,kind,description,data,original=None,base=None):
    manifest[key] = dict(title=title,kind=kind,description=description,original=original,
                         base=base or original or MAIN,page=f'lecturas/{key}.html',data=f'assets/report-reader/data/{key}.js')
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    (ASSETS/'data'/f'{key}.js').write_text(f'window.ReportReaderData[{json.dumps(key)}]={payload};\n')
    (PAGES/f'{key}.html').write_text(f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · OU 2.0</title><link rel="icon" href="data:,"><link rel="stylesheet" href="../assets/report-reader/reader.css"><link rel="stylesheet" href="../assets/evidence/evidence.css"></head>
<body class="reader-standalone" data-reader-page="{key}"><noscript><main class="reader-scroll"><h1>{escape(title)}</h1><p>{escape(description)}</p><p>Activa JavaScript para explorar esta lectura y sus evidencias.</p><a href="../{MAIN}">Volver al reporte</a></main></noscript><script src="../assets/report-reader/manifest.js"></script><script src="../assets/evidence/evidence.js"></script><script src="../assets/report-reader/insights.js"></script><script src="../assets/report-reader/reader.js"></script></body></html>''')

ag=json.loads((STUDY/'datos/agregado.json').read_text())
add('datos-agregados','Los resultados, tramo por tramo','aggregate','32 sesiones sintéticas · cuatro perfiles · cuatro tramos · dos corridas por combinación.',ag,'../datos/agregado.json')
for name,title,desc in [('tecnico','Auditoría técnica','Carga, accesibilidad, permisos y retoma en el entorno de pruebas.'),('auditoria','Evaluación heurística asistida por IA','Tres evaluaciones independientes realizadas por modelos de IA. Observaciones consolidadas con criterios de usabilidad; no equivale a una revisión con tres especialistas humanos.')]:
    add(name,title,'json',desc,json.loads((STUDY/f'datos/{name}.json').read_text()),f'../datos/{name}.json')
for file in sorted((STUDY/'datos/sesiones').glob('*.json')):
    data=json.loads(file.read_text())
    add(file.stem,f"{data.get('nombre',data.get('integrante','Perfil'))} · {data.get('tarea','')} · corrida {data.get('corrida','')}",'session','Registro de un perfil sintético. Sus pensamientos no son testimonios de participantes reales.',data,f'../datos/sesiones/{file.name}')
add('sintesis','Síntesis del estudio','json','Hallazgos, interpretación y recomendaciones conservados desde la fuente editorial.',yaml.safe_load((STUDY/'narrativa.yaml').read_text()),'../narrativa.yaml')
add('protocolo','Cómo se diseñó la investigación','markdown','Objetivos, hipótesis, tareas y límites de la segunda medición.',(STUDY/'PROTOCOLO.md').read_text(),'../PROTOCOLO.md')
first=STUDY.parent/'2026-10-22-ou2-descubrimiento/reporte/oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1.md'
add('primera-medicion','La primera medición','markdown','Antecedente del estudio · 22 de octubre de 2026.',first.read_text(),'../../2026-10-22-ou2-descubrimiento/reporte/oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1.md', '../../2026-10-22-ou2-descubrimiento/reporte/oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1.md')
for suffix,title in [('detalle','Detalle completo'),('tablero-anterior','Tablero anterior')]:
    name=MAIN.replace('.html',f'-{suffix}.html')
    raw=(ROOT/name).read_text(); body=re.search(r'<body[^>]*>([\s\S]*?)</body>',raw,re.I).group(1)
    add(suffix,title,'html','Versión de lectura del documento. El archivo original conserva su presentación y sus gráficos interactivos.',clean(body),name)

source=(ROOT/'fuente-editorial.html').read_text()
for section,title in [('recorrido','El camino se completa. La fricción viaja con él.'),('hallazgos','Se ve la cuota. Falta el costo de la decisión.'),('hipotesis','Seis hipótesis. Tres se sostienen; tres cambian.'),('decisiones','Corregir lo que impide decidir con confianza.'),('metodo','Datos útiles, con límites visibles.')]:
    tag='aside' if section=='metodo' else 'section'
    block=re.search(rf'<{tag}[^>]*id="{section}"[^>]*>([\s\S]*?)</{tag}>',source).group(1)
    add(section,title,'html','Originación Única 2.0 · segunda medición sintética.',clean(block),f'{MAIN}#{section}',MAIN)

stages=[('Elegir y registrarse',7,'Llegan a la selfie','Una sesión se detiene en la autorización de buró. Solo una llega sin fricción.'),('Verificar identidad',8,'Terminan selfie e INE','Las ocho lo logran con fricción: el permiso repetido desde otro dominio reduce la confianza.'),('Completar datos',7,'Alcanzan la oferta','La app vuelve a pedir datos de la INE; una sesión se pierde al confirmar la fachada.'),('Aceptar y cerrar',6,'Finalizan la solicitud','Las dos salidas ocurren en el contrato: el mismo perfil abandona en ambas corridas.')]
for i,(title,n,heading,desc) in enumerate(stages,1):
    sessions=[s for s in ag['metricas']['sesiones'] if s['tarea']==f'T{i}']
    assert len(sessions)==8 and sum(s['completa'] for s in sessions)==n
    add(f'tramo-{i}',title,'stage',f'Tramo {i:02d} · ocho corridas sintéticas independientes.',dict(total=8,complete=n,heading=heading,description=desc,sessions=sessions), '../datos/agregado.json')

# Paired confidence comparison: every difference comes from the same session.
confidence_rows=[]
for file in sorted((STUDY/'datos/sesiones').glob('T2-*.json')):
    session=json.loads(file.read_text())
    before=next(step['perfil']['confianza'] for step in session['pasos'] if step['pantalla']=='inePermisoUbicacion')
    after=next(step['perfil']['confianza'] for step in session['pasos'] if step['pantalla']=='incodeUbicacion')
    confidence_rows.append((session['nombre'],session['corrida'],before,after,before-after,file.stem))
assert len(confidence_rows)==8
before_mean=sum(row[2] for row in confidence_rows)/8
after_mean=sum(row[3] for row in confidence_rows)/8
drop_mean=sum(row[4] for row in confidence_rows)/8
rows=''.join(f'<tr><td><a href="lecturas/{sid}.html">{escape(name)} · corrida {run}</a></td><td>{before}/100</td><td>{after}/100</td><td>{drop} puntos</td></tr>' for name,run,before,after,drop,sid in confidence_rows)
confidence_html=f'''<h2>Qué mide esta cifra</h2><p>En cada pantalla se pide al perfil sintético indicar, de 0 a 100, cuánto confía en el producto en ese momento. Es una valoración de la simulación, no una medición con clientes reales.</p><h2>Qué momentos se comparan</h2><p>Antes: permiso de ubicación de la app, justo antes del proveedor de identidad (inePermisoUbicacion). Después: permiso de ubicación de Incode (incodeUbicacion). Se comparan esos dos registros dentro de cada una de las ocho corridas.</p><table><thead><tr><th>Sesión sintética</th><th>Antes</th><th>Después</th><th>Caída</th></tr></thead><tbody>{rows}</tbody></table><h2>Cómo se calcula</h2><p>Caída por corrida = confianza antes − confianza después. Por ejemplo, en la segunda corrida de Bryan: 60 − 35 = 25 puntos menos.</p><p>Promedio antes: {before_mean}/100. Promedio después: {after_mean}/100. Diferencia media: {drop_mean} puntos, aproximadamente 20. La card muestra 60.3 y 40.5, redondeados a un decimal.</p><p>La caída más pequeña es {min(r[4] for r in confidence_rows)} puntos y la más grande es {max(r[4] for r in confidence_rows)}. El rango anterior de 17 a 25 era incorrecto; se corrigió al revisar los pares de registros originales. No se restan los extremos de los rangos generales.</p>'''
add('confianza-calculo','La confianza, antes y después','html','Escala de 0 a 100 · ocho corridas sintéticas · cálculo comprobable por sesión.',confidence_html,'../datos/agregado.json',MAIN)

# Orientation counts responses (repeated within sessions), never people.
orientation_rows=[]
orientation_counts={'si':0,'mas_o_menos':0,'no':0}
for task in ('T1','T2','T3'):
    for file in sorted((STUDY/'datos/sesiones').glob(task+'-*.json')):
        session=json.loads(file.read_text())
        counts={'si':0,'mas_o_menos':0,'no':0}
        for step in session['pasos']:
            if step.get('fin'): continue
            answer=(step.get('perfil') or {}).get('progreso',{}).get('opcion')
            if answer in counts: counts[answer]+=1
        aggregate=next(row for row in ag['metricas']['sesiones'] if row['sesion']==file.stem)
        assert counts==aggregate['sabe_donde_va'],file.stem
        for answer in counts: orientation_counts[answer]+=counts[answer]
        orientation_rows.append((file.stem,task,counts))
assert len(orientation_rows)==24
orientation_total=sum(orientation_counts.values())
orientation_unclear=orientation_counts['mas_o_menos']+orientation_counts['no']
summary_rows=''.join(f'<tr><td>{task}</td><td>{sum(c["mas_o_menos"] for _,t,c in orientation_rows if t==task)}</td><td>{sum(c["no"] for _,t,c in orientation_rows if t==task)}</td><td>{sum(c["si"] for _,t,c in orientation_rows if t==task)}</td><td>{sum(sum(c.values()) for _,t,c in orientation_rows if t==task)}</td></tr>' for task in ('T1','T2','T3'))
session_rows=''.join(f'<tr><td><a href="lecturas/{sid}.html">{sid}</a></td><td>{c["mas_o_menos"]}</td><td>{c["no"]}</td><td>{c["si"]}</td><td>{sum(c.values())}</td></tr>' for sid,task,c in orientation_rows)
orientation_html=f'''<h2>La pregunta que se repite</h2><blockquote>¿Sabes en qué parte del proceso vas y cuánto te falta?</blockquote><p>En cada paso con una respuesta registrada se cuenta una opción del perfil sintético: sí, más o menos o no. Una misma sesión aporta varias respuestas. Los conteos no representan personas distintas ni pantallas únicas.</p><h2>Qué se incluye</h2><p>24 sesiones sintéticas: cuatro perfiles × tres tramos × dos corridas. T1: elegir y registrarse. T2: verificar identidad. T3: completar datos. Se incluyen todas las respuestas registradas a lo largo de esos tramos, también al volver a una pantalla; se excluyen registros de finalización y pasos sin respuesta. El tramo de aceptación y cierre (T4) queda fuera de esta métrica.</p><h2>Cómo se obtiene el total</h2><p>{orientation_counts['mas_o_menos']} “más o menos” + {orientation_counts['no']} “no” = {orientation_unclear} respuestas con dudas. Al sumar las {orientation_counts['si']} respuestas “sí”, la base es {orientation_total}.</p><table><thead><tr><th>Tramo</th><th>Más o menos</th><th>No</th><th>Sí</th><th>Total</th></tr></thead><tbody>{summary_rows}</tbody></table><h2>Comprobar las 24 sesiones</h2><table><thead><tr><th>Sesión sintética</th><th>Más o menos</th><th>No</th><th>Sí</th><th>Total</th></tr></thead><tbody>{session_rows}</tbody></table><h2>Cómo interpretar este resultado</h2><p>La claridad sobre el avance fue poco frecuente entre las respuestas registradas. Las sesiones más largas aportan más respuestas; esta métrica describe los pasos observados, no una proporción de clientes. Los campos de datos vacíos son un hallazgo separado y no intervienen en este cálculo.</p><p>Nota de corrección: el conteo editorial anterior de 435 de 439 se sustituyó al contrastar todas las sesiones con los datos agregados. El tramo de datos contiene 232 respuestas “no” o “más o menos” de un total de 233.</p>'''
add('orientacion-calculo','Qué significa saber dónde van','html','La pregunta, las opciones y la base del conteo · 24 sesiones sintéticas.',orientation_html,'../datos/agregado.json',MAIN)

evidence_builder=runpy.run_path(str(ROOT/'assets/evidence/build_evidence.py'))
evidence_library=evidence_builder['build'](ROOT,add)

(ASSETS/'manifest.js').write_text('window.ReportReaderData={};\nwindow.ReportReaderManifest='+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n')
print(f'{len(manifest)} páginas de lectura generadas con sus fuentes locales.')
# Destinations stay on designed HTML pages, including opening a new tab.
lookup={}
for key,m in manifest.items():
    if m['original'] and m['kind']!='stage': lookup.setdefault(m['original'],m['page'])
for key in ('recorrido','hallazgos','hipotesis','decisiones','metodo'): lookup['#'+key]=manifest[key]['page']
source=re.sub(r'(<a\b[^>]*\bhref=")([^"]+)',lambda m:m[1]+lookup.get(m[2],m[2]),source)
(ROOT/'fuente-editorial.html').write_text(source)
(ROOT/MAIN).write_text(source)
