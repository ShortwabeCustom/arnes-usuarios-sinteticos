#!/usr/bin/env python3
"""
Análisis reproducible del estudio User Persona GIC.

Uso:
    python3 08-analisis.py [ruta/al/archivo.csv]

Por defecto lee ../actualizacion-user-persona-gic_responses.csv

Reproduce: auditoría de calidad, frecuencias con N válido por pregunta,
cruces bivariados y asignación de segmentos. Sin dependencias externas.

Si aparece un export corregido (con las 84 respuestas, o con el enunciado
de Q8/Q9/Q10), corré este script sobre él antes de reusar cualquier cifra.
"""
import csv
import math
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict

DEFAULT_SRC = "../actualizacion-user-persona-gic_responses.csv"

# Índices de columna. Las preguntas abiertas traen una columna Sentiment extra,
# por eso los índices no corresponden al número de pregunta.
Q = {
    "edad": 14, "genero": 15, "antiguedad": 16, "region": 17,
    "tipo_investigacion": 19, "dispositivo": 20, "por_dia": 21,
    "frec_a": 22, "frec_b": 23, "frec_c": 24,          # Q8/Q9/Q10 — SUSPENDIDAS
    "duracion": 25, "parte_lenta": 26, "duda": 27, "frustraciones": 28,
    "pax_no_ayudo": 29, "motivacion": 31, "pax_apoyo": 32,
    "claridad_pax": 34, "casos_torre": 35, "utilidad_torre": 36,
    "fallo_apoyo": 37, "frase": 39, "estilo": 40,
}
MULTI = {"tipo_investigacion", "frustraciones", "motivacion", "casos_torre"}
ESCALAS = ["frec_a", "frec_b", "frec_c", "claridad_pax", "utilidad_torre"]


def cargar(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    return rows[0], rows[1:]


def val(fila, clave):
    """Valor limpio de una celda: colapsa los saltos de línea embebidos."""
    return " ".join(fila[Q[clave]].split())


def opciones(v):
    """Separa una multi-select. El prefijo 'Other:' puede contener comas."""
    if not v:
        return []
    if "Other:" in v:
        cerradas, otro = v.split("Other:", 1)
        return [p.strip() for p in cerradas.split(",") if p.strip()] + ["Other: " + otro.strip()]
    return [p.strip() for p in v.split(",") if p.strip()]


def normalizar_dispositivo(v):
    t = v.lower().replace("other:", "").strip()
    if "910" in t:
        return "PAX A910"
    if "960" in t or "60" in t:
        return "PAX A960"
    if "920" in t:
        return "PAX A920"
    return "Otro / no identificado"


def normalizar_region(v):
    t = " ".join(v.split()).lower()
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    if not t:
        return None
    if "temascalapa" in t or "tolcayuca" in t:
        return "Temascalapa"
    if "zumpango" in t:
        return "Zumpango"
    if "tepeji" in t:
        return "Tepeji del Rio"
    if any(k in t for k in ("cardonal", "ixmiquilpan", "atotonilco")):
        return "Sierra (Cardonal / Ixmiquilpan)"
    if "jilotepec" in t or "chapa de mota" in t:
        return "Jilotepec / Chapa de Mota"
    if any(k in t for k in ("pachuca 2", "pachuca2", "reyes acozac", "tequixquiac", "tizayuca")):
        return "Pachuca 2 / Reyes Acozac"
    if "pachuca" in t:
        return "Region Pachuca (otras)"
    return "Otro / no clasificable"


def segmento(fila):
    """Reglas de asignación, en orden de prioridad. Ver §7 del reporte."""
    ant, frase, estilo = val(fila, "antiguedad"), val(fila, "frase"), val(fila, "estilo")
    if not frase and not estilo:
        return "Z"                                    # abandono
    if ant in ("Menos de 3 meses", "3 a 6 meses"):
        return "C"                                    # la etapa de aprendizaje domina
    if "resolver rápido" in frase or "Rápido y práctico" in estilo:
        return "B"
    if any(k in frase for k in ("no cometer errores", "guíe paso a paso", "más apoyo cuando algo")):
        return "D"
    if "más información del cliente" in frase:
        return "A"
    return "Z"


def pearson(data, a, b):
    pares = [(int(r[Q[a]]), int(r[Q[b]])) for r in data
             if r[Q[a]].strip().isdigit() and r[Q[b]].strip().isdigit()]
    if len(pares) < 3:
        return None, len(pares)
    xs, ys = [p[0] for p in pares], [p[1] for p in pares]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pares)
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return (num / den if den else 0.0), len(pares)


