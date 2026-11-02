"""El reporte editorial calcula sus cifras y no deja pasar lo que no respaldan las sesiones."""
import json
from pathlib import Path

import pytest
import yaml

from arnes.estudio import Estudio
from arnes.reporte import editorial
from arnes.reporte.editorial import RECURSOS, Contexto, decimal, revisar

OU2 = yaml.safe_load((Path(__file__).parent.parent / "estudios/2026-10-28-ou2-pwa-mvp/estudio.yaml").read_text(encoding="utf-8"))


def _paso(n, pantalla, confianza, pensamiento="Sigo adelante con esto."):
    return dict(n=n, pantalla=pantalla, perfil=dict(confianza=confianza, pensamiento=pensamiento), accion=dict(tipo="tocar", x=1, y=2))


def _estudio(tmp_path, N=None, E=None):
    cfg = dict(id="prueba", titulo="Prueba", metodo="recorrido", fecha="2026-11-02", biblioteca=OU2["biblioteca"], panel=OU2["panel"], corridas=1,
               material="web", tareas=[dict(id="T1"), dict(id="T2")], hipotesis=[dict(id="H1", texto="Una hipótesis")])
    (tmp_path / "estudio.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
    (tmp_path / "narrativa.yaml").write_text(yaml.safe_dump(N or dict(
        titulo_corto="Prueba", titular="El flujo se termina", veredicto="Pasó algo.", positivos=["Carga rápido"],
        hipotesis_resultado=[dict(id="H1", estado="se_sostiene", evidencia="Se vio.")],
        hallazgos=[dict(id="H1", titulo="El costo no aparece en la pantalla", severidad=3, donde="Plazo", pantalla="a", sesiones=["T1-bryan-1", "T1-itzel-1"],
                        hallazgo="h", interpretacion="i", recomendacion="r")]), allow_unicode=True), encoding="utf-8")
    if E is not None:
        (tmp_path / "editorial.yaml").write_text(yaml.safe_dump(E, allow_unicode=True), encoding="utf-8")
    e = Estudio(tmp_path)
    e.sesiones_dir.mkdir(parents=True)
    metricas = []
    for t in ("T1", "T2"):
        for i, (perfil, a, b) in enumerate((("bryan", 60, 40), ("itzel", 61, 41))):
            sid = f"{t}-{perfil}-1"
            s = dict(id=sid, tarea=t, corrida=1, integrante=perfil, nombre=perfil.capitalize() + " Apellido", resultado="abandono" if t == "T2" and i else "exito",
                     pasos=[_paso(1, "a", a, "Ese costo no me lo dicen, y así no sigo."), _paso(2, "b", b)])
            (e.sesiones_dir / f"{sid}.json").write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
            metricas.append(dict(sesion=sid, tarea=t, integrante=perfil, resultado=s["resultado"], completa=s["resultado"] == "exito",
                                 sabe_donde_va=dict(si=1, mas_o_menos=2, no=0)))
    e.ruta("datos", "agregado.json").write_text(json.dumps(dict(n_sesiones=4, resultados={}, metricas=dict(sesiones=metricas, tareas={}))), encoding="utf-8")
    return e


def test_cifras_se_calculan_con_su_base(tmp_path):
    e = _estudio(tmp_path)
    ctx = Contexto(e, e.narrativa())
    assert ctx.cifra("completan").texto() == "3/4"
    assert ctx.cifra("abandonan_T2").texto("de") == "1 de 2"
    # sin tarea, la base es la tarea donde ocurre: 2 de 2 en T1, no 2 de las 4 del estudio
    assert ctx.cifra(dict(hallazgo="H1")).texto() == "2/2"


def test_confianza_sale_de_pares_y_orientacion_de_respuestas(tmp_path):
    e = _estudio(tmp_path)
    ctx = Contexto(e, e.narrativa())
    d = ctx.confianza(dict(tarea="T1", antes="a", despues="b"))
    assert (d["antes"], d["despues"], d["minima"], d["maxima"]) == (60.5, 40.5, 20, 20)
    o = ctx.orientacion({})
    assert (o["dudas"], o["total"], o["sesiones"]) == (8, 12, 4)
    assert decimal(60.25) == "60.3"


def test_sin_editorial_sale_el_template_completo(tmp_path):
    e = _estudio(tmp_path)
    html = editorial.construir(e, e.narrativa(), "informe")
    assert "3/4" in html and "Investigación sintética" in html and 'id="metodo"' in html
    assert e.ruta("reporte/lecturas/T1-bryan-1.html").exists() and e.ruta("reporte/lecturas/tramo-T2.html").exists()
    manifest = e.ruta("reporte/assets/report-reader/manifest.js").read_text(encoding="utf-8")
    assert '"marca":"Prueba"' in manifest and "ReportReaderConfig" in manifest
    ok, avi, err = revisar(e, e.narrativa())
    assert not err and any("sin editorial.yaml" in x for x in avi)


def test_verificar_bloquea_lo_que_no_respaldan_las_sesiones(tmp_path):
    e = _estudio(tmp_path, E=dict(
        cifras=dict(mala=dict(hallazgo="H1", valor="5/8"), fantasma=dict(sesiones=["T9-nadie-1"], tarea="T1")),
        voces=[dict(sesion="T1-bryan-1", cita="Una frase inventada por quien redacta")],
        casos=[dict(id="evidencia-x", sesion="T1-bryan-1", paso=99)],
        apertura=dict(respuesta="Lo dicen 7 de 9 sesiones.")))
    ok, avi, err = revisar(e, e.narrativa())
    texto = " ".join(err)
    assert "dice 5/8 y los datos dicen 2/2" in texto and "sesiones inexistentes" in texto
    assert "no aparece textual" in texto and "paso que no existe" in texto
    assert any("escrito a mano" in x for x in avi)


def test_cita_textual_pasa(tmp_path):
    e = _estudio(tmp_path, E=dict(voces=[dict(sesion="T1-bryan-1", cita="Ese costo no me lo dicen, y así no sigo.")]))
    ok, avi, err = revisar(e, e.narrativa())
    assert not err and any("es textual" in x for x in ok)


def test_cifra_desconocida_en_el_texto_falla(tmp_path):
    e = _estudio(tmp_path)
    with pytest.raises(ValueError, match="no existe"):
        Contexto(e, e.narrativa()).t("{{cifra-rara|de}}")


def test_recursos_sin_referencias_de_un_estudio():
    for f in list(RECURSOS.rglob("*.js")) + list(RECURSOS.rglob("*.css")):
        t = f.read_text(encoding="utf-8")
        for fijo in ("oupwa", "OU 2.0", "Itzel", "Incode", "fachada", "del MVP"):
            assert fijo not in t, f"{f.name}: {fijo}"


def test_plantilla_en_blanco_usa_los_valores_por_omision(tmp_path):
    e = _estudio(tmp_path)
    plantilla = Path(editorial.__file__).parents[2] / "metodos/recorrido/editorial.plantilla.yaml"
    (tmp_path / "editorial.yaml").write_text(plantilla.read_text(encoding="utf-8"), encoding="utf-8")
    html = editorial.construir(e, e.narrativa(), "informe")
    assert "<h1>Prueba</h1>" in html and "El costo no aparece en la pantalla" in html
