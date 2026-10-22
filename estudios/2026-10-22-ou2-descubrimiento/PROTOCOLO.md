---
titulo: "Protocolo · oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1"
fecha: "2026-10-22"
autor: "Alexis Valdez + Claude"
tipo: "Recorrido de flujo con usuarios sintéticos"
estado: "Completado — reporte verificado (LISTO PARA ENTREGAR) y síntesis en el vault"
---

# Protocolo · oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1

## Brief (template de protocolo de UiX)

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | `oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1` (guía de naming de UiX; la fecha final se fija al generar el reporte) |
| **Cliente** | Originación Única · PWA |
| **Fecha de elaboración** | 22/10/2026 |
| **Versión** | v1 |
| **Brief** | Recorrer el prototipo de Originación Única 2.0 (flujo amarillo) de la bienvenida a la selfie con los cuatro segmentos del User Persona, para documentar todo lo que vive el usuario: dónde avanza, duda o se traba, qué tan bien cumple las heurísticas y cuánto le cuesta (pasos, campos, tiempo, permisos). Es la línea base para comparar versiones. |
| **Autorización** | Alexis Valdez |

- **Descripción del proyecto:** descubrimiento preliminar del prototipo de Figma «Originación Única 2.0 · Cliente», flujo «OU 2.0 Flujo Amarillo», de la bienvenida a la toma de selfie (24 pantallas en el recorrido mecánico). El flujo «Mini Juego» queda fuera.
- **Objetivo:** documentar, como benchmark, la experiencia completa del flujo con heurísticas y métricas de producto y de negocio, para priorizar qué mejorar antes de probar con personas.
- **Muestra esperada:** panel sintético «base4» (4 perfiles) × 2 tareas × 2 corridas = 16 sesiones. Para validar con personas, UiX recomienda 8–10 personas (los patrones de experiencia aparecen desde 8).
- **Incentivos:** No aplica (participantes sintéticos).
- **Alcance de la investigación:** Descriptiva.
- **Público objetivo:** clientes nuevos que piden un préstamo personal desde el celular (User Persona OU-PWA: Centennial 43.9%, Millennial 33.4%, Gen X 17.3%, Boomer 5.4%).
- **Equipo:** Alexis Valdez (UX Research, Originación Única) con el arnés de usuarios sintéticos.
- **Fuentes:** prototipo de Figma (link compartido, abre sin sesión); User Persona OU-PWA (685,243 clientes); guía de voz y estilo de la PWA; estudio previo OU-PWA de usabilidad.
- **Metodología:** Prueba de usabilidad, con usuarios sintéticos.
- **Decisión de investigar** (impacto × incertidumbre): impacto alto (es el flujo de originación) · incertidumbre alta (versión 2.0 sin pruebas) → Sí investigar.

**Referencias del vault** (`arnes conocimiento recorrido --producto pwa`):
- [[cognitive-walkthrough]] — cada fricción se ubica en una de las 4 preguntas.
- [[diez-heuristicas-de-nielsen]] y [[evaluacion-heuristica]] — criterio y forma de la auditoría con 3 evaluadores.
- [[wcag-22-criterios-nuevos]] — 2.5.8, tamaño mínimo de los objetivos táctiles.
- [[formularios-copy-y-validacion]] — pantalla de datos y botón deshabilitado (H5).
- [[metricas-ux]] — completitud con su intervalo, tiempo solo junto a la tasa de éxito.
- [[estandares-uix-en-investigacion-sintetica]] — naming, semáforo como referencia, muestra para validar.
- [[voz-y-tono-de-la-originacion-unica]] — criterios G1–G8 en la auditoría.

## 0. Pre-flight

| Recurso | Acceso | Estado | Observación |
|---|---|---|---|
| URL del material | Abre sin sesión (probado como incógnito) | ✓ | Banner de cookies: se descarta en `preparacion`. Barra lateral de flujos cerrada para no mover el marco |
| Dispositivo | «Android Grande» del prototipo | ✓ | Sin cambiar el tamaño de ventana |
| Versión fijada (fecha, hora, node-id de inicio) | 22/10/2026 · inicio `7723-327419` | ✓ | Si el prototipo cambia durante el estudio, repetir el mapeo |
| Zonas tocables | Por resaltados de Figma (hotspot hints) | ✓ | En este prototipo táctil el cursor no distingue botones; dentro de overlays se toca la franja superior para no cerrarlos |
| Biblioteca y panel | `pwa:base4` | ✓ | Sin capa OCEAN |
| Datos de prueba | Los del prototipo («María», 55 6960 7716) | ✓ | El prototipo llena los campos al tocarlos [SUPUESTO METODOLÓGICO] |

