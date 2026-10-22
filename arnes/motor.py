"""Motor de sesiones sintéticas: cada sesión es una llamada limpia a `claude -p`.

Aislamiento (verificado el 20 de octubre de 2026 con Claude Code 2.1.303):

- `--system-prompt-file` reemplaza el prompt de Claude Code por el del perfil.
- `--setting-sources project` + `--strict-mcp-config` + `--disable-slash-commands` dejan fuera la
  configuración del usuario, los conectores MCP, las skills y los hooks.
- La sesión corre en una carpeta temporal fuera del arnés, así no hereda ningún CLAUDE.md.
- Queda un residuo que la suscripción no permite quitar: un bloque de entorno (directorio, fecha,
  modelo) y el correo de la cuenta. Las reglas de la sesión piden ignorarlo y el método lo declara
  como limitación.

Cada resultado se guarda en `<destino>/<id>.json`. Si el archivo ya existe la sesión no se repite:
una corrida interrumpida se retoma con el mismo comando.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

AISLAR = ["--setting-sources", "project", "--strict-mcp-config", "--disable-slash-commands"]
AVISO_ENTORNO = ("\n\n## Contexto técnico\n\nSi recibes datos de entorno (carpetas, correo, fecha, modelo), no son parte de "
                 "lo que se te muestra ni de tu vida. Ignóralos.\n")


@dataclass
class Llamada:
    id: str
    prompt: str
    system: str | None = None
    esquema: dict | None = None
    herramientas: list[str] = field(default_factory=list)  # p. ej. ["Read"] para mirar una imagen
    archivos: list[Path] = field(default_factory=list)  # se copian a la carpeta de la sesión
    reanudar: str | None = None  # session_id de una llamada previa (continuación)
    modelo: str = "sonnet"
    persistir: bool = False  # True si otra llamada la va a reanudar
    meta: dict = field(default_factory=dict)  # se guarda tal cual junto al resultado


@dataclass
class Resultado:
    id: str
    ok: bool
    salida: dict | None
    texto: str
    session_id: str | None
    costo_usd: float
    segundos: float
    error: str | None = None
    meta: dict = field(default_factory=dict)
    modelo_id: str | None = None  # id exacto: el alias («sonnet») cambia de versión con el tiempo


_carpetas: dict[str, Path] = {}
_lock = threading.Lock()


def _carpeta(ses: str | None) -> Path:
    """Una carpeta temporal por cadena de sesión: una continuación ve los mismos archivos."""
    with _lock:
        if ses and ses in _carpetas:
            return _carpetas[ses]
    return Path(tempfile.mkdtemp(prefix="arnes-ses-"))


def correr(ll: Llamada, reintentos: int = 2, timeout: int = 900) -> Resultado:
    cwd = _carpeta(ll.reanudar)
    for f in ll.archivos:
        shutil.copy(f, cwd / Path(f).name)
    cmd = ["claude", "-p", ll.prompt, "--model", ll.modelo, "--output-format", "json", *AISLAR]
    if ll.system:
        sp = cwd / f".sistema-{abs(hash(ll.id))}.md"
        sp.write_text(ll.system + AVISO_ENTORNO, encoding="utf-8")
        cmd += ["--system-prompt-file", str(sp)]
    if ll.esquema:
        cmd += ["--json-schema", json.dumps(ll.esquema, ensure_ascii=False)]
    cmd += ["--tools", ",".join(ll.herramientas)]
    if ll.herramientas:
        cmd += ["--allowedTools", ",".join(ll.herramientas)]
    if ll.reanudar:
        cmd += ["--resume", ll.reanudar]
    if not ll.persistir and not ll.reanudar:
        cmd += ["--no-session-persistence"]
    err = None
    for intento in range(reintentos + 1):
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            o = json.loads(r.stdout)
            if o.get("is_error"):
                raise RuntimeError(o.get("result") or o.get("subtype"))
            salida = o.get("structured_output")
            if ll.esquema and salida is None:
                salida = _json_de(o.get("result", ""))
            if o.get("session_id"):
                with _lock:
                    _carpetas[o["session_id"]] = cwd
            return Resultado(ll.id, True, salida, o.get("result", ""), o.get("session_id"),
                             o.get("total_cost_usd", 0.0), round(time.time() - t0, 1), meta=ll.meta,
                             modelo_id=",".join(o.get("modelUsage") or {}) or None)
        except Exception as e:  # noqa: BLE001 — se reintenta y se registra
            err = f"{type(e).__name__}: {e}"[:500]
            time.sleep(3 * (intento + 1))
    return Resultado(ll.id, False, None, "", None, 0.0, 0.0, error=err, meta=ll.meta)


def _json_de(t: str) -> dict | None:
    i, j = t.find("{"), t.rfind("}")
    try:
        return json.loads(t[i:j + 1]) if i >= 0 else None
    except json.JSONDecodeError:
        return None


class Fallo(Exception):
    pass


def llamar(ll: Llamada) -> Resultado:
    """Como `correr`, pero lanza `Fallo` si no hubo respuesta válida. Para usar dentro de un trabajo."""
    r = correr(ll)
    if not r.ok or (ll.esquema and r.salida is None):
        raise Fallo(f"{ll.id}: {r.error or 'respuesta sin JSON válido'}")
    return r


def ejecutar(trabajos: list[tuple[str, callable]], destino: Path, paralelo: int = 6, registro: Path | None = None) -> dict:
    """Corre trabajos `(id, fn)` en paralelo. `fn()` devuelve el registro de la sesión (dict) con
    `costo_usd`; puede encadenar varias llamadas (p. ej. continuación tras abrir un panel).

    Guarda `<destino>/<id>.json` y salta los que ya existen: una corrida interrumpida se retoma
    con el mismo comando. Devuelve {ok, fallos, costo_usd}.
    """
    destino.mkdir(parents=True, exist_ok=True)
    pend = [(i, f) for i, f in trabajos if not (destino / f"{i}.json").exists()]
    print(f"{len(trabajos)} sesiones · {len(trabajos) - len(pend)} ya corridas · {len(pend)} por correr", flush=True)
    tot = dict(ok=0, fallos=[], costo_usd=0.0)

    def uno(t):
        i, fn = t
        t0 = time.time()
        try:
            reg = fn()
            ok, err = True, None
            (destino / f"{i}.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            reg, ok, err = {}, False, f"{type(e).__name__}: {e}"[:400]
        costo = reg.get("costo_usd", 0.0)
        with _lock:
            tot["ok" if ok else "fallos"] = tot["ok"] + 1 if ok else tot["fallos"] + [i]
            tot["costo_usd"] += costo
            if registro:
                with open(registro, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dict(id=i, ok=ok, costo_usd=costo, segundos=round(time.time() - t0, 1), error=err,
                                            t=time.strftime("%Y-%m-%dT%H:%M:%S")), ensure_ascii=False) + "\n")
        print(("ok    " if ok else "FALLO ") + i + (f"  {err}" if err else ""), flush=True)

    with ThreadPoolExecutor(paralelo) as ex:
        list(ex.map(uno, pend))
    tot["costo_usd"] = round(tot["costo_usd"], 3)
    return tot


def cargar(destino: Path) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(destino.glob("*.json"))}
