# User Persona GIC — outputs reutilizables

Investigación completa sobre el estudio `actualizacion-user-persona-gic_responses.csv`
(**73 respuestas**, 64 completas, 41 columnas, 23 preguntas · Región Pachuca y zonas colindantes).

Reporte visual publicado: https://claude.ai/code/artifact/7478022f-f0c8-4535-b28f-f38202af2b18

---

## Qué hay aquí

| Archivo | Qué es | Para qué sirve |
|---|---|---|
| `01-diccionario-variables.csv` | Las 41 columnas con tipo, clase, N válido, missing y uso en el modelo | Saber qué variable se puede usar y cuál está excluida, y por qué |
| `02-frecuencias.csv` | Todas las distribuciones con frecuencia absoluta, %, N válido y missing | Citar cifras sin recalcular; alimentar dashboards |
| `03-codificacion-cualitativa.csv` | 32 temas codificados de Q15, Q17 y Q21 con N, %, sentimiento y paráfrasis | Priorizar backlog; sustentar hallazgos cualitativos |
| `04-matriz-relaciones.csv` | 13 relaciones entre variables con fuerza, N e interpretación | Ver qué predice qué y qué relaciones son débiles |
| `05-segmentos.csv` | Comparativa de los 4 segmentos por 11 dimensiones | Tabla base para presentaciones |
| `06-usuarios-sinteticos.json` | Los 4 perfiles completos + las 48 reglas, en JSON | **Alimentar simulaciones, agentes o herramientas propias** |
| `07-reglas-conductuales.csv` | Las 48 reglas SI / Y / ENTONCES / PORQUE / probabilidad | Importar a Notion, Sheets o un motor de reglas |
| `08-analisis.py` | Script que reproduce todo el análisis desde el CSV original | Rehacer el análisis si llega un export corregido |
| `09-reporte-completo.html` | El reporte visual completo, offline | Compartir sin depender del link |
| `10-guia-editorial.md` | Voz, tono y etiquetas de evidencia | Escribir el próximo reporte con el mismo criterio |
| `11-diccionario-editorial.md` | ACTUAL → RECOMENDADO → RAZÓN | Evitar jerga y afirmaciones sin respaldo |
| `system-prompts/*.md` | Un prompt listo por usuario sintético | **Pegar en un LLM para entrevistar al perfil** |

---

## Cómo usar los usuarios sintéticos

1. Abrí `system-prompts/A-ruben.md` (o el perfil que necesites) y pegalo como *system prompt*.
2. Entrevistalo, mostrale un concepto, o corré un escenario de campo.
3. **Si responde «Los datos disponibles no permiten determinar con suficiente confianza cómo reaccionaría este perfil», eso es correcto**: significa que el estudio no cubre ese tema. Es una señal de que ahí hace falta investigación real.

Los cuatro perfiles responden distinto ante el mismo escenario. Probalos en paralelo antes de decidir: si una propuesta solo le sirve a uno, ya sabés a quién estás dejando fuera.

### Los cuatro perfiles

| | Nombre | Arquetipo | n | Utilidad de Torre |
|---|---|---|---:|---:|
| **A** | Rubén Ortega | Veterano que necesita contexto | 13 | 2.15 |
| **B** | Diego Salgado | Gestor orientado a velocidad | 13 | 2.00 |
| **C** | Emilio Rentería | Gestor en formación | 18 | 3.67 |
| **D** | Fernando Aguilar | Verificador cuidadoso | 19 | 3.26 |

---

## Límites que hay que respetar

- **N = 73, no 84.** El brief mencionaba 84; el archivo tiene 73. Si aparece un export completo, corré `08-analisis.py` sobre él.
- **Q8, Q9 y Q10 están suspendidas.** Los tres encabezados son idénticos y el enunciado no viaja en el export. No se interpretaron.
- **Género no es modelable:** 71 hombres y 2 mujeres. Estos perfiles no representan la experiencia de una GIC mujer.
- **Edad y antigüedad están confundidas:** 16 de 18 novatos tienen 18–30 años.
- **La región es contextual, no predictiva:** las celdas quedan entre n=4 y n=20.
- **Nada de esto es causalidad.** Las relaciones de `04` son asociaciones observadas.

**Regla de fidelidad:** fidelidad a los datos > consistencia conductual > completitud narrativa.
