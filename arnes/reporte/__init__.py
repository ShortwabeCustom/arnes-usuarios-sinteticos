"""Reporte autocontenido (HTML + Markdown) a partir de los datos del estudio y de narrativa.yaml.

El código pone las cifras, las tablas y los gráficos; la narrativa (titulares, hallazgos,
interpretaciones, recomendaciones) la escribe el investigador o el agente en narrativa.yaml.
Así una cifra nunca se escribe a mano dos veces: `arnes verificar` la recuenta.

Orden (prompt maestro OU-PWA, formato rediseñado): resumen → fuentes → panel → protocolo →
resultados → hallazgos → comparación de perfiles → recomendaciones → lo que funciona →
limitaciones → próximos pasos → trazabilidad. En cada bloque: resumen → interpretación →
detalle → evidencia.
"""

from __future__ import annotations

import base64
import html
import io
import json
import math
import re
from pathlib import Path

from .. import estandares as std
from .. import ocean as oc
from ..estudio import Estudio

AQUI = Path(__file__).resolve().parent
e_ = html.escape
SEV = {0: "Sin problema", 1: "Cosmético", 2: "Menor", 3: "Importante", 4: "Crítico"}
WALKTHROUGH = {1: "¿Intentará lograr el resultado correcto?", 2: "¿Notará que la acción correcta está disponible?",
               3: "¿Asociará la acción con el resultado que busca?", 4: "¿Verá que avanza hacia su objetivo?"}
CLASES_PRIORIDAD = ((48, "Crítico", "s4"), (24, "Alto", "s3"), (10, "Medio", "s2"), (0, "Bajo", "s1"))

CSS_EXTRA = """
.aviso{background:var(--dudabg);border:1px solid var(--duda);border-radius:12px;padding:14px 16px;margin:14px 0;max-width:820px}
.aviso b{color:var(--duda)}
.franja{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:20px;font-size:14px;color:var(--porttx2)}.franja b{color:#fff;font-size:18px}
.oc2{display:grid;gap:5px;margin:.7rem 0}.oc2 .fila{display:grid;grid-template-columns:150px minmax(0,1fr) 92px;gap:8px;align-items:center;font-size:13px}
.oc2 i{display:block;height:7px;border-radius:4px;background:var(--borde);position:relative;overflow:hidden}
.oc2 i::after{content:"";position:absolute;inset:0 auto 0 0;width:var(--v);background:var(--verde)}
.oc2 em{font-style:normal;color:var(--tx2);font-variant-numeric:tabular-nums}
.radar{display:grid;grid-template-columns:minmax(0,420px) minmax(0,1fr);gap:24px;align-items:center}
.radar svg{width:100%;height:auto}
.hgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:8px 0 10px}
.hgrid>div{background:var(--pag);border-radius:10px;padding:10px 12px;font-size:14.5px}.hgrid b{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--tx2)}
.embudo td.c{text-align:center;font-weight:700}.e0{background:var(--grisbg)}.e1{background:var(--okbg)}.e2{background:var(--dudabg)}.e3,.e4{background:var(--malbg);color:var(--mal)}
.linea{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.linea figure{margin:0;background:var(--sup);border:1px solid var(--borde);border-radius:10px;padding:8px;font-size:12.5px}
.linea img{width:100%;border-radius:6px;display:block;margin-bottom:6px}
.linea .r{font-weight:700}.linea .no{color:var(--mal)}.linea .si{color:var(--ok)}
.mv{display:grid;gap:8px}.mv div{background:var(--sup);border:1px solid var(--borde);border-left:6px solid var(--gris);border-radius:10px;padding:10px 14px}
.mv .verde{border-left-color:var(--ok)}.mv .amarillo{border-left-color:var(--duda)}.mv .rojo{border-left-color:var(--mal)}
.tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.05em;padding:1px 6px;border-radius:4px;background:var(--grisbg);color:var(--gris);margin-right:4px}
thead th small{display:block;font-weight:400;text-transform:none;letter-spacing:0}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}.galeria figure{margin:0}.galeria img{width:100%;border-radius:10px;border:1px solid var(--borde)}
@media (max-width:820px){.radar,.hgrid{grid-template-columns:minmax(0,1fr)}.oc2 .fila{grid-template-columns:110px minmax(0,1fr) 80px}}
"""


# ---------------------------------------------------------------------------------------------
# utilidades


