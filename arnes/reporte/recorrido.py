"""Secciones del reporte para el método de recorrido."""

from __future__ import annotations

import json
import re

from . import (
    AVISO_SINTETICO,
    e_,
    img64,
    lista,
    md_comun,
    pagina,
    seccion_auditoria,
    seccion_estilo,
    seccion_hallazgos, seccion_validar,
    seccion_hipotesis,
    seccion_panel,
    seccion_priorizacion,
    seccion_robustez,
    seccion_trazabilidad,
)

RESULTADOS = [("exito", "Éxito", "ok"), ("exito_con_friccion", "Éxito con fricción", "duda"), ("falso_exito", "Cree que terminó", "mal"),
              ("abandono", "Abandono", "mal"), ("atascado", "Atascado", "mal"), ("fallo_max_pasos", "Sin terminar", "mal"),
              ("terminado_sin_criterio", "Terminó (sin criterio de fin)", "gris"), ("guion_completo", "Guion completo", "gris")]


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")[:80]


SEMAFORO = {"verde": "var(--ok)", "amarillo": "var(--duda)", "naranja": "#C8691C", "rojo": "var(--mal)"}


def _resultados(e, R) -> str:
    from ..estandares import semaforo
    from ..robustez import wilson

    cols = [r for r in RESULTADOS if any(r[0] in v for v in R["resultados"].values())]
    tareas = {t["id"]: t for t in e.cfg["tareas"]}
    met = (R.get("metricas") or {}).get("tareas", {})
    filas = ""
    for t, v in R["resultados"].items():
        tot = sum(v.values())
        m = met.get(t) or {}
        sm = semaforo(m.get("completan", 0), m.get("sesiones", 0))
        if sm:
            lo, hi = (round(100 * x) for x in wilson(m["completan"], m["sesiones"]))
            bajo, alto = semaforo(lo, 100)["nivel"], semaforo(hi, 100)["nivel"]
            firme = (e_(sm["accion"]) if bajo == alto else
                     f"el intervalo va de {bajo} a {alto}: sin color firme, faltan corridas")
            sem = (f'<td><span class="pt" style="width:10px;height:10px;border-width:0;vertical-align:middle;background:{SEMAFORO[sm["nivel"]]}"></span> '
                   f'<b>{sm["nivel"].capitalize()}</b> · {m["completan"]} de {m["sesiones"]} ({sm["pct"]}%)'
                   f'<br><small>intervalo {lo}–{hi}% · {firme}</small></td>')
        else:
            sem = "<td>—</td>"
        filas += (f'<tr><th scope="row">{e_(t)}<small>{e_(" ".join(tareas.get(t, {}).get("instruccion", "").split()))}</small></th>'
                  + "".join(f'<td class="n">{v.get(k, 0)} de {tot}</td>' for k, _, _ in cols) + sem + "</tr>")
    cab = "".join(f'<th><span class="pt {c}" style="width:10px;height:10px;border-width:0;vertical-align:middle"></span> {n}</th>' for _, n, c in cols)
    return (f'<div class="tabla-wrap"><table><thead><tr><th>Tarea</th>{cab}<th>Completitud<small>semáforo de UiX, como referencia</small></th>'
            f'</tr></thead><tbody>{filas}</tbody></table></div>'
            '<p class="nota">«Éxito» exige llegar a la pantalla de fin definida en el protocolo, sin fricción alta ni toques sin respuesta. '
            '«Cree que terminó»: el perfil declaró la tarea completa sin haber llegado al fin. Cuenta sesiones sintéticas, no personas.</p>'
            '<p class="nota">Completitud: sesiones que llegan al fin, con o sin fricción. El semáforo es el de la guía de completitud de UiX '
            '(verde ≥ 90% · amarillo 78–89% · naranja 50–77% · rojo &lt; 50%; promedio de referencia 78%, MeasuringU), pensado para '
            'personas. Aplicado a corridas sintéticas es una señal de dónde mirar, no una tasa de éxito: con pocas corridas el '
            'intervalo cruza varios colores <span class="tag">INFERENCIA</span>.</p>')


