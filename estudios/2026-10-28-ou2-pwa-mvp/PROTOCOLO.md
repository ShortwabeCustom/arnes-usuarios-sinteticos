---
titulo: "Protocolo · oupwa-pdu-originacion-unica-2-0-pwa-sintetico_2026-10-28-v1"
fecha: "2026-10-28"
autor: "Alexis Valdez + Claude"
tipo: "Recorrido de flujo con usuarios sintéticos"
estado: "Completado — reporte verificado (LISTO PARA ENTREGAR) y síntesis en el vault"
---

# Protocolo · oupwa-pdu-originacion-unica-2-0-pwa-sintetico_2026-10-28-v1

## Brief (template de protocolo de UiX)

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | `oupwa-pdu-originacion-unica-2-0-pwa-sintetico_2026-10-28-v1` (guía de naming de UiX; la fecha final se fija al generar el reporte) |
| **Cliente** | Originación Única · PWA |
| **Fecha de elaboración** | 28/10/2026 |
| **Versión** | v1 |
| **Brief** | Segunda medición del benchmark de Originación Única 2.0, ahora sobre la PWA funcional (MVP) en una URL de pruebas: de la bienvenida a la encuesta final, con los mismos cuatro perfiles de la primera medición (prototipo de Figma). Se mide todo lo que se puede medir en un MVP sin reglas de negocio del backend: completitud, fricción, confianza, heurísticas, accesibilidad, rendimiento, PWA y retoma. |
| **Autorización** | Alexis Valdez |

- **Descripción del proyecto:** recorrido completo de la PWA «Solicitud Única · Línea Amarilla» (`pwa.productdesign.mx/app`), 16 etapas y 54 estados de la app, con servicios simulados (OTP, selfie, INE, dirección, evaluación y agenda en su escenario feliz; cámara y ubicación simuladas; esperas aceleradas ×10).
- **Objetivo:** medir la experiencia de punta a punta del MVP y compararla, etapa por etapa, con la primera medición del prototipo, para priorizar qué corregir antes de probar con personas.
- **Muestra esperada:** panel sintético «base4» (4 perfiles) × 4 tareas × 2 corridas = 32 sesiones. Para validar con personas, UiX recomienda 8–10 personas (los patrones de experiencia aparecen desde 8).
- **Incentivos:** No aplica (participantes sintéticos).
- **Alcance de la investigación:** Descriptiva.
- **Público objetivo:** clientes nuevos que piden un préstamo personal desde el celular (User Persona OU-PWA: Centennial 43.9%, Millennial 33.4%, Gen X 17.3%, Boomer 5.4%).
- **Equipo:** Alexis Valdez (UX Research, Originación Única) con el arnés de usuarios sintéticos.
- **Fuentes:** PWA en URL de pruebas; documentación del flujo del mismo sitio (Línea Amarilla, leída del archivo de Figma el 20/10/2026); primera medición (`estudios/2026-10-22-ou2-descubrimiento`); User Persona OU-PWA; guía de voz y estilo de la PWA.
- **Metodología:** Prueba de usabilidad, con usuarios sintéticos, más auditoría técnica automatizada (sin perfiles) y evaluación heurística con 3 evaluadores.
- **Decisión de investigar** (impacto × incertidumbre): impacto alto (es el flujo de originación) · incertidumbre alta (primer MVP funcional, sin pruebas) → Sí investigar.

**Referencias del vault** (`arnes conocimiento recorrido --producto pwa`):
- [[cognitive-walkthrough]] — cada fricción se ubica en una de las 4 preguntas.
- [[diez-heuristicas-de-nielsen]] y [[evaluacion-heuristica]] — criterio y forma de la auditoría con 3 evaluadores.
- [[wcag-22-criterios-nuevos]] y [[accesibilidad-cognitiva]] — 2.5.8 y las reglas automáticas de axe; carga cognitiva de permisos y formularios.
- [[formularios-copy-y-validacion]] — datos personales y domicilio (H4).
- [[flujo-de-checkout-y-conversion]] — oferta, agenda y cierre (H6).
- [[first-click-testing]] — `primer_toque` en las cuatro tareas.
- [[metricas-ux]] — completitud con su intervalo, tiempo solo junto a la tasa de éxito.
- [[estandares-uix-en-investigacion-sintetica]] — naming, semáforo como referencia, muestra para validar.
- [[voz-y-tono-de-la-originacion-unica]] — criterios G1–G8 en la auditoría y `arnes estilo`.

## 0. Pre-flight

| Recurso | Acceso | Estado | Observación |
|---|---|---|---|
| URL del material | Abre sin sesión, HTTPS | ✓ | `?velocidad=rapida&camara=simulada&ubicacion=simulada` |
| Dispositivo | Pixel 7 emulado (412 × 839, toque, Android) | ✓ | Emulación de Playwright, no un teléfono físico |
| Identificación de pantallas | `.marco[data-estado]` | ✓ | La URL no cambia: la app declara su estado |
| Versión fijada | 28/10/2026 | ✓ | Si el MVP cambia durante el estudio, repetir `arnes tecnico` |
| Ruta mecánica | 59 acciones, de la bienvenida a «Completaste tu solicitud» | ✓ | Lee el código de verificación del mensaje simulado |
| Preparación de tareas | T2 → selfie, T3 → datos, T4 → oferta | ✓ | Probadas sin perfiles |
| Biblioteca y panel | `pwa:base4` | ✓ | El mismo panel que la primera medición |
| Datos de prueba | Ficticios («Prueba Ficticio Demo», 55 0000 0000, prueba@example.com) | ✓ | Nunca datos reales |

