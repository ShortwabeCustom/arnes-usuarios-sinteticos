"""Curated evidence and traceable media inventory; source records stay unchanged."""
from pathlib import Path
from collections import Counter
from html import escape
import json
import subprocess

CASES = [
 dict(id='evidencia-costo',title='El contrato muestra la cuota, pero deja fuera el total',topic='Decisión financiera',sid='T4-itzel-1',step=7,screen='diaPago',heuristic='Reconocer antes que recordar',interpretation='La persona tiene que calcular el costo por su cuenta para decidir. Conviene mostrar total, número de pagos y condiciones junto a la cuota.',observation='El resumen muestra $22,000, 52 semanas y una cuota semanal aproximada de $728; remite el contrato completo y el costo anual total a la visita.',limit='La cuenta expresada por Itzel es una estimación del perfil sintético. Esta captura no verifica las condiciones de un préstamo real.',map_note='Este mapa agrupa acciones en la pantalla de día de pago. Su imagen base tiene el contrato cerrado; no permite atribuir cada marca al resumen abierto.',criteria=[]),
 dict(id='evidencia-permisos',title='Un permiso llega con un nombre que no reconocen',topic='Confianza y permisos',sid='T2-bryan-2',step=8,screen='incodeUbicacion',heuristic='Correspondencia con el mundo real · ayuda y documentación',interpretation='El nombre técnico del proveedor rompe la continuidad de marca. Anunciar quién verifica la identidad, para qué pide ubicación y qué ocurre al negarla reduce la sorpresa.',observation='El diálogo pide ubicación para identidad-digital-ocrdual.com.mx sobre un fondo negro, sin explicación del proveedor dentro de esta pantalla.',limit='El rechazo de Bryan pertenece a una simulación. No permite estimar cuántos clientes reales negarían el permiso.',map_note='Verde indica que hubo una respuesta visible a la acción. Elegir «No permitir» también puede producir una marca verde; verde no significa consentimiento ni éxito.',criteria=['N2','N10']),
 dict(id='evidencia-fachada',title='La foto no coincide y la corrección no queda clara',topic='Control y recuperación',sid='T3-rosalba-2',step=34,screen='fachada',heuristic='Control y libertad · prevención de errores',interpretation='Confirmar y corregir deben ser opciones comprensibles. Mostrar la dirección y explicar qué pasa al rechazar la foto ayuda a evitar confirmaciones incorrectas.',observation='La pantalla pide confirmar una foto de una posada y ofrece «No es mi fachada» como enlace bajo el botón principal.',limit='La foto forma parte del MVP de pruebas. La corrida termina por límite de pasos; no debe presentarse como un abandono voluntario ni como una falla de datos reales.',map_note='Los toques se agregan sobre la primera captura de esta pantalla. Las repeticiones de una misma sesión también cuentan.',criteria=['N3','N5','N6']),
 dict(id='evidencia-buro',title='El consentimiento depende de un documento que no logra leer',topic='Consentimiento informado',sid='T1-itzel-2',step=8,screen='contacto',heuristic='Control y libertad · ayuda y documentación',interpretation='La autorización necesita un documento accesible y una aceptación explícita. La pantalla de datos no debería obligar a decidir sin poder revisar sus implicaciones.',observation='La autorización de consulta de historial aparece en el texto inferior de la pantalla de contacto. El paso registra un toque sobre ese enlace.',limit='La captura muestra el estado previo al intento. El problema al abrir el documento se describe en el siguiente registro de la sesión; una imagen fija por sí sola no demuestra ese comportamiento.',map_note='Este mapa combina acciones de la pantalla de contacto, incluidos campos de texto. No mide qué textos se leyeron ni la atención visual.',criteria=['N3','N10']),
]

def build(root, add):
    study=root.parent
    sessions={p.stem:json.loads(p.read_text()) for p in sorted((study/'datos/sesiones').glob('*.json'))}
    expert=json.loads((study/'datos/auditoria.json').read_text())
    media_cache=root/'assets/evidence/media-metadata.json'
    cached=json.loads(media_cache.read_text()) if media_cache.exists() else {}
    videos={}
    for sid,s in sessions.items():
        rel=s.get('video');path=study/rel if rel else None
        if not path or not path.is_file(): continue
        signature=[path.stat().st_size,path.stat().st_mtime_ns]
        if sid not in cached or cached[sid].get('signature')!=signature:
            raw=subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(path)],text=True)
            info=json.loads(raw);cached[sid]={'signature':signature,'duration':float(info['format']['duration']),'streams':info['streams']}
        videos[sid]={'src':'../'+rel,'seconds':cached[sid]['duration'],'audio':any(x['codec_type']=='audio' for x in cached[sid]['streams']),'poster':'../'+s['pasos'][0]['captura']}
    media_cache.write_text(json.dumps(cached,ensure_ascii=False,indent=2)+'\n')
    actions={}
    for sid,s in sessions.items():
        for p in s['pasos']:
            a=p.get('accion') or {}
            if a.get('tipo') not in ('tocar','escribir'): continue
            rows=actions.setdefault(p['pantalla'],[])
            rows.append({'sid':sid,'step':p['n'],'action':a['tipo'],'response':p.get('respuesta'),'x':a.get('x'),'y':a.get('y')})
    maps=[]
    for file in sorted((study/'heatmaps').glob('toques-*.png')):
        screen=file.stem.removeprefix('toques-');rows=actions.get(screen,[])
        counts=Counter(row['response'] for row in rows)
        item=dict(id='mapa-'+screen,title='Toques · '+screen,screen=screen,image='../heatmaps/'+file.name,actions=len(rows),sessions=len({x['sid'] for x in rows}),responded=counts.get('si',0),unconfirmed=len(rows)-counts.get('si',0),rows=rows)
        add(item['id'],item['title'],'heatmap','Acciones ejecutadas por el arnés durante sesiones sintéticas. No es seguimiento de mirada.',item,item['image'])
        maps.append(item)
    resolved=[]
    for source in CASES:
        c=dict(source);s=sessions[c['sid']];step=next(p for p in s['pasos'] if p['n']==c['step'])
        assert step['pantalla']==c['screen']
        c.update(name=s['nombre'],task=s['tarea'],run=s['corrida'],image='../'+step['captura'],thought=step.get('perfil',{}).get('pensamiento',''),action=step.get('perfil',{}).get('accion',{}).get('texto',''),video=videos.get(c['sid']),sessionPage=f"lecturas/{c['sid']}.html",map=next((m for m in maps if m['screen']==c['screen']),None))
        c['expert']=[x for x in expert['consolidado'] if x['pantalla']==c['screen'] and x['criterio'] in c['criteria']]
        if c['sid']=='T1-itzel-2':c['nextThought']=next(p['perfil']['pensamiento'] for p in s['pasos'] if p['n']==9)
        add(c['id'],c['title'],'evidence-case','Captura, grabación, toques y criterio UX · '+c['sid'],c,f"../datos/sesiones/{c['sid']}.json")
        resolved.append(c)
    library=dict(cases=resolved,maps=maps,sessions=[dict(id=sid,title=s['nombre'],task=s['tarea'],run=s['corrida'],result=s['resultado'],steps=len(s['pasos']),video=videos.get(sid),page=f'lecturas/{sid}.html') for sid,s in sessions.items()])
    add('evidencias','Biblioteca de evidencias','evidence-library','Explora los hallazgos, las grabaciones de 32 sesiones y los mapas de acciones. Todo conserva su fuente.',library,None)
    return library