def _embudo(e, N, R, S) -> str:
    nombres = N.get("pantallas") or {}
    sev = {}
    for h in N.get("hallazgos") or []:
        for p in [h.get("pantalla")] + (h.get("pantallas") or []):
            if p:
                sev[str(p)] = max(sev.get(str(p), 0), int(h.get("severidad", 0)))
    ses = sorted(S, key=lambda s: (s["tarea"], s["integrante"]))
    cab = "".join(f'<th>{e_(s["nombre"].split()[0])}<small>{e_(s["tarea"])}</small></th>' for s in ses)
    filas = ""
    for x in R["embudo"]:
        pid = x["pantalla"]
        celdas = ""
        for s in ses:
            ns = [p["n"] for p in s["pasos"] if p.get("pantalla") == pid]
            celdas += f'<td class="c">{",".join(map(str, ns)) if ns else "—"}</td>'
        sv = sev.get(pid, 0)
        filas += (f'<tr><th scope="row" class="e{sv}">{e_(nombres.get(pid, pid))}<small>{e_(pid)}'
                  f'{" · severidad máxima " + str(sv) if sv else ""}</small></th><td class="n">{x["sesiones"]} de {len(S)}</td>{celdas}</tr>')
    return ('<div class="aviso"><b>No es un mapa de comportamiento medido.</b> El color de cada pantalla es la severidad más alta asignada '
            'por criterio experto a sus hallazgos, sobre la ruta real que recorrieron los perfiles. Los números son el paso en que cada '
            'sesión estuvo en esa pantalla.</div>'
            f'<div class="tabla-wrap"><table class="embudo"><thead><tr><th>Pantalla</th><th>Alcanzada</th>{cab}</tr></thead>'
            f'<tbody>{filas}</tbody></table></div>')


def _primer_toque(R) -> str:
    pt = R.get("primer_toque") or {}
    if not pt:
        return ""
    filas = "".join(f'<tr><th scope="row">{e_(t)}</th><td class="n">{v["correcto"]} de {v["total"]}</td>'
                    f'<td class="n">{e_(v["completan_si_correcto"])}</td><td class="n">{e_(v["completan_si_incorrecto"])}</td></tr>'
                    for t, v in pt.items())
    return ('<h3>Primer toque</h3><div class="tabla-wrap"><table><thead><tr><th>Tarea</th><th>Primer toque correcto</th>'
            f'<th>Completan si acierta</th><th>Completan si no</th></tr></thead><tbody>{filas}</tbody></table></div>'
            '<p class="nota">Referencia con personas ([[first-click-testing]]): acertar el primer clic se asocia con 87% de tareas '
            'completadas, contra 46% si falla. Aquí son corridas sintéticas.</p>')


