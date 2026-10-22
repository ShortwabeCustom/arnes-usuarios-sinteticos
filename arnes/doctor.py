"""`arnes doctor`: revisa que el entorno esté completo, con el arreglo de cada cosa que falte.

Pensado para quien instala el arnés por primera vez y para cuando algo deja de funcionar.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from .navegador import PW
from .personas import RAIZ, bibliotecas


def _git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def doctor() -> bool:
    revisiones = []

    def rev(nombre, ok, arreglo="", obligatorio=True):
        revisiones.append((nombre, ok, arreglo, obligatorio))

    v = sys.version_info
    rev(f"Python {v.major}.{v.minor}", (3, 12) <= v[:2] < (3, 14), "uv venv --python 3.12 .venv")
    rev("Entorno .venv activo", sys.prefix != sys.base_prefix, "source .venv/bin/activate")
    rev("Claude Code (motor de las sesiones)", bool(shutil.which("claude")), "instalar Claude Code e iniciar sesión")
    rev("CLI de Playwright (recorridos)", os.path.exists(PW),
        "instalar el skill de Playwright de Claude Code", obligatorio=False)
    libs = bibliotecas()
    rev(f"Bibliotecas de personas ({', '.join(libs) or 'ninguna'})", bool(libs), "revisar la carpeta personas/")

    try:
        from .conocimiento import vault

        V = vault()
        rev(f"Vault ({V.name})", True)
        if (V / ".git").exists():
            from . import vault as mv

            rev("Vault: sincronización automática", mv.PLIST.exists(), "arnes vault automatizar", obligatorio=False)
    except FileNotFoundError:
        rev("Vault", False, "git submodule update --init vault  (o sincronizar Google Drive)")

    rev("Guardia antes de cada commit", _git("config", "core.hooksPath") == ".githooks",
        "git config core.hooksPath .githooks")
    rev("Repositorio conectado a GitHub", bool(_git("remote", "get-url", "origin")), "git remote add origin <url>",
        obligatorio=False)

    print("Revisión del entorno del arnés:\n")
    for nombre, ok, arreglo, obligatorio in revisiones:
        marca = "✓" if ok else ("✗" if obligatorio else "·")
        print(f"  {marca} {nombre}" + ("" if ok else f"\n      → {arreglo}"))
    faltan = [r for r in revisiones if not r[1] and r[3]]
    print("\nListo para trabajar." if not faltan else f"\nFaltan {len(faltan)} cosas obligatorias.")
    return not faltan
