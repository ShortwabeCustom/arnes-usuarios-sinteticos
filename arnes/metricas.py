"""Métricas de flujo que producto siempre pide: pasos, clics, campos solicitados, tiempo, validaciones,
cambios de canal, retoma de solicitud, visibilidad de estatus y distancia a la compra.

Cada métrica dice de dónde sale:
- [EVIDENCIA]  medida sobre la ruta real que recorrió el arnés (toques, pantallas, DOM, URL, espera del sistema).
- [MODELO]     el tiempo humano no se mide en una sesión sintética: se estima con un modelo tipo KLM (Card, Moran y
               Newell) declarado en `modelo_tiempo`, más la espera real del sistema. Es [SUPUESTO] en sus constantes.
- [INFERENCIA] detecciones por texto (pantallas de verificación, menciones de otro canal).
- [SIMULACIÓN] lo que dice el perfil (si sabe en qué paso va, esfuerzo percibido CES).

Del vault ([[metricas-ux]]): el tiempo en tarea solo es significativo junto con la tasa de éxito, por eso se
reporta para las sesiones que completan.
"""

from __future__ import annotations

import re
import statistics

TIEMPO = dict(palabras_por_segundo=3.5, decision_s=1.35, toque_s=0.4, tecla_s=0.3, relectura=0.25, velocidades=[2.5, 4.5])
VERIFICACION = r"\b(c[óo]digo|OTP|verific\w+|INE|identificaci[óo]n oficial|selfie|rostro|biom[ée]tric\w*|firma|comprobante)\b"
OTRO_CANAL = {
    "sucursal": r"\bsucursal(es)?\b", "llamada": r"\bll[aá]ma(nos|r)?\b|\bcall center\b|\btel[eé]fono de atenci[óo]n\b",
    "WhatsApp": r"\bwhats ?app\b", "app": r"\b(descarga|abre|usa) (la|nuestra) app\b|\bapp banco azteca\b",
    "correo": r"\b(correo|e-?mail)\b", "SMS": r"\bSMS\b|\bmensaje de texto\b", "visita": r"\bvisita (en|a) tu (domicilio|negocio)\b",
}
COMPLETAN = ("exito", "exito_con_friccion")


def _resumen(vals: list) -> dict | None:
    v = [x for x in vals if isinstance(x, (int, float))]
    if not v:
        return None
    num = lambda x: int(x) if float(x).is_integer() else round(x, 1)  # noqa: E731 — «7», no «7.0»
    return dict(mediana=num(statistics.median(v)), min=num(min(v)), max=num(max(v)), n=len(v))


def _tiempo_paso(p: dict, vista_antes: bool, cfg: dict, vps: float) -> float:
    pal = p.get("palabras") or 0
    lectura = pal / vps * (cfg["relectura"] if vista_antes else 1)
    a = p.get("accion") or {}
    t = lectura + (cfg["decision_s"] if p.get("perfil") else 0)
    if a.get("tipo") in ("tocar", "escribir"):
        t += cfg["toque_s"]
    if a.get("tipo") == "escribir":
        t += cfg["tecla_s"] * len(a.get("texto") or "")
    t += (p.get("espera_ms") or 0) / 1000
    return t


