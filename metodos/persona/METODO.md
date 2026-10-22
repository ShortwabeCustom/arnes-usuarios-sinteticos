# Método 1 · Construir un User Persona con usuarios sintéticos

Convierte una fuente real (encuesta, mazo de investigación, arquetipos cualitativos, hallazgos de producto)
en una **biblioteca de usuarios sintéticos** que los métodos 2 y 3 pueden usar. Destilado de «GIC-User Person»
(73 respuestas de encuesta) y «PWA-User Person» (685,243 clientes, datos dentro de láminas y PDF).

**Regla de fidelidad:** fidelidad a los datos > consistencia conductual > completitud narrativa.

## El pipeline

| Paso | Entregable | Qué es |
|---|---|---|
| 0 | `00-fuente/*.csv` | El dataset. Si los datos están en imágenes de PPTX o PDF, este paso es construirlo: extraer tablas del XML, leer láminas como imagen, decodificar PDF con sus CMaps. **La única fuente de verdad.** |
| 1 | `01-diccionario-variables.csv` | Cada variable con fuente, clase, N válido, granularidad y uso en el modelo (eje, modelable, contextual, suspendida) y su razón |
| 2 | `02-frecuencias.csv` | Todas las distribuciones con frecuencia, % y base, o la declaración explícita de que la base falta |
| 3 | `03-codificacion-cualitativa.csv` | Temas codificados con fuentes, sentimiento y cita representativa |
| 4 | `04-matriz-relaciones.csv` | Relaciones con fuerza, n, interpretación y nivel de evidencia. Asociaciones, nunca causalidad |
| 5 | `05-segmentos.csv` | Segmentos comparados. El eje se elige por n suficiente en cada celda y gradientes claros, no por costumbre |
| 6 | `06-usuarios-sinteticos.json` | Perfiles completos + `meta.limites` + lo no modelado |
| 7 | `07-reglas-conductuales.csv` | `id, perfil, [capa,] si_y, entonces, porque, probabilidad`. Cada regla con su evidencia en PORQUE |
| 8 | `08-analisis.py` | Reproduce el análisis desde `00-fuente/`, sin dependencias externas |
| 9 | `09-reporte.html` | Reporte visual offline |
| 10 | `10-guia-editorial.md` | Voz, tres niveles de lenguaje, etiquetas de evidencia |
| 11 | `11-diccionario-editorial.md` | ACTUAL → RECOMENDADO → RAZÓN sobre frases reales del proyecto |
| 12 | `12-auditoria-*.md` | Si existía un User Persona previo: cada cifra contrastada con su fuente |
| — | `system-prompts/*.md` | Un prompt por perfil, listo para usar como system prompt |
| — | `biblioteca.yaml` | Manifiesto para el arnés: perfiles, paneles, no-perfiles, reglas de lectura |

## Lo que todo system prompt debe tener

`arnes persona validar` lo revisa:

- `## Reglas de interpretación de este rol` con la frase exacta de sin cobertura:
  «Los datos disponibles no permiten determinar con suficiente confianza cómo reaccionaría este perfil.»
- `No puedes opinar sobre: …; …; …` con los temas que ninguna fuente cubre.
- `## Perfil` con cada dato etiquetado: [OBSERVADO], [INFERIDO], [HIPÓTESIS], [AUSENTE], [APROXIMACIÓN].
- `## Objetivos`, `## Motivaciones`, `## Pain points`, `## Reglas conductuales`, `## Cómo hablas`
  (frases marcadas como sintéticas, no citas).

## Lo que aprendimos

- **El objetivo de negocio no es una población.** El «Cliente Ideal» de PWA declaraba 60% mujeres; ninguna
  generación observada pasa de 48%. Va en `no_perfiles` de `biblioteca.yaml`, nunca como usuario sintético.
- **Suspender en vez de forzar.** Si dos tablas de la misma fuente no reconcilian (estado civil en PWA) o los
  encabezados no viajan en el export (Q8–Q10 en GIC), la variable queda suspendida y se dice por qué.
- **Declarar lo que no es modelable.** Género en GIC (71 hombres, 2 mujeres) no se modela.
- **Dos capas no se mezclan.** En PWA: capa 1 (población) responde quién es; capa 2 (hallazgos en producto)
  responde dónde se rompe; una regla «1+2» es cruce interpretativo y se etiqueta así.
- **Una tasa simulada no es una tasa observada** (el «5 de 8» de PWA).

## Publicar la biblioteca

1. Copiar los entregables a `personas/<id>/` y escribir `biblioteca.yaml` (ver `personas/pwa/biblioteca.yaml`).
   Cada perfil declara `demograficos` con los cuatro datos que UiX pide desde mayo 2026 (edad por generación,
   género, región Norte · Centro-norte · Centro · Sur, ocupación), cada uno con su evidencia o `AUSENTE`
   (`fuentes-equipo/uix/Demográficos.md`). Son descriptivos, para comparar estudios: el eje de segmentación sigue
   siendo el comportamiento. En productos para usuarios específicos, la ocupación es el rol (en GIC: Gestor de
   Investigación de Campo).
2. `arnes persona validar <id>` → debe decir «Válido».
3. `arnes persona probar <id>` → batería de fidelidad: preguntas fuera de cobertura (deben usar la frase
   exacta), una dentro (no debe negarse) y una que sugiere la respuesta (revisar a mano si busca agradar).
   Resultado guardado en `personas/<id>/pruebas/`. Referencia PWA: 12 de 12 y 4 de 4.
4. Opcional: agregar paneles con capa OCEAN. Los valores son de diseño, no medidos: justificar cada uno con
   evidencia del segmento y marcar `ocean_supuesto: true` cuando no la hay.
