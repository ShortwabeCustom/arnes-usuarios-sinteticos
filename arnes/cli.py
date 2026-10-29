"""arnes — línea de comandos del arnés de investigación UX sintética.

    arnes bibliotecas                         lista bibliotecas y paneles
    arnes panel <estudio|biblioteca:panel>    fichas del panel, diversidad OCEAN, system prompt de muestra
    arnes nuevo <metodo> <nombre>             crea estudios/<fecha>-<nombre>/ desde la plantilla del método
    arnes estado <estudio>                    fases completadas, sesiones, consumo en tokens
    arnes medir <estudio>                     comprensión: fases 0, 2 y 3
    arnes sesiones <estudio> [--filtro=X] [--simular] [--piloto] [--paralelo N] [--forzar]
    arnes analizar <estudio>
    arnes recorrido <estudio> <integrante|todos> [--tarea T1] [--guion] [--corridas N] [--simular]
    arnes revisar <estudio>                   instrumento: preguntas sugestivas, baseline, lenguaje de la interfaz
    arnes auditar <estudio> [--evaluadores 3] evaluación experta independiente (UX writing o heurísticas) y consolidación
    arnes estilo <estudio>                    textos contra la guía de estilo del producto (guia_estilo en estudio.yaml)
    arnes conocimiento <metodo>               notas del vault de Obsidian para diseñar el protocolo
    arnes sintesis <estudio> [--simular]      archiva lo aprendido en 03-Sintesis/ del vault (y lo sube a GitHub)
    arnes vault [estado|sincronizar|automatizar|quitar]   el vault como repositorio: estado, subir, sincronizar solo
    arnes doctor                              revisa que el entorno esté completo (para quien empieza)
    arnes reporte <estudio>                   arma reporte/<id>.html autocontenido
    arnes verificar <estudio>                 control final: cifras, etiquetas, checklist
    arnes persona validar <carpeta>           revisa los entregables 01–12 de un User Persona
    arnes persona probar <biblioteca> [--panel P]   batería de fidelidad (preguntas sin cobertura)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import textwrap
import time

from . import ocean
from .estudio import ESTUDIOS, Estudio
from .personas import RAIZ, Biblioteca, bibliotecas


def _metodo(e: Estudio, fase: str | None = None):
    from importlib import import_module

    m = import_module(f".metodos.{e.metodo}", __package__)
    if fase and not hasattr(m, fase):
        sys.exit(f"«{fase}» no aplica al método {e.metodo}. Ver metodos/{e.metodo}/METODO.md")
    return m


def cmd_bibliotecas(a):
    for b in bibliotecas():
        bib = Biblioteca(b)
        print(f"{b:6s} {bib.meta['nombre']}  ·  huella {bib.huella()}")
        print(f"       base: {bib.meta.get('base', '')}")
        for p, d in bib.paneles.items():
            desc = textwrap.fill(f"{len(d['integrantes'])} integrantes · {' '.join(d.get('descripcion', '').split())}",
                                 width=100, initial_indent=f"       panel {p:12s} ", subsequent_indent=" " * 26)
            print(desc)


def cmd_panel(a):
    if ":" in a.objetivo:
        b, p = a.objetivo.split(":")
        panel = Biblioteca(b).panel(p)
    else:
        panel = Estudio(a.objetivo).panel()
    w = max([2] + [len(it.id) for it in panel])
    print(f"{'id':{w}s} {'nombre':18s} {'perfil':6s} {'segmento':22s} {'edad':>4s} {'género':7s}  O  C  E  A  N")
    for it in panel:
        o = it.ocean or {}
        print(f"{it.id:{w}s} {it.nombre:18s} {it.perfil:6s} {it.segmento[:22]:22s} {str(it.edad or ''):>4s} {str(it.genero or ''):7s} "
              + " ".join(f"{o.get(k, '·'):>2}" for k in "OCEAN") + ("  [OCEAN SUPUESTO]" if it.ocean_supuesto else ""))
    d = ocean.diversidad({it.id: it.ocean for it in panel})
    if d["rasgos"]:
        print("\nDiversidad OCEAN")
        for k, v in d["rasgos"].items():
            print(f"  {k} {v['rasgo']:26s} {v['min']:3d}–{v['max']:3d}  media {v['media']:5.1f}  {'; '.join(v['vacios'])}")
        if d["gemelos"]:
            print("  Perfiles casi idénticos:", ", ".join(f"{a}≈{b} ({x})" for a, b, x in d["gemelos"]))
    if a.prompt:
        it = next(x for x in panel if x.id == a.prompt)
        print("\n" + "=" * 80 + "\n" + it.system_prompt())


def cmd_nuevo(a):
    from . import estandares as std
    from .yamlx import cargar

    plant = RAIZ / "metodos" / a.metodo
    if not (plant / "estudio.plantilla.yaml").exists():
        sys.exit(f"No hay plantilla para el método «{a.metodo}»")
    nombre = f"{time.strftime('%Y-%m-%d')}-{a.nombre}"
    d = ESTUDIOS / nombre
    if d.exists():
        sys.exit(f"Ya existe {d}")
    d.mkdir(parents=True)
    for sub in ("material", "datos", "heatmaps", "reporte"):
        (d / sub).mkdir()
    txt = (plant / "estudio.plantilla.yaml").read_text(encoding="utf-8")
    for k, v in (("id", nombre), ("fecha", time.strftime("%Y-%m-%d")), ("proyecto", std.limpio(a.proyecto).replace("-", "")),
                 ("tema", std.limpio(a.tema or a.nombre))):
        txt = txt.replace("{{" + k + "}}", v)
    (d / "estudio.yaml").write_text(txt, encoding="utf-8")
    prot = (plant / "PROTOCOLO.plantilla.md").read_text(encoding="utf-8")
    if a.metodo != "persona":
        cfg = cargar(txt)
        met = cfg["uix"]["metodologia"]
        m = std.muestra(met)
        muestra = (f"panel sintético «{cfg.get('panel')}» × {cfg.get('corridas', 2)} corridas. Para validar con personas, "
                   f"UiX recomienda {m[0]} ({m[1].lower()})." if m else f"panel sintético «{cfg.get('panel')}».")
        for k, v in (("naming", std.naming(cfg, a.metodo)), ("cliente", cfg["uix"].get("cliente", "")),
                     ("fecha_dmy", time.strftime("%d/%m/%Y")), ("muestra", muestra),
                     ("metodologia", std.std()["naming"]["metodologias"].get(met, met))):
            prot = prot.replace("{{" + k + "}}", v)
    (d / "PROTOCOLO.md").write_text(prot, encoding="utf-8")
    shutil.copy(RAIZ / "metodos" / "narrativa.plantilla.yaml", d / "narrativa.yaml")
    print(f"Creado {d.relative_to(RAIZ)}\n  1. Copia el material a material/\n  2. Completa estudio.yaml (bloque uix incluido)\n"
          f"  3. Completa PROTOCOLO.md, empezando por el brief, y apruébalo antes de correr sesiones")


def cmd_estado(a):
    e = Estudio(a.estudio)
    st = e.estado()
    print(f"{e.cfg.get('titulo', e.dir.name)}\n  método {e.metodo} · biblioteca {e.cfg.get('biblioteca')} · panel {e.cfg.get('panel')}")
    for f, v in st.get("fases", {}).items():
        print(f"  ✓ {f:10s} {v['t']}  " + " ".join(f"{k}={v[k]}" for k in v if k != "t"))
    if e.sesiones_dir.exists():
        print(f"  sesiones guardadas: {len(list(e.sesiones_dir.glob('*.json')))}")
    print(f"  consumo: {e.texto_consumo()}")


def cmd_medir(a):
    e = Estudio(a.estudio)
    _metodo(e, "medir").medir(e)


def _revisar_o_salir(e: Estudio, forzar: bool):
    from .revisar import revisar

    err, _ = revisar(e)
    if err and not forzar:
        sys.exit("El instrumento tiene errores (preguntas sugestivas o cargadas). Corrígelos o usa --forzar.")


def cmd_revisar(a):
    from .revisar import revisar

    err, _ = revisar(Estudio(a.estudio))
    sys.exit(1 if err else 0)


def cmd_sesiones(a):
    e = Estudio(a.estudio)
    if e.metodo == "recorrido":
        sys.exit("En recorridos se usa: arnes recorrido <estudio> <integrante|todos>")
    _revisar_o_salir(e, a.forzar or a.simular)
    r = _metodo(e, "sesiones").sesiones(e, a.filtro or "", a.simular, a.paralelo, piloto=a.piloto)
    if not a.simular:
        print(json.dumps(r, ensure_ascii=False))


def cmd_analizar(a):
    e = Estudio(a.estudio)
    _metodo(e, "analizar").analizar(e)


def cmd_recorrido(a):
    e = Estudio(a.estudio)
    from .metodos import recorrido

    if a.simular:
        recorrido.simular(e, a.integrante, tarea=a.tarea, corridas=a.corridas)
        return
    _revisar_o_salir(e, a.forzar)
    if a.integrante == "todos" and (a.paralelo or 1) > 1:
        # un proceso por perfil (cada uno con su navegador y su sala), hasta `--paralelo` a la vez
        import subprocess
        from concurrent.futures import ThreadPoolExecutor

        ids = [it.id for it in e.panel()]
        extra = (["--tarea", a.tarea] if a.tarea else []) + (["--corridas", str(a.corridas)] if a.corridas else []) + ["--forzar"]
        log = e.ruta("datos", "paralelo")
        log.mkdir(parents=True, exist_ok=True)

        def uno(i):
            with open(log / f"{i}.log", "w", encoding="utf-8") as f:
                return i, subprocess.run([sys.executable, "-m", "arnes.cli", "recorrido", str(e.dir), i, *extra], stdout=f,
                                         stderr=subprocess.STDOUT).returncode

        print(f"{len(ids)} perfiles, {a.paralelo} a la vez · bitácoras en {log}")
        with ThreadPoolExecutor(a.paralelo) as ex:
            for i, rc in ex.map(uno, ids):
                print(f"  {i}: {'terminó' if rc == 0 else f'se detuvo (código {rc}); revisa su bitácora'}")
        return
    recorrido.sesion(e, a.integrante, tarea=a.tarea, guion=a.guion, corridas=a.corridas)


def cmd_ensayar(a):
    from .metodos import recorrido

    r = recorrido.ensayar(Estudio(a.estudio), visible=a.visible)
    sys.exit(1 if r["problemas"] else 0)


def cmd_tecnico(a):
    from .tecnico import auditar

    auditar(Estudio(a.estudio), visible=a.visible)


def cmd_auditar(a):
    from .auditar import auditar

    auditar(Estudio(a.estudio), a.evaluadores, a.modelo, a.simular)


def cmd_estilo(a):
    from .estilo import revisar_estudio

    r = revisar_estudio(Estudio(a.estudio))
    sys.exit(1 if any(x["nivel"] == "error" for x in r["hallazgos"]) and a.estricto else 0)


def cmd_conocimiento(a):
    from . import conocimiento

    print(f"Notas del vault para el método «{a.metodo}»" + (f" y el producto «{a.producto}»:" if a.producto else ":"))
    conocimiento.imprimir_notas(a.metodo, a.producto)


def cmd_sintesis(a):
    from . import conocimiento

    conocimiento.sintesis(Estudio(a.estudio), simular=a.simular, enlazar=not a.sin_enlazar, subir=not a.sin_subir)


def cmd_vault(a):
    from . import vault as V

    if a.accion == "estado":
        d = V.estado()
        print(f"Vault: {d['ruta']}")
        if not d["repositorio"]:
            return print("  no es un repositorio git")
        print(f"  último commit: {d['ultimo']}")
        print(f"  cambios sin commit: {len(d['pendientes'])}" + "".join(f"\n    {x}" for x in d["pendientes"][:15]))
        print(f"  commits sin subir: {d['sin_subir']} · en GitHub sin bajar: {d['sin_bajar']}")
        print(f"  sincronización automática: {'activa' if V.PLIST.exists() else 'no instalada'}")
    elif a.accion == "sincronizar":
        try:
            r = V.sincronizar(a.mensaje, silencioso=a.auto)
            if a.auto and r != "sin cambios":
                V.registrar(r)
        except V.ErrorVault as err:
            if not a.auto:
                sys.exit(f"Vault: {err}")
            V.registrar(f"ERROR {err}")
            import subprocess

            subprocess.run(["osascript", "-e", 'display notification "No se pudo sincronizar el vault. '
                            f'Revisa {V.BITACORA}" with title "Arnés"'], capture_output=True)
            sys.exit(1)
    elif a.accion == "automatizar":
        p = V.automatizar(a.cada)
        print(f"Sincronización automática instalada: cada {a.cada} min ({p}).\nBitácora: {V.BITACORA}\n"
              "Para quitarla: arnes vault quitar")
    elif a.accion == "quitar":
        V.quitar_automatizacion() or print("No había sincronización automática instalada.")


def cmd_doctor(a):
    from .doctor import doctor

    sys.exit(0 if doctor() else 1)


def cmd_reporte(a):
    from .reporte import construir

    e = Estudio(a.estudio)
    if e.metodo == "persona":
        sys.exit("El método persona entrega su propio 09-reporte.html (ver metodos/persona/METODO.md)")
    print(construir(e))


def cmd_verificar(a):
    from .verificar import verificar

    ok = verificar(Estudio(a.estudio))
    sys.exit(0 if ok else 1)


def cmd_persona(a):
    from .metodos import persona

    if a.accion == "validar":
        sys.exit(0 if persona.validar(a.objetivo) else 1)
    persona.probar(a.objetivo, a.panel, a.modelo)


def main(argv=None):
    p = argparse.ArgumentParser(prog="arnes", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("bibliotecas").set_defaults(fn=cmd_bibliotecas)
    x = s.add_parser("panel")
    x.add_argument("objetivo")
    x.add_argument("--prompt", help="imprime el system prompt completo de este integrante")
    x.set_defaults(fn=cmd_panel)
    x = s.add_parser("nuevo")
    x.add_argument("metodo", choices=["comprension", "recorrido", "persona"])
    x.add_argument("nombre")
    x.add_argument("--proyecto", default="oupwa", help="proyecto del naming de UiX (una sola forma por proyecto)")
    x.add_argument("--tema", help="tema del naming de UiX; por omisión, el nombre")
    x.set_defaults(fn=cmd_nuevo)
    for n, fn in (("estado", cmd_estado), ("medir", cmd_medir), ("analizar", cmd_analizar), ("reporte", cmd_reporte),
                  ("verificar", cmd_verificar)):
        x = s.add_parser(n)
        x.add_argument("estudio")
        x.set_defaults(fn=fn)
    x = s.add_parser("sesiones")
    x.add_argument("estudio")
    x.add_argument("--filtro")
    x.add_argument("--simular", action="store_true", help="lista lo que correría, sin llamar al modelo")
    x.add_argument("--paralelo", type=int)
    x.add_argument("--piloto", action="store_true", help="solo el primer integrante y la corrida 1: estudio piloto")
    x.add_argument("--forzar", action="store_true", help="corre aunque la revisión del instrumento marque errores")
    x.set_defaults(fn=cmd_sesiones)
    x = s.add_parser("revisar")
    x.add_argument("estudio")
    x.set_defaults(fn=cmd_revisar)
    x = s.add_parser("auditar")
    x.add_argument("estudio")
    x.add_argument("--evaluadores", type=int, default=3)
    x.add_argument("--modelo", default="sonnet")
    x.add_argument("--simular", action="store_true")
    x.set_defaults(fn=cmd_auditar)
    x = s.add_parser("estilo")
    x.add_argument("estudio")
    x.add_argument("--estricto", action="store_true", help="sale con error si hay errores de guía")
    x.set_defaults(fn=cmd_estilo)
    x = s.add_parser("conocimiento")
    x.add_argument("metodo", choices=["comprension", "recorrido", "persona"])
    x.add_argument("--producto", help="agrega las notas del producto, p. ej. pwa")
    x.set_defaults(fn=cmd_conocimiento)
    x = s.add_parser("sintesis")
    x.add_argument("estudio")
    x.add_argument("--simular", action="store_true", help="muestra qué escribiría en el vault, sin escribir")
    x.add_argument("--sin-enlazar", action="store_true", help="no agrega el enlace en las notas de concepto")
    x.add_argument("--sin-subir", action="store_true", help="escribe en el vault pero no hace commit ni push")
    x.set_defaults(fn=cmd_sintesis)
    x = s.add_parser("vault")
    x.add_argument("accion", nargs="?", default="estado", choices=["estado", "sincronizar", "automatizar", "quitar"])
    x.add_argument("-m", "--mensaje", help="mensaje del commit (por omisión, la lista de notas que cambiaron)")
    x.add_argument("--cada", type=int, default=60, help="minutos entre sincronizaciones automáticas")
    x.add_argument("--auto", action="store_true", help=argparse.SUPPRESS)
    x.set_defaults(fn=cmd_vault)
    s.add_parser("doctor").set_defaults(fn=cmd_doctor)
    x = s.add_parser("recorrido")
    x.add_argument("estudio")
    x.add_argument("integrante")
    x.add_argument("--tarea")
    x.add_argument("--guion", action="store_true", help="ejecuta el guion escrito en lugar de que el perfil decida")
    x.add_argument("--corridas", type=int, help="repeticiones por integrante y tarea (para medir qué se repite)")
    x.add_argument("--simular", action="store_true", help="cuántas sesiones y tokens, sin correr nada")
    x.add_argument("--forzar", action="store_true")
    x.add_argument("--paralelo", type=int, help="con «todos»: cuántos perfiles corren a la vez (un navegador cada uno)")
    x.set_defaults(fn=cmd_recorrido)
    x = s.add_parser("ensayar", help="recorre las tareas como un perfil, sin modelo: lo que fallaría antes de gastar; 0 tokens")
    x.add_argument("estudio")
    x.add_argument("--visible", action="store_true")
    x.set_defaults(fn=cmd_ensayar)
    x = s.add_parser("tecnico", help="auditoría técnica de un producto web (accesibilidad, rendimiento, PWA); 0 tokens")
    x.add_argument("estudio")
    x.add_argument("--visible", action="store_true", help="muestra la ventana del navegador mientras mide")
    x.set_defaults(fn=cmd_tecnico)
    x = s.add_parser("persona")
    x.add_argument("accion", choices=["validar", "probar"])
    x.add_argument("objetivo")
    x.add_argument("--panel", default="base4")
    x.add_argument("--modelo", default="sonnet")
    x.set_defaults(fn=cmd_persona)
    a = p.parse_args(argv)
    from .conocimiento import VaultNoEncontrado

    try:
        a.fn(a)
    except VaultNoEncontrado as err:
        sys.exit(str(err))


if __name__ == "__main__":
    main()