def sesion(s: dict, cfg_estudio: dict) -> dict:
    cfg = dict(TIEMPO, **(cfg_estudio.get("modelo_tiempo") or {}))
    manual = cfg_estudio.get("pantallas_info") or {}
    pasos = [p for p in s["pasos"] if not p.get("fin")]
    for p in s["pasos"]:  # datos cargados a mano (p. ej. Figma, donde no hay DOM)
        for k, v in (manual.get(p.get("pantalla")) or {}).items():
            if p.get(k) is None:
                p[k] = v if k != "texto" else None
            if k == "texto" and p.get("palabras") is None:
                p["palabras"] = len(str(v).split())
    acciones = [p.get("accion") or {} for p in pasos]
    toques = [a for a in acciones if a.get("tipo") in ("tocar", "escribir")]
    vistas, primera = [], {}
    for i, p in enumerate(s["pasos"]):
        if p.get("pantalla") not in primera:
            primera[p.get("pantalla")] = i
        vistas.append(p.get("pantalla") in [q.get("pantalla") for q in s["pasos"][:i]])
    tiempos = {str(v): [_tiempo_paso(p, vistas[i], cfg, v) for i, p in enumerate(s["pasos"])]
               for v in [cfg["palabras_por_segundo"]] + list(cfg["velocidades"])}
    base = tiempos[str(cfg["palabras_por_segundo"])]
    campos = [s["pasos"][i].get("campos") for i in primera.values()]
    textos = {p.get("pantalla"): p.get("texto_pantalla") or "" for p in s["pasos"] if p.get("texto_pantalla")}
    hosts = [h for h in dict.fromkeys(p.get("host") for p in s["pasos"] + [{"host": p.get("host_despues")} for p in pasos]) if h]
    paginas = max([p.get("paginas") or 1 for p in s["pasos"]] + [p.get("paginas_despues") or 1 for p in pasos])
    permisos = sorted({x for p in s["pasos"] for x in p.get("permisos") or []})
    menciones = sorted({canal for t in textos.values() for canal, pat in OTRO_CANAL.items() if re.search(pat, t, re.I)})
    verif = sorted(pid for pid, t in textos.items() if re.search(VERIFICACION, t, re.I))
    con_dato = [p for p in (s["pasos"][i] for i in primera.values()) if p.get("progreso_visible") is not None or p.get("texto_pantalla")]
    estatus = sum(1 for p in con_dato if p.get("progreso_visible"))
    sabe = [(p.get("perfil") or {}).get("progreso", {}).get("opcion") for p in pasos if (p.get("perfil") or {}).get("progreso")]
    completa = s.get("resultado") in COMPLETAN
    n_tot = len(s["pasos"])
    distancia = {}
    if completa:
        for pid, i in primera.items():
            distancia[pid] = dict(pasos=n_tot - 1 - i, tiempo_s=round(sum(base[i:]), 1),
                                  clics=sum(1 for p in s["pasos"][i:] if (p.get("accion") or {}).get("tipo") in ("tocar", "escribir")),
                                  campos=sum(s["pasos"][j].get("campos") or 0 for pp, j in primera.items() if j >= i))
    return dict(
        sesion=s["id"], tarea=s["tarea"], integrante=s["integrante"], resultado=s.get("resultado"), completa=completa,
        pasos=len(pasos), pantallas=len(primera),
        clics=len(toques), clics_sin_respuesta=sum(1 for p in pasos if p.get("respuesta") == "no"),
        intentos_fuera_de_zonas=sum(1 for p in pasos if p.get("respuesta") == "fuera_de_marcas"),
        campos=sum(c for c in campos if c) if any(c is not None for c in campos) else None,
        caracteres_escritos=sum(len(a.get("texto") or "") for a in toques),
        tiempo_estimado_s=round(sum(base), 1),
        tiempo_rango_s=[round(sum(v), 1) for k, v in tiempos.items() if k != str(cfg["palabras_por_segundo"])],
        espera_sistema_s=round(sum((p.get("espera_ms") or 0) for p in pasos) / 1000, 1),
        validaciones_disparadas=sum(1 for p in pasos if p.get("validacion_disparada")),
        mensajes_validacion=sorted({m for p in pasos for m in p.get("validacion_disparada") or []}),
        pantallas_verificacion=verif,
        cambios_dominio=max(0, len(hosts) - 1), dominios=hosts, pestanas_nuevas=max(0, paginas - 1), permisos=permisos,
        menciones_otro_canal=menciones,
        retoma=(s.get("retoma") or {}).get("resultado"),
        pantallas_con_estatus=estatus, pantallas_revisadas_estatus=len(con_dato),
        sabe_donde_va={k: sabe.count(k) for k in ("si", "mas_o_menos", "no")},
        ces=(s.get("ces") or {}).get("ces"),
        distancia_a_la_compra=distancia,
    )


def calcular(S: list[dict], cfg_estudio: dict) -> dict:
    por = [sesion(s, cfg_estudio) for s in S]
    tareas = {}
    for t in dict.fromkeys(x["tarea"] for x in por):
        xs = [x for x in por if x["tarea"] == t]
        comp = [x for x in xs if x["completa"]]
        tareas[t] = dict(
            sesiones=len(xs), completan=len(comp),
            pasos=_resumen([x["pasos"] for x in xs]), pantallas=_resumen([x["pantallas"] for x in xs]),
            clics=_resumen([x["clics"] for x in xs]), clics_sin_respuesta=_resumen([x["clics_sin_respuesta"] for x in xs]),
            campos=_resumen([x["campos"] for x in xs]),
            tiempo_completan_s=_resumen([x["tiempo_estimado_s"] for x in comp]),
            espera_sistema_s=_resumen([x["espera_sistema_s"] for x in xs]),
            validaciones_disparadas=_resumen([x["validaciones_disparadas"] for x in xs]),
            pantallas_verificacion=sorted({p for x in xs for p in x["pantallas_verificacion"]}),
            cambios_dominio=_resumen([x["cambios_dominio"] for x in xs]), dominios=sorted({d for x in xs for d in x["dominios"]}),
            pestanas_nuevas=_resumen([x["pestanas_nuevas"] for x in xs]), permisos=sorted({p for x in xs for p in x["permisos"]}),
            menciones_otro_canal=sorted({m for x in xs for m in x["menciones_otro_canal"]}),
            retoma={r: sum(1 for x in xs if x["retoma"] == r) for r in {x["retoma"] for x in xs if x["retoma"]}},
            estatus=dict(con_indicador=max((x["pantallas_con_estatus"] for x in xs), default=0),
                         pantallas=max((x["pantallas_revisadas_estatus"] for x in xs), default=0)),
            sabe_donde_va={k: sum(x["sabe_donde_va"][k] for x in xs) for k in ("si", "mas_o_menos", "no")},
            ces=_resumen([x["ces"] for x in xs]),
        )
    pantallas = {}
    for x in por:
        for pid, d in x["distancia_a_la_compra"].items():
            pantallas.setdefault(pid, []).append(d)
    distancia = {pid: {k: _resumen([d[k] for d in ds]) for k in ("pasos", "clics", "campos", "tiempo_s")} for pid, ds in pantallas.items()}
    return dict(sesiones=por, tareas=tareas, distancia_por_pantalla=distancia,
                modelo_tiempo=dict(TIEMPO, **(cfg_estudio.get("modelo_tiempo") or {})))
