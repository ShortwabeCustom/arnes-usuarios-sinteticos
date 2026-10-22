# Auditoría de `User-person-PWA.md` v2.0 contra sus propias fuentes

**Fecha:** 18 de septiembre de 2026
**Documento auditado:** `User-person-PWA.md`, versión 2.0, 967 líneas
**Fuentes contrastadas:** `buyer-persona-9junio.pptx` (30 láminas, texto y tablas extraídos), `User persona.pdf` (María PA), `User persona-1.pdf` (María PO)
**Método:** cada cifra del documento se buscó en la lámina o el PDF que la sostiene. Las láminas de sólo imagen se leyeron como imagen.

---

## Resumen

El documento v2.0 declara en su encabezado «Basada en investigación de 685K clientes reales» y abre con una sección titulada **«Validación empírica»**. Trece de sus afirmaciones cuantitativas no resisten el contraste con la fuente que citan.

Tres son de fondo y cambian a quién está describiendo el documento:

1. **La premisa central del arquetipo es un objetivo comercial presentado como hallazgo.**
2. **El usuario modal real —Centennial de 19 a 22 años— quedó fuera del arquetipo.**
3. **Una cifra usada nueve veces en el documento no existe en ninguna fuente.**

Seis son errores de lectura de tabla. Cuatro son omisiones. Ninguna es un problema de redacción.

El error se propagó: el reporte `dev-onboarding/reporte-investigacion-sintetica-dev-onboarding.md` abre su sección 4 con «Mujer de 30 a 55 años (Millennials y Gen X son el cliente ideal; 60% mujeres)», heredando la premisa sin verificarla.

---

## Hallazgos de fondo

### A1 — «60% mujeres» es un objetivo de negocio, no una población observada

**Qué dice el documento.** Línea 8: «Millennials + Gen X, 30-55 años, **60% mujeres**». Línea 18, bajo el título «Validación empírica»: «Cliente ideal: Millennials (30-44) + Gen X (45-55) **[Estrellas doradas en investigación]**».

**Qué dice la fuente.** La lámina 12 tiene tres columnas: *Antes de la OU* (Gen X), *Ahora en la OU* (Centennials) y *Cliente Ideal*. Las dos primeras describen poblaciones observadas. La tercera declara un objetivo: 40% hombres / 60% mujeres.

**La proporción observada, lámina 7:**

| Generación | Hombres | Mujeres |
|---|---:|---:|
| Centennials (Z) | 54% | 46% |
| Millennials (Y) | 52% | **48% ← el máximo** |
| Gen X | 54% | 46% |
| Boomers | 57% | 43% |
| **Base completa** | **53.2%** | **46.8%** |

Ninguna generación llega a 60% de mujeres. El documento tomó la columna de objetivo y la puso bajo el título «Validación empírica».

**Consecuencia.** Todo el arquetipo «María» se construye sobre un rasgo que la base no tiene.

---

### A2 — El usuario modal real quedó fuera del arquetipo

**Qué dice la fuente.** La lámina 7 reporta la edad que más se repite en toda la base: **19 años en hombres (4.4%) y 22 años en mujeres (4.1%)**, con la nota explícita «ambos pertenecen a la generación Centennial (Z)». Los Centennials son **301 mil clientes, el 43.9% de la base** — el segmento más grande por amplio margen.

**Qué hace el documento.** Define el arquetipo como 30–55 años y clasifica a los Centennials como «el público actual pero con MAYOR pérdida esperada» (línea 20). La versión 1.0 del documento describía a una empleada de 24–34 años; la v2.0 la movió a 30–55 y en esa mudanza dejó fuera a María PA (24 años), el único arquetipo cualitativo que coincidía con el usuario modal.

**Consecuencia.** El documento describe a quien la empresa quiere tener, no a quien tiene. Para diseñar el producto que esos 301 mil clientes están usando hoy, el arquetipo no sirve.

---

### A3 — «47% de Centennials siente desconfianza» no existe en ninguna fuente