def img64(ruta: Path, ancho: int | None = None, calidad: int = 82) -> str:
    from PIL import Image

    im = Image.open(ruta).convert("RGB")
    if ancho and im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=calidad)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def parrafos(t) -> str:
    if not t:
        return ""
    if isinstance(t, list):
        return "".join(f"<p>{x}</p>" for x in t)
    return "".join(f"<p>{x.strip()}</p>" for x in str(t).split("\n\n") if x.strip())


def lista(xs, ordenada=False) -> str:
    if not xs:
        return ""
    t = "ol" if ordenada else "ul"
    return f"<{t}>" + "".join(f"<li>{x}</li>" for x in xs) + f"</{t}>"


def prioridad(h: dict, n_total: int) -> tuple[int, int, int, int, str, str]:
    """Priority = Frequency (1–5) × Severity (1–4) × Business Impact (1–5). Prompt maestro OU-PWA §17."""
    afect = len(h.get("sesiones") or h.get("integrantes") or [])
    f = max(1, math.ceil(5 * afect / n_total)) if n_total and afect else h.get("frecuencia_1a5", 1)
    s = max(1, int(h.get("severidad", 1)))
    i = int(h.get("impacto_negocio", 3))
    sc = f * s * i
    nom, cls = next((n, c) for u, n, c in CLASES_PRIORIDAD if sc >= u)
    return f, s, i, sc, nom, cls


# ---------------------------------------------------------------------------------------------
# componentes comunes


def radar_svg(panel) -> str:
    """Radar OCEAN: media y rango mín–máx. Etiquetas ancladas hacia afuera para que no se corten."""
    vals = {k: [it.ocean[k] for it in panel if it.ocean] for k in "OCEAN"}
    if not any(vals.values()):
        return ""
    W, H, cx, cy, R = 520, 420, 260, 210, 135
    ang = [-math.pi / 2 + i * 2 * math.pi / 5 for i in range(5)]
    pt = lambda i, v: (cx + R * v / 100 * math.cos(ang[i]), cy + R * v / 100 * math.sin(ang[i]))  # noqa: E731
    poly = lambda vs: " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, v) for i, v in enumerate(vs)))  # noqa: E731
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cobertura OCEAN del panel: media y rango por rasgo">']
    for r in (25, 50, 75, 100):
        s.append(f'<polygon points="{poly([r] * 5)}" fill="none" stroke="var(--borde)" stroke-width="1"/>')
    for i, k in enumerate("OCEAN"):
        x, y = pt(i, 100)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--borde)"/>')
        lx, ly = pt(i, 116)
        anc = "middle" if abs(math.cos(ang[i])) < 0.2 else ("start" if math.cos(ang[i]) > 0 else "end")
        s.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="{anc}" font-size="13" font-weight="650" fill="var(--tx)">'
                 f'{oc.RASGOS[k][0]}</text>')
    mx = [max(vals[k]) for k in "OCEAN"]
    mn = [min(vals[k]) for k in "OCEAN"]
    me = [sum(vals[k]) / len(vals[k]) for k in "OCEAN"]
    s.append(f'<polygon points="{poly(mx)}" fill="var(--verde)" fill-opacity=".14" stroke="var(--verde)" stroke-dasharray="4 3"/>')
    s.append(f'<polygon points="{poly(mn)}" fill="var(--pag)" fill-opacity=".9" stroke="var(--verde)" stroke-dasharray="4 3"/>')
    s.append(f'<polygon points="{poly(me)}" fill="none" stroke="var(--b8)" stroke-width="2.5"/>')
    s.append("</svg>")
    return "".join(s)


def tarjeta_integrante(it, extra: dict | None = None) -> str:
    extra = extra or {}
    oc_html = ""
    if it.ocean:
        oc_html = '<div class="oc2" aria-label="Personalidad OCEAN">' + "".join(
            f'<div class="fila"><span>{oc.RASGOS[k][0]}</span><i style="--v:{it.ocean[k]}%"></i>'
            f'<em>{it.ocean[k]}/100 · {oc.nivel(it.ocean[k])}</em></div>' for k in "OCEAN") + "</div>"
        if it.ocean_supuesto:
            oc_html += '<p class="nota"><span class="tag">SUPUESTO</span>Valores OCEAN de diseño del panel, sin fuente.</p>'
    dl = "".join(f"<dt>{e_(k)}</dt><dd>{v}</dd>" for k, v in (("Qué entiende", extra.get("entiende")),
                                                             ("Dónde se rompe", extra.get("rompe")),
                                                             ("Reglas y rasgos que más pesaron", extra.get("reglas"))) if v)
    cita = f'<blockquote>{e_(extra["cita"])} <span class="tag">SIMULACIÓN</span></blockquote>' if extra.get("cita") else ""
    sub = " · ".join(str(x) for x in (it.segmento, f"{it.edad} años" if it.edad else None, it.genero,
                                      "variante del perfil " + it.perfil if it.variante else "perfil base " + it.perfil) if x)
    return f'<article class="perfil"><h3>{e_(it.id)} · {e_(it.nombre)}</h3><div class="segm">{e_(sub)}</div>{oc_html}{cita}<dl>{dl}</dl></article>'