def auditoria(data):
    print("=" * 72)
    print("AUDITORÍA")
    print("=" * 72)
    total = len(data)
    abandonos = [r for r in data if r[4] == "Not finished"]
    print(f"  Registros: {total}   completos: {total - len(abandonos)}   abandonos: {len(abandonos)}")
    dur = [float(r[5]) for r in data if r[5].replace(".", "").isdigit()]
    if dur:
        print(f"  Duración de sesión: mediana {statistics.median(dur):.0f}s  "
              f"rango {min(dur):.0f}-{max(dur):.0f}s  (n={len(dur)})")
    # Las tres escalas de frecuencia comparten encabezado: no se pueden nombrar.
    print("\n  AVISO — Q8/Q9/Q10 comparten encabezado idéntico en el export.")
    print("  Sin el enunciado de cada ítem quedan SUSPENDIDAS. No las interpretes.")
    print("\n  Missing por pregunta:")
    for k in Q:
        n = sum(1 for r in data if val(r, k))
        if n < total:
            print(f"    {k:20} N={n:3}  missing={total - n}")


def frecuencias(data):
    print("\n" + "=" * 72)
    print("FRECUENCIAS")
    print("=" * 72)
    for k in Q:
        if k in ESCALAS:
            continue
        vals = [val(r, k) for r in data if val(r, k)]
        if not vals or k in ("region", "pax_no_ayudo", "pax_apoyo", "fallo_apoyo"):
            continue
        n = len(vals)
        c = Counter()
        for v in vals:
            if k == "dispositivo":
                c[normalizar_dispositivo(v)] += 1
            elif k in MULTI:
                for p in opciones(v):
                    c[p] += 1
            else:
                c[v] += 1
        etiqueta = " (multi-select)" if k in MULTI else ""
        print(f"\n  {k.upper()}{etiqueta}  N={n}  missing={len(data) - n}")
        for op, f in c.most_common():
            print(f"    {f:3}  {f / n * 100:5.1f}%  {op[:70]}")

    print("\n  REGIÓN (normalizada)")
    c = Counter(normalizar_region(val(r, "region")) for r in data if normalizar_region(val(r, "region")))
    n = sum(c.values())
    for op, f in c.most_common():
        print(f"    {f:3}  {f / n * 100:5.1f}%  {op}")

    print("\n  ESCALAS 1-5")
    for k in ESCALAS:
        v = [int(r[Q[k]]) for r in data if r[Q[k]].strip().isdigit()]
        d = Counter(v)
        nota = "  [SUSPENDIDA]" if k.startswith("frec_") else ""
        print(f"    {k:15} n={len(v):3}  media={statistics.mean(v):.2f}  "
              f"mediana={statistics.median(v)}  sd={statistics.pstdev(v):.2f}  "
              f"dist={[d.get(i, 0) for i in range(1, 6)]}{nota}")


