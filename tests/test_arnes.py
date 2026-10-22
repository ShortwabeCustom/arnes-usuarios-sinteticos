"""Pruebas sin llamadas al modelo. Correr con: .venv/bin/python -m pytest tests -q"""

import json
from pathlib import Path

from arnes import ocean
from arnes.estudio import Estudio
from arnes.metodos import comprension
from arnes.metodos.persona import _limites, validar
from arnes.personas import Biblioteca
from arnes.verificar import _x_de_y
from arnes.yamlx import cargar

RAIZ = Path(__file__).resolve().parent.parent
REPLICA = RAIZ / "estudios" / "2026-10-05-recompra-comprension-replica"
ORIGINAL = RAIZ.parent / "Investigacion comprension de pantallas en recompra" / "datos" / "medicion.json"


def test_yaml_no_es_texto():
    d = cargar("opciones: [si, no, on, off]\nx: true\ny: false")
    assert d["opciones"] == ["si", "no", "on", "off"]
    assert d["x"] is True and d["y"] is False


def test_bibliotecas_y_paneles():
    b = Biblioteca("pwa")
    p = b.panel("ocean8")
    assert len(p) == 8
    assert {it.id for it in p if it.variante} == {"S02", "S04", "S06", "S08"}
    sp = p[1].system_prompt()
    assert "## Variante" in sp and "Daniela" in sp and "## Personalidad (OCEAN" in sp
    assert b.frase_sin_cobertura in sp
    assert "E-objetivo" not in " ".join(it.base["prompt"] for it in p)


def test_sin_ocean_para_sensibilidad():
    it = Biblioteca("pwa").panel("ocean8")[0]
    assert "Personalidad" not in it.system_prompt(con_ocean=False)


def test_diversidad_detecta_gemelos():
    d = ocean.diversidad({"a": dict(O=50, C=50, E=50, A=50, N=50), "b": dict(O=52, C=50, E=50, A=50, N=50)})
    assert d["gemelos"] and d["gemelos"][0][:2] == ("a", "b")


def test_validar_bibliotecas():
    assert validar("pwa") and validar("gic")


def test_limites_del_prompt():
    t = (RAIZ / "personas/pwa/system-prompts/A-bryan.md").read_text(encoding="utf-8")
    lim = _limites(t)
    assert len(lim) >= 4 and all("(" not in x for x in lim)


def test_x_de_y():
    assert _x_de_y("19 de 24") == (19, 24) and _x_de_y("3/4") == (3, 4) and _x_de_y("86%") is None


def test_plantilla_de_sesion_validada():
    e = Estudio(REPLICA)
    qs = comprension._preguntas_de(e.cfg, "E2")
    t = comprension._plantilla(qs)
    assert '"p3": {"opcion": "si | no | no_se"' in t
    assert "p9" not in t  # solo en la continuación
    assert '"sin_cobertura"' in t


def test_medicion_reproduce_el_original():
    if not ORIGINAL.exists():
        return
    o = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    n = json.loads((REPLICA / "datos" / "medicion.json").read_text(encoding="utf-8"))
    for p in o["zonas"]:
        assert o["zonas"][p]["orden"] == n["pantallas"][p]["orden"]
        for z, v in o["zonas"][p]["zonas"].items():
            w = n["pantallas"][p]["zonas"][z]
            assert (v["porcion"], v["densidad"], v["alto_banda"], v["contraste"]) == (w["porcion"], w["densidad"], w["alto_px"], w["contraste"])
        for per in ("bryan", "itzel", "rosalba", "arturo"):
            assert o["lectura"][p][per]["vistazo"] == n["lectura"][p][per]["vistazo"]


# ---- mejoras desde el vault -------------------------------------------------------------------

class _E:
    """Estudio mínimo para funciones que solo leen cfg."""
    def __init__(self, cfg, metodo="recorrido"):
        self.cfg, self.metodo = cfg, metodo