**Qué dice el documento.** La cifra aparece tres veces, y una de ellas es un Pain Point entero: línea 33 «desconfianza en instituciones (especialmente Centennials: 47% siente desconfianza)»; línea 87 «Centennials: 47% siente desconfianza a instituciones»; línea 178, encabezando el Pain Point 3: «47% de Centennials siente desconfianza a instituciones tradicionales».

**Qué dice la fuente.** El mazo no mide desconfianza. No hay ninguna pregunta, escala ni gráfico sobre el tema. Los dos únicos 47% del estudio son:

- Lámina 6: **«47% de nuestros clientes se registraron como solteros»** (322,838 de 685,243).
- Lámina 12: Centennials, **47% mujeres** / 53% hombres.

**Qué sí sostiene la idea.** La desconfianza institucional está atestiguada, pero de forma cualitativa y sin porcentaje: el arquetipo María PA declara «siente desconfianza hacia instituciones tradicionales» y María PO declara «miedo a los robos y estafas digitales». Es un hallazgo real al que se le adosó un número que no le corresponde.

**Consecuencia.** Un Pain Point entero del documento se sostiene sobre una cifra fabricada.

---

## Errores de lectura de tabla

| # | Qué afirma el documento | Qué dice la fuente | Gravedad |
|---|---|---|---|
| **B1** | «Pérdida esperada en Gen X: 11.4% \| Millennials: 12.3% \| Centennials: 14.3-15.1%» (línea 21) | La lámina 16 reporta pérdida por **rango de edad**, no por generación: ≤21 = 14.3 · (21,25] = 14.4 · (25,30] = 15.1 · (30,40] = 14.5 · (40,50] = 12.3 · >50 = 11.4. El 12.3 es el bucket (40,50], que cruza la frontera Millennial/Gen X. La lectura correcta: **plana hasta los 40 y luego cae**. El corte real está en los 40, no en la etiqueta generacional | Alta |
| **B2** | «Gen X: **15.9% pérdida observable** (aún así, más baja que Centennials 15.1%)» (línea 114) | 15.9% es el **% de colocación** de >50 años, no una pérdida. El documento leyó la columna equivocada de la lámina 16, y además la comparación queda invertida: 15.9 no es más bajo que 15.1 | Alta |
| **B3** | «Edad 45-60 = 15.9%» (línea 109) | La lámina 16 no tiene un bucket 45–60. Tiene **>50**. El rango se renombró para hacerlo coincidir con Gen X. La línea 814 del mismo documento lo escribe bien («Edad >50 = 15.9%»), así que el documento se contradice a sí mismo | Media |
| **B4** | «98.9% Millennials tiene smartphone; 72.6% usa streaming» (línea 126) | El 98.9% de smartphone es de **Centennials** (anexo 2). El 72.6% de streaming es de **Gen X** (anexo 4). El de Millennials es **83.1%** (anexo 3) — cifra que el propio documento usa correctamente en la línea 44, contradiciéndose a sí mismo | Media |
| **B5** | «Millennials que son transicionales: 20% acceso a tarjetas» (línea 90) | El 20% de tarjeta departamental y el 2% de crédito personal salen del arquetipo **María PA**, que describe a «jóvenes mujeres» de 24 años — Centennials, no Millennials | Media |
| **B6** | «Gen X: 60% acceso tradicional» (línea 90) | No hay fuente. Ninguna lámina ni PDF reporta esa cifra | Media |

---

## Omisiones