def seccion_panel(e: Estudio, N: dict) -> str:
    panel = e.panel()
    perf = N.get("perfiles") or {}
    tarjetas = "".join(tarjeta_integrante(it, perf.get(it.id)) for it in panel)
    rad = radar_svg(panel)
    div = oc.diversidad({it.id: it.ocean for it in panel})
    cob = ""
    if rad:
        filas = "".join(f"<li><b>{v['rasgo']}</b>: {v['min']}–{v['max']} (media {v['media']}). "
                        f"{'Vacíos: ' + '; '.join(v['vacios']) + '.' if v['vacios'] else 'Cobertura amplia.'}</li>"
                        for v in div["rasgos"].values())
        gem = (f"<p class='nota'>Perfiles casi idénticos en OCEAN: {', '.join(f'{a} y {b}' for a, b, _ in div['gemelos'])}.</p>"
               if div["gemelos"] else "")
        cob = (f'<h3>Cobertura de personalidad del panel</h3><div class="radar"><div>{rad}</div><div>'
               f'<p class="nota">Línea gruesa: media del panel. Banda punteada: rango entre el valor más bajo y el más alto de cada rasgo. '
               f'Los valores OCEAN no se midieron: son de diseño del panel <span class="tag">SUPUESTO METODOLÓGICO</span>.</p>'
               f'<ul>{filas}</ul>{gem}{parrafos(N.get("cobertura_texto"))}</div></div>')
    b = e.biblioteca
    return (f'<p class="sub">{len(panel)} perfiles de la biblioteca «{e_(b.meta["nombre"])}» (panel «{e_(e.cfg["panel"])}»). '
            f'{e_(b.meta.get("base", ""))}. Cada perfil responde desde su system prompt y sus reglas conductuales; '
            f'cuando una pregunta cae fuera de lo que su fuente cubre, contesta «sin cobertura».</p>'
            f'<div class="perfiles">{tarjetas}</div>{seccion_demograficos(panel)}{cob}')


def seccion_demograficos(panel) -> str:
    """Los 4 datos que UiX pide en toda investigación, con su evidencia. Describen el panel: no lo segmentan."""
    cols = (("edad", "Edad (generación)"), ("genero", "Género"), ("region", "Región"), ("ocupacion", "Ocupación"))

    def celda(v):
        if not v["valor"]:
            return f'<td><span class="tag">{e_(v["evidencia"])}</span> <small>{e_(v["detalle"])}</small></td>'
        det = f' <small>{e_(v["detalle"])}</small>' if v["detalle"] else ""
        tag = f' <span class="tag">{e_(v["evidencia"])}</span>' if v["evidencia"] else ""
        return f"<td>{e_(v['valor'])}{det}{tag}</td>"

    filas = "".join(f'<tr><th scope="row">{e_(it.nombre)}</th>' + "".join(celda(std.demograficos(it)[k]) for k, _ in cols) + "</tr>"
                    for it in panel)
    return ('<h3>Datos demográficos del panel</h3><div class="tabla-wrap"><table><thead><tr><th>Perfil</th>'
            + "".join(f"<th>{n}</th>" for _, n in cols) + f"</tr></thead><tbody>{filas}</tbody></table></div>"
            '<p class="nota">Categorías de la guía de demográficos de UiX (generación, género, región de México, ocupación), con la '
            'evidencia del User Persona. Describen a los perfiles para comparar estudios; los perfiles se definen por comportamiento, '
            'no por estos datos.</p>')


