# Guía de naming de archivos

*UiX · Última actualización: abril 2026*

## Por qué estandarizar

Un nombre claro y común nos permite encontrar, entender y dar seguimiento a la información, no solo a UiX, también a POs, PMs y Devs. Además da control documental y trazabilidad: sirve como evidencia en auditorías, revisiones internas, solicitudes de clientes y temas legales (qué información se usó y cuál es la versión final).

## Estructura

| Tipo | Formato |
|---|---|
| Investigación | `proyecto-metodologia-tema_aaaa-mm-dd-vN` |
| Documentación general (no research) | `proyecto-tema_aaaa-mm-dd-vN` |

**Ejemplo:** `zeus-pdu-home_2026-04-23-v1`

| Proyecto | Metodología | Tema | Fecha | Versión |
|---|---|---|---|---|
| zeus | pdu | home | 2026-04-23 | v1 |

**Reglas de formato**
- Minúsculas, sin espacios, sin acentos.
- Guion `-` entre elementos y guion bajo `_` solo antes de la fecha.

## Dónde aplicarlo

- Protocolo
- Maze, Forms o cualquier herramienta de research
- Presentación de resultados (frame y PDF)
- Archivo o página de Figma del flujo evaluado

## Qué va en cada campo

### 1. Proyecto: ¿para qué producto es?

- Usa el nombre completo o la abreviatura (`prestaprenda`/`pp`, `originacion`/`ou`, `cobranza`/`cob`), pero **elige una sola forma por proyecto** y úsala siempre.
- Si el proyecto tiene varios productos, inclúyelos en el nombre:
  - `oupwa-pdu-biometricos_2026-04-23-v1`
  - `oupax-pdu-minegocio_2026-04-28-v1`
  - `oucanales-abtesting_2026-04-30-v1`

**Cómo elegir el nombre.** Antes de decidirlo, pregunta a tu Customer Success y/o Product Designer:
1. ¿Cómo lo nombran los clientes?
2. ¿Cómo quedó formalizado en la contratación con UiX?
3. ¿Cómo lo conoce el equipo UiX?

El nombre puede cambiar desde la etapa conceptual hasta producción. Abre la conversación con CS, PD y diseñadores para acordar si se mantiene.

> **Ejemplo:** un proyecto nació como "Botón de Pago". El cliente propuso "Proceso Único de Pago" y "Botón Único de Pago", pero nunca se oficializaron, así que se conservó el original. Finalmente el producto se llamó oficialmente "Azteca Pago", y UiX adoptó ese nombre.

### 2. Metodología: ¿qué tipo de investigación es?

| Código | Metodología |
|---|---|
| `abtesting` | A/B Testing |
| `pdu` | Prueba de usabilidad |
| `psus` | Prueba SUS |
| `entrevistas` | Entrevistas a profundidad |
| `cardsorting` | Card Sorting |
| `treetesting` | Tree Testing |
| `encuestas` | Encuestas |
| `hmw` | How Might We |
| `mystery` | Mystery Shopper |
| `aheuristico` | Análisis heurístico |
| `bench` | Benchmark |
| `focusg` | Focus Group |

### 3. Tema: ¿qué se evalúa?

Flujo, fase, paso, pantalla o componente. Ejemplos: `compraexpress-shopinbaz`, `compraexpress-elektra`, `documentos-ine`, `documentos-domicilio`, `dashboard`, `pagoinicial`, `login`, `biometricos`.

### 4. Fecha: ¿cuándo terminó el estudio?

Formato `aaaa-mm-dd` (ISO 8601): ordena bien por año, mes y día y evita confusiones entre formatos.

**Dos estudios iguales el mismo día** (mismo proyecto, metodología y tema): agrega `waveN` al final del tema.
- `zeus-pdu-home-wave1_2026-04-23-v1`
- `zeus-pdu-home-wave2_2026-04-23-v1`

### 5. Versión

`v1`, `v2`, etc. Sube el número cada vez que se actualiza el archivo.

## Por qué la fecha va al final

ISO 8601 recomienda la fecha al inicio, pero para nuestros stakeholders (en su mayoría POs y PMs) lo primero que buscan es el proyecto. Dejamos el proyecto al frente y la fecha al final.
