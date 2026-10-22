"""Bibliotecas de usuarios sintéticos y armado del system prompt de cada sesión.

Estructura del prompt (protocolo A/B de recompra §3.6):

    [system prompt del perfil base, sin modificar]
    ## Variante            (solo si el integrante es una variante del perfil)
    ## Personalidad OCEAN  (solo si el panel la trae)
    ## Reglas de la sesión (las pone el método)
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import ocean as oc
from .yamlx import cargar as _yaml

RAIZ = Path(__file__).resolve().parent.parent
PERSONAS = RAIZ / "personas"

REGLAS_SESION_BASE = """## Reglas de la sesión

- Usa solo lo que se te muestra. No supongas funciones, políticas ni pasos que no aparezcan.
- No completes información que falte. Si algo es ambiguo o se contradice, dilo.
- No intentes agradar a quien pregunta ni adivinar qué respuesta espera.
- Si una pregunta cae fuera de lo que tu perfil cubre, responde exactamente: «{frase}» y anota la pregunta en "sin_cobertura".
- En "reglas" anota los ids de las reglas conductuales de tu perfil que aplicaste (p. ej. B-07)."""


@dataclass
class Integrante:
    id: str
    nombre: str
    perfil: str  # letra del perfil base
    biblioteca: "Biblioteca"
    ocean: dict[str, int] | None = None
    variante: str | None = None
    edad: int | None = None
    genero: str | None = None
    ocean_supuesto: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def base(self) -> dict:
        return self.biblioteca.perfiles[self.perfil]

    @property
    def segmento(self) -> str:
        return self.base.get("segmento", "")

    def system_prompt(self, reglas_sesion: str | None = None, con_ocean: bool = True) -> str:
        b = self.biblioteca
        partes = [(b.raiz / self.base["prompt"]).read_text(encoding="utf-8").rstrip()]
        if self.variante:
            partes.append("## Variante\n\n" + self.variante.strip()
                          + "\n\nHeredas del perfil de arriba el segmento, la mezcla de producto y las reglas conductuales. "
                            "Cambian tu nombre, edad, género y personalidad.")
        if con_ocean and self.ocean:
            partes.append(oc.bloque_prompt(self.ocean))
        partes.append((reglas_sesion or REGLAS_SESION_BASE).format(frase=b.frase_sin_cobertura))
        return "\n\n".join(partes) + "\n"

    def ficha(self) -> dict:
        return dict(id=self.id, nombre=self.nombre, perfil=self.perfil, segmento=self.segmento,
                    edad=self.edad, genero=self.genero, ocean=self.ocean, ocean_supuesto=self.ocean_supuesto,
                    es_variante=bool(self.variante), prompt_base=self.base["prompt"])


class Biblioteca:
    def __init__(self, id_o_ruta: str | Path):
        p = Path(id_o_ruta)
        self.raiz = p if p.is_dir() else PERSONAS / str(id_o_ruta)
        meta = _yaml((self.raiz / "biblioteca.yaml").read_text(encoding="utf-8"))
        self.meta = meta
        self.id = meta["id"]
        self.perfiles: dict = meta["perfiles"]
        self.paneles: dict = meta.get("paneles", {})
        self.frase_sin_cobertura: str = meta["frase_sin_cobertura"]
        self.lectura: dict = meta.get("lectura", {}) or {}
        no = {Path(x["archivo"]).name for x in meta.get("no_perfiles", [])}
        for k, v in self.perfiles.items():
            if Path(v["prompt"]).name in no:
                raise ValueError(f"{self.id}: el perfil {k} apunta a un archivo marcado como no-perfil")

    # ---- reglas conductuales ------------------------------------------------
    def reglas(self) -> dict[str, dict]:
        with open(self.raiz / self.meta["reglas"], encoding="utf-8") as f:
            return {r["id"]: r for r in csv.DictReader(f)}

    # ---- paneles ------------------------------------------------------------
    def panel(self, nombre: str) -> list[Integrante]:
        if nombre not in self.paneles:
            raise KeyError(f"{self.id}: no existe el panel «{nombre}». Hay: {', '.join(self.paneles)}")
        out = []
        for iid, d in self.paneles[nombre]["integrantes"].items():
            base = self.perfiles[d["perfil"]]
            out.append(Integrante(
                id=iid, nombre=d.get("nombre", base["nombre"]), perfil=d["perfil"], biblioteca=self,
                ocean=d.get("ocean"), variante=self._variante(d.get("variante")),
                edad=d.get("edad", base.get("edad")), genero=d.get("genero", base.get("genero")),
                ocean_supuesto=bool(d.get("ocean_supuesto"))))
        return out

    def _variante(self, v: str | None) -> str | None:
        # "@archivo.json#CLAVE" lee el texto de la variante de un JSON de la biblioteca
        if not v or not v.startswith("@"):
            return v
        archivo, clave = v[1:].split("#")
        return json.loads((self.raiz / archivo).read_text(encoding="utf-8"))[clave]["variante"]

    # ---- trazabilidad -------------------------------------------------------
    def huella(self) -> str:
        """sha256 corto de prompts, reglas y manifiesto: queda en cada estudio para saber qué versión usó."""
        h = hashlib.sha256()
        archivos = ["biblioteca.yaml", self.meta["reglas"]] + [v["prompt"] for v in self.perfiles.values()]
        for a in sorted(archivos):
            h.update(a.encode())
            h.update((self.raiz / a).read_bytes())
        return h.hexdigest()[:12]


def bibliotecas() -> list[str]:
    return sorted(p.name for p in PERSONAS.iterdir() if (p / "biblioteca.yaml").exists())
