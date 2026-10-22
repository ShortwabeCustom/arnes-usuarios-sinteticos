"""YAML sin la trampa de YAML 1.1: `no`, `si`, `on`, `off` quedan como texto.

En los estudios `no` es una opción de respuesta, no un booleano. Solo `true` y `false` lo son.
"""

import re

import yaml


class Cargador(yaml.SafeLoader):
    pass


Cargador.yaml_implicit_resolvers = {k: [(t, r) for t, r in v if t != "tag:yaml.org,2002:bool"]
                                    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}
Cargador.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
                               list("tTfF"))


def cargar(texto: str):
    return yaml.load(texto, Loader=Cargador)