def seccion_validar(e: Estudio, N: dict) -> str:
    """Qué validar con personas y con cuántas, según la tabla de tamaño de muestra de UiX."""
    met = (e.cfg.get("uix") or {}).get("metodologia") or std.std()["naming"]["por_metodo"].get(e.metodo)
    m = std.muestra(met) if met else None
    n = (f'<p class="nota">Para validar estos hallazgos con personas en una {e_(std.std()["naming"]["metodologias"][met].lower())}, '
         f'UiX recomienda {m[0]}: {e_(m[1].lower())}. Las corridas sintéticas no cuentan para esa muestra.</p>') if m else ""
    xs = N.get("validar_con_personas")
    return (("<h3>Para validar con personas</h3>" + lista(xs)) if xs else "") + n if xs or n else ""


def seccion_hipotesis(e: Estudio, N: dict) -> str:
    hs = e.cfg.get("hipotesis") or []
    if not hs:
        return ""
    res = {h["id"]: h for h in N.get("hipotesis_resultado") or []}
    est = {"se_sostiene": ("ok", "Se sostiene"), "se_cae": ("mal", "Se cae"), "no_concluyente": ("duda", "No concluyente")}
    filas = ""
    for h in hs:
        r = res.get(h["id"], {})
        c, t = est.get(r.get("estado"), ("gris", "Sin evaluar"))
        filas += (f'<tr><th scope="row">{e_(h["id"])}</th><td>{e_(h["texto"])}<small class="nota"><br>Se sostiene si: '
                  f'{e_(h.get("se_sostiene_si", "—"))} · Se cae si: {e_(h.get("se_cae_si", "—"))}</small></td>'
                  f'<td><span class="pt {c}" style="width:auto;border-radius:6px;padding:0 8px">{t}</span></td>'
                  f'<td>{r.get("evidencia", "")}</td></tr>')
    return ('<div class="tabla-wrap"><table><thead><tr><th>#</th><th>Hipótesis</th><th>Resultado</th><th>Evidencia</th></tr></thead>'
            f'<tbody>{filas}</tbody></table></div>')


def seccion_hallazgos(N: dict, n_total: int, con_prioridad: bool) -> str:
    out = ""
    hs = sorted(N.get("hallazgos") or [], key=lambda h: -int(h.get("severidad", 0)))
    for h in hs:
        sev = int(h.get("severidad", 0))
        pr = ""
        if con_prioridad:
            f, s, i, sc, nom, _ = prioridad(h, n_total)
            pr = f" · prioridad {nom} ({f}×{s}×{i} = {sc})"
        afect = h.get("sesiones") or h.get("integrantes") or []
        frec = f" · {len(afect)} de {n_total}" if afect and n_total else ""
        tags = "".join(f'<span class="tag">{e_(t)}</span>' for t in h.get("etiquetas", []))
        opo = std.oportunidades().get(h.get("oportunidad") or "")
        tags = (f'<span class="tag">Oportunidad: {e_(opo)}</span>' if opo else "") + tags
        cw = f"Cognitive walkthrough, pregunta {h['walkthrough']}: {WALKTHROUGH[int(h['walkthrough'])]}" if h.get("walkthrough") else None
        marco = " · ".join(x for x in (h.get("heuristica"), f"WCAG {h['wcag']}" if h.get("wcag") else None, cw) if x)
        rw = "".join(f"<tr><td>{e_(a)}</td><td>{e_(r)}</td><td>{e_(z)}</td></tr>" for a, r, z in h.get("reescritura", []))
        rw = (f'<div class="tabla-wrap"><table class="rw"><thead><tr><th>Actual</th><th>Recomendado</th><th>Razón</th></tr></thead>'
              f'<tbody>{rw}</tbody></table></div>') if rw else ""
        out += (f'<details class="h s{sev}" id="{e_(h.get("id", ""))}"><summary><span class="sev">{SEV[sev]}</span>'
                f'<span class="ht">{e_(h.get("id", ""))} · {e_(h["titulo"])}</span><span class="donde">{e_(h.get("donde", ""))}{frec}{pr}'
                f' · confianza {e_(h.get("confianza", "—"))}</span></summary><div class="hb">'
                f'<div class="hgrid"><div><b>Hallazgo</b>{h.get("hallazgo", "")}</div><div><b>Interpretación</b>{h.get("interpretacion", "")}</div>'
                f'<div><b>Recomendación</b>{h.get("recomendacion", "")}</div></div>'
                f'<p class="ev"><b>Evidencia.</b> {h.get("evidencia", "")}</p>'
                f'{f"<p class=ev><b>Marco.</b> {e_(marco)}</p>" if marco else ""}{rw}<p>{tags}</p></div></details>')
    return out