| # | Qué falta | Qué dice la fuente | Por qué importa |
|---|---|---|---|
| **C1** | **Telefonía** no aparece en ninguna parte del documento | Lámina 8: Telefonía es **9% de la demanda, 62 mil clientes** — el cuarto producto. Y es el producto que más se inclina hacia los Centennials: 10.9% de su mezcla contra 7.0–8.0% en el resto | El producto omitido es el que más apunta a la generación mayoritaria de la base |
| **C2** | Jalisco (38 mil) y Puebla (36 mil) | Lámina 5 publica el top 5, no el top 3 | El documento cita «CDMX 86K, Edo. Mex. 72K, Veracruz 55K» y corta ahí |
| **C3** | La tabla de colocación por estado civil de la lámina 16 | Divorciado es **7% del registro** (lámina 6) y **21.8% de la colocación** (lámina 16). Unión Libre es **23%** y **8.1%**. Las dos tablas del mismo mazo no reconcilian | El documento cita solo la primera y afirma en la línea 942: «✅ Sin contradicciones entre fuentes» |
| **C4** | Que el test de experiencia partió de **12 propuestas** | Lámina 13: «Hicimos un total de 12 propuestas de diseño». Lámina 14: «Obtuvimos 3 finalistas». Solo la Experiencia B trae cifra (50% Millennials, 25% Centennials); A y C tienen atribución cualitativa sin número | El documento dice «3 experiencias UI/UX testadas» y trata las tres preferencias como si tuvieran el mismo respaldo |

---

## Contradicciones internas de las fuentes que el documento no reporta

El documento afirma en la línea 942: «**✅ Sin contradicciones entre fuentes**». Hay cuatro:

1. **Cortes de edad inconsistentes dentro del mismo mazo.** Lámina 7: Centennials 18–30, Millennials 31–45, Gen X 46–60. Láminas 9 y 10: Centennials 18–29, Millennials 30–44, Gen X 45–60.
2. **«Pérdida Observada» contra «pérdida esperada».** La lámina 16 titula la columna «Pérdida Observada»; la lámina 12 remite a «análisis de pérdida esperada». El mazo no define ninguna de las dos.
3. **Estado civil irreconciliable** entre láminas 6 y 16 (ver C3).
4. **María PO se contradice a sí misma.** El encabezado del PDF dice «Funcionaria pública»; el cuerpo dice «empleada administrativa en el sector privado».

---

## Qué sí quedó bien en el documento v2.0

La auditoría no encontró problemas en:

- **Género total 49% / 51%** en colocación (lámina 16). Correcto.
- **Estado civil del registro:** 47% solteras, 23% unión libre, 22% casadas, 7% divorciadas, 1% viudas (lámina 6). Correcto.
- **Mezcla de producto principal:** Efectivo 54% / 369K, Movilidad 24% / 161K, Hogar 13% / 91K (lámina 8). Correcto.
- **Colocación por edad:** 30–40 = 25%, 40–50 = 17.6% (lámina 16). Correcto.
- **Experiencia B preferida en 50% por Millennials** (lámina 14). Correcto y es la única cifra dura del test.
- **La regla principal de diseño** —mostrar la cuota antes de pedir cualquier dato personal— es una síntesis legítima de las frustraciones declaradas en los dos arquetipos. El producto real la cumple (acierto F01 del reporte dev).
- **Los pain points cualitativos** (miedo al historial, desconfianza institucional, todo desde el celular, comparar antes de decidir) están correctamente atestiguados en María PA y María PO. El problema no son los temas: son los números que se les adosaron.

---

## Qué hacer con esto

1. **No publicar la v2.0 como está.** La sección «Validación empírica» describe un objetivo comercial, no una validación.
2. **Separar objetivo de observación.** El Cliente Ideal es una decisión legítima de negocio; está escrito con su etiqueta correcta en `system-prompts/E-objetivo-de-negocio.md`.
3. **Reemplazar la justificación del enfoque en la clienta mujer.** No hace falta el 60%: la mujer pierde menos en los cuatro productos sin una sola excepción (13.4 contra 14.1), y los mayores de 40 pierden menos que el resto (12.3 y 11.4 contra 14.3–15.1). Es mejor evidencia que la que el documento usa hoy.
4. **Pedir al equipo de datos el cruce edad × género para pérdida.** Es el dato que convertiría la inferencia «la clienta mujer mayor de 40 es la mejor» en un hallazgo.
5. **Pedir el catálogo y los denominadores de la lámina 16** para poder levantar la suspensión de estado civil.
6. **Reincorporar Telefonía** a cualquier modelo de producto.
7. **Decidir explícitamente qué se hace con los 301 mil Centennials.** Son el 43.9% de la base y hoy ningún artefacto de diseño los toma como destinatario.
