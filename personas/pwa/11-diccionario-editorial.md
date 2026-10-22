# Diccionario editorial — ACTUAL → RECOMENDADO → RAZÓN

Corrige frases reales tomadas de `User-person-PWA.md` v2.0 y del reporte dev. No es una lista de estilo abstracta: cada entrada arregla algo que ya está escrito en el proyecto.

---

## 1. Objetivo presentado como hallazgo

| | |
|---|---|
| **ACTUAL** | «**Validación empírica:** Cliente ideal: Millennials (30-44) + Gen X (45-55), 60% mujeres» |
| **RECOMENDADO** | «**Objetivo de negocio declarado (lámina 12):** Millennials + Gen X, 30–55 años, 60% mujeres. La proporción femenina observada no supera el 48% en ninguna generación.» |
| **RAZÓN** | La palabra «validación» convierte una intención comercial en un hallazgo. Es el error de fondo del documento. |

## 2. Rango de edad renombrado para que calce

| | |
|---|---|
| **ACTUAL** | «Edad 45-60 = 15.9%» |
| **RECOMENDADO** | «Edad >50 = 15.9% de la colocación» |
| **RAZÓN** | La lámina 16 no tiene un bucket 45–60. Renombrar el rango para hacerlo coincidir con Gen X fabrica una precisión que el dato no tiene. |

## 3. Columna equivocada de la tabla

| | |
|---|---|
| **ACTUAL** | «Gen X: 15.9% pérdida observable» |
| **RECOMENDADO** | «Los mayores de 50 concentran el 15.9% de la colocación y registran la pérdida más baja del estudio: 11.4.» |
| **RAZÓN** | 15.9% es colocación, no pérdida. Y al usarlo como pérdida, la comparación que sigue queda invertida. |

## 4. Cifra sin fuente

| | |
|---|---|
| **ACTUAL** | «47% de Centennials siente desconfianza a instituciones tradicionales» |
| **RECOMENDADO** | «La desconfianza institucional está declarada en el arquetipo María PA, sin cifra asociada. El estudio no mide desconfianza.» |
| **RAZÓN** | El único 47% del estudio es el de clientes solteros. El hallazgo cualitativo es real; el número es fabricado. |

## 5. Generación equivocada

| | |
|---|---|
| **ACTUAL** | «98.9% Millennials tiene smartphone; 72.6% usa streaming» |
| **RECOMENDADO** | «98.9% de los Centennials con móvil tiene smartphone (anexo 2). Entre Millennials, 83.1% usa streaming (anexo 3); entre Gen X, 72.6% (anexo 4).» |
| **RAZÓN** | Las tres cifras existen, las tres están asignadas a la generación equivocada. |

## 6. Etiqueta generacional sobre un corte de edad

| | |
|---|---|
| **ACTUAL** | «Pérdida esperada en Gen X: 11.4% \| Millennials: 12.3% \| Centennials: 14.3-15.1%» |
| **RECOMENDADO** | «La pérdida observada es plana hasta los 40 (14.3 a 15.1) y cae después: 12.3 entre 40 y 50, y 11.4 por encima de 50. El corte está en la edad, no en la generación.» |
| **RAZÓN** | Los buckets de la lámina 16 cruzan las fronteras generacionales. Traducirlos a generaciones inventa un límite que el dato no tiene. |

## 7. Coherencia declarada que no se verificó

| | |
|---|---|
| **ACTUAL** | «✅ Sin contradicciones entre fuentes» |
| **RECOMENDADO** | «Cuatro contradicciones abiertas: cortes de edad inconsistentes entre láminas 7 y 9/10; 'pérdida observada' contra 'pérdida esperada' sin definición; estado civil irreconciliable entre láminas 6 y 16; María PO declarada 'funcionaria pública' en el título y 'sector privado' en el cuerpo.» |
| **RAZÓN** | Declarar coherencia sin haberla probado es la afirmación más cara de un documento de investigación. |

## 8. Universo del test inflado

| | |
|---|---|
| **ACTUAL** | «3 experiencias UI/UX testadas; 50% Millennials prefirió B» |
| **RECOMENDADO** | «12 propuestas de diseño evaluadas, 3 finalistas. Solo la Experiencia B reporta cifra: 50% de Millennials y 25% de Centennials. La preferencia por A y por C es atribución cualitativa sin número.» |
| **RAZÓN** | Tratar tres preferencias con respaldo distinto como si fueran equivalentes. |

## 9. Producto desaparecido

| | |
|---|---|
| **ACTUAL** | «Efectivo (54%), Movilidad (24%), Productos del hogar (13%)» |
| **RECOMENDADO** | «Efectivo 54%, Movilidad 24%, Hogar 13%, **Telefonía 9% (62 mil clientes)**, Préstamo para autos 0.18%.» |
| **RAZÓN** | Telefonía no aparece en ninguna parte del documento y es el producto más inclinado hacia la generación mayoritaria de la base. |

## 10. Conducta inventada junto a una etiqueta de validación

| | |
|---|---|
| **ACTUAL** | «**Respuesta habitual:** Cierra la app. Busca alternativa (Mercado Libre, Nu, Ualá). Pregunta en WhatsApp a amiga.» |
| **RECOMENDADO** | «**Respuesta esperada [HIPÓTESIS]:** abandona y busca alternativa. Ninguna fuente mide el comportamiento de abandono: no hay analítica de embudo en el estudio.» |
| **RAZÓN** | El documento intercala conducta inventada con bloques marcados «[Validado]». El lector no puede distinguirlas. |

## 11. Premisa heredada sin verificar

| | |
|---|---|
| **ACTUAL** (reporte dev, §4) | «Mujer de 30 a 55 años (Millennials y Gen X son el cliente ideal; 60% mujeres)» |
| **RECOMENDADO** | «El modelo de usuario se toma de `User-person-PWA.md` v2.0. Advertencia: su premisa demográfica es un objetivo de negocio, no una población observada. Ver `12-auditoria-user-person-pwa.md`.» |
| **RAZÓN** | Un artefacto que hereda una premisa sin verificarla propaga el error y le agrega autoridad. |

## 12. Dos poblaciones en una sola frase

| | |
|---|---|
| **ACTUAL** | «El 50% de Millennials prefiere el simulador y 5 de 8 usuarios completan el flujo» |
| **RECOMENDADO** | «El 50% de Millennials eligió la Experiencia B [capa 1, n no reportado]. En la simulación conductual, 5 de 8 perfiles completaron el flujo [capa 2, simulación — no son usuarios reales].» |
| **RAZÓN** | Dos poblaciones distintas, dos unidades distintas y una de ellas no es observación. Juntarlas en una frase las vuelve indistinguibles. |

---

## Tabla rápida

| ACTUAL | RECOMENDADO |
|---|---|
| validación empírica (sobre un objetivo) | objetivo de negocio declarado |
| cliente ideal | cliente ideal **declarado** |
| pérdida esperada | pérdida observada (y anotar que el mazo no la define) |
| 3 experiencias testadas | 12 propuestas, 3 finalistas |
| Gen X 11.4% | mayores de 50: 11.4% |
| datos empíricos | dato observado (lámina N) |
| respuesta habitual | respuesta esperada [HIPÓTESIS] |
| usuarios completaron | perfiles sintéticos completaron [SIMULACIÓN] |
| el estudio demuestra | el estudio reporta |
| basado en 685K clientes reales | transcrito de un estudio sobre 685,243 clientes (mayo 2025) |
