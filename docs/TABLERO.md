# Tablero de investigación (reporte de recorrido)

> Desde noviembre de 2026 el reporte principal de un recorrido es el editorial ([REPORTE-EDITORIAL.md](REPORTE-EDITORIAL.md)).
> El tablero sigue generándose como `<nombre>-tablero.html` y se abre desde «Cómo leer este estudio».

Un tablero para decidir con evidencia UX, no un informe lineal. Lo genera `arnes reporte` (`arnes/reporte/tablero.py`,
`tablero.css`, `tablero.js`) desde los datos del estudio. El reporte completo y lineal sigue disponible como
`<nombre>-detalle.html`.

Principio: **Resumen → Hallazgo → Evidencia → Detalle**. Menos información visible a la vez no es menos información
disponible: todo lo del reporte anterior sigue a un clic.

---

## A. Auditoría del reporte anterior

| | |
|---|---|
| **Funciona** | Titular con la conclusión; KPIs recontados por `arnes verificar`; hallazgos con hallazgo → interpretación → recomendación; aviso de investigación sintética; trazabilidad a capturas y sesiones. |
| **Sobrecarga** | 11 pestañas al mismo nivel; todo se lee en orden; los 9 hallazgos con el mismo peso visual; tablas largas de auditoría en la página principal; la confianza y la fricción por pantalla no se ven como recorrido. |
| **Sale del primer nivel** | Tabla completa de la auditoría, guía de estilo, accesibilidad (WCAG), demográficos, fases y huellas. Pasan a Metodología y Evidencia. |
| **Gana jerarquía** | El veredicto, los 3 hallazgos que piden acción, dónde cae la confianza en el recorrido y qué validar con personas. |

## B. Arquitectura de información

```
01 Resumen       veredicto · KPIs · qué requiere atención (top 3) · fricción del recorrido · qué cambiar primero · lo que ya funciona
02 Recorrido     mapa del recorrido (nodos por etapa) · confianza por etapa (línea) · mapa de fricción (etapas × perfiles) · métricas por tarea
03 Hallazgos     filtros (severidad, confianza) · tarjetas de hallazgo · matriz severidad × confianza · hipótesis
04 Perfiles      selector de perfil · hallazgo × perfil · lo que dijo cada perfil
05 Evidencia     sesiones (tabla → cajón con la sesión paso a paso) · auditoría con consenso · qué validar con personas
06 Metodología   alcance · etiquetas de evidencia · límites · estado de prototipado · aprendizajes del método · fuentes · reporte completo
```

Si el estudio tiene `datos/tecnico.json` (`arnes tecnico`, productos web y PWA), aparece **Calidad técnica** entre
Perfiles y Evidencia: KPIs con estado (pantallas sin fallas WCAG, objetivos < 24 px, foco visible, LCP, INP,
legibilidad INFLESZ, sin conexión, retoma), reglas de axe con criterio WCAG, impacto y pantallas, tabla pantalla por
pantalla (clic → cajón con captura y reglas), carga en frío y con caché contra los umbrales de Core Web Vitals,
lista de PWA, retoma y ruta mínima. El Resumen muestra 4 de esos KPIs, también en modo ejecutivo. Todo es
EVIDENCIA medida en el producto; la legibilidad es métrica derivada.

Controles globales: modo **Ejecutivo / Investigación**, **Tarea** (Todas · T1 · T2) y **Perfil** (Todos · cada perfil).
El modo ejecutivo deja solo el Resumen (lectura < 2 minutos).

## C. Plan de visualización

| Pregunta | Dato | Visualización | Interacción | Razón |
|---|---|---|---|---|
| ¿Cuál es el estado general? | completitud, sin fricción, CES, pasos, confianza mínima, primer toque | Tarjetas KPI con estado (positivo · atención · crítico · contexto) | — | Son números absolutos; el estado lleva color + símbolo + texto |
| ¿Dónde ocurre el problema? | confianza y fricción medias por etapa, hallazgos por etapa | Mapa del recorrido (nodos horizontales) | Pasar el cursor o el foco: métricas de la etapa | Ubica el problema en el orden del flujo |
| ¿Dónde empieza a caer la confianza? | confianza media por etapa, general y por perfil | Línea (0–100) con anotaciones de los momentos rojos | Botones por perfil; cruz y tooltip; vista de tabla | Cambio a lo largo de una secuencia ordenada |
| ¿La fricción es de todos o de algunos? | fricción media por etapa × perfil | Mapa de calor (escala de un solo tono, valor escrito en la celda) | Tooltip con confianza y una cita; en móvil, lista ordenada | Concentración, consistencia y casos aislados |
| ¿Qué atiendo primero? | severidad y confianza de investigación por hallazgo | Dispersión severidad × confianza | Clic en un punto: abre la evidencia | Dos dimensiones ordinales; el cuadrante «actuar primero» se ve solo |
| ¿Le pasa a todos los perfiles? | sesiones afectadas por hallazgo e integrante | Matriz hallazgo × perfil (● ◐ ○ —) | Clic en la fila: evidencia | Se escanea en segundos |
| ¿Cuánto cuesta cada tarea? | pasos, clics, campos, tiempo estimado por tarea | Barras horizontales, una escala por métrica | — | Métricas de distinta escala: nunca en un mismo eje |

Reglas: sin gráficos de pastel, velocímetros ni radar; un solo eje por gráfico; el color sigue a la entidad (cada perfil
conserva su color con cualquier filtro); cada gráfico tiene resumen en texto o vista de tabla.

## D. Estructura de la página

