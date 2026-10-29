"""Guardia de lo que se sube a GitHub: correos, llaves, CURP y tarjetas en las líneas que se agregan.

La usan el hook de pre-commit del arnés (`.githooks/pre-commit`), la sincronización del vault y la integración
continua. Los estudios usan datos de prueba ficticios; si algo real se cuela, se bloquea antes del commit.

    python -m arnes.guardia                 revisa lo que está en stage (git diff --cached)
    python -m arnes.guardia --todo          revisa todos los archivos versionados
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Dominios de ejemplo que aparecen en plantillas y en notas de UX writing.
# Dominios de ejemplo y textos de ayuda típicos de un campo de correo («ejemplo@mail.com», «tucorreo@…»).
CORREOS_DE_EJEMPLO = re.compile(r"@(example\.(com|org|net)|ejemplo\.com|empresa\.com|correo\.com|dominio\.com)$"
                                r"|^(noreply|ejemplo|example|tucorreo|tu\.correo|usuario|nombre|correo)@", re.I)

PATRONES = [
    ("correo", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
    ("llave de Anthropic", re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}")),
    ("token de GitHub", re.compile(r"\b(ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")),
    ("llave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("llave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("contraseña escrita", re.compile(r"(?i)\b(password|contrase(ñ|n)a|passwd)\s*[:=]\s*[\"']?[^\s\"'{}]{4,}")),
    ("CURP", re.compile(r"\b[A-Z][AEIOUX][A-Z]{2}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b")),
    ("número de tarjeta", re.compile(r"\b(?:\d[ -]?){15,16}\b")),
]


def _luhn(n: str) -> bool:
    d = [int(c) for c in re.sub(r"\D", "", n)][::-1]
    return len(d) in (15, 16) and sum(x if i % 2 == 0 else (x * 2 - 9 if x > 4 else x * 2) for i, x in enumerate(d)) % 10 == 0


def revisar_texto(texto: str) -> list[str]:
    """Motivos por los que este texto no debería subirse (vacío si está limpio)."""
    out = []
    for nombre, rx in PATRONES:
        for m in rx.finditer(texto):
            v = m.group(0)
            if nombre == "correo" and CORREOS_DE_EJEMPLO.search(v):
                continue
            if nombre == "número de tarjeta" and not _luhn(v):
                continue
            out.append(f"{nombre}: «{v[:6]}…»")
    return out


SUSTITUTOS = {"correo": "[correo]", "CURP": "[CURP]", "número de tarjeta": "[tarjeta]"}


def limpiar(obj):
    """Copia de `obj` (texto, lista o dict) con correos, CURP y tarjetas sustituidos. Se aplica a lo que guarda una
    sesión: un perfil puede leer o escribir el correo de ejemplo de un prototipo, y eso no debe llegar a GitHub."""
    if isinstance(obj, str):
        for nombre, rx in PATRONES:
            if nombre not in SUSTITUTOS:
                continue
            obj = rx.sub(lambda m, n=nombre: m.group(0) if (n == "correo" and CORREOS_DE_EJEMPLO.search(m.group(0)))
                         or (n == "número de tarjeta" and not _luhn(m.group(0))) else SUSTITUTOS[n], obj)
        return obj
    if isinstance(obj, list):
        return [limpiar(x) for x in obj]
    if isinstance(obj, dict):
        return {k: limpiar(v) for k, v in obj.items()}
    return obj


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


# Código de terceros copiado tal cual (p. ej. axe-core): sus constantes numéricas minificadas pasan Luhn por azar y
# no son datos de nadie. Solo carpetas `vendor/`, revisadas al agregarlas.
TERCEROS = ("arnes/vendor/",)


def revisar_stage(repo: Path) -> list[str]:
    """Revisa solo las líneas que se agregan en el commit en curso."""
    hallazgos, archivo = [], None
    for linea in _git(repo, "diff", "--cached", "-U0", "--no-color", "--diff-filter=AM").splitlines():
        if linea.startswith("+++ "):
            archivo = linea[6:] if linea.startswith("+++ b/") else None
            if archivo and archivo.startswith(TERCEROS):
                archivo = None
        elif linea.startswith("+") and archivo:
            hallazgos += [f"{archivo}: {m}" for m in revisar_texto(linea[1:])]
    return hallazgos


def revisar_todo(repo: Path) -> list[str]:
    hallazgos = []
    for f in _git(repo, "ls-files").splitlines():
        p = repo / f
        if f.startswith(TERCEROS):
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webm", ".mp4", ".gif", ".pdf", ".ico", ".woff", ".woff2"}:
            continue
        try:
            hallazgos += [f"{f}: {m}" for m in revisar_texto(p.read_text(encoding="utf-8"))]
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
    return hallazgos


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    repo = Path(next((a for a in argv if not a.startswith("-")), "."))
    h = revisar_todo(repo) if "--todo" in argv else revisar_stage(repo)
    if h:
        print("Guardia: esto no debería subirse a GitHub:")
        print("\n".join(f"  ✗ {x}" for x in h))
        print("Quítalo, o si es un dato de ejemplo usa un dominio como @example.com.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