def seccion_priorizacion(N: dict, n_total: int) -> str:
    hs = N.get("hallazgos") or []
    if not hs:
        return ""
    filas = sorted(((prioridad(h, n_total), h) for h in hs), key=lambda x: x[0][3], reverse=True)
    t = "".join(f'<tr class="{cls}"><th scope="row"><a href="#{e_(h.get("id", ""))}">{e_(h.get("id", ""))}</a> {e_(h["titulo"])}</th>'
                f'<td class="n">{f}</td><td class="n">{s}</td><td class="n">{i}</td><td class="n"><b>{sc}</b></td>'
                f'<td><span class="sev">{nom}</span></td><td>{e_(std.oportunidades().get(h.get("oportunidad") or "", "—"))}</td></tr>'
                for (f, s, i, sc, nom, cls), h in filas)
    return ('<div class="tabla-wrap"><table><thead><tr><th>Problema</th><th>Frecuencia 1–5</th><th>Severidad 1–4</th>'
            '<th>Impacto 1–5</th><th>Puntaje</th><th>Prioridad</th><th>Oportunidad</th></tr></thead>'
            f'<tbody>{t}</tbody></table></div><p class="nota">Puntaje = frecuencia × severidad × impacto de negocio. '
            'Frecuencia: proporción de sesiones afectadas llevada a 1–5. Crítico ≥ 48 · Alto ≥ 24 · Medio ≥ 10. '
            'Oportunidad: clasificación del template de protocolo de UiX (Mantener · Mejorar · Incorporar · Hacer diferente).</p>')


def seccion_trazabilidad(e: Estudio, N: dict) -> str:
    st = e.estado()
    ses = [json.loads(p.read_text(encoding="utf-8")) for p in e.sesiones_dir.glob("*.json")] if e.sesiones_dir.exists() else []
    modelos = sorted({s.get("modelo_id") or "" for s in ses} - {""})
    for s in ses:
        for p in s.get("pasos", []):
            if p.get("modelo_id"):
                modelos = sorted(set(modelos) | {p["modelo_id"]})
    fases = "".join(f"<li><b>{e_(f)}</b> · {v['t']}</li>" for f, v in st.get("fases", {}).items())
    bib = st.get("biblioteca", {})
    fuentes = "".join(f"<li><b>{e_(x.get('nombre', ''))}</b> — {e_(x.get('uso', ''))}<br><small>{e_(x.get('ruta', ''))}</small></li>"
                      for x in N.get("fuentes") or [])
    tec = lista(N.get("limitaciones_tecnicas"))
    return (f'<div class="metodo"><p><b>Biblioteca:</b> {e_(bib.get("id", ""))} · huella {e_(bib.get("huella", ""))} · panel {e_(bib.get("panel", ""))}</p>'
            f'<p><b>Sesiones:</b> {len(ses)} guardadas · {e_(e.texto_consumo())}</p>'
            f'<p><b>Modelos:</b> {e_(", ".join(modelos) or "—")}</p>'
            f'<p><b>Fuentes consultadas:</b></p><ul>{fuentes}</ul><p><b>Fases ejecutadas:</b></p><ul>{fases}</ul>'
            f'{"<p><b>Limitaciones técnicas:</b></p>" + tec if tec else ""}'
            f'<p><b>Carpeta del estudio:</b> {e_(str(e.dir))}</p></div>')


