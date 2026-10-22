"""El vault como repositorio git: estado, sincronización con GitHub y sincronización automática (launchd).

El vault se edita en Obsidian (Google Drive) y el arnés escribe ahí sus síntesis. `sincronizar` trae lo que haya en
GitHub, hace commit de lo nuevo con un mensaje que dice qué notas cambiaron y lo sube. Antes del commit pasa la
guardia (`arnes/guardia.py`): si hay un correo o una llave, no sube nada.
"""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .conocimiento import vault
from .guardia import revisar_stage

ETIQUETA = "com.arnes.vault-sincronizar"
PLIST = Path.home() / "Library/LaunchAgents" / f"{ETIQUETA}.plist"
BITACORA = Path.home() / "Library/Logs/arnes-vault.log"


class ErrorVault(RuntimeError):
    pass


def _git(V: Path, *args: str, ok: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(V), *args], capture_output=True, text=True)
    if r.returncode and not ok:
        raise ErrorVault(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()}")
    return r


def es_repositorio(V: Path | None = None) -> bool:
    V = V or vault()
    return (V / ".git").exists()


def mensaje_de_cambios(V: Path) -> str:
    """«Vault: 2 notas nuevas, 3 editadas» + la lista de notas, a partir de lo que está en stage."""
    filas = [ln.split("\t") for ln in _git(V, "diff", "--cached", "--name-status").stdout.splitlines() if ln]
    cuenta = {"A": 0, "M": 0, "D": 0}
    for f in filas:
        cuenta[f[0][0]] = cuenta.get(f[0][0], 0) + 1
    partes = [f"{n} {t}" for t, n in (("nuevas", cuenta["A"]), ("editadas", cuenta["M"]), ("borradas", cuenta["D"])) if n]
    lista = "\n".join(f"- {Path(f[-1]).with_suffix('').as_posix()}" for f in filas[:30])
    return f"Vault: notas {', '.join(partes) or 'sin cambios'}\n\n{lista}" + ("\n- …" if len(filas) > 30 else "")


def estado() -> dict:
    V = vault()
    d = dict(ruta=str(V), repositorio=es_repositorio(V))
    if d["repositorio"]:
        d["pendientes"] = [ln for ln in _git(V, "status", "--porcelain").stdout.splitlines() if ln]
        _git(V, "fetch", "-q", ok=True)
        r = _git(V, "rev-list", "--left-right", "--count", "HEAD...@{u}", ok=True).stdout.split()
        d["sin_subir"], d["sin_bajar"] = (int(r[0]), int(r[1])) if len(r) == 2 else (None, None)
        d["ultimo"] = _git(V, "log", "-1", "--format=%cr · %s", ok=True).stdout.strip()
    return d


def sincronizar(mensaje: str | None = None, subir: bool = True, silencioso: bool = False) -> str:
    """Trae, hace commit de lo nuevo y sube. Devuelve qué hizo; lanza ErrorVault si algo bloquea."""
    V = vault()
    if not es_repositorio(V):
        raise ErrorVault(f"El vault en {V} no es un repositorio git.")
    hay_remoto = bool(_git(V, "remote").stdout.strip())
    _git(V, "add", "-A")
    hecho = []
    if _git(V, "diff", "--cached", "--quiet", ok=True).returncode:
        h = revisar_stage(V)
        if h:
            _git(V, "reset", "-q")
            raise ErrorVault("La guardia bloqueó el commit:\n" + "\n".join(f"  ✗ {x}" for x in h))
        msg = mensaje_de_cambios(V)
        if mensaje:
            msg = f"{mensaje}\n\n" + msg.split("\n\n", 1)[-1]
        _git(V, "commit", "-q", "-m", msg)
        hecho.append(msg.splitlines()[0])
    if hay_remoto and subir and _git(V, "rev-parse", "--abbrev-ref", "@{u}", ok=True).returncode:
        rama = _git(V, "branch", "--show-current").stdout.strip()
        _git(V, "fetch", "-q", "origin", ok=True)
        if _git(V, "rev-parse", "--verify", "-q", f"origin/{rama}", ok=True).returncode:
            _git(V, "push", "-q", "-u", "origin", rama)        # primer push: la rama aún no existe en GitHub
            hecho.append("subido a GitHub")
            subir = False
        else:
            _git(V, "branch", "-q", f"--set-upstream-to=origin/{rama}")
    if hay_remoto and subir:
        r = _git(V, "pull", "--rebase", "-q", ok=True)
        if r.returncode:
            _git(V, "rebase", "--abort", ok=True)
            raise ErrorVault("No pude integrar los cambios de GitHub (conflicto en alguna nota). Resuélvelo a mano: "
                             f"git -C \"{V}\" pull --rebase\n{r.stderr.strip()}")
        if _git(V, "rev-list", "--count", "@{u}..HEAD", ok=True).stdout.strip() not in ("", "0"):
            _git(V, "push", "-q")
            hecho.append("subido a GitHub")
    res = " · ".join(hecho) or "sin cambios"
    if not silencioso:
        print(f"Vault: {res}")
    return res


# ---- sincronización automática (macOS, launchd) ---------------------------------------------------------------


def automatizar(cada_min: int = 60) -> Path:
    """Instala un agente de launchd que corre `arnes vault sincronizar --auto` cada `cada_min` minutos."""
    arnes = shutil.which("arnes") or str(Path(sys.executable).with_name("arnes"))
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    BITACORA.parent.mkdir(parents=True, exist_ok=True)
    datos = dict(
        Label=ETIQUETA,
        ProgramArguments=[arnes, "vault", "sincronizar", "--auto"],
        StartInterval=cada_min * 60,
        RunAtLoad=True,
        StandardOutPath=str(BITACORA),
        StandardErrorPath=str(BITACORA),
        EnvironmentVariables={"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
                              **({"ARNES_VAULT": os.environ["ARNES_VAULT"]} if os.environ.get("ARNES_VAULT") else {})},
    )
    quitar_automatizacion(silencioso=True)
    PLIST.write_bytes(plistlib.dumps(datos))
    subprocess.run(["launchctl", "load", "-w", str(PLIST)], check=True)
    return PLIST


def quitar_automatizacion(silencioso: bool = False) -> bool:
    if not PLIST.exists():
        return False
    subprocess.run(["launchctl", "unload", "-w", str(PLIST)], capture_output=True)
    PLIST.unlink()
    if not silencioso:
        print(f"Quitada la sincronización automática ({PLIST.name}).")
    return True


def registrar(texto: str) -> None:
    """Línea con fecha para la bitácora de launchd."""
    print(f"{time.strftime('%Y-%m-%d %H:%M')} {texto}", flush=True)
