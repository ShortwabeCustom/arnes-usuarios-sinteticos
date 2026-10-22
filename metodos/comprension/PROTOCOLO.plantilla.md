---
titulo: "Protocolo · {{naming}}"
fecha: ""
autor: "Alexis Valdez + Claude"
tipo: "Comprensión de pantallas con usuarios sintéticos"
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

**Referencias del vault** (`arnes conocimiento comprension`): [[…]] — qué decisión del protocolo sostiene cada una.

Etiquetas de evidencia: **[EVIDENCIA]** medido en la pantalla o el prototipo · **[MODELO]** salida de un modelo
de atención, igual para todos los perfiles · **[SIMULACIÓN]** atribuido a un perfil sintético, con la regla que
lo sostiene · **[INFERENCIA]** conclusión derivada · **[SUPUESTO]** dato faltante · **[SUPUESTO METODOLÓGICO]**
decisión del método.

## 1. Lo que ya se verificó del material [EVIDENCIA]

Revisado el …

1. Qué cambia entre A y B (si cambia más de una cosa, decirlo: el resultado será de la pantalla completa).
2. Alto de cada frame y qué queda sobre el pliegue en cada variante.
3. Qué está cableado en el prototipo y qué no.

### Textos bajo prueba

| Zona | Variante A | Variante B |
|---|---|---|

## 2. Hipótesis

Cada una nombra qué la confirmaría y qué la descartaría.

| # | Hipótesis | Se sostiene si | Se cae si |
|---|---|---|---|

## 3. Diseño

**Factores:** variante × perfil × modo de lectura × corrida.

**Panel:** biblioteca `…`, panel `…`. Reglas conductuales que aplican a estas pantallas:

| Perfil | Segmento | Reglas que aplican |
|---|---|---|

**Corridas:** … por celda. Total: … sesiones (`arnes sesiones <estudio> --simular`).

**Cobertura:** qué no cubre ninguna fuente (p. ej. cómo lee un perfil). Una respuesta «Los datos disponibles
no permiten determinar…» cuenta como **sin cobertura**, no como fallo de comprensión.

## 4. Fases

0 medición · 1 UX writing (W1–W10) · 2 atención predicha · 3 puntos de lectura · 4 sesiones · 5 análisis.
Detalle en `metodos/comprension/METODO.md`. Desviaciones de ese método: **[SUPUESTO METODOLÓGICO]** …

**Consigna:** «…» (no anticipa el resultado).

**Preguntas** (primero la abierta):

| # | Pregunta | Respuesta correcta |
|---|---|---|

## 5. Métricas

- Aciertos por celda (variante × modo) en las preguntas con respuesta correcta.
- Interpretaciones distintas entre corridas (no porcentajes de población).
- Preguntas sin cobertura por perfil.

## 6. Límites

- Perfiles sintéticos: hipótesis a validar con personas.
- Velocidad de lectura [SUPUESTO]: 3.5 palabras/s, con sensibilidad a 2.5 y 4.5.
- La saliencia no distingue perfiles y no es seguimiento ocular.

## 7. Oportunidades, tiempos y entregables

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

## 8. Aprobación

- [ ] `arnes revisar` sin errores (preguntas sugestivas) y avisos leídos
- [ ] Baseline incluido (diseño actual) o razón declarada
- [ ] Piloto corrido y revisado
- [ ] 2–3 corridas planeadas
- [ ] Material verificado
- [ ] Hipótesis con criterio de confirmación y descarte
- [ ] Panel y reglas aplicables revisados
- [ ] Brief completo, con autorización y decisión de investigar
- [ ] Total de sesiones y costo estimado aceptados
