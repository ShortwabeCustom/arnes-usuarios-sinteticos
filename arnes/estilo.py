"""Revisión de textos contra la guía de estilo del producto (fuentes-producto/<id>/reglas-estilo.yaml).

Revisa lo que el arnés tiene como texto:
- comprensión: el texto de cada zona y de las continuaciones declaradas;
- recorrido (web): el texto visible de cada pantalla recorrida.

Es [EVIDENCIA] sobre el texto, no sobre la persona: dice qué contradice la guía escrita del producto.
Lo que no se puede verificar con un patrón (tono, cercanía) lo evalúan los evaluadores de `arnes auditar`.
"""

from __future__ import annotations

import json
import re

from .estudio import Estudio
from .personas import RAIZ
from .yamlx import cargar

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U000F0000-\U000FFFFF]")
SIGLAS = {"PWA", "INE", "OTP", "CAT", "MXN", "IVA", "RFC", "CURP", "SMS", "OU", "SAC", "RPI", "OCR", "GIC", "PAX", "CDMX", "SPEI", "CLABE"}


def guia(id_: str) -> dict:
    return cargar((RAIZ / "fuentes-producto" / id_ / "reglas-estilo.yaml").read_text(encoding="utf-8"))


def _frases(t: str) -> list[str]:
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+|\n+", t or "") if f.strip()]


def _especial(tipo: str, texto: str, nombre: str | None) -> list[str]:
    out = []
    if tipo == "apertura":
        for f in _frases(texto):
            for cierre, apertura in (("!", "¡"), ("?", "¿")):
                if cierre in f and apertura not in f:
                    out.append(f)
            if f.startswith("!"):
                out.append(f)
    elif tipo == "mayusculas":
        for m in re.finditer(r"\b([A-ZÁÉÍÓÚÑ]{3,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})+)\b", texto or ""):
            if not set(m.group(1).split()) <= SIGLAS:
                out.append(m.group(1))
    elif tipo == "emoji":
        out += EMOJI.findall(texto or "")
    elif tipo == "tu":
        for f in _frases(texto):
            if len(re.findall(r"\btus?\b", f, re.I)) >= 3:
                out.append(f)
    elif tipo == "nombre" and nombre:
        if len(re.findall(rf"\b{re.escape(nombre)}\b", texto or "")) >= 2:
            out.append(f"«{nombre}» aparece {len(re.findall(rf'\b{re.escape(nombre)}\b', texto))} veces")
    return out


def revisar_texto(texto: str, reglas: list[dict], nombre: str | None = None) -> list[dict]:
    out = []
    for r in reglas:
        if r.get("especial"):
            hall = _especial(r["especial"], texto, nombre)
        else:
            exc = {x.lower() for x in r.get("excepciones", [])}
            hall = [m.group(0) for m in re.finditer(r["patron"], texto or "", re.I) if m.group(0).lower() not in exc]
        for h in dict.fromkeys(hall):
            out.append(dict(regla=r["id"], nombre=r["nombre"], nivel=r["nivel"], fuente=r["fuente"], fragmento=h[:120]))
    return out


def _textos(e: Estudio) -> list[tuple[str, str, str]]:
    """(pantalla, zona, texto)."""
    c = e.cfg
    out = []
    if e.metodo == "comprension":
        # Una frase puede repartirse en varias zonas («¡María, tienes» + «… listos para usar!»): se revisa el texto
        # de la pantalla completo, en orden de lectura vertical, y cada hallazgo se ubica después en su zona.
        for pid, zs in (c.get("zonas") or {}).items():
            orden = sorted(((k, z) for k, z in (zs or {}).items() if z.get("texto") and z.get("rol") != "tarjeta"),
                           key=lambda kz: kz[1]["caja"][1])  # las tarjetas mezclan marcas y textos de terceros
            if orden:
                out.append((pid, "|".join(k for k, _ in orden), " ".join(z["texto"] for _, z in orden)))
        for k in c.get("continuaciones", []):
            if k.get("texto"):
                out.append((k["id"], "continuacion", k["texto"]))
    elif e.metodo == "recorrido":
        vistos = set()
        for f in sorted(e.sesiones_dir.glob("*.json")):
            s = json.loads(f.read_text(encoding="utf-8"))
            for p in s["pasos"]:
                if p.get("texto_pantalla") and p["pantalla"] not in vistos:
                    vistos.add(p["pantalla"])
                    out.append((p["pantalla"], "pantalla", p["texto_pantalla"]))
    return out


def revisar_estudio(e: Estudio, imprimir: bool = True) -> dict:
    gid = e.cfg.get("guia_estilo")
    if not gid:
        raise SystemExit("El estudio no declara `guia_estilo` (p. ej. `guia_estilo: pwa`).")
    g = guia(gid)
    nombre = e.cfg.get("nombre_de_ejemplo")
    res = []
    textos = _textos(e)
    zonas = {pid: zs or {} for pid, zs in (e.cfg.get("zonas") or {}).items()}
    for pid, zona, t in textos:
        for x in revisar_texto(t, g["reglas"], nombre):
            if "|" in zona:  # ubicar el hallazgo en la zona cuyo texto lo contiene
                cand = [k for k in zona.split("|") if x["fragmento"] in zonas[pid][k]["texto"] or zonas[pid][k]["texto"] in x["fragmento"]]
                if x["regla"] == "E02":  # el signo vive en una zona concreta
                    cand = sorted(cand, key=lambda k: not any(ch in zonas[pid][k]["texto"] for ch in "!?"))
                zona_x = cand[0] if cand else "varias zonas"
            else:
                zona_x = zona
            res.append(dict(pantalla=pid, zona=zona_x, **x))
    out = dict(guia=gid, nombre_guia=g["nombre"], textos=len(textos), hallazgos=res, contradicciones_guia=g.get("contradicciones", []))
    e.ruta("datos", "estilo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    e.marcar("estilo", guia=gid, errores=sum(x["nivel"] == "error" for x in res), avisos=sum(x["nivel"] == "aviso" for x in res))
    if imprimir:
        if not textos and e.metodo == "recorrido":
            print("Sin texto de pantallas: el recorrido guarda texto solo en material web, desde esta versión del arnés.")
        for x in sorted(res, key=lambda x: (x["nivel"] != "error", x["pantalla"])):
            print(f"  {'✕' if x['nivel'] == 'error' else '!'} {x['pantalla']:10s} {x['zona'][:14]:14s} {x['regla']} {x['nombre']}: «{x['fragmento']}»")
        print(f"Guía «{g['nombre']}»: {len(textos)} textos · {sum(x['nivel'] == 'error' for x in res)} errores · "
              f"{sum(x['nivel'] == 'aviso' for x in res)} avisos")
    return out
