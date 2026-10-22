---
titulo: "Protocolo · {{naming}}"
fecha: ""
autor: "Alexis Valdez + Claude"
tipo: "Recorrido de flujo con usuarios sintéticos"
estado: "Diseño — pendiente de aprobación antes de correr"
---

# Protocolo · {{naming}}

## Brief (template de protocolo de UiX)

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | `{{naming}}` (guía de naming de UiX; la fecha final se fija al generar el reporte) |
| **Cliente** | {{cliente}} |
| **Fecha de elaboración** | {{fecha_dmy}} |
| **Versión** | v1 |
| **Brief** | Qué recorreremos, qué queremos saber y para qué, en 2–3 líneas. |
| **Autorización** | Nombre y apellido de quien aprueba |

- **Descripción del proyecto:** qué se estudia y con qué alcance.
- **Objetivo:** una frase: qué se documenta, compara o valida, y para qué.
- **Muestra esperada:** {{muestra}}
- **Incentivos:** No aplica (participantes sintéticos).
- **Alcance de la investigación:** Superficial · Descriptiva · Profunda · Predictiva.
- **Público objetivo:** a quién va dirigido el producto o el flujo.
- **Equipo:** área o personas que participan.
- **Fuentes:** flujo del producto, prototipo, research previo, User Persona usado.
- **Metodología:** {{metodologia}}, con usuarios sintéticos.
- **Decisión de investigar** (impacto × incertidumbre): impacto ___ · incertidumbre ___ → ___.

**Referencias del vault** (`arnes conocimiento recorrido`): [[…]] — qué decisión del protocolo sostiene cada una.

## 0. Pre-flight

| Recurso | Acceso | Estado | Observación |
|---|---|---|---|
| URL del material | | | |
| Dispositivo | | | |
| Versión fijada (fecha, hora, node-id de inicio) | | | |
| Biblioteca y panel | | | |
| Datos de prueba | | | |

## 1. Objetivo y preguntas de investigación

**Objetivo:** …

**Pregunta principal:** …

1. …

## 2. Hipótesis

| # | Hipótesis | Se sostiene si | Se cae si |
|---|---|---|---|

## 3. Panel

Biblioteca `…`, panel `…` (`arnes panel <estudio>`). Matriz de diversidad y vacíos: pegar la salida.

## 4. Tareas

| ID | Escenario | Instrucción exacta | Objetivo | Criterio de éxito (fin) | Señales de fracaso |
|---|---|---|---|---|---|

No se alteran las tareas originales salvo imposibilidad técnica, y entonces se marca **[SUPUESTO METODOLÓGICO]**.

## 5. Qué se observa en cada paso

Pantalla observada · primera impresión · qué mira primero · interpretación · intención · acción y razón ·
pensamiento en voz alta · resultado · confianza (0–100) · fricción (0–5).

Resultado por tarea: éxito · éxito con fricción · cree que terminó · abandono · atascado · sin terminar.

## 6. Métricas

- Tasa de completitud por tarea (sesiones, no personas).
- Toques sin respuesta y fuera de zonas activas.
- Caídas de confianza y fricción máxima por pantalla.
- Incidentes: frecuencia, severidad 0–4, categoría A/C, prioridad F × S × I.

## 7. Límites

- Perfiles sintéticos: hipótesis a validar con personas.
- El perfil ve las zonas activas numeradas [SUPUESTO METODOLÓGICO].
- La duración de la sesión no mide tiempo de tarea.

## 8. Oportunidades, tiempos y entregables

**Oportunidades.** Cada hallazgo se clasifica como Mantener · Mejorar · Incorporar · Hacer diferente
(`oportunidad` en `narrativa.yaml`).

| Actividad | Días |
|---|---|
| Documentación | |
| Creación de materiales | |
| Levantamiento (sesiones sintéticas) | |
| Análisis | |
| Reporte | |

- **Fecha de inicio:** dd de mes de aaaa · **Fecha de entrega final:** dd de mes de aaaa
- **Entregables:** Reporte · Flash report · Infografía · Matriz comparativa · Insights y oportunidades priorizadas.

## 9. Aprobación

- [ ] `arnes revisar` sin errores y avisos leídos
- [ ] Baseline (`baseline_url`) o razón declarada; `primer_toque` por tarea
- [ ] Piloto: un perfil, una tarea, capturas revisadas
- [ ] 2 corridas por perfil planeadas
- [ ] Pre-flight completo, sin bloqueos
- [ ] Tareas con criterio de fin verificable por el arnés
- [ ] Panel revisado
- [ ] Brief completo, con autorización y decisión de investigar
- [ ] Consumo estimado aceptado (`arnes recorrido <estudio> todos --simular`, en tokens)
