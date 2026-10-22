"""Secciones del reporte para el método de comprensión."""

from __future__ import annotations

import json

from . import (
    AVISO_SINTETICO,
    e_,
    img64,
    lista,
    md_comun,
    pagina,
    parrafos,
    seccion_auditoria,
    seccion_estilo,
    seccion_hallazgos, seccion_validar,
    seccion_hipotesis,
    seccion_panel,
    seccion_robustez,
    seccion_trazabilidad,
)

TONOS = {"no_se": ("duda", "?"), "": ("gris", "·")}


def _cod(q: dict, grupo: str, momento: str = "antes") -> dict:
    cor = (q.get("correcta") or {}).get(grupo)
    if isinstance(cor, dict):
        cor = cor.get(momento)
    cor = cor if isinstance(cor, list) else [cor] if cor else []
    out = {}
    for o in q.get("opciones", []):
        if o in TONOS and o not in cor:
            out[o] = (TONOS[o][0], TONOS[o][1], o.replace("_", " "))
        elif cor:
            out[o] = ("ok", "✓", o.replace("_", " ")) if o in cor else ("mal", "✕", o.replace("_", " "))
        else:
            out[o] = ("neu", o[:1].upper(), o.replace("_", " "))
    return out


def _marcas(vals, cod) -> str:
    out = []
    for v in vals:
        c, s, etq = cod.get(v, ("gris", "·", v or "sin dato"))
        out.append(f'<span class="pt {c}" title="{e_(etq)}"><span aria-hidden="true">{e_(s)}</span><span class="vh">{e_(etq)}</span></span>')
    return "".join(out) or '<span class="pt gris">·</span>'


def _leyenda(cod, extra="Cada marca es una corrida.") -> str:
    ley = "".join(f'<span class="ley"><span class="pt {c}" aria-hidden="true">{e_(s)}</span>{e_(etq)}</span>' for c, s, etq in cod.values())
    return f'<div class="leyenda">{ley}<span class="ley">{e_(extra)}</span></div>'


def _matriz(e, AGG, q, grupo, bloque="principal", momento="antes", modos=None) -> str:
    c = e.cfg
    vars_ = [p.get("variante", k) for k, p in c["pantallas"].items() if p.get("grupo", "E") == grupo]
    modos = modos or c.get("modos", ["vistazo", "completa"])
    cod = _cod(q, grupo, momento)
    cab = "".join(f'<th colspan="{len(modos)}">Variante {e_(v)}</th>' for v in vars_)
    cab2 = "".join(f"<th>{e_(m)}</th>" for _ in vars_ for m in modos)
    filas = ""
    for it in e.panel():
        o = it.ocean
        sub = f"{it.segmento}" + (f" · N {o['N']} · C {o['C']}" if o else "")
        celdas = "".join(f'<td>{_marcas(AGG.get("|".join((bloque, grupo, v, it.id, m, momento, q["id"])), []), cod)}</td>'
                         for v in vars_ for m in modos)
        filas += f'<tr><th scope="row">{e_(it.nombre)}<small>{e_(sub)}</small></th>{celdas}</tr>'
    return (f'<div class="tabla-wrap"><table class="mx"><thead><tr><th rowspan="2">Perfil</th>{cab}</tr><tr>{cab2}</tr></thead>'
            f'<tbody>{filas}</tbody></table></div>{_leyenda(cod)}')


def _aciertos(e, A, grupo) -> str:
    c = e.cfg
    qs = [q for q in c["preguntas"] if (q.get("correcta") or {}).get(grupo) and (not q.get("solo") or grupo in q["solo"])]
    if not qs:
        return ""
    vars_ = [p.get("variante", k) for k, p in c["pantallas"].items() if p.get("grupo", "E") == grupo]
    momentos = ["antes"] + [k["id"] for k in c.get("continuaciones", []) if not k.get("solo") or grupo in k["solo"]]
    filas = ""
    for q in qs:
        for mom in momentos:
            celdas, hay = "", False
            for v in vars_:
                for m in c.get("modos", ["vistazo", "completa"]):
                    x = A.get("|".join(("principal", grupo, v, m, mom, q["id"])))
                    hay |= bool(x)
                    txt = f"{x['aciertos']} de {x['total']}" if x else "—"
                    celdas += f'<td class="n">{txt}</td>'
            if hay:
                filas += f'<tr><th scope="row">{e_(q["texto"])}<small>{e_(q["id"])} · {"antes" if mom == "antes" else "tras " + mom}</small></th>{celdas}</tr>'
    cab = "".join(f"<th>{e_(v)} · {e_(m)}</th>" for v in vars_ for m in c.get("modos", ["vistazo", "completa"]))
    return (f'<div class="tabla-wrap"><table><thead><tr><th>Pregunta</th>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'
            '<p class="nota">Respuestas que coinciden con la lectura correcta de la pantalla, sobre el total de corridas. '
            'Cuentan corridas de perfiles sintéticos, no personas.</p>')


