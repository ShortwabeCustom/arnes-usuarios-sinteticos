# Research en tus proyectos

*Cómo investigar sin morir en el intento · UiX*

No podemos medir nuestras experiencias sin evaluarlas con usuarios. Pero **hacer research estratégico no es investigar siempre**: se investiga cuando aporta más de lo que cuesta.

## 1. Cuándo investigar

### Decisión rápida

| No investigar cuando... | Sí investigar cuando... |
|---|---|
| Es una mejora cosmética sin impacto en el usuario | Se afecta un comportamiento crítico (checkout, registro, pago) |
| Es mantenimiento técnico | Cambia la arquitectura o el flujo |
| Ya hay evidencia sólida y reciente | Hay desacuerdo entre stakeholders |
| El riesgo es bajo | El impacto en negocio es alto |

También vale la pena investigar si hay suposiciones sin comprobar, riesgo alto de abandono, impacto en conversión o cambios en el comportamiento del usuario.

### Matriz de decisión

|  | **Incertidumbre alta** | **Incertidumbre baja** |
|---|---|---|
| **Impacto en negocio alto** | Sí investigar | Validar rápido |
| **Impacto en negocio bajo** | Explorar | No investigar |

### Qué método usar según la fase

| Fase | Para qué | Métodos |
|---|---|---|
| Empatizar | Descubrir cómo los usuarios perciben o usan un flujo, pantalla o componente | Entrevistas, AEIOU, desk research, benchmark, Mystery Shopper |
| Definición | Definir la propuesta según usabilidad y reglas de negocio | Tree testing, Focus Group, Card Sorting |
| Diseño (prototipar) | Diseñar a partir de lo descubierto y definido | Pruebas rápidas, concept testing, 5 seg testing |
| Testear (pre-release) | Validar antes de la entrega formal del diseño | Pruebas de usabilidad, SUS, Churn |
| Medir (post-release) | Medir después de la entrega formal | Métricas, mapas de calor, A/B Testing |

Los templates de estas herramientas están en el repositorio del equipo.

## 2. Cómo incluir el research en el flujo de trabajo

Usamos una metodología basada en **Double Diamond + ciclos ágiles**, en cuatro etapas:

| Etapa | Objetivo | Actividades |
|---|---|---|
| **1. Descubrir** | Entender el problema | Priorizar investigaciones, definir objetivo, identificar hipótesis |
| **2. Definir** | Estructurar el research | Elegir metodología, diseñar protocolo, reclutar participantes |
| **3. Explorar** | Realizar la investigación | Ejecutar pruebas, analizar resultados, identificar patrones |
| **4. Entregar** | Documentar hallazgos | Sintetizar insights, presentar resultados, definir siguientes pasos |

**Ciclo de una semana:** lunes Descubrir · martes Definir · miércoles y jueves Explorar · viernes Entregar.

## 3. Cómo investigar de forma eficiente

### Tamaño de muestra recomendado

| Metodología | Usuarios | Por qué |
|---|---|---|
| Encuestas | 5-10 | Un patrón de 5 usuarios da el panorama |
| Entrevistas a profundidad | 5-10 | Los patrones aparecen desde 5 usuarios |
| Focus Group | 6+ | Los patrones de comportamiento aparecen desde 6 |
| AEIOU | 6-10 | Las 5 dimensiones se identifican desde 6 |
| A/B testing | 8-20 | La comparación es equiparable desde 8 |
| Usability testing | 8-10 | Los patrones de experiencia aparecen desde 8 |
| SUS testing | 20-40 | La evaluación es confiable desde 20 |
| Tree testing | 30-60 | Con menos de 30 los datos son solo orientativos; para tasas de éxito confiables se recomiendan unos 50 por grupo de usuarios |
| Card sorting | 20-40 | Los patrones de jerarquía aparecen desde 20 |

### Buenas prácticas

- **Protocolo en toda investigación.** Define objetivos, métricas y mejoras esperadas en la experiencia.
- **Usa IA sin limitaciones.** Un trabajo de 3 días se puede hacer en 1.
- **Los hallazgos mandan.** Los resultados deben guiar las decisiones en los flujos que diseñamos.

## Kit de todo UX Researcher

- Template de protocolo (datos del proyecto, metodología, fechas de implementación y entrega, equipo y stakeholders)
- Prompts de IA para bajar hallazgos
- Guías para trabajar IA en FigJam
- Guías para armar un Maze efectivo
- Checklist de calidad
