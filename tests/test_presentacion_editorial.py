"""La edición local del HTML no se pierde al regenerar un reporte."""
from types import SimpleNamespace

import pytest

from arnes.reporte import _presentacion_editorial


def test_presentacion_editorial_optativa(tmp_path):
    estudio = SimpleNamespace(dir=tmp_path)
    assert _presentacion_editorial(estudio, {}, "generado") == "generado"
    fuente = tmp_path / "fuente.html"
    fuente.write_text('<h1>Edición revisada</h1>', encoding="utf-8")
    assert _presentacion_editorial(
        estudio, {"presentacion": {"html_local": "fuente.html"}}, "generado"
    ) == '<h1>Edición revisada</h1>'


def test_presentacion_editorial_falla_sin_sobreescribir(tmp_path):
    estudio = SimpleNamespace(dir=tmp_path)
    with pytest.raises(FileNotFoundError):
        _presentacion_editorial(estudio, {"presentacion": {"html_local": "ausente.html"}}, "generado")
    with pytest.raises(ValueError, match="dentro del estudio"):
        _presentacion_editorial(estudio, {"presentacion": {"html_local": "../fuera.html"}}, "generado")


def test_regenerar_conserva_fuente_y_markdown(tmp_path, monkeypatch):
    import importlib
    from arnes.reporte import construir

    fuente = tmp_path / "fuente.html"
    fuente.write_text('<h1>Edición conservada</h1>', encoding="utf-8")
    modulo = SimpleNamespace(armar=lambda e, n: ("HTML genérico", "Markdown de los datos"))
    monkeypatch.setattr(importlib, "import_module", lambda *args: modulo)
    marcas = []
    estudio = SimpleNamespace(
        dir=tmp_path, metodo="comprension",
        narrativa=lambda: {"presentacion": {"html_local": "fuente.html"}},
        entregable=lambda **kwargs: "informe",
        ruta=lambda *parts: tmp_path.joinpath(*parts),
        marcar=lambda *args, **kwargs: marcas.append((args, kwargs)),
    )
    (tmp_path / "reporte").mkdir()
    construir(estudio)
    assert (tmp_path / "reporte/informe.html").read_text() == fuente.read_text()
    assert (tmp_path / "reporte/informe.md").read_text() == "Markdown de los datos"
    assert marcas[0][0] == ("reporte",)