**Mapa del flujo (recorrido mecánico, sin perfiles).** Bienvenida (carrusel) → uso del préstamo (solo «Efectivo»
conectado) → monto y plazo (hoja «Elige tu plazo») → datos de contacto (3 campos) → código de verificación →
¿te ayuda un asesor? (número de empleado) → introducción a la selfie → permiso de cámara → permiso de ubicación →
cargando → toma de selfie (fin del prototipo: «Tomar selfie» sin conexión, categoría B).

## 1. Objetivo y preguntas de investigación

**Objetivo:** documentar la experiencia completa del flujo como línea base.

**Pregunta principal:** ¿un cliente nuevo puede llegar de la bienvenida a la selfie sin ayuda, y qué le cuesta
en cada pantalla?

1. ¿Dónde duda, se equivoca o pierde confianza cada segmento?
2. ¿Qué heurísticas y criterios de accesibilidad incumple el flujo, y con qué severidad?
3. ¿Cuánto cuesta el flujo: pasos, toques, campos, permisos, tiempo estimado, distancia a la oferta?
4. ¿La promesa de la bienvenida («menos de 5 minutos», «4 pasos») coincide con lo que se recorre?

## 2. Hipótesis

| # | Hipótesis | Se sostiene si | Se cae si |
|---|---|---|---|
| H1 | La promesa «menos de 5 minutos · 4 pasos» no coincide con lo recorrido | La mitad de las sesiones o más menciona más pasos o tiempo, o pierde la noción del paso | Ninguna lo menciona y la confianza no baja |
| H2 | El pago semanal aparece tarde: se confirma sin saber cuánto se pagará | Alguna sesión confirma sin mencionarlo o duda del total | Todas lo mencionan antes de confirmar |
| H3 | Cámara y ubicación seguidas causan la mayor caída de confianza, más en Gen X y Boomer | Caída ≥ 15 o permiso negado en alguna sesión | Confianza estable en ambas pantallas |
| H4 | «¿Te está ayudando un asesor?» confunde a quien solicita solo | Duda, «Sí» sin asesor o pregunta para qué | Todos responden sin duda |
| H5 | El «Continuar» deshabilitado no explica qué falta | Toque al botón gris o «no sé qué falta» | Nadie intenta antes de completar |

## 3. Panel

Biblioteca `pwa`, panel `base4`: Bryan (Centennial, 22), Itzel (Millennial, 36), Rosalba (Gen X, 52) y Arturo
(Boomer, 66). Sin capa OCEAN: no hay matriz de diversidad de personalidad; la variedad viene de los segmentos.
**Vacío declarado:** cuatro perfiles no cubren la variación dentro de cada segmento.

## 4. Tareas

| ID | Escenario | Instrucción exacta | Objetivo | Criterio de éxito (fin) | Señales de fracaso |
|---|---|---|---|---|---|
| T1 | Quieres un préstamo en efectivo y entraste desde tu celular a la página de Banco Azteca para pedirlo. | Pide un préstamo en efectivo y avanza hasta donde la aplicación te deje llegar. | Flujo de quien va solo, de la bienvenida a la pregunta del asesor | Llega a «¿te está ayudando un asesor?» (`9830-189949`) y contesta la pregunta de cierre sin actuar | Abandona, se atasca 4 pasos sin cambio, más de 22 pasos |
| T2 | Estás en una sucursal y un asesor te ayuda; ya elegiste monto y plazo, llenaste tus datos y verificaste tu número; el asesor te dio su número de empleado. | Continúa tu solicitud hasta donde la aplicación te deje llegar. | Tramo asistido: número de empleado, selfie y permisos | Llega a «cargando» o a la toma de selfie (`7723-327412`, `7723-327416`) | Abandona, niega un permiso, más de 14 pasos |