def _visor(e, M, grupo) -> str:
    c = e.cfg
    pids = [k for k, p in c["pantallas"].items() if p.get("grupo", "E") == grupo]
    figs = ""
    for pid in pids:
        H, W = M["pantallas"][pid]["alto"], M["pantallas"][pid]["ancho"]
        nom = f"Variante {c['pantallas'][pid].get('variante', pid)}"
        figs += (f'<figure class="tel"><div class="marco" style="aspect-ratio:{W}/{H}"><img class="base" src="{img64(e.ruta(c["pantallas"][pid]["imagen"]), 720)}" alt="Pantalla {e_(nom)}">'
                 f'<img class="sal" src="{img64(e.ruta("heatmaps", f"atencion-{pid}.png"), 720)}" alt="Atención predicha, {e_(nom)}" hidden>'
                 f'<svg class="ov" viewBox="0 0 {W} {H}" data-k="{pid}" role="img" aria-label="Puntos de lectura, {e_(nom)}"></svg></div>'
                 f'<figcaption><b>{e_(nom)}.</b> <span class="cap" data-k="{pid}"></span></figcaption></figure>')
    perf = "".join(f'<button type="button" data-p="{e_(it.id)}" aria-pressed="false">{e_(it.nombre.split()[0])}</button>' for it in e.panel())
    return (f'<div class="visor"><div class="ctrl"><div class="seg" role="group" aria-label="Capa">'
            f'<button type="button" data-c="pantalla" aria-pressed="false">Pantalla</button>'
            f'<button type="button" data-c="atencion" aria-pressed="true">Atención predicha</button>'
            f'<button type="button" data-c="lectura" aria-pressed="false">Puntos de lectura</button></div>'
            f'<div class="seg perf" role="group" aria-label="Perfil" hidden>{perf}</div>'
            f'<label class="chk"><input type="checkbox" checked> Líneas de pliegue</label></div>'
            f'<div class="tels">{figs}</div><p class="pie" data-pie></p></div>')


def _zonas(e, M, grupo) -> str:
    c = e.cfg
    filas = ""
    for pid, p in c["pantallas"].items():
        if p.get("grupo", "E") != grupo:
            continue
        for z in M["pantallas"][pid]["zonas"].values():
            if not z["es_texto"]:
                continue
            vis = " · ".join(f"{k}: {'sí' if v else 'no'}" for k, v in z["sin_scroll"].items())
            filas += (f'<tr><td>{e_(p.get("variante", pid))}</td><th scope="row">{e_(z["nombre"])}</th><td class="n">{z["alto_px"] or "—"}</td>'
                      f'<td class="n">{z["contraste"]}:1</td><td class="n">{z["densidad"]:.2f}</td><td>{vis}</td></tr>')
    return ('<details class="plano"><summary>Zonas medidas: alto de línea, contraste, atención y pliegue</summary>'
            '<div class="tabla-wrap"><table><thead><tr><th>Variante</th><th>Zona</th><th>Alto de línea (px)</th><th>Contraste</th>'
            f'<th>Atención</th><th>Sin desplazar</th></tr></thead><tbody>{filas}</tbody></table></div>'
            '<p class="nota">Contraste: caso más favorable (píxel más oscuro contra el fondo dominante). Atención: porción de saliencia '
            'dividida entre porción de área; arriba de 1 atrae más que el promedio <span class="tag">MODELO</span>.</p></details>')


