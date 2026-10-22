# User Persona OU-PWA — outputs reutilizables

Reconstrucción completa del User Persona de la Originación Única a partir de sus fuentes
originales, siguiendo el mismo pipeline usado en `GIC-User Person`.

**Base:** 685,243 clientes reales (UIX by UPAX, mayo 2025, semanas 1 a 20) · 2 arquetipos
cualitativos · 19 hallazgos verificados contra la aplicación web real en ambiente dev.

Reporte visual: `09-reporte.html` (abrilo en el navegador, funciona offline).

---

## La diferencia con el proyecto GIC

En el GIC había un CSV con 73 respuestas. **Acá no había dataset.** Los datos estaban dentro de
las imágenes de un PPTX y de dos PDF con fuentes subset. El paso 0 del pipeline fue construirlo:

- Se extrajeron las tablas de la lámina 16 del XML del PPTX.
- Se extrajeron y leyeron como imagen las láminas 5 a 10 (gráficos que no son texto).
- Se decodificó el texto de los dos PDF de arquetipo usando sus CMaps `/ToUnicode`.

El resultado está en `00-fuente/`. Todo lo demás se deriva de ahí.

---

## Qué hay aquí

| Archivo | Qué es | Para qué sirve |
|---|---|---|
| `00-fuente/*.csv` | El dataset que no existía: 6 archivos con las tablas transcritas de las láminas, los dos arquetipos y los 23 hallazgos del reporte dev | **La única fuente de verdad.** Si llega un export corregido, se actualiza acá |
| `01-diccionario-variables.csv` | Las 24 variables con fuente, clase, N, granularidad y uso en el modelo | Saber qué se puede usar, qué está suspendido y por qué |
| `02-frecuencias.csv` | Todas las distribuciones con frecuencia, % y base — o declaración explícita de base ausente | Citar cifras sin recalcular |
| `03-codificacion-cualitativa.csv` | 32 temas codificados con las fuentes que los atestiguan, sentimiento y cita representativa | Priorizar backlog; sustentar hallazgos cualitativos |
| `04-matriz-relaciones.csv` | 15 relaciones con fuerza, n, interpretación y nivel de evidencia | Ver qué predice qué, y qué cruce es interpretación y no dato |
| `05-segmentos.csv` | Los 4 segmentos generacionales comparados en 27 dimensiones | Tabla base para presentaciones |
| `06-usuarios-sinteticos.json` | Los 4 perfiles completos + metadatos + límites, en JSON | **Alimentar simulaciones, agentes o herramientas propias** |
| `07-reglas-conductuales.csv` | Las 48 reglas SI / Y / ENTONCES / PORQUE / probabilidad, con su capa de evidencia | Importar a Notion, Sheets o un motor de reglas |
| `08-analisis.py` | Script que reproduce auditoría, frecuencias, mezcla ponderada y cruces desde `00-fuente/` | Rehacer el análisis si llegan datos corregidos |
| `09-reporte.html` | El reporte visual completo, offline | Compartir sin depender de un link |
| `10-guia-editorial.md` | Voz, tres niveles de lenguaje y etiquetas de evidencia | Escribir el próximo reporte con el mismo criterio |
| `11-diccionario-editorial.md` | ACTUAL → RECOMENDADO → RAZÓN, sobre frases reales del proyecto | Corregir el documento vigente frase por frase |
| `12-auditoria-user-person-pwa.md` | Contraste de cada cifra de `User-person-PWA.md` v2.0 contra su fuente | **Leelo antes de reusar el documento vigente** |
| `system-prompts/*.md` | Un prompt listo por usuario sintético | **Pegar en un LLM para entrevistar al perfil** |

---

## Cómo usar los usuarios sintéticos

1. Abrí `system-prompts/A-bryan.md` (o el perfil que necesites) y pegalo como *system prompt*.
2. Entrevistalo, mostrale un concepto, o corré un escenario del flujo de originación.
3. **Si responde «Los datos disponibles no permiten determinar con suficiente confianza cómo
   reaccionaría este perfil», eso es correcto**: significa que el estudio no cubre ese tema. Es
   una señal de que ahí hace falta investigación real.

Los cuatro responden distinto ante la misma pantalla. Probalos en paralelo antes de decidir: si
una propuesta solo le sirve a uno, ya sabés a quién estás dejando fuera.

### Los cuatro perfiles

| | Nombre | Generación | Arquetipo | n | % base | Pérdida |
|---|---|---|---|---:|---:|---:|
| **A** | Bryan Nájera | Centennials (Z) | El que ya está adentro y nadie diseñó para él | 301,000 | 43.9% | ~14.6 |
| **B** | Itzel Camacho | Millennials (Y) | La que decide por la cuota y paga el precio | 229,000 | 33.4% | ~13.8 |
| **C** | Rosalba Quintero | Gen X | La que mejor paga y peor ve la letra | 119,000 | 17.3% | ~11.6 |
| **D** | Arturo Belmont | Boomers | El que menos pierde y a quien nadie le habló | 37,000 | 5.4% | 11.4 |

### El quinto archivo no es un perfil

`system-prompts/E-objetivo-de-negocio.md` documenta el «Cliente Ideal» declarado en la lámina 12.
**No lleva reglas conductuales y no debe usarse como usuario sintético.** Existe para que el
objetivo comercial esté escrito con su etiqueta correcta. Ver el hallazgo A1 de la auditoría.

---

## Las dos capas de evidencia

Este proyecto tiene dos poblaciones y no son intercambiables. Cada regla conductual declara de
cuál sale:

- **Capa 1** — 685,243 clientes reales. Responde *quién es y qué pide*.
- **Capa 2** — 19 hallazgos verificados contra la aplicación real. Responde *dónde se rompe*.
- **Capa 1+2** — cruce interpretativo. **Nunca es observación directa.**

---

## Límites que hay que respetar

- **El «Cliente Ideal» es un objetivo de negocio, no una población.** Declara 60% mujeres;
  ninguna generación observada pasa de 48%. La base completa es 46.8% mujeres.
- **El usuario modal es Centennial:** 19 años en hombres, 22 en mujeres. El arquetipo vigente
  describe a alguien de 30 a 55.
- **Estado civil está SUSPENDIDO.** Las dos tablas del mismo mazo no reconcilian: Divorciado es
  7% del registro y 21.8% de la colocación.
- **La pérdida por generación es una aproximación.** Los rangos de la lámina 16 no coinciden con
  los cortes generacionales de la lámina 7. Solo Boomers cae limpio en un bucket.
- **No hay cruce edad × género para pérdida.** Combinar ambas ventajas es inferencia, no dato.
- **Ausente en todas las fuentes:** monto promedio solicitado, motivo real de abandono, ingreso
  del cliente, perfiles de accesibilidad y alfabetización digital baja, marcas y apps de Boomers.
- **5 de 8 no es una tasa de completitud observada:** es simulación conductual. Ningún número de
  estos artefactos se apoya en ella.
- **Nada de esto es causalidad.** Las relaciones de `04` son asociaciones observadas.

**Regla de fidelidad:** fidelidad a los datos > consistencia conductual > completitud narrativa.

---

## Reproducir el análisis

```bash
cd outputs
python3 08-analisis.py            # lee ./00-fuente
python3 08-analisis.py otra/ruta  # o apuntá a otro dataset
```

Sin dependencias externas. Imprime auditoría de consistencia entre láminas, frecuencias con base,
mezcla de producto ponderada por n de género, los cruces que sostienen los perfiles y la
asignación de segmentos.