**Por qué dos tareas [SUPUESTO METODOLÓGICO].** El prototipo solo conecta «Sí» en la pregunta del asesor (piloto 3:
Bryan respondió «No» y no pudo seguir). T1 cubre a quien va solo y, al llegar a esa pregunta, el perfil contesta qué
respondería y por qué (`pregunta_cierre`), sin depender de la rama sin conectar. T2 empieza en esa pantalla con un
asesor presente. Primer toque esperado: «Inicia tu solicitud» (T1) y «Sí, me están ayudando» (T2).

| Hipótesis | Dónde se observa |
|---|---|
| H1 promesa de 5 minutos y 4 pasos | T1 y la calificación de facilidad |
| H2 pago total | T1, monto y plazo |
| H3 permisos | T2 |
| H4 pregunta del asesor | T1, pregunta de cierre |
| H5 «Continuar» deshabilitado | T1, datos de contacto |

No se alteran las tareas originales salvo imposibilidad técnica, y entonces se marca **[SUPUESTO METODOLÓGICO]**.

## 5. Qué se observa en cada paso

Pantalla observada · primera impresión · qué mira primero · interpretación · intención · acción y razón ·
pensamiento en voz alta · resultado · confianza (0–100) · fricción (0–5).

Resultado por tarea: éxito · éxito con fricción · cree que terminó · abandono · atascado · sin terminar.

## 6. Métricas

- Tasa de completitud por tarea (sesiones, no personas), con su intervalo y el semáforo de UiX como referencia.
- Primer toque, pasos, toques, campos solicitados, permisos pedidos, distancia a la oferta y tiempo estimado
  (modelo declarado + espera real del prototipo).
- WCAG 2.2 · 2.5.8 sobre las zonas tocables (aproximado en Figma).
- Toques sin respuesta y fuera de zonas activas.
- Caídas de confianza y fricción máxima por pantalla.
- Incidentes: frecuencia, severidad 0–4, categoría A/C, prioridad F × S × I.

## 7. Límites

- Perfiles sintéticos: hipótesis a validar con personas.
- El perfil ve las zonas activas numeradas [SUPUESTO METODOLÓGICO].
- La duración de la sesión no mide tiempo de tarea.
- Es un prototipo: lo que no está conectado es estado de prototipado (categoría B), no defecto. Solo «Efectivo»
  está conectado en el uso del préstamo; el resto de las opciones queda fuera.
- Los datos los llena el prototipo: no se mide el esfuerzo real de escribir.
- En T2 el perfil llega «fresco» a los permisos, sin el cansancio de todo el flujo: su confianza ahí es un techo;
  si aun así cae, la señal es fuerte. El tiempo total del flujo es la suma estimada de T1 y T2.
- El camino de quien responde «No» al asesor no existe en el prototipo: no se evalúa.
- Un toque que no cambia el teléfono se repite una vez (`reintento`) [SUPUESTO METODOLÓGICO].
- El perfil ve la captura recortada al teléfono; la burbuja con su pensamiento queda fuera, solo para observar.

## 8. Oportunidades, tiempos y entregables

**Oportunidades.** Cada hallazgo se clasifica como Mantener · Mejorar · Incorporar · Hacer diferente
(`oportunidad` en `narrativa.yaml`).

| Actividad | Días |
|---|---|
| Documentación | 0.5 |
| Creación de materiales | 0.5 |
| Levantamiento (sesiones sintéticas) | 0.5 |
| Análisis | 1 |
| Reporte | 0.5 |

- **Fecha de inicio:** dd de mes de aaaa · **Fecha de entrega final:** dd de mes de aaaa
- **Entregables:** Reporte · Flash report · Infografía · Matriz comparativa · Insights y oportunidades priorizadas.

## 9. Aprobación

- [x] `arnes revisar` sin errores y avisos leídos
- [x] Baseline (`baseline_url`) o razón declarada; `primer_toque` por tarea
- [x] Piloto: un perfil, una tarea, capturas revisadas (3 intentos; los 2 primeros fallaron por el instrumento)
- [x] 2 corridas por perfil planeadas
- [x] Pre-flight completo, sin bloqueos
- [x] Tareas con criterio de fin verificable por el arnés
- [x] Panel revisado
- [x] Brief completo, con autorización y decisión de investigar
- [x] Consumo estimado aceptado (`arnes recorrido <estudio> todos --simular`, en tokens)