def seccion_robustez(R: dict, metodo: str) -> str:
    """«Creer en lo que se repite»: estabilidad entre corridas, brechas con intervalo, homogeneidad del panel."""
    out = ('<p class="sub">Del vault ([[investigacion-con-usuarios-sinteticos]]): con muestras chicas dos opciones cercanas no se '
           'distinguen; confiar en brechas grandes y en lo que se repite entre corridas. Las corridas no son población.</p>')
    if metodo == "comprension":
        est = R.get("estabilidad") or {}
        if est.get("global_") is not None:
            out += (f'<p><b>Estabilidad entre corridas:</b> {est["global_"]:.0%} de coincidencia media de cada perfil consigo mismo. '
                    f'{len(est["inestables"])} perfil-celdas cambian de respuesta.</p>')
            if est["inestables"]:
                out += lista([f"{e_(x['clave'].replace('|', ' · '))}: {e_(', '.join(x['respuestas']))}" for x in est["inestables"][:12]])
        else:
            out += '<div class="aviso"><b>Una sola corrida por celda.</b> No se puede saber qué se repite: tratar cada resultado como señal, no como patrón.</div>'
        cmps = R.get("comparaciones") or []
        if cmps:
            filas = "".join(
                f'<tr><th scope="row">{e_(" · ".join(c["a"].split("|")[1:2] + c["a"].split("|")[3:]))}</th>'
                f'<td>{e_(c["a"].split("|")[2])} {c["pa"]:.0%} <small class="nota">[{c["ic_a"][0]:.0%}–{c["ic_a"][1]:.0%}]</small></td>'
                f'<td>{e_(c["b"].split("|")[2])} {c["pb"]:.0%} <small class="nota">[{c["ic_b"][0]:.0%}–{c["ic_b"][1]:.0%}]</small></td>'
                f'<td class="n">{abs(c["brecha"]) * 100:.0f} pts</td><td><span class="sev" style="background:var(--{"okbg" if c["clara"] else "grisbg"});'
                f'color:var(--{"ok" if c["clara"] else "gris"})">{"Clara" if c["clara"] else "No concluyente"}</span></td></tr>'
                for c in sorted(cmps, key=lambda c: -abs(c["brecha"])))
            out += ('<h3>Diferencias entre variantes</h3><div class="tabla-wrap"><table><thead><tr><th>Pregunta · modo · momento</th>'
                    '<th>Variante</th><th>Variante</th><th>Brecha</th><th>Lectura</th></tr></thead>'
                    f'<tbody>{filas}</tbody></table></div><p class="nota">Aciertos sobre corridas con intervalo de Wilson al 95%. '
                    '«Clara» solo si los intervalos no se tocan.</p>')
        al = (R.get("homogeneidad") or {}).get("alertas", [])
    else:
        rb = R.get("robustez") or {}
        if rb.get("con_repeticion"):
            out += f'<p><b>Resultado repetido entre corridas:</b> {rb["estables"]} de {rb["con_repeticion"]} perfil-tareas.</p>'
        else:
            out += '<div class="aviso"><b>Una sola corrida por perfil y tarea.</b> Lo que hizo cada perfil es señal, no patrón.</div>'
        al = rb.get("alertas", [])
    for a in al:
        out += f'<div class="aviso"><b>Atención.</b> {e_(a)}</div>'
    return out


def seccion_auditoria(e: Estudio) -> str:
    f = e.ruta("datos", "auditoria.json")
    if not f.exists():
        return ""
    A = json.loads(f.read_text(encoding="utf-8"))
    filas = "".join(
        f'<tr><th scope="row">{e_(x["pantalla"])}<small>{e_(x["zona"])}</small></th><td><b>{e_(x["criterio"])}</b> {e_(x["nombre_criterio"])}</td>'
        f'<td class="n">{x["evaluadores"]} de {x["de"]}</td><td class="n">{x["severidad_media"]}</td><td>{e_(x["problemas"][0])}</td>'
        f'<td>{e_(x["recomendaciones"][0])}</td></tr>' for x in A["consolidado"] if x["consenso"])
    revisar = sum(not x["consenso"] for x in A["consolidado"])
    return (f'<p class="sub">{A["evaluadores"]} evaluaciones expertas independientes por pantalla, consolidadas como en una evaluación '
            f'heurística ([[evaluacion-heuristica]]). Se muestra lo que marcaron {A["umbral_consenso"]} o más; {revisar} observaciones '
            'de un solo evaluador quedan en datos/auditoria.json para revisar. <span class="tag">INFERENCIA</span></p>'
            '<div class="tabla-wrap"><table><thead><tr><th>Pantalla · zona</th><th>Criterio</th><th>Evaluadores</th><th>Severidad</th>'
            f'<th>Problema</th><th>Recomendación</th></tr></thead><tbody>{filas}</tbody></table></div>')