```
┌ barra: OU 2.0 · Investigación UX sintética · [Ejecutivo | Investigación] · Tarea · Perfil ──────────┐
│ VEREDICTO (máx. 2 líneas)                                                                             │
│ Confianza: Alta · Tipo: investigación sintética · Estado: requiere validación con personas          │
│ [KPI] [KPI] [KPI] [KPI] [KPI] [KPI]                                                                  │
│ QUÉ REQUIERE ATENCIÓN   01 ……  02 ……  03 ……   (problema · impacto · evidencia · recomendación)      │
│ FRICCIÓN DEL RECORRIDO  ●──●──●──◉──●──◉──●──●──●──●                                                  │
│ QUÉ CAMBIAR PRIMERO 1 · 2 · 3          LO QUE YA FUNCIONA ✓ ✓ ✓                                       │
├ pestañas: Resumen · Recorrido · Hallazgos · Perfiles · Evidencia · Metodología ─────────────────────┤
│ … contenido de la pestaña …                                                         [cajón lateral]   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## E. Componentes

| Componente | Qué muestra | Datos |
|---|---|---|
| `Veredicto` | titular, confianza global, tipo y estado | `narrativa.titular`, `narrativa.confianza` |
| `TarjetaKPI` | valor, etiqueta, contexto, estado, comparador | `agregado.json` (derivados marcados) |
| `MapaRecorrido` | nodos por etapa con estado de fricción | sesiones, `narrativa.pantallas` |
| `GraficoConfianza` | línea por etapa, general y por perfil, anotaciones | sesiones, `narrativa.momentos` |
| `MapaFriccion` | etapas × perfiles | sesiones |
| `TarjetaHallazgo` | observación · interpretación · recomendación · validación · impacto en el usuario · severidad · confianza · fuente | `narrativa.hallazgos` |
| `MatrizHallazgoPerfil` | ● ◐ ○ — | `hallazgos[].sesiones` |
| `CajonEvidencia` | sesiones, capturas, pensamientos (PERFIL SIMULADO), métricas, fuente | sesiones, capturas, auditoría |
| `SelectorPerfil` | filtra recorrido, gráficos, hallazgos y citas | panel |
| `AvisoMetodologico` | investigación sintética, siempre visible | — |
| `TarjetaValidacion` | qué validar, método, qué aprender, muestra UiX, prioridad | `narrativa.validar_con_personas` |
| `TarjetaHipotesis` | estado (✓ · ✕ · ◐ · ?) y evidencia | `estudio.hipotesis`, `narrativa.hipotesis_resultado` |

## F. Sistema visual

- **Tipografía:** sans del sistema. Veredicto 28–34 px / 600; título de sección 20 px; enunciado de hallazgo 17 px / 600;
  cuerpo 15 px / 1.55; nota 13 px. Cifras de tablas y ejes con `tabular-nums`.
- **Espaciado y retícula:** múltiplos de 4 px; contenedor de 1200 px; 12 columnas en escritorio, 6 en tableta, 1 en móvil;
  margen lateral de 16 px en móvil.
- **Superficies:** claras y neutras (`#f9f9f7` página, `#fcfcfb` tarjeta), bordes de 1 px, sin sombras ni degradados.
- **Color con significado:** verde = evidencia positiva, ámbar = atención, rojo = fricción alta o severidad, azul/neutro =
  contexto, violeta = investigación sintética o simulación. Siempre con símbolo y texto: ✓ positivo · ▲ atención ·
  ✕ crítico · ○ contexto.
- **Datos:** perfiles en las ranuras categóricas 1–4 (azul, naranja, aqua, amarillo), validadas en claro y oscuro;
  general en tinta primaria; magnitudes con la rampa azul.
- **Estados e interacción:** foco visible de 2 px; objetivos de al menos 44 × 44 px; transiciones de 150–200 ms que se
  apagan con `prefers-reduced-motion`; tooltips también con teclado.
- **Modo oscuro:** pasos propios de cada rampa, no inversión automática.

## G y H. Interfaz final y estados adaptables

La implementación está en `arnes/reporte/tablero.*`. Escritorio: tablero completo. Tableta: el recorrido sigue
horizontal y con desplazamiento. Móvil: lectura vertical; el mapa de calor se vuelve una lista ordenada por fricción y
el recorrido, una lista de etapas.

## Reglas de integridad

- No se inventa ningún dato. Lo calculado a partir de los datos lleva la etiqueta **Métrica derivada**; la interpretación,
  **Inferencia**; lo que falta, **Sin dato**.
- «8 sesiones sintéticas» o «8 de 8 sesiones del panel», nunca «8 usuarios» ni porcentajes de clientes.
- Prioridad del hallazgo = severidad (1–4) × frecuencia (sesiones afectadas ÷ sesiones de la tarea) × confianza de
  investigación (baja 1 · media 2 · alta 3). Es una métrica derivada; el impacto de negocio se muestra aparte, sin mezclarse.

## Campos opcionales de `narrativa.yaml` que usa el tablero

```yaml
confianza: alta                 # confianza global del veredicto
tablero: {pasos_prometidos: 4}  # comparador del KPI de pasos, si el producto promete algo
etapas: {"node-id": "Etapa"}    # si falta, la etapa es el nombre de la pantalla antes de « · »
hallazgos:
  - impacto_usuario: [confianza, decision]   # comprension · confianza · esfuerzo · decision · continuidad
    validacion: "Qué hay que probar con personas"
validar_con_personas:
  - {que: "…", metodo: abtesting, aprender: "…", hallazgo: H1, prioridad: alta}
```
