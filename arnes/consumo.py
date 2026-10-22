"""Consumo de las sesiones en tokens.

Las sesiones corren con la suscripción de Claude (`claude -p`), así que no hay un precio por sesión: lo que se
gasta es cuota de uso. El arnés registra los tokens que reporta cada llamada y estima en tokens antes de correr.

Cuatro tipos de token, como los reporta Claude Code:
- entrada: texto nuevo que lee el modelo;
- caché (escritura): contexto que se guarda para reutilizarlo en la siguiente llamada;
- caché (lectura): contexto que se vuelve a leer de la caché, mucho más barato que leerlo nuevo;
- salida: lo que escribe el modelo.
"""

from __future__ import annotations

CAMPOS = ("entrada", "cache_escritura", "cache_lectura", "salida")

# Modelo de consumo de un recorrido. Cada paso son 2 llamadas (abrir la captura y responder) sobre un contexto que
# crece con cada paso: texto más 2 imágenes (la limpia y la marcada); Claude cuenta una imagen como ≈ ancho × alto
# / 750 tokens. Calibrado con las 16 sesiones del panel de OU 2.0 (22/10/2026, captura recortada al teléfono):
# texto ≈ 2,200 por paso, caché nueva ≈ 3 × el crecimiento, salida ≈ 890; error medio del total ≈ 3%.
RECORRIDO = dict(contexto_inicial=7_600, texto_por_paso=2_200, llamadas_por_paso=2, salida_por_paso=890,
                 factor_cache_nueva=3)
CAPTURA_VENTANA = (1200, 1026)      # ventana completa de Figma (pilotos 1–3)
CAPTURA_TELEFONO = (380, 850)       # captura recortada al teléfono (desde el 22/10/2026)


def tokens_imagen(ancho: int, alto: int) -> int:
    return round(ancho * alto / 750)


def de_usage(u: dict | None) -> dict:
    """Tokens de una llamada a partir del campo `usage` de `claude -p --output-format json`."""
    u = u or {}
    return dict(entrada=int(u.get("input_tokens") or 0), cache_escritura=int(u.get("cache_creation_input_tokens") or 0),
                cache_lectura=int(u.get("cache_read_input_tokens") or 0), salida=int(u.get("output_tokens") or 0))


def sumar(*ds: dict | None) -> dict:
    return {k: sum(int((d or {}).get(k, 0)) for d in ds) for k in CAMPOS}


def total(d: dict | None) -> int:
    return sum(int((d or {}).get(k, 0)) for k in CAMPOS)


def cifra(n: float) -> str:
    """1234567 → «1.2 M» · 24061 → «24 mil» · 812 → «812»."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} M".replace(".0 M", " M")
    if n >= 1_000:
        return f"{round(n / 1_000):,} mil"
    return str(int(n))


def nuevos(d: dict | None) -> int:
    """Tokens que no son relectura de caché: entrada, caché nueva y salida."""
    d = d or {}
    return int(d.get("entrada", 0)) + int(d.get("cache_escritura", 0)) + int(d.get("salida", 0))


def texto(d: dict | None) -> str:
    """«1.2 M tokens · 80 mil nuevos (el resto es relectura de caché)»."""
    t = total(d)
    if not t:
        return "0 tokens"
    n = nuevos(d)
    return f"{cifra(t)} tokens" + (f" · {cifra(n)} nuevos (el resto es relectura de caché)" if n < 0.95 * t else "")


def estimar_recorrido(pasos: int, sesiones: int = 1, captura: tuple[int, int] = CAPTURA_TELEFONO) -> dict:
    """Tokens esperados de `sesiones` recorridos de `pasos` pasos (más la pregunta final), con capturas de `captura`."""
    m = RECORRIDO
    crece = m["texto_por_paso"] + 2 * tokens_imagen(*captura)
    ctx = [m["contexto_inicial"] + crece * k for k in range(pasos)]
    lectura_total = sum(m["llamadas_por_paso"] * c for c in ctx) + (ctx[-1] if ctx else 0)
    escritura = m["factor_cache_nueva"] * crece * pasos
    d = dict(entrada=0, cache_escritura=escritura, cache_lectura=max(0, lectura_total - escritura),
             salida=m["salida_por_paso"] * pasos + 60)
    return {k: v * sesiones for k, v in d.items()}