def seccion_estilo(e: Estudio) -> str:
    f = e.ruta("datos", "estilo.json")
    if not f.exists():
        return ""
    G = json.loads(f.read_text(encoding="utf-8"))
    hs = sorted(G["hallazgos"], key=lambda x: (x["nivel"] != "error", x["pantalla"], x["regla"]))
    filas = "".join(f'<tr><th scope="row">{e_(x["pantalla"])}<small>{e_(x["zona"])}</small></th>'
                    f'<td><span class="sev" style="background:var(--{"malbg" if x["nivel"] == "error" else "dudabg"});'
                    f'color:var(--{"mal" if x["nivel"] == "error" else "duda"})">{"Error" if x["nivel"] == "error" else "Revisar"}</span></td>'
                    f'<td><b>{e_(x["regla"])}</b> {e_(x["nombre"])}<small class="nota"><br>{e_(x["fuente"])}</small></td>'
                    f'<td>«{e_(x["fragmento"])}»</td></tr>' for x in hs)
    tabla = ('<div class="tabla-wrap"><table><thead><tr><th>Pantalla · zona</th><th>Nivel</th><th>Regla</th><th>Texto</th></tr></thead>'
             f'<tbody>{filas}</tbody></table></div>') if hs else "<p>Ningún texto contradice las reglas verificables de la guía.</p>"
    contra = ("<details class='plano'><summary>Contradicciones dentro de la propia guía</summary>" + lista(G.get("contradicciones_guia"))
              + "</details>") if G.get("contradicciones_guia") else ""
    return (f'<p class="sub">{G["textos"]} textos revisados contra «{e_(G["nombre_guia"])}», las reglas que se pueden comprobar con '
            'un patrón. El tono y la cercanía los evalúan los evaluadores de la auditoría (criterios G). <span class="tag">EVIDENCIA</span></p>'
            f'{tabla}{contra}')


AVISO_SINTETICO = ('<div class="aviso"><b>Investigación sintética.</b> Los resultados vienen de perfiles sintéticos construidos sobre '
                   'evidencia, no de personas. Son hipótesis de UX a validar con usuarios reales: no reportar sus proporciones como '
                   'si fueran de la población.</div>')


# ---------------------------------------------------------------------------------------------
# armado


def pagina(e: Estudio, N: dict, secciones: list[tuple[str, str, str, str]], datos_js: dict | None = None,
           franja: list[tuple[str, str]] | None = None) -> str:
    c = e.cfg
    css = (AQUI / "base.css").read_text(encoding="utf-8") + CSS_EXTRA
    if (c.get("marca") or {}).get("color"):
        css += f":root{{--port2:{c['marca']['color']}}}"
    kpis = "".join(f'<div class="kpi"><div class="v {k.get("tono", "")}">{e_(str(k["valor"]))}</div><div class="e">{e_(k["etiqueta"])}</div>'
                   f'<div class="d">{e_(k.get("detalle", ""))}</div></div>' for k in N.get("kpis") or [])
    chips = "".join(f'<span class="chip {"si" if x.get("si", True) else "no"}">{e_(x["texto"])}</span>' for x in N.get("decision") or [])
    fr = "".join(f"<span><b>{e_(str(v))}</b> {e_(t)}</span>" for v, t in franja or [])
    nav = "".join(f'<a href="#{i}">{e_(n)}</a>' for i, n, _, _ in secciones)
    cuerpo = "".join(f'<section id="{i}"><h2>{e_(t)}</h2>{h}</section>' for i, _, t, h in secciones if h)
    js = ""
    if datos_js is not None:
        js = (f"<script>const D = {json.dumps(datos_js, ensure_ascii=False)};</script>"
              f"<script>{(AQUI / 'visor.js').read_text(encoding='utf-8')}</script>")
    from ..conocimiento import titulo

    cuerpo = re.sub(r"\[\[([^\]|]+)\]\]", lambda m: f'<cite title="Nota del vault de conocimiento">{e_(titulo(m.group(1)))}</cite>', cuerpo)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e_(N.get("titulo_corto") or c.get("titulo", e.dir.name))}</title>
