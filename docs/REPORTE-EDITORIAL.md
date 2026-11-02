# Reporte editorial (template de recorrido)

Es el reporte principal de un estudio de recorrido desde noviembre de 2026. El diseño es el que Alexis definió con
OU 2.0 PWA MVP. `arnes reporte` lo genera; nadie edita el HTML.

Ejemplo completo: `estudios/2026-10-28-ou2-pwa-mvp/editorial.yaml`.

## Quién pone qué

| Qué | Dónde | Quién |
|---|---|---|
| Diseño, portada, panel de lecturas, biblioteca de evidencias | `arnes/reporte/plantilla_editorial/assets/` | El template |
| Sesiones, tramos, completitud, confianza, orientación, método | datos del estudio | Se calcula |
| Hallazgos, hipótesis, límites | `narrativa.yaml` | Investigación |
| Titular, tramos con nombre, casos, voces, capítulos, decisiones | `editorial.yaml` | Investigación |

Sin `editorial.yaml` el reporte sale igual, con textos automáticos. Sirve para revisar, no para entregar: `arnes verificar`
lo avisa.

## Qué genera

```
reporte/<nombre>.html            reporte editorial
reporte/<nombre>-tablero.html    tablero interactivo (docs/TABLERO.md)
reporte/<nombre>-detalle.html    documento completo
reporte/<nombre>.md              versión en texto
reporte/lecturas/                una página por sesión, tramo, caso, mapa y fuente
reporte/assets/                  recursos copiados del template y datos de cada lectura
```

Abre con doble clic y sin servidor, pero **no es un solo archivo**: para compartirlo van `reporte/` y `datos/` juntos. Las
carpetas `lecturas/` y `assets/report-reader/data/` se borran y se regeneran en cada `arnes reporte`: no editarlas.

## Las cifras no se escriben a mano

En `cifras` se declara de dónde sale cada número y en el texto se usa `{{nombre}}`:

```yaml
cifras:
  buscan_total: {hallazgo: H1, tarea: T1}     # sesiones del hallazgo sobre las de la tarea
  notan_buro: {sesiones: [T1-bryan-1, T1-itzel-2], tarea: T1}

portada:
  intro: "En el simulador, **{{buscan_total|de}} sesiones** buscaron el costo total."   # → 8 de 8
```

Disponibles sin declarar: `completan`, `abandonan`, `completan_T1`, `abandonan_T4`. Formatos: `{{x}}` 8/8 · `{{x|de}}` 8 de 8 ·
`{{x|x}}` 8. Sin tarea, la base son las tareas donde ocurre, no todo el estudio.

Dos tarjetas se calculan solas de las sesiones, con su lectura de cálculo:

- `tipo: confianza` (`tarea`, `antes`, `despues`): compara dos pantallas dentro de cada corrida.
- `tipo: orientacion` (`tareas`): cuenta respuestas a «¿sabes en qué parte vas?». Son respuestas repetidas, no personas.

## Qué revisa `arnes verificar`

| Bloquea | Avisa |
|---|---|
| Cifra declarada distinta a la calculada | Número escrito a mano en un texto |
| Sesiones inexistentes en una cifra | Cifra sin sesiones que la respalden |
| Cita que no aparece textual en su sesión | Hallazgo de severidad 3–4 fuera de los capítulos |
| Caso con sesión, paso o pantalla incorrectos | Reporte sin `editorial.yaml` |
| Enlace o recurso local roto | Palabras que prohíbe la guía editorial |

Lo que no puede revisar: si la lista de sesiones de una cifra describe de verdad lo que dice el texto. Eso sigue siendo
criterio de quien investiga.

## Pasos para un estudio nuevo

1. `arnes nuevo recorrido <nombre>` ya deja `editorial.yaml` en blanco.
2. Después de `arnes analizar` y de escribir `narrativa.yaml`, llenar `editorial.yaml`. Empezar por `tramos` y `cifras`.
3. `arnes reporte` y `arnes verificar`, y mirar la página a 1440 y 390 px.

## Estudios con HTML propio

`presentacion: {html_local: reporte/fuente-editorial.html}` en `narrativa.yaml` conserva un HTML revisado y salta el generador.
Lo usa OU 2.0 PWA MVP. Si cambian sus resultados, hay que revisar ese HTML a mano.

## Límites

- Solo método `recorrido`. Comprensión conserva su reporte autocontenido.
- La imagen de portada es una escena conceptual fija. Los retratos solo existen para los perfiles del panel PWA; otros perfiles
  muestran su inicial.