**Lo que el MVP no tiene y no se mide:** reglas de negocio del backend (buró real, scoring, listas), errores de
servicio reales y tiempos de espera reales (se usan los acelerados; la app declara 20, 45, 40 y 18 s reales).
Las ramas de error existen en la app (OTP incorrecto, selfie no reconocida, INE vencida, rechazo) pero este estudio
recorre la ruta feliz. **[SUPUESTO METODOLÓGICO]**

## 1. Objetivo y preguntas de investigación

**Objetivo:** medir la experiencia de punta a punta del MVP y compararla con el prototipo.

**Pregunta principal:** ¿un cliente nuevo puede pedir su préstamo de punta a punta en la PWA sin ayuda, qué le
cuesta en cada etapa y qué cambió frente al prototipo de Figma?

1. ¿Qué etapas se completan sin fricción y en cuáles cae la confianza?
2. ¿Se corrigieron los hallazgos de la primera medición (total a pagar, buró, progreso, asesor)?
3. ¿Cuánto pide el flujo (pasos, campos, permisos, esperas) y qué tan accesible es?
4. ¿Qué entiende la persona al terminar: qué sigue y cuándo tendrá su dinero?

## 2. Hipótesis

| # | Hipótesis | Se sostiene si | Se cae si |
|---|---|---|---|
| H1 | El simulador muestra solo el pago semanal, no el total: confirman sin saber cuánto pagarán (repite el hallazgo principal del prototipo) | ≥ la mitad de las sesiones de T1 confirma sin mencionar el total o lo pregunta | Las sesiones de T1 mencionan o encuentran el total |
| H2 | La autorización de buró va en letra chica bajo «Continuar»: continúan sin notarla | La mayoría de T1 continúa sin mencionar el buró | La mayoría lo menciona |
| H3 | Cinco permisos en identidad (dos de ubicación en la INE, con un dominio externo): la confianza cae en la INE, más en Gen X y Boomer | Caída ≥ 15 en una pantalla de permisos de T2, o un perfil niega uno o nota que lo repite | La confianza se mantiene |
| H4 | «Confirma tus datos» pide coincidir con la INE pero muestra vacíos apellidos y fecha: esperan que la app los tenga | Algún perfil lo comenta o duda de la lectura de la INE | Todos llenan sin comentarlo |
| H5 | Sin indicador de progreso hasta el domicilio: en T1 y T2 dicen no saber cuánto falta más que en T3 | Proporción de progreso «no» o «más o menos» mayor en T1 y T2 que en T3 | Igual o menor |
| H6 | Al terminar no saben cuándo tendrán el dinero | En el cierre de T4, la mitad o más no lo sabe o lo dice mal | La mayoría explica visita → depósito |

## 3. Panel

Biblioteca `pwa`, panel `base4` (sin capa OCEAN), el mismo de la primera medición para comparar:

| id | Perfil | Segmento | Edad |
|---|---|---|---|
| bryan | Bryan Nájera | Centennial · 43.9% | 22 |
| itzel | Itzel Camacho | Millennial · 33.4% | 36 |
| rosalba | Rosalba Quintero | Gen X · 17.3% | 52 |
| arturo | Arturo Belmont | Boomer · 5.4% | 66 |

## 4. Tareas

Un recorrido de punta a punta en una sola sesión serían ≈ 80 pasos y ≈ 21 M de tokens por sesión (el contexto crece
con cada captura). Se divide por etapas: cada sesión empieza con contexto limpio y las tareas 2–4 empiezan donde las
deja la ruta mecánica; el escenario le cuenta al perfil lo que ya hizo. **[SUPUESTO METODOLÓGICO]** Cada sesión
empieza sin datos guardados (como alguien que nunca abrió la app).

| ID | Empieza en | Escenario e instrucción | Criterio de éxito (fin) | Primer toque esperado |
|---|---|---|---|---|
| T1 | Bienvenida | Va solo, quiere efectivo: elegir monto y plazo, dejar contacto, verificar el celular, hasta la selfie | «¡Empezamos con tu selfie!» (`selfieIntro`) | «Inicia tu solicitud» |
| T2 | Selfie | Comprobar su identidad con lo que pida la app | «Confirma tus datos» (`datosPersonales`) | «Tomar foto» |
| T3 | Datos | Revisar datos y domicilio hasta saber cuánto le prestan. **Retoma:** tras el paso 10 sale y vuelve a entrar | Oferta (`oferta`) | Primer apellido |
| T4 | Oferta | Decidir si acepta y terminar. **Cierre:** ¿qué pasa ahora y cuándo tendrás tu dinero? | `completada`, `encuesta` o `gracias` | «Continuar» |

