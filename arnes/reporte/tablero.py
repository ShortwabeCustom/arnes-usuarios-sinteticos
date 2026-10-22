"""Tablero de investigación de un recorrido: el reporte principal, para decidir con evidencia (docs/TABLERO.md).

Este módulo junta los datos (estudio, narrativa, agregado, sesiones, auditoría) en un solo JSON y lo inserta en una
página autocontenida (`tablero.css`, `tablero.js`). No inventa datos: lo calculado aquí va marcado como derivado.
"""

from __future__ import annotations

import html
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

from .. import estandares as std
from ..estudio import Estudio

AQUI = Path(__file__).parent
COMPLETAN = {"exito", "exito_con_friccion", "falso_exito"}
NIVEL_CONF = {"alta": 3, "media": 2, "baja": 1}
SEVERIDAD = {4: "Crítico", 3: "Importante", 2: "Menor", 1: "Cosmético", 0: "Sin problema"}
FUENTE = {"SIMULACIÓN": "Sesión sintética", "MODELO": "Auditoría", "EVIDENCIA": "Prototipo", "INFERENCIA": "Inferencia",
          "SUPUESTO": "Supuesto"}
IMPACTO = {"comprension": "Comprensión", "confianza": "Confianza", "esfuerzo": "Esfuerzo", "decision": "Decisión",
           "continuidad": "Continuidad"}