def test_wcag_258_falla_y_excepcion_por_espaciado():
    from arnes.metodos.recorrido import tamano_objetivos
    zonas = [dict(x=100, y=100, w=16, h=16, tipo="button", etiqueta="−"), dict(x=118, y=100, w=16, h=16, tipo="button", etiqueta="+"),
             dict(x=20, y=300, w=42, h=12, tipo="a", etiqueta="Términos"), dict(x=64, y=300, w=47, h=12, tipo="a", etiqueta="Privacidad")]
    S = [dict(pasos=[dict(pantalla="p", zonas_detalle=zonas, marco=dict(x=0, y=0, w=360, h=800), captura=None)])]
    r = tamano_objetivos(_E({"material": "web", "dispositivo": {"ancho": 360}}), S)
    fallan = {f["etiqueta"] for f in r[0]["fallan"]}
    assert fallan == {"−", "+"}  # pegados y chicos; los enlaces anchos pasan por espaciado


def test_wilson_y_brecha():
    from arnes.robustez import comparar
    A = {"x|g|A|v|antes|p": dict(aciertos=19, total=24), "x|g|B|v|antes|p": dict(aciertos=4, total=24),
         "x|g|C|v|antes|p": dict(aciertos=2, total=4), "x|g|D|v|antes|p": dict(aciertos=1, total=4)}
    assert comparar(A, "x|g|A|v|antes|p", "x|g|B|v|antes|p")["clara"]
    assert not comparar(A, "x|g|C|v|antes|p", "x|g|D|v|antes|p")["clara"]


def test_estabilidad():
    from arnes.robustez import estabilidad
    r = estabilidad({"b|g|A|ana|v|antes|p": ["si", "si", "si"], "b|g|A|beto|v|antes|p": ["si", "no", "no_se"]})
    assert len(r["inestables"]) == 1 and r["inestables"][0]["integrante"] == "beto"


def test_revisar_detecta_sugestivas():
    from arnes.revisar import revisar
    cfg = {"preguntas": [{"id": "p1", "texto": "Este proceso es muy claro, ¿verdad?"},
                         {"id": "p2", "texto": "¿Qué tanto te gustó la pantalla?", "opciones": ["mucho", "poco"]}],
           "consigna": "", "pantallas": {}, "zonas": {}}
    err, avi = revisar(_E(cfg, "comprension"), imprimir=False)
    assert len(err) >= 2 and any("salida neutra" in a for a in avi)


def test_guia_de_estilo_pwa():
    from arnes.estilo import guia, revisar_texto
    g = guia("pwa")["reglas"]
    ids = lambda t, n=None: {x["regla"] for x in revisar_texto(t, g, n)}  # noqa: E731
    assert "E01" in ids("Tu crédito está listo")
    assert "E02" in ids("!María, tienes $30,000 para tus productos favoritos!")
    assert "E02" not in ids("¡María, tienes $30,000 para tus productos favoritos!")
    assert "E06" in ids("La visita es agendada para confirmar tu solicitud.")
    assert "E09" in ids("Te prestamos hasta veinte mil pesos")
    assert "E10" in ids("La visita será el 5 de octubre de 2025")
    assert "E11" in ids("a las 15:00 horas")
    assert "E15" in ids("María, vamos. Solo María, necesitamos tu INE", "María")
    assert "E08" not in ids("Tus productos favoritos y tu cuenta Guardadito")
    assert not ids("Aprobamos tu préstamo por $12,000.")