def armar(e, N):
    c = e.cfg
    M = json.loads(e.ruta("datos", "medicion.json").read_text(encoding="utf-8"))
    R = json.loads(e.ruta("datos", "agregado.json").read_text(encoding="utf-8"))
    AGG, A = R["agregado"], R["aciertos"]
    grupos = list(dict.fromkeys(p.get("grupo", "E") for p in c["pantallas"].values()))
    res = ""
    for g in grupos:
        tit = (N.get("grupos") or {}).get(g, {})
        res += f'<h3>{e_(tit.get("titulo", "Grupo " + g))}</h3>{parrafos(tit.get("texto"))}'
        res += _visor(e, M, g) + _zonas(e, M, g) + _aciertos(e, A, g)
        for q in c["preguntas"]:
            if not q.get("opciones") or q.get("solo_continuacion") or (q.get("solo") and g not in q["solo"]):
                continue
            qt = (N.get("preguntas") or {}).get(q["id"], {})
            res += (f'<h3>{e_(qt.get("titulo", q["texto"]))}</h3><p class="sub">{qt.get("texto", "")}</p>'
                    + _matriz(e, AGG, q, g))
        for k in c.get("continuaciones", []):
            if k.get("solo") and g not in k["solo"]:
                continue
            img = f'<div class="sheet"><img src="{img64(e.ruta(k["imagen"]), 520)}" alt="{e_(k["consigna"])}"><div>'
            res += f'<h3>Tras «{e_(k["consigna"])}»</h3>{img}'
            for qid in k["preguntas"]:
                q = next(x for x in c["preguntas"] if x["id"] == qid)
                if q.get("opciones"):
                    res += f'<p class="sub"><b>{e_(q["texto"])}</b></p>' + _matriz(e, AGG, q, g, momento=k["id"], modos=["completa"])
            res += "</div></div>"
    if R["n_por_bloque"].get("sensibilidad"):
        res += '<h3>Control de sensibilidad OCEAN</h3><p class="sub">Los perfiles base sin capa OCEAN. Si las respuestas no cambian, los hallazgos «por personalidad» bajan a confianza baja.</p>'
        for g in grupos:
            for q in c["preguntas"]:
                if q.get("correcta") and q.get("opciones") and (not q.get("solo") or g in q["solo"]) and not q.get("solo_continuacion"):
                    res += f'<p class="sub"><b>{e_(g)} · {e_(q["texto"])}</b></p>' + _matriz(e, AGG, q, g, bloque="sensibilidad",
                                                                                         modos=c["sensibilidad_ocean"].get("modos", ["vistazo"]))
    sin_cob = R.get("sin_cobertura") or []
    if sin_cob:
        res += ('<h3>Preguntas sin cobertura</h3><p class="sub">El perfil respondió que sus datos no alcanzan. Cuenta como vacío de la '
                'fuente, no como fallo de comprensión.</p>' + lista([f"{x['integrante']} · {x['pregunta']}: {x['n']} veces" for x in sin_cob]))
    n_total = R["n_sesiones"]
    pies = {"pantalla": "Las líneas marcan hasta dónde se ve sin desplazar en cada alto de pantalla.",
            "atencion": "Modelo de saliencia visual: predice hacia dónde tiran el contraste y el tamaño. Es igual para todos los perfiles y no es seguimiento ocular.",
            "lectura": f"Orden estimado de lectura. Naranja: entra en un vistazo de 5 segundos a {c.get('velocidad_vistazo', 3.5)} palabras por segundo. "
                       "Punteado: quedó a medias. Blanco: solo en lectura completa. Recuadro punteado: el perfil no la lee (letra chica o cerró al llegar a una acción)."}
    datos_js = dict(zonas=M["pantallas"], lectura=M["lectura"], pies=pies, pliegues=c.get("pliegues", [640, 800]),
                    vel=str(float(c.get("velocidad_vistazo", 3.5))))
    secciones = [
        ("panel", "Panel", "Quiénes respondieron", seccion_panel(e, N)),
        ("hipotesis", "Hipótesis", "Qué se puso a prueba", seccion_hipotesis(e, N)),
        ("resultados", "Resultados", N.get("resultados_titulo", "Qué entendió cada perfil"), res),
        ("firmeza", "Firmeza", "Qué tan firme es lo que dicen las sesiones", seccion_robustez(R, "comprension")),
        ("auditoria", "Auditoría", "Auditoría de UX writing", seccion_auditoria(e)),
        ("estilo", "Guía de estilo", "Textos frente a la guía de estilo del producto", seccion_estilo(e)),
        ("hallazgos", "Hallazgos", "Hallazgos y recomendaciones", seccion_hallazgos(N, n_total, False)),
        ("funciona", "Lo que funciona", "Lo que funciona y conviene conservar", lista(N.get("positivos"))),
        ("limites", "Límites", "Alcance y límites", AVISO_SINTETICO + lista(N.get("limitaciones"))
         + seccion_validar(e, N)),
        ("siguientes", "Próximos pasos", "Próximos pasos", lista(N.get("proximos_pasos"), True)),
        ("traza", "Trazabilidad", "Trazabilidad", seccion_trazabilidad(e, N)),
    ]
    franja = [(n_total, "sesiones"), (len(e.panel()), "perfiles"), (len(c["pantallas"]), "pantallas"),
              (len(N.get("hallazgos") or []), "hallazgos")]
    html_txt = pagina(e, N, secciones, datos_js, franja)
    filas = []
    for k, v in sorted(A.items()):
        b, g, var, m, mom, q = k.split("|")
        filas.append(f"| {g} | {var} | {m} | {mom} | {q} | {v['aciertos']} de {v['total']} |")
    cuerpo = ("## Aciertos por celda\n\n| Grupo | Variante | Modo | Momento | Pregunta | Aciertos |\n|---|---|---|---|---|---|\n"
              + "\n".join(filas))
    return html_txt, md_comun(e, N, cuerpo)