def _mediana(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def _media(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 1) if xs else None


def datos(e: Estudio, N: dict, img64) -> dict:
    """Todo lo que dibuja el tablero, en un dict serializable."""
    c = e.cfg
    R = json.loads(e.ruta("datos", "agregado.json").read_text(encoding="utf-8"))
    S = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(e.sesiones_dir.glob("*.json"))]
    af = e.ruta("datos", "auditoria.json")
    A = json.loads(af.read_text(encoding="utf-8")) if af.exists() else {}
    nombres = N.get("pantallas") or {}
    etapa_de = lambda pid: (N.get("etapas") or {}).get(pid) or nombres.get(pid, pid).split(" · ")[0]  # noqa: E731

    panel = e.panel()
    perfiles = [dict(id=it.id, nombre=it.nombre.split()[0], completo=it.nombre, segmento=it.segmento,
                     edad=it.edad, perfil=it.perfil) for it in panel]
    integrante = {s["id"]: s["integrante"] for s in S}
    tareas = [dict(id=t["id"], nombre=t.get("exito", ""), escenario=" ".join(t.get("escenario", "").split()),
                   instruccion=" ".join(t.get("instruccion", "").split())) for t in c.get("tareas", [])]

    # ---- etapas en el orden del recorrido (embudo), y observaciones por paso
    etapas = []
    for x in R.get("embudo", []):
        et = etapa_de(x["pantalla"])
        if et not in etapas:
            etapas.append(et)
    obs = []
    for s in S:
        for p in s["pasos"]:
            q = p.get("perfil")
            if not q:
                continue
            obs.append(dict(s=s["id"], t=s["tarea"], p=s["integrante"], e=etapa_de(p.get("pantalla")), pid=p.get("pantalla"),
                            n=p["n"], c=q.get("confianza"), f=q.get("friccion"), txt=q.get("pensamiento", ""),
                            acc=(q.get("accion") or {}).get("opcion", ""), r=p.get("respuesta")))
    etapas = [et for et in etapas if any(o["e"] == et for o in obs)] or sorted({o["e"] for o in obs})

    # ---- sesiones (resumen por sesión, para la tabla y el cajón)
    sesiones = []
    for s in S:
        cs = [o["c"] for o in obs if o["s"] == s["id"] and o["c"] is not None]
        sesiones.append(dict(id=s["id"], t=s["tarea"], p=s["integrante"], resultado=s.get("resultado"), pasos=len(s["pasos"]),
                             ces=(s.get("ces") or {}).get("ces"), ces_txt=(s.get("ces") or {}).get("texto", ""),
                             cmin=min(cs) if cs else None, cierre=s.get("cierre"),
                             recorrido=[dict(n=o["n"], e=o["e"], c=o["c"], f=o["f"], acc=o["acc"], r=o["r"], txt=o["txt"])
                                        for o in obs if o["s"] == s["id"]]))

    # ---- KPIs (de agregado.json; lo calculado aquí va como derivado)
    met = (R.get("metricas") or {}).get("tareas") or {}
    res = R.get("resultados") or {}
    kpis = []
    tot = sum(sum(v.values()) for v in res.values())
    comp = sum(n for v in res.values() for r, n in v.items() if r in COMPLETAN)
    kpis.append(dict(id="completitud", etiqueta="Llegan al final definido", valor=f"{comp}/{tot}",
                     contexto="sesiones sintéticas que llegan al criterio de fin de su tarea",
                     estado="positivo" if tot and comp / tot >= .75 else "atencion" if tot and comp / tot >= .5 else "critico"))
    sinf = {t: (v.get("exito", 0), sum(v.values())) for t, v in res.items()}
    peor = min((a / b for a, b in sinf.values() if b), default=1)
    kpis.append(dict(id="sin_friccion", etiqueta="Sin fricción", partes=[dict(t=t, a=a, b=b) for t, (a, b) in sinf.items()],
                     contexto="sesiones que llegan sin fricción ≥ 3 ni toques sin respuesta",
                     estado="positivo" if peor >= .75 else "atencion" if peor >= .5 else "critico"))
    ces = {t: (met.get(t, {}).get("ces") or {}).get("mediana") for t in met}
    peor_ces = min((v for v in ces.values() if v is not None), default=None)
    kpis.append(dict(id="ces", etiqueta="Facilidad percibida (CES 1–7)", partes=[dict(t=t, v=v) for t, v in ces.items()],
                     contexto="mediana por tarea · 7 = muy fácil",
                     estado="contexto" if peor_ces is None else "positivo" if peor_ces >= 5.5 else "atencion" if peor_ces >= 4 else "critico"))
    t1 = next(iter(met), None)
    if t1 and (met[t1].get("pasos") or {}).get("mediana") is not None:
        prom = (N.get("tablero") or {}).get("pasos_prometidos")
        kpis.append(dict(id="pasos", etiqueta=f"Pasos en {t1} (mediana)", valor=f"{met[t1]['pasos']['mediana']:g}",
                         comparador=f"Promesa: {prom}" if prom else None,
                         contexto=f"{met[t1].get('pantallas', {}).get('mediana', '—')} pantallas · {met[t1].get('campos', {}).get('mediana', '—')} campos",
                         estado="atencion" if prom and met[t1]["pasos"]["mediana"] > prom else "contexto"))
    por_etapa = {}
    for et in etapas:
        os_ = [o for o in obs if o["e"] == et]
        por_etapa[et] = dict(c=_media([o["c"] for o in os_]), f=_media([o["f"] for o in os_]), n=len(os_),
                             alta=sum(1 for o in os_ if (o["f"] or 0) >= 3),
                             sesiones=len({o["s"] for o in os_}))
    por_pantalla = {}
    for o in obs:
        por_pantalla.setdefault(o["pid"], []).append(o["c"])
    baja = min(((round(_media(v)), nombres.get(pid, pid)) for pid, v in por_pantalla.items() if _media(v) is not None), default=None)
    if baja:
        kpis.append(dict(id="confianza", etiqueta="Confianza más baja (media de una pantalla)", valor=f"{baja[0]}/100", contexto=baja[1],
                         derivado=True, estado="critico" if baja[0] < 50 else "atencion" if baja[0] < 65 else "positivo"))
    pt = R.get("primer_toque") or {}
    if pt:
        a, b = sum(v["correcto"] for v in pt.values()), sum(v["total"] for v in pt.values())
        kpis.append(dict(id="primer_toque", etiqueta="Primer toque esperado", valor=f"{a}/{b}",
                         contexto="sesiones cuyo primer toque fue el esperado",
                         estado="positivo" if b and a / b >= .75 else "atencion" if b and a / b >= .5 else "critico"))

    # ---- hallazgos con prioridad derivada y evidencia
    n_tarea = {t: sum(v.values()) for t, v in res.items()}
    hallazgos = []
    for h in N.get("hallazgos") or []:
        ses = h.get("sesiones") or []
        tareas_h = sorted({x.split("-")[0] for x in ses})
        base = sum(n_tarea.get(t, 0) for t in tareas_h)
        frec = round(len(ses) / base, 2) if base else None
        conf = NIVEL_CONF.get(str(h.get("confianza", "")).lower(), 2)
        sev = int(h.get("severidad", 0))
        prio = round(sev * frec * conf, 2) if frec is not None else None
        por_int = defaultdict(int)
        for x in ses:
            por_int[integrante.get(x, x.split("-")[1] if "-" in x else x)] += 1
        corridas = {p["id"]: sum(1 for s in S if s["integrante"] == p["id"] and s["tarea"] in tareas_h) for p in perfiles}
        matriz = {p["id"]: ("na" if not ses else "si" if por_int.get(p["id"], 0) >= max(1, corridas[p["id"]]) else
                            "parcial" if por_int.get(p["id"]) else "no") for p in perfiles}
        pid = h.get("pantalla")
        citas = [dict(s=o["s"], p=o["p"], txt=o["txt"], c=o["c"], f=o["f"]) for o in obs
                 if o["pid"] == pid and o["s"] in ses][:4]
        capturas = []
        for x in ses:
            sj = next((s for s in S if s["id"] == x), None)
            paso = next((p for p in (sj or {}).get("pasos", []) if p.get("pantalla") == pid and p.get("captura")), None)
            if paso and e.ruta(paso["captura"]).exists() and len(capturas) < 3:
                capturas.append(dict(s=x, src=img64(e.ruta(paso["captura"]), 300, 78)))
        if not capturas and pid:   # hallazgo de auditoría: la primera captura de esa pantalla
            for s in S:
                paso = next((p for p in s["pasos"] if p.get("pantalla") == pid and p.get("captura")), None)
                if paso and e.ruta(paso["captura"]).exists():
                    capturas.append(dict(s=s["id"], src=img64(e.ruta(paso["captura"]), 300, 78)))
                    break
        os_ = [o for o in obs if o["pid"] == pid]
        aud = [dict(criterio=x["criterio"], nombre=x["nombre_criterio"], ev=f'{x["evaluadores"]} de {x["de"]}',
                    sev=x["severidad_media"], problema=x["problemas"][0]) for x in A.get("consolidado", [])
               if x.get("pantalla") == pid and x.get("consenso")][:3]
        hallazgos.append(dict(
            id=h["id"], titulo=h.get("titulo", ""), severidad=sev, severidad_txt=SEVERIDAD.get(sev, str(sev)),
            confianza=str(h.get("confianza", "")).lower() or "media", categoria=h.get("categoria", ""),
            oportunidad=std.oportunidades().get(h.get("oportunidad"), h.get("oportunidad") or ""),
            etapa=etapa_de(pid) if pid else "", pantalla=nombres.get(pid, pid or ""), pid=pid,
            sesiones=ses, n_ses=len(ses), base=base, frecuencia=frec, prioridad=prio,
            impacto_negocio=h.get("impacto_negocio"),
            observacion=h.get("hallazgo", ""), interpretacion=h.get("interpretacion", ""),
            recomendacion=h.get("recomendacion", ""), validacion=h.get("validacion", ""),
            impacto_usuario=[IMPACTO.get(x, x) for x in h.get("impacto_usuario") or []],
            heuristica=h.get("heuristica", ""), wcag=h.get("wcag", ""), walkthrough=h.get("walkthrough"),
            evidencia=h.get("evidencia", ""), etiquetas=h.get("etiquetas") or [],
            fuente=sorted({FUENTE.get(x, x) for x in h.get("etiquetas") or []}),
            reescritura=h.get("reescritura") or [], matriz=matriz, citas=citas, capturas=capturas,
            metricas=dict(c=_media([o["c"] for o in os_]), f=_media([o["f"] for o in os_]), n=len(os_)),
            auditoria=aud))
    orden = sorted(hallazgos, key=lambda h: (h["prioridad"] is None, -(h["prioridad"] or 0), -h["severidad"]))
    top = [h["id"] for h in orden[:3]]

    # ---- hipótesis, validación, metodología
    hip_cfg = {h["id"]: h for h in c.get("hipotesis") or []}
    hipotesis = [dict(id=x["id"], estado=x.get("estado", "no_concluyente"), texto=(hip_cfg.get(x["id"]) or {}).get("texto", ""),
                      evidencia=x.get("evidencia", ""), sostiene=(hip_cfg.get(x["id"]) or {}).get("se_sostiene_si", ""),
                      cae=(hip_cfg.get(x["id"]) or {}).get("se_cae_si", "")) for x in N.get("hipotesis_resultado") or []]
    validar = []
    for v in N.get("validar_con_personas") or []:
        v = v if isinstance(v, dict) else dict(que=v)
        m = v.get("metodo") or (c.get("uix") or {}).get("metodologia") or "pdu"
        mu = std.muestra(m)
        validar.append(dict(que=v.get("que", ""), metodo=std.std()["naming"]["metodologias"].get(m, m),
                            aprender=v.get("aprender", ""), muestra=mu[0] if mu else "Sin dato",
                            hallazgo=v.get("hallazgo", ""), prioridad=v.get("prioridad", "")))
    ncorr = c.get("corridas", 1)
    alcance = dict(perfiles=len(perfiles), corridas=ncorr, tareas=len(tareas), sesiones=len(S),
                   material="Prototipo de Figma" if c.get("material") == "figma" else "Sitio web",
                   biblioteca=c.get("biblioteca"), panel=c.get("panel"))
    metricas = {t: {k: (v.get("mediana") if isinstance(v, dict) else v) for k, v in m.items()
                    if k in ("pasos", "clics", "campos", "tiempo_completan_s", "espera_sistema_s")} for t, m in met.items()}
    aud_top = [dict(pantalla=nombres.get(x["pantalla"], x["pantalla"]), criterio=x["criterio"], nombre=x["nombre_criterio"],
                    ev=f'{x["evaluadores"]} de {x["de"]}', sev=x["severidad_media"], problema=x["problemas"][0],
                    recomendacion=(x.get("recomendaciones") or [""])[0])
               for x in A.get("consolidado", []) if x.get("consenso")]
    return dict(
        titulo=N.get("titulo_corto") or c.get("titulo", ""), producto=c.get("producto", ""), fecha=str(c.get("fecha", "")),
        estudio=c.get("titulo", ""), autor=c.get("autor", ""), entregable=e.entregable(al_construir=True),
        veredicto=N.get("titular", ""), detalle_veredicto=N.get("veredicto", ""),
        confianza=str(N.get("confianza", "")).lower(), pregunta=c.get("pregunta_principal", ""),
        kpis=kpis, kpis_nota=N.get("kpis_nota", ""), perfiles=perfiles, tareas=tareas, etapas=etapas, por_etapa=por_etapa,
        obs=[{k: o[k] for k in ("s", "t", "p", "e", "c", "f", "txt")} for o in obs],
        momentos=[dict(etapa=etapa_de(next((pid for pid, nm in nombres.items() if nm == m["pantalla"]), m["pantalla"])),
                       tipo=m.get("tipo"), texto=m.get("texto", "")) for m in N.get("momentos") or []],
        hallazgos=hallazgos, top=top, hipotesis=hipotesis, validar=validar,
        positivos=N.get("positivos") or [], limitaciones=N.get("limitaciones") or [],
        prototipado=N.get("estado_prototipado") or [], aprendizajes=N.get("aprendizajes_metodo") or [],
        fuentes=N.get("fuentes") or [], tecnicas=N.get("limitaciones_tecnicas") or [], resumen=N.get("resumen") or [],
        perfiles_txt=N.get("perfiles") or {}, sesiones=sesiones, metricas=metricas, auditoria=aud_top,
        alcance=alcance, robustez=(R.get("robustez") or {}).get("alertas") or [],
        proximos=N.get("proximos_pasos") or [], decision=N.get("decision") or [],
        auditoria_n=dict(evaluadores=A.get("evaluadores"), consenso=sum(1 for x in A.get("consolidado", []) if x.get("consenso")))
        if A else None)


def armar(e: Estudio, N: dict, detalle: str, img64) -> str:
    """Página del tablero. `detalle` es el nombre del archivo con el reporte completo (formato documento)."""
    D = datos(e, N, img64)
    D["detalle"] = detalle
    css = (AQUI / "tablero.css").read_text(encoding="utf-8")
    js = (AQUI / "tablero.js").read_text(encoding="utf-8")
    datos_js = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    titulo = html.escape(f"{D['titulo']} · investigación UX sintética")
    ids = "".join(f'<span id="{html.escape(h["id"])}" hidden></span>' for h in D["hallazgos"])  # anclas para `arnes verificar`
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>{css}</style>
</head>
<body>
<a class="saltar" href="#contenido">Ir al contenido</a>
<div id="app" aria-live="polite"><noscript><p>Este tablero necesita JavaScript. El reporte completo en formato documento está en
<a href="{html.escape(detalle)}">{html.escape(detalle)}</a>.</p></noscript>
<p class="aviso-inicial">Investigación sintética: perfiles construidos sobre evidencia, no personas.</p></div>
{ids}
<script>const D = {datos_js};</script>
<script>{js}</script>
</body>
</html>
"""