def test_metricas_de_flujo():
    from arnes.metricas import calcular
    paso = lambda n, pid, acc=None, **k: dict(n=n, pantalla=pid, perfil={"progreso": {"opcion": "si"}} if acc else None,  # noqa: E731
                                              accion=acc, respuesta="si" if acc else None, **k)
    S = [dict(id="T1-a", tarea="T1", integrante="a", resultado="exito", ces={"ces": 6}, retoma={"resultado": "vuelve_al_inicio"}, pasos=[
        paso(1, "inicio", {"tipo": "tocar", "x": 1, "y": 1}, palabras=35, campos=0, progreso_visible="Paso 1 de 3", host="a.mx",
             texto_pantalla="Paso 1 de 3. Te prestamos hasta $30,000", espera_ms=500),
        paso(2, "datos", {"tipo": "escribir", "x": 1, "y": 1, "texto": "Alex García"}, palabras=10, campos=2, host="a.mx",
             texto_pantalla="Tus datos. Ingresa el código que enviamos por SMS", espera_ms=300, validacion_disparada=["Completa tu nombre"]),
        paso(3, "pago", {"tipo": "tocar", "x": 1, "y": 1}, palabras=7, campos=0, host="pagos.com", host_despues="pagos.com",
             texto_pantalla="Para dudas visita tu sucursal", espera_ms=200),
        dict(n=4, pantalla="listo", fin=True)])]
    m = calcular(S, {})
    x = m["sesiones"][0]
    assert (x["pasos"], x["clics"], x["campos"], x["caracteres_escritos"]) == (3, 3, 2, 11)
    assert x["cambios_dominio"] == 1 and x["menciones_otro_canal"] == ["SMS", "sucursal"]
    assert x["pantallas_verificacion"] == ["datos"] and x["validaciones_disparadas"] == 1
    assert x["pantallas_con_estatus"] == 1 and x["retoma"] == "vuelve_al_inicio"
    # tiempo: lectura 52/3.5 + 3 decisiones × 1.35 + 3 toques × 0.4 + 11 × 0.3 + 1.0 s de espera
    assert abs(x["tiempo_estimado_s"] - round(52 / 3.5 + 3 * 1.35 + 1.2 + 3.3 + 1.0, 1)) < 0.11
    assert m["distancia_por_pantalla"]["datos"]["pasos"]["mediana"] == 2


def test_estandares_uix():
    from arnes import estandares as std

    cfg = {"uix": {"proyecto": "OU PWA", "tema": "Documentos INE", "version": 2, "fecha_fin": "2026-04-23"}}
    assert std.naming(cfg, "recorrido") == "oupwa-pdu-documentos-ine-sintetico_2026-04-23-v2"
    assert std.naming({"uix": dict(cfg["uix"], tema="home-sintetico-wave1")}, "comprension").startswith("oupwa-abtesting-home-sintetico-wave1_")
    assert std.revisar_naming(dict(cfg, uix=dict(cfg["uix"], metodologia="usabilidad")), "recorrido")[0]
    assert std.naming({}, "recorrido") is None
    assert [std.semaforo(k, 10)["nivel"] for k in (10, 8, 5, 4)] == ["verde", "amarillo", "naranja", "rojo"]
    assert std.generacion(30).startswith("Centennials") and std.generacion(61).startswith("Boomers")
    assert std.generacion("31-45").startswith("Millennials")
    assert std.region_de("Veracruz") == "Sur" and std.region_de("Estado de México") == "Centro"
    assert std.decision("alto", "baja") == "Validar rápido"
    assert std.muestra("pdu")[0] == "8–10 personas"
    for b, p in (("pwa", "ocean8"), ("gic", "base4")):
        panel = Biblioteca(b).panel(p)
        assert std.revisar_demograficos(panel) == []
        assert all(set(std.demograficos(it)) == {"edad", "genero", "region", "ocupacion"} for it in panel)


# ---- guardia y vault como repositorio -----------------------------------------------------------


def test_guardia():
    from arnes.guardia import revisar_texto

    assert revisar_texto("contacto: ana.lopez@" + "hotmail.com")
    assert revisar_texto("token sk-" + "ant-api03-abcdefghijklmnop")
    assert revisar_texto("CURP: GOMA850101" + "HDFRRN09")
    assert revisar_texto("tarjeta 4111 1111 " + "1111 1111")              # pasa Luhn
    assert not revisar_texto("folio 1234 5678 9012 3456")            # no pasa Luhn
    assert not revisar_texto("correo: prueba@example.com · nombre@empresa.com")
    assert not revisar_texto("Co-Authored-By: Claude <noreply@anthropic.com>")