def _metricas(e, N, R) -> str:
    M = R.get("metricas")
    if not M:
        return ""
    nombres = N.get("pantallas") or {}
    f = lambda d, suf="": "—" if not d else (f"{d['mediana']}{suf}" + (f" <small class='nota'>({d['min']}–{d['max']})</small>" if d["min"] != d["max"] else ""))  # noqa: E731
    out = ""
    for t, m in M["tareas"].items():
        filas = [
            ("Pasos", f(m["pasos"]), "EVIDENCIA", "Decisiones del perfil hasta terminar o salir."),
            ("Pantallas", f(m["pantallas"]), "EVIDENCIA", ""),
            ("Clics", f(m["clics"]), "EVIDENCIA", f"Sin respuesta: {f(m['clics_sin_respuesta'])}."),
            ("Campos solicitados", f(m["campos"]), "EVIDENCIA", "Campos visibles de entrada en la ruta (web). En Figma, cargados a mano en `pantallas_info`."),
            ("Tiempo estimado", f(m["tiempo_completan_s"], " s"), "MODELO", f"Solo sesiones que completan ({m['completan']} de {m['sesiones']}). Incluye la espera real del sistema: {f(m['espera_sistema_s'], ' s')}."),
            ("Validaciones", f(m["validaciones_disparadas"]), "EVIDENCIA", "Mensajes de validación que aparecieron tras una acción. Pantallas de verificación: "
             + (", ".join(e_(nombres.get(p, p)) for p in m["pantallas_verificacion"]) or "ninguna detectada") + " <span class='tag'>INFERENCIA</span>"),
            ("Cambios de canal", f(m["cambios_dominio"]), "EVIDENCIA", "Cambios de dominio. Dominios: " + (", ".join(map(e_, m["dominios"])) or "—")
             + f". Pestañas nuevas: {f(m['pestanas_nuevas'])}. Permisos del navegador: {', '.join(m['permisos']) or 'ninguno'}. "
             + "Menciones a otro canal: " + (", ".join(m["menciones_otro_canal"]) or "ninguna") + " <span class='tag'>INFERENCIA</span>"),
            ("Retoma de solicitud", ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in m["retoma"].items()) or "no se probó", "EVIDENCIA",
             "Salir del proceso y volver a entrar (`retoma` en la tarea)."),
            ("Visibilidad de estatus", f"{m['estatus']['con_indicador']} de {m['estatus']['pantallas']} pantallas", "EVIDENCIA",
             "Pantallas con indicador de paso o barra de progreso. El perfil dice saber dónde va: "
             + f"sí {m['sabe_donde_va']['si']} · más o menos {m['sabe_donde_va']['mas_o_menos']} · no {m['sabe_donde_va']['no']} pasos <span class='tag'>SIMULACIÓN</span>"),
            ("Esfuerzo percibido (CES 1–7)", f(m["ces"]), "SIMULACIÓN", "7 = muy fácil. Leer junto a la tasa de éxito, nunca sola."),
        ]
        out += (f"<h3>{e_(t)}</h3><div class='tabla-wrap'><table><thead><tr><th>Métrica</th><th>Mediana (rango)</th><th>Origen</th><th>Detalle</th></tr></thead><tbody>"
                + "".join(f"<tr><th scope='row'>{n}</th><td class='n'>{v}</td><td><span class='tag'>{o}</span></td><td>{d}</td></tr>" for n, v, o, d in filas)
                + "</tbody></table></div>")
    dist = M.get("distancia_por_pantalla") or {}
    if dist:
        orden = [x["pantalla"] for x in R.get("embudo", []) if x["pantalla"] in dist]
        filas = "".join(f"<tr><th scope='row'>{e_(nombres.get(p, p))}</th><td class='n'>{f(dist[p]['pasos'])}</td><td class='n'>{f(dist[p]['clics'])}</td>"
                        f"<td class='n'>{f(dist[p]['campos'])}</td><td class='n'>{f(dist[p]['tiempo_s'], ' s')}</td></tr>" for p in orden)
        out += ("<h3>Distancia a la compra</h3><p class='sub'>Lo que falta desde cada pantalla hasta el fin de la tarea, en las sesiones que completan.</p>"
                "<div class='tabla-wrap'><table><thead><tr><th>Desde</th><th>Pasos</th><th>Clics</th><th>Campos</th><th>Tiempo estimado</th></tr></thead>"
                f"<tbody>{filas}</tbody></table></div>")
    mt = M["modelo_tiempo"]
    out += (f"<p class='nota'>Tiempo estimado <span class='tag'>MODELO</span> <span class='tag'>SUPUESTO</span>: lectura a {mt['palabras_por_segundo']} "
            f"palabras/s (rango con {' y '.join(map(str, mt['velocidades']))}), {mt['decision_s']} s por decisión (operador M del modelo KLM), "
            f"{mt['toque_s']} s por toque, {mt['tecla_s']} s por carácter, relectura al {int(mt['relectura'] * 100)}%, más la espera real "
            "del sistema. La duración de la sesión sintética no se usa: no mide a una persona.</p>")
    return out


def _wcag(e, R) -> str:
    w = R.get("wcag_258") or []
    if not w:
        return ""
    nombres = (e.narrativa() or {}).get("pantallas") or {}
    filas = ""
    for x in w:
        det = "; ".join(f"«{f['etiqueta'] or f['tipo']}» {f['ancho_css']}×{f['alto_css']}" for f in x["fallan"][:6]) or "—"
        filas += (f'<tr><th scope="row">{e_(nombres.get(x["pantalla"], x["pantalla"]))}</th><td class="n">{x["objetivos"]}</td>'
                  f'<td class="n">{len(x["fallan"])}</td><td>{e_(det)}</td></tr>')
    aprox = any(x["aproximado"] for x in w)
    return ('<p class="sub">WCAG 2.2 · 2.5.8 Tamaño del objetivo (mínimo), nivel AA: 24×24 px CSS, o espaciado suficiente '
            '([[wcag-22-criterios-nuevos]]). Medido sobre las zonas que responden al toque. <span class="tag">EVIDENCIA</span></p>'
            '<div class="tabla-wrap"><table><thead><tr><th>Pantalla</th><th>Objetivos</th><th>Bajo el mínimo</th><th>Cuáles</th></tr></thead>'
            f'<tbody>{filas}</tbody></table></div><p class="nota">Revisar a mano las excepciones que el arnés no ve: enlaces dentro de '
            'un texto, tamaño definido por el navegador, controles esenciales.'
            + (' En Figma la medición es aproximada: las zonas salen de una rejilla de 12 px de pantalla.' if aprox else '') + '</p>')


