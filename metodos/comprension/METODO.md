# Método 2 · Comprensión de pantallas estáticas

Para preguntas del tipo **«¿se entiende lo que dice esta pantalla?»** y **«¿cuál de dos variantes se entiende mejor?»**.
Destilado de «Investigacion-pantallas-de-recompra» y «Investigacion comprension de pantallas en recompra».
Validado con una réplica: `estudios/2026-10-05-recompra-comprension-replica` (ver `docs/VALIDACION.md`).

## Cuándo usarlo

- Hay pantallas finales (exports de Figma, capturas) y una pregunta de comprensión o de UX writing.
- Se comparan variantes A/B de la misma pantalla.
- Si la pregunta es sobre **navegar** un flujo (dónde se traban, si llegan al final), usar el método 3.

## Fases

| Fase | Qué hace | Quién | Etiqueta |
|---|---|---|---|
| 0 · Medición | Zonas de lectura (AOI), alto de línea, contraste, pliegue | `arnes medir` | EVIDENCIA |
| 1 · UX writing | Revisión experta de cada texto contra W1–W10, severidad 0–4 | investigador → `narrativa.yaml` | EVIDENCIA + INFERENCIA |
| 2 · Atención predicha | Saliencia visual (OpenCV), porción por zona | `arnes medir` | MODELO |
| 3 · Puntos de lectura | Orden y tiempo por zona; vistazo de 5 s por perfil | `arnes medir` | EVIDENCIA + SIMULACIÓN |
| 4 · Sesiones | Perfil × pantalla × modo × corrida, contexto limpio | `arnes sesiones` | SIMULACIÓN |
| 4b · Opcionales | Continuaciones, comparación pareada, sensibilidad OCEAN | `arnes sesiones` | SIMULACIÓN |
| 5 · Análisis | Aciertos por celda, matrices, sin cobertura, reglas usadas | `arnes analizar` | — |
| 6 · Reporte | Narrativa + HTML autocontenido + .md | investigador + `arnes reporte` | — |
| 7 · Control final | Recuento de cifras, cadena hallazgo → recomendación | `arnes verificar` | — |

## Cómo se arma cada sesión

- **Vistazo**: el perfil recibe solo el texto que alcanzó a leer en 5 segundos, en orden, con su jerarquía
  («letra muy grande», «letra chica», «botón»). Lo que no alcanzó, no lo ve.
- **Completa**: el perfil abre la imagen con la herramienta Read y recibe la tabla de altos de línea medidos.
- **Primero la pregunta abierta**, después las cerradas, para no sembrar la respuesta.
- **El texto de la sesión es parte del instrumento.** Cambiar la redacción cambió los resultados en la
  validación (79% → 86% de coincidencia con el original). La plantilla JSON en línea y las reglas de sesión
  de `arnes/metodos/comprension.py` son las validadas: no reescribirlas sin volver a correr la réplica.

## Puntos de lectura: reglas antes que OCEAN

El orden base sale de la saliencia y la posición vertical (lo que se ve sin desplazar va primero). Después:

1. **Reglas del User Persona** (en `personas/<bib>/biblioteca.yaml`, clave `lectura`): p. ej. C-01 y D-02
   marcan como no leída la letra de menos de 13 px; A-04 cierra la lectura al llegar al botón.
2. **Umbrales OCEAN** [SUPUESTO METODOLÓGICO] (`arnes/ocean.py`): C ≤ 45 cierra en la primera acción;
   N ≥ 65 salta a notas y asteriscos; O ≥ 70 se detiene más en enlaces y tarjetas.
3. **Si chocan, gana la regla.** Fidelidad a los datos > consistencia conductual > completitud narrativa.

Lo que no tiene regla queda igual para todos y se rotula «sin cobertura».

## Diseño típico

