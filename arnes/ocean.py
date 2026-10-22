"""Capa OCEAN: umbrales, manifestaciones esperadas y control de diversidad del panel.

Ninguna fuente de las bibliotecas mide personalidad. Los valores son de diseño del panel y los
efectos de abajo son [SUPUESTO METODOLÓGICO]: se declaran en el protocolo y se ponen a prueba con
el control de sensibilidad (mismos perfiles sin capa OCEAN). Cuando una regla conductual del User
Persona choca con un rasgo, gana la regla.
"""

from __future__ import annotations

RASGOS = {
    "O": ("Apertura a la experiencia", "Openness"),
    "C": ("Responsabilidad", "Conscientiousness"),
    "E": ("Extraversión", "Extraversion"),
    "A": ("Amabilidad", "Agreeableness"),
    "N": ("Neuroticismo", "Neuroticism"),
}

# (rasgo, comparador, umbral, manifestación en la sesión, efecto en el modelo de lectura o None)
UMBRALES = [
    ("C", ">=", 75, "Revisas todos los textos, incluidos asteriscos y notas, y buscas inconsistencias antes de decidir.", "lee_todo"),
    ("C", "<=", 45, "Decides con lo primero que lees; no repasas lo que ya pasaste.", "corta_en_accion"),
    ("N", ">=", 65, "La ambigüedad te suena a riesgo o engaño; reaccionas con intensidad ante lo que no se explica.", "nota_primero"),
    ("O", ">=", 70, "Te da curiosidad tocar enlaces y tarjetas para ver qué hay.", "explora"),
    ("O", "<=", 40, "Te quedas con lo conocido; no exploras opciones que no necesitas.", None),
    ("A", ">=", 75, "Aceptas la explicación de la institución sin tomarla como reproche.", None),
    ("A", "<=", 55, "Lees una negativa como trato injusto con más facilidad.", None),
    ("E", ">=", 70, "Tiendes a comentar la decisión con alguien antes de seguir.", None),
    ("E", "<=", 40, "Resuelves solo; no buscas a otras personas para decidir.", None),
]


def nivel(v: int) -> str:
    return "muy alta" if v >= 80 else "alta" if v >= 65 else "media" if v >= 45 else "baja" if v >= 30 else "muy baja"


def _cumple(v: int, comp: str, u: int) -> bool:
    return v >= u if comp == ">=" else v <= u


def manifestaciones(ocean: dict[str, int]) -> list[str]:
    return [m for r, c, u, m, _ in UMBRALES if _cumple(ocean[r], c, u)]


def efectos_lectura(ocean: dict[str, int] | None) -> set[str]:
    if not ocean:
        return set()
    return {e for r, c, u, _, e in UMBRALES if e and _cumple(ocean[r], c, u)}


def bloque_prompt(ocean: dict[str, int]) -> str:
    vals = " · ".join(f"{k} {ocean[k]}" for k in "OCEAN")
    lin = [f"- {RASGOS[k][0]} ({k}): {ocean[k]}/100 · {nivel(ocean[k])}" for k in "OCEAN"]
    man = manifestaciones(ocean)
    out = ["## Personalidad (OCEAN, 0–100)", "", vals, "", *lin]
    if man:
        out += ["", "Manifestaciones esperadas:", *[f"- {m}" for m in man]]
    out += ["", "Si una regla conductual de tu perfil contradice tu personalidad, sigue la regla."]
    return "\n".join(out)


def diversidad(panel: dict[str, dict[str, int]]) -> dict:
    """Rango por rasgo y vacíos. `panel` = {id: ocean}. Devuelve filas listas para el protocolo."""
    filas = {}
    for k in "OCEAN":
        vs = [o[k] for o in panel.values() if o]
        if not vs:
            continue
        lo, hi = min(vs), max(vs)
        vacios = []
        if hi < 80:
            vacios.append("falta un extremo alto (> 80)")
        if lo > 30:
            vacios.append("falta un extremo bajo (< 30)")
        if hi - lo < 25:
            vacios.append(f"rango estrecho ({hi - lo} puntos)")
        filas[k] = dict(rasgo=RASGOS[k][0], min=lo, max=hi, media=round(sum(vs) / len(vs), 1), vacios=vacios)
    # pares casi idénticos: distancia euclidiana < 15 en los cinco rasgos
    ids = [i for i, o in panel.items() if o]
    gemelos = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            d = sum((panel[a][k] - panel[b][k]) ** 2 for k in "OCEAN") ** 0.5
            if d < 15:
                gemelos.append((a, b, round(d, 1)))
    return dict(rasgos=filas, gemelos=gemelos)
