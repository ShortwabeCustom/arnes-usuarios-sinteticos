---
name: investigacion-sintetica
description: Diseña, corre y reporta un estudio de UX research con usuarios sintéticos usando el arnés de este repositorio — construir un User Persona desde datos, medir la comprensión de pantallas (A/B, vistazo vs. lectura completa) o recorrer un prototipo de Figma o un sitio dev con perfiles que deciden cada paso. Usar siempre que pidan investigar, testear, comparar o validar pantallas, flujos, prototipos o textos con usuarios sintéticos, perfiles, personas, panel OCEAN, Bryan/Itzel/Rosalba/Arturo, o «correr un estudio», aunque no digan «arnés».
---

# Investigación UX sintética con el arnés

Lee `CLAUDE.md` (reglas) y la guía del método antes de proponer nada. El arnés pone la medición, las sesiones,
los agregados, el reporte y el control final; tú pones el diseño del estudio y la narrativa.

## 1. Elegir el método

| Si la pregunta es… | Método | Insumo mínimo |
|---|---|---|
| ¿Quién es el usuario? ¿Qué dice la data? | `persona` | encuesta, mazo, arquetipos |
| ¿Se entiende esta pantalla? ¿A o B? ¿El texto dice lo que creemos? | `comprension` | imágenes de las pantallas |
| ¿Completan el flujo? ¿Dónde se traban o abandonan? | `recorrido` | URL de prototipo Figma o sitio |

Si no está claro, pregunta con una sola pregunta y ofrece la recomendación primero.

## 2. Armar el estudio

```bash
arnes nuevo <metodo> <nombre-corto> --proyecto oupwa --tema <tema>   # naming de UiX
arnes bibliotecas          # bibliotecas y paneles disponibles
arnes conocimiento <metodo>   # notas del vault de Obsidian para este método: léelas antes de escribir el protocolo
```

- Cita en `PROTOCOLO.md` («Referencias del vault») las notas que usaste para decidir algo.
- Los estándares de UiX (`fuentes-equipo/uix/`) aplican a todo estudio: naming con `-sintetico`, cada hallazgo con
  `oportunidad` (mantener · mejorar · incorporar · hacer_diferente), demográficos con evidencia y el semáforo de
  completitud solo como referencia, con su intervalo.

- Copia el material a `material/` tal como llega.
- Completa `estudio.yaml` desde la plantilla. En comprensión, mide las cajas de las zonas mirando la imagen (Read)
  y declara `rol` y `texto` de cada una. En recorrido, define un `fin` que el arnés pueda comprobar.
- Escribe `PROTOCOLO.md` desde la plantilla, empezando por el brief de UiX (brief, autorización, alcance, público,
  decisión de investigar con la matriz impacto × incertidumbre); después: material verificado, hipótesis con criterio de confirmación y de
  descarte, panel, preguntas o tareas, métricas, límites.
- `arnes panel <estudio>`: pega la matriz de diversidad en el protocolo y nombra los vacíos.
- `arnes sesiones <estudio> --simular` (comprensión) o `arnes recorrido <estudio> todos --simular` (recorrido) para
  el total. El consumo se expresa en **tokens**, no en dinero: las sesiones usan la suscripción. Un recorrido de 20
  pasos ≈ 1.1 M tokens, casi todos relectura de caché (≈ 75 mil nuevos).

- Marca el diseño actual como `baseline: true` (comprensión) o `baseline_url` (recorrido). Define `primer_toque` por tarea.
- Si el producto tiene guía (`guia_estilo: pwa`), corre `arnes estilo <estudio>` y `arnes conocimiento <metodo> --producto pwa`.
- `arnes revisar <estudio>`: corrige todo error (preguntas sugestivas o cargadas) y lee los avisos.
- Planea 2–3 corridas: con una sola, ninguna diferencia entre variantes será concluyente.

## 3. ⏸ Aprobación

Muestra en el chat: hipótesis, panel, total de sesiones y costo estimado. **No corras sesiones sin un sí.**

## 4. Correr

- Comprensión: `arnes medir` → revisa el orden de lectura impreso (¿tiene sentido?) → `arnes sesiones --piloto` y
  lee esas sesiones → `arnes sesiones` en segundo plano → `arnes analizar`.
- `arnes auditar <estudio>`: 3 evaluaciones expertas independientes (UX writing en comprensión, Nielsen en recorrido).
  Usa el consenso como primera pasada de la Fase 1 o de la evaluación heurística.
- Recorrido: pide a la persona usuaria que comparta el link sin restricciones y lo pruebe en incógnito; luego verifica que abre (pre-flight). `arnes recorrido <estudio> <integrante|todos>`; empieza
  con un integrante y una tarea, mira las capturas de `datos/capturas/`, y recién después corre el panel.
  `arnes analizar`.
- Persona: sigue `metodos/persona/METODO.md`; al final `arnes persona validar` y `arnes persona probar`.

Si una sesión falla, el mismo comando la retoma (las hechas no se repiten).

## 5. Narrativa

Lee `datos/agregado.json`, `datos/respuestas.csv` o `datos/pasos.csv`, y una muestra de sesiones completas. En
recorrido mira las capturas de los momentos candidatos. Escribe `narrativa.yaml`:

- Titular = conclusión. KPIs con `verificar` para que el arnés recuente la cifra.
- Cada hallazgo: hallazgo (con cifra y base) → interpretación → recomendación, evidencia (archivo o sesión),
  severidad 0–4, confianza, etiquetas. En recorrido: `categoria` A o C y `sesiones` afectadas; lo de categoría B
  va en `estado_prototipado`.
- Positivos, límites, qué validar con personas, próximos pasos, fuentes.
- Lee el bloque de firmeza de `arnes analizar`: no presentes como diferencia una comparación «no concluyente» (usa
  `compara` en el KPI para que el verificador lo controle). En recorrido, `walkthrough: 1–4` en cada fricción.
- `aprendizajes_metodo`: qué enseñó este estudio sobre el método. Es lo que viaja al vault.

## 6. Reporte y control final

```bash
arnes reporte <estudio>
arnes verificar <estudio>     # debe terminar en LISTO PARA ENTREGAR
```

Abre el HTML en el navegador (sírvelo por HTTP local: el CLI de Playwright no abre `file://`) y míralo completo
antes de entregar: radar con las cinco etiquetas legibles, visor o embudo, sin errores de consola.

## 7. Archivar en el vault

`arnes sintesis <estudio> --simular`, revisa la lista de cambios, y después `arnes sintesis <estudio>`. No archives
estudios de prueba.

## 8. Entregar

Respuesta breve en el chat: qué se corrió, dónde quedó el reporte, cuántas sesiones, 3–5 hallazgos principales,
limitaciones técnicas. Si el reporte es para otras personas, publícalo como Artifact privado y da el link.