`variantes × perfiles × modos × corridas`. Con 2 variantes, 8 perfiles, 2 modos y 3 corridas: 96 sesiones
(≈ US$ 5–8). Las corridas buscan **interpretaciones distintas**, no porcentajes: nunca reportar «2 de 3
entenderían» como tasa de una población.

Con el panel `ocean8` los Boomers quedan sobrerrepresentados a propósito (2 de 8 frente a 5.4% de la base).

## Auditoría de UX writing (Fase 1)

| # | Criterio | Qué se revisa |
|---|---|---|
| W1 | Lo importante primero | ¿La noticia que cambia la decisión está en el texto de mayor jerarquía? |
| W2 | Coherencia entre textos | ¿Algún texto desmiente a otro en la misma pantalla? |
| W3 | Una idea por frase | Frases partidas en varios tamaños, sin puntuación entre ideas |
| W4 | Lenguaje del cliente | Términos internos frente a los del cliente |
| W5 | Negativas dichas de frente | ¿El «no» se dice claro, sin esconderlo ni culpar? |
| W6 | Causa y salida | ¿Dice por qué y qué puede hacer el cliente? |
| W7 | El botón anticipa el resultado | ¿El verbo describe lo que pasa al tocar? |
| W8 | Enlaces que se explican solos | ¿El enlace dice a dónde lleva? |
| W9 | Ortografía y concordancia | Signos, acentos, género y número |
| W10 | Tamaño y contraste del texto que decide | Lo que cambia la decisión, ¿se alcanza a leer? |

Cada observación va como hallazgo en `narrativa.yaml` con `reescritura: [[actual, recomendado, razón]]`.

## Tropiezos conocidos

- **YAML y «no».** El arnés usa un cargador propio que deja `no`, `si`, `on` y `off` como texto. Si se lee un
  `estudio.yaml` con otro programa, `no` se vuelve `false`.
- **Texto claro sobre color.** La medición automática del alto de línea no lo detecta (p. ej. un chip blanco
  sobre verde). Usar `alto_px` en la zona y declararlo.
- **Nombre de ejemplo.** Si la pantalla dice «María», poner `nombre_de_ejemplo: María`; si no, los perfiles
  se distraen («dice María y yo me llamo Bryan»).
- **Un A/B de varias variables.** Si A y B difieren en más de una cosa, el resultado es de la pantalla
  completa, no de un elemento. Declararlo en el protocolo.
- **Saliencia ≠ ojos.** El mapa de atención es igual para todos los perfiles y no es seguimiento ocular;
  decirlo en el gráfico, no en una nota al pie.

## Firmeza y auditoría (del vault)

- `arnes revisar` antes de correr: los 5 tipos de pregunta sugestiva bloquean; preguntas que copian el texto de la
  pantalla, opciones sin salida neutra o grupos sin `baseline: true` son avisos.
- `arnes sesiones --piloto`: un perfil, corrida 1. Leer los estímulos y las respuestas antes de correr el resto.
- `arnes auditar`: Fase 1 con 3 evaluadores independientes contra W1–W10; el consenso (2 o más) es la primera pasada.
- `arnes analizar` informa estabilidad entre corridas, brechas entre variantes con intervalo de Wilson y si el panel
  responde todo igual. Una brecha «no concluyente» no se presenta como diferencia (`compara` en el KPI).

## Guía de estilo del producto

Con `guia_estilo: pwa`, `arnes estilo` revisa cada pantalla completa (las frases pueden repartirse en varias zonas)
contra las reglas verificables de los manuales de la PWA (`fuentes-producto/pwa/reglas-estilo.yaml`): «crédito»
prohibido, signos de apertura, voz pasiva, condicionales, formatos de dinero, fecha y hora, emojis, género marcado,
exceso de «tu» y de «María», acentos. `arnes auditar` suma los criterios de tono G1–G8 a W1–W10. Cuando dos
secciones de la guía se contradicen, el reporte lo dice como tensión de la guía, no como error de la pantalla.