def cruces(data):
    print("\n" + "=" * 72)
    print("RELACIONES")
    print("=" * 72)

    def media_por(cat, escala):
        d = defaultdict(list)
        for r in data:
            k, v = val(r, cat), r[Q[escala]].strip()
            if k and v.isdigit():
                d[k].append(int(v))
        return {k: (statistics.mean(v), len(v)) for k, v in d.items()}

    print("\n  Utilidad de Torre por antigüedad  (el gradiente más limpio del estudio)")
    orden = ["Menos de 3 meses", "3 a 6 meses", "1 a 3 años", "Más de 3 años"]
    for k in orden:
        m = media_por("antiguedad", "utilidad_torre").get(k)
        if m:
            print(f"    {k:20} media={m[0]:.2f}  n={m[1]}")

    print("\n  Utilidad de Torre por frase (Q22)")
    for k, (m, n) in sorted(media_por("frase", "utilidad_torre").items(), key=lambda x: -x[1][0]):
        print(f"    {k[:48]:50} media={m:.2f}  n={n}")

    print("\n  Dispositivo: percepción y frustraciones")
    for equipo in ("PAX A910", "PAX A960"):
        sub = [r for r in data if val(r, "dispositivo")
               and normalizar_dispositivo(val(r, "dispositivo")) == equipo]
        cl = [int(r[Q["claridad_pax"]]) for r in sub if r[Q["claridad_pax"]].strip().isdigit()]
        con_frust = [r for r in sub if val(r, "frustraciones")]
        c = Counter()
        for r in con_frust:
            for p in opciones(val(r, "frustraciones")):
                c[p] += 1
        nf = len(con_frust)
        lenta = c["PAX lenta o con errores"] / nf * 100 if nf else 0
        senal = c["Falta de señal o conexión"] / nf * 100 if nf else 0
        print(f"    {equipo}  n={len(sub):3}  claridad={statistics.mean(cl):.2f}  "
              f"'PAX lenta'={lenta:.0f}%  'falta de señal'={senal:.0f}%")
    print("    -> el equipo separa la lentitud percibida, NO la cobertura (control)")

    r18_20, n = pearson(data, "claridad_pax", "utilidad_torre")
    print(f"\n  Claridad de PAX x Utilidad de Torre: r={r18_20:+.2f} (n={n})")

    print("\n  Parte más lenta x momento de mayor duda")
    tab = defaultdict(Counter)
    for r in data:
        a, b = val(r, "parte_lenta"), val(r, "duda")
        if a and b:
            tab[a][b] += 1
    for a in sorted(tab, key=lambda x: -sum(tab[x].values())):
        tot = sum(tab[a].values())
        top, f = tab[a].most_common(1)[0]
        print(f"    {a[:36]:38} n={tot:3}  → {top[:38]} ({f / tot * 100:.0f}%)")


def segmentos(data):
    print("\n" + "=" * 72)
    print("SEGMENTOS")
    print("=" * 72)
    nombres = {"A": "Veterano que pide inteligencia previa",
               "B": "Ejecutor de ruta rápida",
               "C": "Gestor en formación",
               "D": "Verificador que teme el error",
               "Z": "Sin clasificar (abandonos + Other)"}
    S = defaultdict(list)
    for r in data:
        S[segmento(r)].append(r)
    clasificados = sum(len(S[k]) for k in "ABCD")
    for k in "ABCD":
        rs = S[k]
        cl = [int(r[Q["claridad_pax"]]) for r in rs if r[Q["claridad_pax"]].strip().isdigit()]
        to = [int(r[Q["utilidad_torre"]]) for r in rs if r[Q["utilidad_torre"]].strip().isdigit()]
        print(f"\n  [{k}] {nombres[k]}   n={len(rs)}  ({len(rs) / clasificados * 100:.1f}% de clasificados)")
        print(f"      claridad PAX={statistics.mean(cl):.2f}   utilidad Torre={statistics.mean(to):.2f}"
              f"   califican Torre<=2: {sum(1 for x in to if x <= 2)}/{len(to)}")
        for campo in ("antiguedad", "duracion", "parte_lenta", "duda"):
            top = Counter(val(r, campo) for r in rs if val(r, campo)).most_common(2)
            print(f"      {campo:14} " + " · ".join(f"{a[:34]}={b}" for a, b in top))
    print(f"\n  [Z] {nombres['Z']}   n={len(S['Z'])}")
    print(f"\n  Cobertura: {clasificados} de {clasificados + len(S['Z'])} registros.")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    try:
        _, data = cargar(src)
    except FileNotFoundError:
        print(f"No encuentro {src}\nUso: python3 08-analisis.py [ruta/al/archivo.csv]")
        return 1
    print(f"\nFuente: {src}\n")
    auditoria(data)
    frecuencias(data)
    cruces(data)
    segmentos(data)
    print("\n" + "=" * 72)
    print("Fidelidad a los datos > consistencia conductual > completitud narrativa.")
    print("=" * 72 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