Señales de fracaso: abandono, atascado (4 pasos sin cambio), máximo de pasos, cree que terminó sin llegar.

## 5. Qué se observa en cada paso

Pantalla observada · primera impresión · qué mira primero · interpretación · intención · acción y razón ·
pensamiento en voz alta · resultado · ubicación en el proceso · confianza (0–100) · fricción (0–5).
Al cierre: facilidad percibida (CES 1–7).

## 6. Métricas

**De las sesiones sintéticas** (`arnes analizar`): completitud por tarea con intervalo y semáforo de UiX como
referencia; éxito sin fricción; primer toque; pasos, toques, campos, validaciones, espera del sistema y tiempo
estimado (modelo); toques sin respuesta y fuera de los elementos; caídas de confianza y fricción por etapa; ubicación
en el proceso; retoma; CES; estabilidad entre corridas.

**De la auditoría técnica** (`arnes tecnico`, 0 tokens, sobre la ruta mecánica): WCAG 2.0/2.1/2.2 A y AA con axe-core
por pantalla; objetivos táctiles < 24 y < 44 px; foco visible con teclado; reflujo a 320 px; campos con etiqueta,
autocompletado y teclado adecuado; legibilidad INFLESZ; errores de consola y de red; carga en frío y con caché en red
móvil lenta (TTFB, FCP, LCP, CLS, TBT, peso, peticiones) y respuesta a toques (INP aproximado); PWA (manifiesto,
íconos, service worker, sin conexión); retoma al recargar y al volver a entrar; ruta mínima (acciones, campos, espera).

**De la auditoría experta** (`arnes auditar`, 3 evaluadores): heurísticas de Nielsen, cognitive walkthrough y criterios
G1–G8 de la guía de voz, con consenso. **De la guía de estilo** (`arnes estilo`): reglas E01–E16 sobre los textos.

## 7. Límites

- Perfiles sintéticos: hipótesis a validar con personas. «19 de 24 corridas», nunca porcentajes de clientes.
- El perfil ve los elementos tocables numerados y su lista de etiquetas. **[SUPUESTO METODOLÓGICO]**
- Al escribir, el texto reemplaza lo que había en el campo; en un deslizador, «escribir» un valor toca el punto de la
  barra que le corresponde. **[SUPUESTO METODOLÓGICO]**
- Cámara y ubicación simuladas: la app lo dice en pantalla («No encontramos una cámara…»); se avisa al perfil que es
  parte de la prueba. Esa leyenda no existe en producción.
- Celular emulado, no físico. Rendimiento medido en laboratorio, no en campo.
- La duración de la sesión no mide tiempo de tarea.
- axe-core detecta una parte de los problemas de accesibilidad; lo demás exige revisión manual y lectores de pantalla.

## 8. Oportunidades, tiempos y entregables

**Oportunidades.** Cada hallazgo se clasifica como Mantener · Mejorar · Incorporar · Hacer diferente.

| Actividad | Días |
|---|---|
| Documentación y ruta mecánica | 0.5 |
| Auditoría técnica | incluida (0 tokens) |
| Levantamiento (piloto + 32 sesiones) | 1 |
| Análisis y auditoría experta | 0.5 |
| Reporte y síntesis | 0.5 |

- **Entregables:** tablero de investigación (con «Calidad técnica»), reporte completo, comparación con la primera
  medición, síntesis en el vault.

## 9. Consumo estimado (tokens de la suscripción)

| Bloque | Sesiones | Tokens (≈) | Nuevos (≈) |
|---|---|---|---|
| Piloto (Bryan, T1) | 1 | 1.3 M | 0.2 M |
| T1 · contacto y verificación | 8 | 10.4 M | 1.5 M |
| T2 · identidad | 8 | 6.7 M | 1.1 M |
| T3 · datos y domicilio | 8 | 20.3 M | 2.1 M |
| T4 · oferta y cierre | 8 | 3.8 M | 0.8 M |
| Auditoría experta (3 evaluadores, 30 pantallas) | — | ≈ 1 M | ≈ 0.3 M |
| **Total con 2 corridas** | 33 | **≈ 44 M** | **≈ 6 M** |
| Total con 1 corrida | 17 | ≈ 23 M | ≈ 3 M |

La mayor parte es relectura de caché. Modelo calibrado con las 16 sesiones de la primera medición (error medio ≈ 3%),
ajustado al tamaño de captura del Pixel 7.

## 10. Aprobación

- [x] `arnes revisar` sin errores ni avisos
- [x] Baseline: la primera medición (prototipo); `primer_toque` por tarea
- [x] Piloto: Bryan, T1 (3 intentos; los 2 primeros, fallas del instrumento en `datos/historial/`)
- [x] 2 corridas por perfil planeadas
- [x] Pre-flight completo, sin bloqueos
- [x] Tareas con criterio de fin verificable por el arnés
- [x] Panel revisado
- [x] Brief completo, con autorización y decisión de investigar
- [x] Consumo estimado aceptado (28/10/2026: piloto + panel con 2 corridas, ≈ 44 M tokens)