def test_vault_sincronizar(tmp_path, monkeypatch):
    import subprocess

    import pytest

    from arnes import vault as mv

    def git(d, *a):
        subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)

    remoto, V, otro = tmp_path / "remoto.git", tmp_path / "vault", tmp_path / "otro"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remoto)], check=True)
    (V / "02-Conceptos").mkdir(parents=True)
    (V / "02-Conceptos" / "a.md").write_text("# A\n", encoding="utf-8")
    git(V.parent, "init", "-q", "-b", "main", str(V))
    for d in (V,):
        git(d, "config", "user.email", "prueba@example.com")
        git(d, "config", "user.name", "Prueba")
    git(V, "remote", "add", "origin", str(remoto))
    monkeypatch.setenv("ARNES_VAULT", str(V))

    assert "subido" in mv.sincronizar(silencioso=True)

    # una nota nueva y otra editada: el mensaje lo dice
    (V / "02-Conceptos" / "b.md").write_text("# B\n", encoding="utf-8")
    (V / "02-Conceptos" / "a.md").write_text("# A\nmás\n", encoding="utf-8")
    assert mv.sincronizar(silencioso=True).startswith("Vault: notas 1 nuevas, 1 editadas")

    # un cambio hecho en otro clon se integra antes de subir
    subprocess.run(["git", "clone", "-q", str(remoto), str(otro)], check=True)
    git(otro, "config", "user.email", "prueba@example.com")
    git(otro, "config", "user.name", "Prueba")
    (otro / "02-Conceptos" / "c.md").write_text("# C\n", encoding="utf-8")
    git(otro, "add", "-A")
    git(otro, "commit", "-qm", "c")
    git(otro, "push", "-q")
    (V / "02-Conceptos" / "d.md").write_text("# D\n", encoding="utf-8")
    assert "subido" in mv.sincronizar(silencioso=True)
    assert (V / "02-Conceptos" / "c.md").exists()

    # la guardia bloquea y no deja nada en stage
    (V / "02-Conceptos" / "e.md").write_text("correo real: ana.lopez@" + "hotmail.com\n", encoding="utf-8")
    with pytest.raises(mv.ErrorVault, match="guardia"):
        mv.sincronizar(silencioso=True)
    assert subprocess.run(["git", "-C", str(V), "diff", "--cached", "--quiet"]).returncode == 0


# ---- recorrido en Figma: zonas por resaltados y overlays ----------------------------------------


def test_zonas_por_resaltados_de_figma(tmp_path):
    from PIL import Image, ImageDraw

    from arnes.navegador import overlay_abierto, zonas_por_pistas

    marco = dict(x=0, y=0, w=400, h=800)
    base = Image.new("RGB", (400, 800), (20, 130, 90))
    d = ImageDraw.Draw(base)
    d.rectangle([40, 700, 360, 740], fill=(255, 255, 255))          # botón blanco
    base.save(tmp_path / "base.png")
    pistas = base.copy()
    ImageDraw.Draw(pistas).rectangle([38, 698, 362, 742], fill=(173, 224, 245), outline=(0, 170, 220), width=2)
    pistas.save(tmp_path / "pistas.png")
    z = zonas_por_pistas(tmp_path / "base.png", tmp_path / "pistas.png", marco)
    assert len(z) == 1 and abs(z[0]["tocar"][1] - 720) <= 3

    # overlay: la mitad de arriba se oscurece (velo) y abajo aparece una hoja clara
    previa = Image.new("RGB", (400, 800), (200, 200, 200))
    previa.save(tmp_path / "previa.png")
    actual = Image.new("RGB", (400, 800), (110, 110, 110))
    ImageDraw.Draw(actual).rectangle([0, 300, 399, 799], fill=(245, 245, 245))
    actual.save(tmp_path / "actual.png")
    p = overlay_abierto(tmp_path / "previa.png", tmp_path / "actual.png", marco)
    assert p and 300 <= p["y"] <= 320
    assert overlay_abierto(tmp_path / "previa.png", tmp_path / "previa.png", marco) is None


def test_consumo_en_tokens():
    from arnes import consumo

    u = {"input_tokens": 2, "cache_creation_input_tokens": 2865, "cache_read_input_tokens": 21665, "output_tokens": 758}
    d = consumo.de_usage(u)
    assert consumo.total(d) == 25290 and consumo.nuevos(d) == 3625
    assert consumo.total(consumo.sumar(d, d, None)) == 50580
    assert consumo.cifra(1_234_567) == "1.2 M" and consumo.cifra(24_061) == "24 mil"
    # el modelo reproduce lo medido: una sesión de 5 pasos ≈ 120–135 mil tokens
    assert 110_000 <= consumo.total(consumo.estimar_recorrido(5)) <= 140_000