def _momentos(N, R) -> str:
    ms = N.get("momentos")
    if ms:
        return '<div class="mv">' + "".join(f'<div class="{e_(m.get("tipo", ""))}"><b>{e_(m.get("pantalla", ""))}</b> · {m["texto"]}</div>'
                                           for m in ms) + "</div>"
    cand = R.get("momentos") or []
    if not cand:
        return ""
    return ('<p class="sub">Candidatos automáticos (caída de confianza de 15 puntos o más, o fricción 3 o más). Falta que el investigador '
            'los clasifique en narrativa.yaml.</p><div class="mv">' + "".join(
                f'<div class="{"rojo" if m["friccion"] >= 4 else "amarillo"}"><b>{e_(m["sesion"])} · paso {m["paso"]}</b> · confianza '
                f'{m["confianza"]} (−{m["caida"]}) · fricción {m["friccion"]}<br>«{e_(m["pensamiento"])}» <span class="tag">SIMULACIÓN</span></div>'
                for m in cand) + "</div>")


def _sesiones(e, S) -> str:
    out = ""
    for s in sorted(S, key=lambda s: (s["tarea"], s["integrante"])):
        figs = ""
        for p in s["pasos"]:
            x = p.get("perfil") or {}
            cap = e.ruta(p["captura"]) if p.get("captura") else None
            img = f'<img src="{img64(cap, 300, 70)}" alt="Paso {p["n"]}" loading="lazy">' if cap and cap.exists() else ""
            acc = (x.get("accion") or {}).get("opcion") or ((p.get("accion") or {}).get("tipo") if p.get("accion") else "")
            resp = p.get("respuesta")
            r = {"si": '<span class="si">respondió</span>', "no": '<span class="no">sin respuesta</span>',
                 "fuera_de_marcas": '<span class="no">fuera de las zonas activas</span>'}.get(resp, "")
            pen = x.get("pensamiento") or p.get("dice") or ""
            pen_html = f"<div>«{e_(pen)}»</div>" if pen else ""
            puntajes = f'<div class="nota">confianza {x.get("confianza")} · fricción {x.get("friccion")}</div>' if x else ""
            etiqueta = e_(acc or ("fin" if p.get("fin") else ""))
            figs += f'<figure>{img}<div class="r">Paso {p["n"]} · {etiqueta} {r}</div>{pen_html}{puntajes}</figure>'
        res = dict((k, n) for k, n, _ in RESULTADOS).get(s.get("resultado"), s.get("resultado"))
        out += (f'<details class="plano"><summary>{e_(s["nombre"])} · {e_(s["tarea"])} · {e_(res)} en {len(s["pasos"])} pasos</summary>'
                f'<div class="linea">{figs}</div><p class="nota">Ruta y toques reales sobre el material. Pensamiento, decisiones y '
                f'puntajes: <span class="tag">SIMULACIÓN</span></p></details>')
    return out


def _toques(e, N) -> str:
    nombres = {slug(k): v for k, v in (N.get("pantallas") or {}).items()}
    figs = ""
    for f in sorted(e.ruta("heatmaps").glob("toques-*.png")):
        pid = f.stem[len("toques-"):]
        figs += f'<figure><img src="{img64(f, 480)}" alt="Toques en {e_(nombres.get(pid, pid))}"><figcaption>{e_(nombres.get(pid, pid))}</figcaption></figure>'
    if not figs:
        return ""
    return ('<p class="sub">Toques reales de todas las sesiones sobre la primera captura de cada pantalla. Verde: la pantalla respondió. '
            f'Rojo: no pasó nada visible.</p><div class="galeria">{figs}</div>')


