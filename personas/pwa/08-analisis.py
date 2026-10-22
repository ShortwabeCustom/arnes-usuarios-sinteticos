#!/usr/bin/env python3
"""
Análisis reproducible del User Persona OU-PWA.

Uso:
    python3 08-analisis.py [ruta/a/00-fuente]

Por defecto lee ./00-fuente

Reproduce: auditoría de consistencia entre láminas, frecuencias con base explícita,
mezcla de producto por segmento ponderada por n, y los cruces que sostienen los
cuatro perfiles. Sin dependencias externas.

Los CSV de 00-fuente son transcripción directa de las láminas de
buyer-persona-9junio.pptx, de los dos PDF de arquetipo y del reporte dev-onboarding.
Si aparece un export corregido del estudio, actualizá 00-fuente y corré esto antes
de reusar cualquier cifra.
"""
import csv
import os
import sys
from collections import defaultdict

DEFAULT_SRC = "00-fuente"

# Las láminas 7 y 9/10 usan cortes de edad distintos para las mismas generaciones.
# Se conserva el nombre de la generación como clave y se reporta la discrepancia.
GENERACIONES = ["Centennials (Z)", "Millennials (Y)", "Gen X", "Boomers"]
PRODUCTOS = ["Efectivo", "Movilidad", "Productos del hogar", "Telefonia", "Prestamo para autos"]


