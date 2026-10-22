# Crecer el arnés sin romperlo

Reglas para cambiar el arnés y mantenerlo confiable. Valen para personas y para Claude.

## Lo automático

| Cuándo | Qué corre | Dónde |
|---|---|---|
| Antes de cada commit del arnés | guardia (correos, llaves, CURP, tarjetas), lint, pruebas | `.githooks/pre-commit` (activar: `git config core.hooksPath .githooks`) |
| En cada push a GitHub | lo mismo, sobre todo el repositorio | `.github/workflows/pruebas.yml` |
| Al escribir una síntesis | commit y push del vault, con guardia | `arnes sintesis` |
| Cada hora | commit y push de lo que se escribió en Obsidian | `arnes vault automatizar` (launchd; bitácora en `~/Library/Logs/arnes-vault.log`) |
| Al clonar o abrir Claude Code | Python, dependencias, vault, Playwright, guardia, comando `arnes` | `bin/instalar` (hook `SessionStart` en `.claude/settings.json`) |
| Al cambiar `pyproject.toml` | reinstalación de dependencias en el siguiente `arnes` | `bin/arnes` |
| Cuando algo falla o alguien empieza | revisión del entorno | `arnes doctor` |

## Lo que se hace a mano

1. **Cada cambio de código, con su prueba** en `tests/test_arnes.py`. Las pruebas no llaman al modelo ni gastan.
2. **El texto de las sesiones es parte del instrumento** (`arnes/metodos/comprension.py` y `recorrido.py`). Si cambia,
   se vuelve a correr la réplica (`docs/VALIDACION.md`) antes de usarlo en un estudio.
3. **Un estándar nuevo** (de UiX, del producto, del vault) entra como fuente cruda en `fuentes-*/`, más una versión
   verificable en YAML que lee el código. Nunca se reescribe la fuente.
4. **Una biblioteca de personas nueva** sigue `metodos/persona/METODO.md` y pasa `arnes persona validar` y `probar`.
5. **Datos de prueba siempre ficticios.** Correos con `@example.com`. La guardia bloquea lo que parece real.
6. **Al cerrar una sesión de trabajo**, una entrada en `docs/BITACORA.md`: qué se hizo, qué se decidió y por qué,
   qué quedó pendiente.
7. **Una dependencia nueva** va en `pyproject.toml`: los clones la instalan solos. La versión de Playwright está
   fija en `bin/playwright-cli`; cambiarla es cambiar el instrumento de recorrido.
8. **Cambios grandes en una rama** (`git switch -c <tema>`) y se integran cuando las pruebas pasan en GitHub.

## Saltarse la guardia

`git commit --no-verify` existe, pero solo para un falso positivo que no se pueda reescribir (por ejemplo, un número
de folio que pasa la validación de tarjeta). Si pasa, se ajusta `arnes/guardia.py` con su prueba, no se salta de nuevo.