<style>{css}</style>
</head>
<body>
<header class="portada"><div class="env">
<div class="sello">Investigación UX sintética · {e_(c.get("producto", ""))} · {e_(str(c.get("fecha", "")))}</div>
<h1>{e_(N.get("titular") or c.get("titulo", ""))}</h1>
<p class="veredicto">{N.get("veredicto", "")}</p>
<div class="decision">{chips}</div>
<div class="franja">{fr}</div>
<p class="firma">{e_(c.get("titulo", ""))} · {e_(c.get("autor", ""))}</p>
</div></header>
<nav class="pills" aria-label="Secciones"><div class="env">{nav}</div></nav>
<main class="env">
<section id="resumen"><h2>Resumen</h2>{AVISO_SINTETICO}<div class="kpis">{kpis}</div>{f'<p class="nota">{e_(N["kpis_nota"])}</p>' if N.get("kpis_nota") else ""}{lista(N.get("resumen"), True)}</section>
{cuerpo}
</main>
<footer class="pie-inv"><div class="env"><span><b>Arnés de investigación UX sintética</b> · reporte generado desde los datos del estudio</span><span>Estudio: {e_(e.entregable(al_construir=True))}</span></div></footer>
{js}
</body>
</html>
"""


def construir(e: Estudio) -> str:
    from importlib import import_module

    N = e.narrativa()
    mod = import_module(f".{e.metodo}", __package__)
    html_txt, md = mod.armar(e, N)
    nombre = e.entregable(al_construir=True)
    salida = e.ruta("reporte", f"{nombre}.html")
    salida.write_text(html_txt, encoding="utf-8")
    e.ruta("reporte", f"{nombre}.md").write_text(md, encoding="utf-8")
    e.marcar("reporte", html=str(salida.relative_to(e.dir)), kb=round(len(html_txt.encode()) / 1024))
    return f"{salida}  ({round(len(html_txt.encode()) / 1024)} KB)"


# ---------------------------------------------------------------------------------------------
# Markdown (mismo contenido sustantivo, sin gráficos interactivos)


def md_comun(e: Estudio, N: dict, cuerpo: str) -> str:
    c = e.cfg
    panel = e.panel()
    filas = "\n".join(f"| {it.id} | {it.nombre} | {it.segmento} | " + " | ".join(str((it.ocean or {}).get(k, "—")) for k in "OCEAN") + " |"
                      for it in panel)
    hs = sorted(N.get("hallazgos") or [], key=lambda h: -int(h.get("severidad", 0)))
    hal = "\n\n".join(f"### {h.get('id', '')} · {h['titulo']}\n\n**Severidad:** {h.get('severidad')} ({SEV[int(h.get('severidad', 0))]}) · "
                      f"**Confianza:** {h.get('confianza', '—')}\n\n**Hallazgo.** {h.get('hallazgo', '')}\n\n**Interpretación.** "
                      f"{h.get('interpretacion', '')}\n\n**Recomendación.** {h.get('recomendacion', '')}"
                      + (f" **Oportunidad:** {std.oportunidades()[h['oportunidad']]}." if h.get("oportunidad") in std.oportunidades() else "")
                      + f"\n\n**Evidencia.** {h.get('evidencia', '')}"
                      for h in hs)
    li = lambda xs: "\n".join(f"- {x}" for x in xs or [])  # noqa: E731
    dm = lambda v: " ".join(x for x in (v["valor"], f"({v['detalle']})" if v["detalle"] else "", f"[{v['evidencia']}]" if v["evidencia"] else "") if x)  # noqa: E731
    demo = "\n".join(f"| {it.nombre} | " + " | ".join(dm(v) for v in std.demograficos(it).values()) + " |" for it in panel)
    return f"""# {N.get('titular') or c.get('titulo')}

**Estudio:** {c.get('titulo')}  ·  **Fecha:** {c.get('fecha')}  ·  **Método:** {e.metodo}
**Biblioteca:** {c.get('biblioteca')} · panel {c.get('panel')} ({len(panel)} perfiles)
**Tipo de investigación:** simulación UX con usuarios sintéticos — no sustituye investigación con usuarios reales.

{N.get('veredicto', '')}

## Resumen

{li(f"**{k['valor']}** {k['etiqueta']} — {k.get('detalle', '')}" for k in N.get('kpis') or [])}

{li(N.get('resumen'))}

## Panel

| ID | Nombre | Segmento | O | C | E | A | N |
|---|---|---|---:|---:|---:|---:|---:|
{filas}

**Datos demográficos (categorías de UiX, con su evidencia):**

| Perfil | Edad (generación) | Género | Región | Ocupación |
|---|---|---|---|---|
{demo}

{cuerpo}

## Hallazgos

{hal}

## Lo que funciona

{li(N.get('positivos'))}

## Limitaciones

{li(N.get('limitaciones'))}

## Para validar con personas

{li(N.get('validar_con_personas'))}

{re.sub(r"<[^>]+>", "", seccion_validar(e, N).split("</ul>")[-1]).strip()}

## Próximos pasos

{li(N.get('proximos_pasos'))}

## Trazabilidad

- Carpeta: `{e.dir}`
- Consumo: {e.texto_consumo()}
- Fuentes:
{chr(10).join(f"  - {x.get('nombre')} — {x.get('ruta', '')}" for x in N.get('fuentes') or [])}
"""