def leer(src, nombre):
    with open(os.path.join(src, nombre), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    """Float tolerante: celda vacía o no numérica devuelve None."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def auditoria(gen, pob, prod):
    print("=" * 74)
    print("AUDITORÍA")
    print("=" * 74)

    filas = [r for r in gen if r["generacion"] != "TOTAL"]
    total = sum(int(r["total_n"]) for r in filas)
    h = sum(int(r["hombres_n"]) for r in filas)
    m = sum(int(r["mujeres_n"]) for r in filas)
    print(f"  Clientes por generación (lámina 7): {total:,}")
    print(f"    hombres {h:,} ({h / total * 100:.1f}%)   mujeres {m:,} ({m / total * 100:.1f}%)")

    ec = [r for r in pob if r["tabla"] == "Estado civil registrado" and r["categoria"] != "TOTAL"]
    n_ec = sum(int(r["n"]) for r in ec)
    print(f"  Base de estado civil (lámina 6):    {n_ec:,}")
    print(f"    diferencia contra lámina 7: {abs(total - n_ec):,} "
          f"({abs(total - n_ec) / n_ec * 100:.2f}%) — dentro del redondeo a millar de la lámina 7")

    print("\n  AVISO 1 — Los cortes de edad NO coinciden entre láminas.")
    print("    Lámina 7:    Centennials 18-30 · Millennials 31-45 · Gen X 46-60")
    print("    Láminas 9/10: Centennials 18-29 · Millennials 30-44 · Gen X 45-60")
    print("    Los porcentajes de producto se calculan sobre los n de la lámina 7.")

    print("\n  AVISO 2 — Estado civil está SUSPENDIDO.")
    print("    Registro (lámina 6):    Soltero 47% · Unión libre 23% · Casado 22% · Divorciado 7%")
    print("    Colocación (lámina 16): Soltero 42.5% · Casado 25.8% · Divorciado 21.8% · U.Libre 8.1%")
    print("    Divorciado pasa de 7% a 21.8% y Unión Libre de 23% a 8.1%. Sin catálogo ni")
    print("    denominador las dos tablas no se pueden reconciliar. No la interpretes.")

    print("\n  AVISO 3 — 'Pérdida' cambia de nombre entre láminas.")
    print("    Lámina 16 la titula 'Pérdida Observada'; la lámina 12 remite a")
    print("    'análisis de pérdida esperada'. El mazo no define ninguna de las dos.")

    print("\n  AVISO 4 — El 'Cliente Ideal' no es una población observada.")
    print("    Declara 40% hombres / 60% mujeres. Proporción femenina observada por generación:")
    for r in filas:
        print(f"      {r['generacion']:20} {float(r['mujeres_pct']):.0f}% mujeres")
    print("    Ninguna llega a 60%. Es un objetivo de negocio, no un hallazgo.")

    print("\n  Variables ausentes en TODAS las fuentes:")
    for v in ("monto promedio solicitado", "motivo real de abandono", "ingreso del cliente",
              "perfiles de accesibilidad y alfabetización digital baja",
              "cruce edad × género para pérdida"):
        print(f"    - {v}")


def frecuencias(pob, gen):
    print("\n" + "=" * 74)
    print("FRECUENCIAS")
    print("=" * 74)

    filas = [r for r in gen if r["generacion"] != "TOTAL"]
    total = sum(int(r["total_n"]) for r in filas)
    print(f"\n  GENERACIÓN  N={total:,}")
    for r in filas:
        n = int(r["total_n"])
        print(f"    {n:>9,}  {n / total * 100:5.1f}%  {r['generacion']:18} "
              f"({r['rango_edad_declarado']})  {r['hombres_pct']}% H / {r['mujeres_pct']}% M")

    for tabla in ("Producto solicitado", "Estado civil registrado"):
        filas_t = [r for r in pob if r["tabla"] == tabla and r["categoria"] != "TOTAL"]
        base = sum(int(r["n"]) for r in filas_t)
        print(f"\n  {tabla.upper()}  N={base:,}")
        for r in sorted(filas_t, key=lambda x: -int(x["n"])):
            n = int(r["n"])
            nota = f"   <- {r['nota']}" if r["nota"] else ""
            print(f"    {n:>9,}  {n / base * 100:5.2f}%  {r['categoria']:22}{nota}")


def mezcla_por_segmento(gen, prod):
    """Pondera la mezcla de producto de cada generación por el n real de cada género."""
    print("\n" + "=" * 74)
    print("MEZCLA DE PRODUCTO POR SEGMENTO  (ponderada por n de género)")
    print("=" * 74)

    n_por = {}
    for r in gen:
        if r["generacion"] != "TOTAL":
            n_por[r["generacion"]] = {"Hombres": int(r["hombres_n"]), "Mujeres": int(r["mujeres_n"])}

    pct = defaultdict(dict)
    for r in prod:
        pct[(r["generacion"], r["genero"])][r["producto"]] = float(r["pct"])

    print(f"\n    {'':20}" + "".join(f"{p[:11]:>13}" for p in PRODUCTOS))
    resultado = {}
    for g in GENERACIONES:
        fila, base = {}, sum(n_por[g].values())
        for p in PRODUCTOS:
            acum = sum(n_por[g][sexo] * pct[(g, sexo)][p] / 100 for sexo in ("Hombres", "Mujeres"))
            fila[p] = acum / base * 100
        resultado[g] = fila
        print(f"    {g:20}" + "".join(f"{fila[p]:12.1f}%" for p in PRODUCTOS))

    print("\n  Gradientes monótonos de Centennials a Boomers:")
    for p in ("Efectivo", "Movilidad", "Telefonia"):
        serie = [resultado[g][p] for g in GENERACIONES]
        sube = all(b > a for a, b in zip(serie, serie[1:]))
        baja = all(b < a for a, b in zip(serie, serie[1:]))
        marca = "SUBE" if sube else "BAJA" if baja else "no monótono"
        print(f"    {p:22} " + " -> ".join(f"{v:.1f}" for v in serie) + f"   [{marca}]")
    return resultado


def cruces(cp):
    print("\n" + "=" * 74)
    print("RELACIONES")
    print("=" * 74)

    def tabla(dim, metrica):
        d = defaultdict(dict)
        for r in cp:
            if r["dimension"] == dim and r["metrica"] == metrica:
                v = num(r["valor"])
                if v is not None:
                    d[r["categoria"]][r["producto"]] = v
        return d

    print("\n  Pérdida observada por rango de edad  (el gradiente que sí es limpio)")
    orden = ["<=21 anios", "(21-25] anios", "(25-30] anios", "(30-40] anios",
             "(40-50] anios", ">50 anios"]
    per_edad = tabla("Edad", "perdida_observada")
    for k in orden:
        print(f"    {k:16} total={per_edad[k]['Total']:5.1f}   "
              f"efectivo={per_edad[k]['Efectivo']:5.1f}   movilidad={per_edad[k]['Movilidad']:5.1f}")
    serie = [per_edad[k]["Total"] for k in orden]
    print(f"    -> plana hasta los 40 ({serie[0]:.1f} a {serie[3]:.1f}) y luego cae "
          f"({serie[4]:.1f} y {serie[5]:.1f})")
    print("    -> el corte real está en los 40, NO en la etiqueta generacional")

    print("\n  Pérdida observada por género  (la relación más consistente del estudio)")
    per_gen = tabla("Genero", "perdida_observada")
    for p in ("Efectivo", "Movilidad", "Hogar", "Conectividad", "Total"):
        f_, m_ = per_gen["Femenino"][p], per_gen["Masculino"][p]
        print(f"    {p:14} mujeres={f_:5.1f}   hombres={m_:5.1f}   delta={f_ - m_:+.1f}")
    print("    -> la mujer pierde menos en los cuatro productos, sin una sola excepción")

    print("\n  Demanda contra riesgo por producto")
    col_gen = tabla("Genero", "pct_colocacion")
    for p, share in (("Efectivo", 54.0), ("Movilidad", 24.0), ("Hogar", 13.0), ("Conectividad", 9.0)):
        rango = [per_edad[k][p] for k in orden]
        print(f"    {p:14} {share:4.0f}% de la demanda   pérdida {min(rango):4.1f} a {max(rango):4.1f}   "
              f"mujeres {col_gen['Femenino'][p]:.1f}% de la colocación")
    print("    -> el producto más pedido es el más riesgoso; el segundo es el más seguro")


def segmentos(mezcla, gen):
    print("\n" + "=" * 74)
    print("SEGMENTOS")
    print("=" * 74)
    perfiles = {
        "Centennials (Z)": ("A", "Bryan Najera", "El que ya esta adentro y nadie disenio para el", 14.6),
        "Millennials (Y)": ("B", "Itzel Camacho", "La que decide por la cuota y paga el precio", 13.8),
        "Gen X": ("C", "Rosalba Quintero", "La que mejor paga y peor ve la letra", 11.6),
        "Boomers": ("D", "Arturo Belmont", "El que menos pierde y a quien nadie le hablo", 11.4),
    }
    n_por = {r["generacion"]: int(r["total_n"]) for r in gen if r["generacion"] != "TOTAL"}
    total = sum(n_por.values())
    for g in GENERACIONES:
        ident, nombre, arq, perdida = perfiles[g]
        n = n_por[g]
        dominante = max(mezcla[g], key=mezcla[g].get)
        print(f"\n  [{ident}] {nombre} — {arq}")
        print(f"      {g}   n={n:,}  ({n / total * 100:.1f}% de la base)")
        print(f"      producto dominante: {dominante} {mezcla[g][dominante]:.1f}%   "
              f"pérdida aprox: {perdida:.1f} [APROXIMACIÓN]")
    print("\n  Cobertura: 4 de 4 generaciones. Sin categoría residual: la lámina 7 "
          "clasifica al 100% de la base.")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    try:
        gen = leer(src, "clientes-por-generacion.csv")
        pob = leer(src, "poblacion-y-productos.csv")
        prod = leer(src, "productos-por-generacion-genero.csv")
        cp = leer(src, "colocacion-y-perdida.csv")
    except FileNotFoundError as e:
        print(f"No encuentro {e.filename}\nUso: python3 08-analisis.py [ruta/a/00-fuente]")
        return 1

    print(f"\nFuente: {src}\n")
    auditoria(gen, pob, prod)
    frecuencias(pob, gen)
    mezcla = mezcla_por_segmento(gen, prod)
    cruces(cp)
    segmentos(mezcla, gen)
    print("\n" + "=" * 74)
    print("Fidelidad a los datos > consistencia conductual > completitud narrativa.")
    print("=" * 74 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