def _matriz_problema(e, N, S) -> str:
    hs = N.get("hallazgos") or []
    if not hs:
        return ""
    ints = sorted({s["integrante"] for s in S})
    nombre = {s["integrante"]: s["nombre"].split()[0] for s in S}
    integ_de = {s["id"]: s["integrante"] for s in S}
    filas = ""
    for h in hs:
        af = {integ_de.get(x) for x in h.get("sesiones") or []} | set(h.get("integrantes") or [])
        filas += (f'<tr><th scope="row">{e_(h.get("id", ""))} {e_(h["titulo"])}</th>' + "".join(
            f'<td class="c">{"✓" if i in af else "—"}</td>' for i in ints) + f'<td class="n">{len(af & set(ints))} de {len(ints)}</td></tr>')
    return ('<div class="tabla-wrap"><table class="embudo"><thead><tr><th>Problema</th>' + "".join(f"<th>{e_(nombre[i])}</th>" for i in ints)
            + f'<th>Total</th></tr></thead><tbody>{filas}</tbody></table></div>')


def armar(e, N):
    R = json.loads(e.ruta("datos", "agregado.json").read_text(encoding="utf-8"))
    S = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(e.sesiones_dir.glob("*.json"))]
    n = len(S)
    supuestos = ('<div class="aviso"><b>Ayudas del instrumento.</b> El perfil ve numerados los elementos que responden al toque; un '
                 'usuario real no los ve <span class="tag">SUPUESTO METODOLÓGICO</span>. Por eso declara primero su intención con sus '
                 'palabras. La duración de las sesiones no mide tiempo de tarea.</div>')
    secciones = [
        ("panel", "Panel", "Quiénes recorrieron el flujo", seccion_panel(e, N)),
        ("hipotesis", "Protocolo", "Qué se puso a prueba", seccion_hipotesis(e, N)),
        ("resultados", "Resultados", "Qué ocurrió en las sesiones", _resultados(e, R) + _primer_toque(R) + supuestos),
        ("embudo", "Recorrido", "Dónde se concentra la fricción", _embudo(e, N, R, S)),
        ("momentos", "Momentos", "Momentos de verdad", _momentos(N, R)),
        ("firmeza", "Firmeza", "Qué tan firme es lo que dicen las sesiones", seccion_robustez(R, "recorrido")),
        ("auditoria", "Heurísticas", "Evaluación heurística", seccion_auditoria(e)),
        ("metricas", "Métricas", "Métricas del flujo", _metricas(e, N, R)),
        ("accesibilidad", "Accesibilidad", "Accesibilidad medible", _wcag(e, R)),
        ("estilo", "Guía de estilo", "Textos frente a la guía de estilo del producto", seccion_estilo(e)),
        ("hallazgos", "Hallazgos", "Hallazgos y recomendaciones", seccion_hallazgos(N, n, True)),
        ("perfiles", "Perfiles × problemas", "A quién afecta cada problema", _matriz_problema(e, N, S)),
        ("prioridad", "Prioridad", "Priorización", seccion_priorizacion(N, n)),
        ("sesiones", "Sesiones", "Cada sesión, paso a paso", _sesiones(e, S) + _toques(e, N)),
        ("funciona", "Lo que funciona", "Lo que funciona y conviene conservar", lista(N.get("positivos"))),
        ("prototipo", "Estado del material", "Estado de prototipado (no son defectos de diseño)", lista(N.get("estado_prototipado"))),
        ("limites", "Límites", "Alcance y límites", AVISO_SINTETICO + lista(N.get("limitaciones"))
         + seccion_validar(e, N)),
        ("siguientes", "Próximos pasos", "Próximos pasos", lista(N.get("proximos_pasos"), True)),
        ("traza", "Trazabilidad", "Trazabilidad", seccion_trazabilidad(e, N)),
    ]
    tot = sum(sum(v.values()) for v in R["resultados"].values())
    exitos = sum(v.get("exito", 0) + v.get("exito_con_friccion", 0) for v in R["resultados"].values())
    franja = [(n, "sesiones"), (len(e.panel()), "perfiles"), (f"{exitos} de {tot}", "completan"),
              (len(N.get("hallazgos") or []), "hallazgos"), (len(R["embudo"]), "pantallas")]
    html_txt = pagina(e, N, secciones, None, franja)
    filas = "\n".join(f"| {s['sesion']} | {s['resultado']} | {s['pasos']} | {s['sin_respuesta']} | {s['confianza_inicial']} → {s['confianza_final']} | {s['friccion_max']} |"
                      for s in R["sesiones"])
    cuerpo = ("## Sesiones\n\n| Sesión | Resultado | Pasos | Sin respuesta | Confianza | Fricción máx. |\n|---|---|---:|---:|---|---:|\n" + filas)
    return html_txt, md_comun(e, N, cuerpo)
