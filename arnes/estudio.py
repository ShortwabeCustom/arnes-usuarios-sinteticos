"""Un estudio = una carpeta en estudios/ con estudio.yaml. Todo lo que el arnés produce queda adentro.

    estudios/<fecha>-<nombre>/
      estudio.yaml        configuración (la única entrada que se edita a mano, junto con narrativa.yaml)
      PROTOCOLO.md        protocolo generado y aprobado antes de correr
      material/           pantallas, capturas, exports — tal como llegan
      datos/              mediciones, sesiones/, agregados, CSV
      heatmaps/           imágenes derivadas
      narrativa.yaml      hallazgos y textos del reporte, escritos por el investigador (o el agente)
      reporte/            HTML autocontenido + .md
      estado.json         fases completadas, huella de la biblioteca, costos
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .personas import RAIZ, Biblioteca
from .yamlx import cargar as _yaml

ESTUDIOS = RAIZ / "estudios"
METODOS = ("comprension", "recorrido", "persona")


class Estudio:
    def __init__(self, ruta: str | Path):
        p = Path(ruta)
        if not p.is_dir():
            p = ESTUDIOS / str(ruta)
        if not (p / "estudio.yaml").exists():
            raise FileNotFoundError(f"No hay estudio.yaml en {p}")
        self.dir = p.resolve()
        self.cfg: dict = _yaml((p / "estudio.yaml").read_text(encoding="utf-8"))
        if self.cfg.get("metodo") not in METODOS:
            raise ValueError(f"metodo debe ser uno de {METODOS}")
        self.metodo: str = self.cfg["metodo"]
        for d in ("material", "datos", "heatmaps", "reporte"):
            (self.dir / d).mkdir(exist_ok=True)

    # ---- rutas -------------------------------------------------------------
    def ruta(self, *partes) -> Path:
        return self.dir.joinpath(*partes)

    @property
    def sesiones_dir(self) -> Path:
        return self.ruta("datos", "sesiones")

    # ---- panel -------------------------------------------------------------
    @property
    def biblioteca(self) -> Biblioteca:
        return Biblioteca(self.cfg["biblioteca"])

    def panel(self):
        ps = self.biblioteca.panel(self.cfg["panel"])
        solo = self.cfg.get("integrantes")
        return [p for p in ps if not solo or p.id in solo]

    # ---- estado ------------------------------------------------------------
    def estado(self) -> dict:
        f = self.ruta("estado.json")
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"fases": {}}

    def marcar(self, fase: str, **datos):
        e = self.estado()
        e["fases"][fase] = dict(t=time.strftime("%Y-%m-%dT%H:%M:%S"), **datos)
        if self.metodo != "persona":
            e["biblioteca"] = dict(id=self.cfg["biblioteca"], huella=self.biblioteca.huella(), panel=self.cfg["panel"])
        self.ruta("estado.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")

    def entregable(self, al_construir: bool = False) -> str:
        """Nombre del reporte: naming de UiX (proyecto-metodologia-tema_aaaa-mm-dd-vN) si estudio.yaml tiene bloque
        `uix`; si no, el de la carpeta. Fuera de `arnes reporte` devuelve el del último reporte construido."""
        from .estandares import naming

        if not al_construir:
            h = self.estado()["fases"].get("reporte", {}).get("html")
            if h:
                return Path(h).stem
        return naming(self.cfg, self.metodo) or self.dir.name

    def costo_total(self) -> tuple[float, int]:
        f = self.ruta("datos", "registro-sesiones.jsonl")
        if not f.exists():
            return 0.0, 0
        filas = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
        return round(sum(x["costo_usd"] for x in filas), 2), len(filas)

    def narrativa(self) -> dict:
        f = self.ruta("narrativa.yaml")
        return _yaml(f.read_text(encoding="utf-8")) if f.exists() else {}
