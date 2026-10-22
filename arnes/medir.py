"""Medición de pantallas estáticas [EVIDENCIA] y atención predicha [MODELO].

Consolida `datos/medir.py` de los dos estudios de recompra. Por zona de lectura (AOI):
alto de línea en px, contraste (caso más favorable), visibilidad sobre cada pliegue, y porción de
saliencia visual. El orden de lectura estimado combina el rango de saliencia con la posición
vertical, y pone primero lo que se ve sin desplazar.

Límite que se declara siempre: la saliencia predice hacia dónde tiran el contraste y el tamaño, no
lo que una persona busca, y es igual para todos los perfiles. No es seguimiento ocular.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

ROLES = {"titular", "monto", "accion", "enlace", "nota", "ilustracion", "cuerpo", "tarjeta", "estado", "otro"}


def palabras(texto: str | None) -> int:
    return len(texto.split()) if texto else 0


def _lum(c) -> float:
    v = np.array(c[:3], float) / 255
    v = np.where(v <= 0.03928, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def contraste(a: np.ndarray, caja) -> float:
    """Contraste WCAG entre el color dominante de la caja (fondo) y el píxel más alejado (texto)."""
    x0, y0, x1, y1 = caja
    seg = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3).astype(int)
    q = (seg // 8) * 8
    vals, n = np.unique(q, axis=0, return_counts=True)
    bg = vals[n.argmax()] + 4
    txt = seg[np.abs(seg - bg).sum(axis=1).argmax()]
    l1, l2 = sorted((_lum(bg), _lum(txt)), reverse=True)
    return round((l1 + 0.05) / (l2 + 0.05), 2)


def alto_banda(a: np.ndarray, caja) -> int:
    """Alto de línea de texto en px: mediana de las bandas horizontales con tinta."""
    x0, y0, x1, y1 = caja
    seg = a[y0:y1 + 1, x0:x1 + 1].astype(int)
    med = np.median(seg.reshape(-1, 3), axis=0)
    on = (np.abs(seg - med).sum(axis=2) > 90).sum(axis=1) >= 2
    runs, c = [], 0
    for v in on:
        if v:
            c += 1
        elif c:
            runs.append(c)
            c = 0
    if c:
        runs.append(c)
    runs = [r for r in runs if r >= 6]
    return int(np.median(runs)) if runs else 0


def saliencia(bgr: np.ndarray) -> np.ndarray:
    """Promedio normalizado de residuo espectral y grano fino (OpenCV), suavizado."""
    if cv2 is None:
        raise RuntimeError("Falta opencv-contrib-python-headless")
    sr = cv2.saliency.StaticSaliencySpectralResidual_create().computeSaliency(bgr)[1]
    fg = cv2.saliency.StaticSaliencyFineGrained_create().computeSaliency(bgr)[1]
    n = lambda m: (m - m.min()) / (m.max() - m.min() + 1e-9)  # noqa: E731
    s = (n(cv2.GaussianBlur(sr.astype(np.float32), (0, 0), 6)) + n(cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 6))) / 2
    return n(s)


def mapa_atencion(bgr: np.ndarray, s: np.ndarray, escala: int = 2) -> np.ndarray:
    cm = cv2.applyColorMap((s * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    al = (np.clip(s, 0, 1) ** 0.9 * 0.82)[..., None]
    gris = cv2.cvtColor(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    ov = ((0.55 * gris + 0.45 * bgr) * (1 - al) + cm * al).astype(np.uint8)
    H, W = s.shape
    return cv2.resize(ov, (W * escala, H * escala), interpolation=cv2.INTER_CUBIC)


def medir_pantalla(imagen, zonas: dict, pliegues=(640, 800), recorte_superior: int = 0, salida_mapa=None,
                   orden_por_pliegue: bool = True) -> dict:
    """`zonas` = {clave: {caja: [x0,y0,x1,y1], texto, rol, nombre, alto_px?}} en px de la imagen.

    `orden_por_pliegue`: lo que se ve sin desplazar va primero (protocolo A/B de recompra, Fase 3).
    El primer estudio de recompra no lo aplicaba; la réplica lo apaga para reproducirlo.
    """
    im = Image.open(imagen).convert("RGB")
    a = np.asarray(im)
    H, W = a.shape[:2]
    bgr = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    s = saliencia(bgr)
    s[:recorte_superior] = 0  # p. ej. barra del navegador en la captura
    tot = s.sum()
    area_tot = (H - recorte_superior) * W
    if salida_mapa:
        cv2.imwrite(str(salida_mapa), mapa_atencion(bgr, s))
    z = {}
    for k, d in zonas.items():
        x0, y0, x1, y1 = d["caja"]
        rol = d.get("rol", "otro")
        if rol not in ROLES:
            raise ValueError(f"zona {k}: rol «{rol}» no es uno de {sorted(ROLES)}")
        es_texto = bool(d.get("texto")) and rol != "ilustracion"
        ar = (x1 - x0 + 1) * (y1 - y0 + 1)
        por = float(s[y0:y1 + 1, x0:x1 + 1].sum() / tot)
        z[k] = dict(
            caja=[x0, y0, x1, y1], nombre=d.get("nombre", k), rol=rol, texto=d.get("texto"), es_texto=es_texto,
            palabras=palabras(d.get("texto")) if es_texto else 0,
            porcion=round(por * 100, 1), densidad=round(por / (ar / area_tot), 2),
            pico=round(float(s[y0:y1 + 1, x0:x1 + 1].max()), 2),
            alto_px=(d.get("alto_px") or alto_banda(a, (x0, y0, x1, y1))) if es_texto else None,
            contraste=contraste(a, (x0, y0, x1, y1)) if es_texto else None,
            visible={str(p): ("completa" if y1 < p else "cortada" if y0 < p else "no") for p in pliegues},
            sin_scroll={str(p): (y0 + y1) / 2 < p for p in pliegues},
        )
    txt = [k for k in z if z[k]["es_texto"]]
    rd = {k: i for i, k in enumerate(sorted(txt, key=lambda k: -z[k]["densidad"]))}
    rp = {k: i for i, k in enumerate(sorted(txt, key=lambda k: z[k]["caja"][1]))}
    p_ref = str(max(pliegues))
    orden = sorted(txt, key=lambda k: (orden_por_pliegue and not z[k]["sin_scroll"][p_ref], (rd[k] + rp[k]) / 2, rp[k]))
    for k in z:
        z[k]["rango_saliencia"] = rd[k] + 1 if k in rd else None
    return dict(alto=H, ancho=W, zonas=z, orden=orden)


# ---------------------------------------------------------------------------------------------
# Puntos de lectura por integrante [EVIDENCIA + SIMULACIÓN]


def config_lectura(integrante) -> dict:
    """Reglas del User Persona primero; los umbrales OCEAN completan. Si chocan, gana la regla."""
    from .ocean import efectos_lectura

    reg = dict(integrante.biblioteca.lectura.get(integrante.perfil, {}))
    ef = efectos_lectura(integrante.ocean)
    return dict(
        corta_en_accion=reg.get("corta_en_accion", False) or "corta_en_accion" in ef,
        ilustracion_s=reg.get("ilustracion_s", 0),
        umbral_px=reg.get("umbral_px", 0),
        nota_primero="nota_primero" in ef,
        explora="explora" in ef,
        reglas=reg.get("reglas", []),
        rasgos=sorted(ef),
    )


def puntos_de_lectura(med: dict, cfg: dict, velocidades=(2.5, 3.5, 4.5), vel_base: float = 3.5,
                      vistazo_s: float = 5.0, vistazo_sin_scroll: bool = True) -> dict:
    z = med["zonas"]
    orden = list(med["orden"])
    legible = lambda k: not (cfg["umbral_px"] and z[k]["alto_px"] and z[k]["alto_px"] < cfg["umbral_px"])  # noqa: E731
    if cfg["nota_primero"]:
        notas = [k for k in orden if z[k]["rol"] == "nota" and legible(k)]
        montos = [k for k in orden if z[k]["rol"] == "monto"]
        for k in notas:
            orden.remove(k)
            orden.insert(orden.index(montos[0]) + 1 if montos else 1, k)
    ilus = [k for k in z if z[k]["rol"] == "ilustracion"]
    if cfg["ilustracion_s"] and ilus:
        orden = orden[:1] + ilus[:1] + orden[1:]
    pasos, t, cerrado = [], 0.0, False
    for k in orden:
        if cerrado:
            dur, estado = 0, "no_leida_cierre"
        elif z[k]["rol"] == "ilustracion":
            dur, estado = cfg["ilustracion_s"], "leida"
        elif not legible(k):
            dur, estado = 0, "no_leida_tamano"
        else:
            f = 1.3 if cfg["explora"] and z[k]["rol"] in ("accion", "enlace", "tarjeta") else 1
            dur, estado = z[k]["palabras"] / vel_base * f, "leida"
        pasos.append(dict(zona=k, inicio=round(t, 2), dur=round(dur, 2), estado=estado))
        t += dur
        if cfg["corta_en_accion"] and estado == "leida" and z[k]["rol"] == "accion":
            cerrado = True
    vist = {}
    p_ref = max(z[next(iter(z))]["sin_scroll"], key=int) if z else "800"
    for v in velocidades:
        tt, dentro = 0.0, []
        for x in pasos:
            if x["estado"] != "leida":
                continue
            k = x["zona"]
            if z[k]["rol"] == "ilustracion":
                tt += x["dur"]
                dentro.append([k, 0])
                continue
            if vistazo_sin_scroll and not z[k]["sin_scroll"][p_ref]:
                continue  # el vistazo no desplaza
            pal = z[k]["palabras"]
            caben = int((vistazo_s + 1e-4 - tt) * v)
            if caben <= 0:
                break
            dentro.append([k, min(pal, caben)])
            tt += min(pal, caben) / v
            if caben < pal:
                break
        vist[str(v)] = dentro
    return dict(pasos=pasos, vistazo=vist, total=round(t, 1), config=cfg)
