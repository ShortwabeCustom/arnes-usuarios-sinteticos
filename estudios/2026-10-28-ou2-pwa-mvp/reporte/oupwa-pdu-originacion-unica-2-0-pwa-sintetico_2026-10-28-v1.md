# La PWA se recorre de punta a punta, pero el costo total del préstamo no aparece en ningún momento: 8 de 8 sesiones lo buscan al elegir el plazo y 8 de 8 al aceptar el contrato

**Estudio:** Segunda medición de Originación Única 2.0: la PWA funcional (MVP), de la bienvenida a la encuesta  ·  **Fecha:** 2026-10-28  ·  **Método:** recorrido
**Biblioteca:** pwa · panel base4 (4 perfiles)
**Tipo de investigación:** simulación UX con usuarios sintéticos — no sustituye investigación con usuarios reales.

Los cuatro perfiles llegan de la bienvenida a la verificación del celular (7 de 8 sesiones), completan selfie e INE (8 de 8), llenan datos y domicilio hasta la oferta (7 de 8) y terminan la solicitud (6 de 8). La técnica responde: carga en 2.4 s en red móvil lenta, funciona sin conexión y conserva el avance al salir y volver. Lo que frena es de información y de confianza: el total a pagar no aparece ni en el simulador ni en el contrato (el pago es «aproximado»), el permiso de ubicación se pide por tercera vez desde un dominio que no es del banco, y la visita a domicilio aparece al final como sorpresa. Frente al prototipo, se corrigió el código de verificación y se conectó la rama sin asesor; siguen abiertos el total, el buró y la ubicación en el proceso. Son hipótesis para validar con personas.

## Resumen

- **6 de 8** sesiones de T1 llegan a la selfie con fricción — Una llega sin fricción y una abandona en el consentimiento de buró. La fricción se concentra en el simulador (sin total) y en los datos de contacto.
- **8 de 8** sesiones de T2 completan la identidad con fricción — La confianza cae unos 20 puntos en el permiso de ubicación de Incode, que llega desde otro dominio y por tercera vez.
- **2 de 8** sesiones de T4 abandonan en el contrato — Itzel, las dos veces: el pago es «aproximado», no hay total y el costo real se lo darían en la visita.
- **16.5** pasos de la bienvenida a la selfie (mediana) — La bienvenida promete «4 pasos»; el flujo completo son 59 acciones en la ruta mínima y 30 pantallas.
- **4.5** facilidad percibida en datos y domicilio (CES 1–7, mediana) — La más baja de las cuatro tareas; en T1, T2 y T4 la mediana es 5.

- En 8 de 8 sesiones de T1 el perfil busca el total a pagar en el simulador y no lo encuentra; con 128 semanas como primera opción, varios hacen la cuenta solos. En 8 de 8 sesiones de T4 lo vuelven a buscar al aceptar el contrato, donde el pago semanal dice «aproximado».
- Itzel abandona T4 en las dos corridas en «Día de pago»: «Son 52 semanas de $728, unos $37,800 por $22,000, y eso lo saqué yo. El costo total me lo darán en mi casa». Es la confianza más baja del flujo (28).
- La verificación de identidad pide cinco permisos. En el tercero de ubicación, ahora desde «identidad-digital-ocrdual.com.mx», la confianza cae de alrededor de 60 a 40 en 8 de 8 sesiones de T2; Bryan lo niega en sus dos corridas (pasa por «cámara negada» y luego acepta).
- La autorización de buró sigue implícita al tocar «Continuar». 8 de 8 sesiones de T1 la notan, la mayoría no la lee («Ni me puse a leer la letra chiquita») y el enlace «Consulta de Historial Crediticio» abre la página de inicio del banco, no el documento: Itzel se detiene ahí.
- La visita a domicilio aparece hasta la agenda. 4 de 8 sesiones de T4 lo dicen así: «Yo quería resolverlo desde el celular».
- Saber dónde va: en T1–T3, 435 de 439 respuestas dicen «no» o «más o menos». La barra de progreso del domicilio se nota (6 de 8 sesiones de T3 la mencionan), pero arranca vacía por etapa: «La barra casi vacía… otra vez a empezar» (Bryan).
- En «Confirma tus datos» 8 de 8 sesiones de T3 notan que la app pide coincidir con la INE pero no trae los apellidos ni la dirección que acaba de leer.
- La foto de fachada de ejemplo parece un hotel: 8 de 8 sesiones de T3 lo comentan; 7 confirman «para avanzar» y Rosalba se niega en una corrida y no llega a la oferta.
- Técnica: carga en 2.4 s (LCP) con red móvil lenta, 667 KB, funciona sin conexión y conserva el avance al volver (8 de 8 sesiones de T3). Accesibilidad automática (WCAG 2.2 AA): 21 de 30 pantallas sin fallas; contraste insuficiente en 7 (los botones «No permitir», el contador del código) y carruseles sin teclado.
- Frente al prototipo (primera medición): el código de verificación ya no se atora (se valida solo y el SMS ofrece autollenado; 7 de 7 lo resuelven en un paso) y la rama sin asesor ya existe; siguen el total, el buró y la ubicación en el proceso.

## Panel

| ID | Nombre | Segmento | O | C | E | A | N |
|---|---|---|---:|---:|---:|---:|---:|
| bryan | Bryan Nájera | Centennial · 43.9% | — | — | — | — | — |
| itzel | Itzel Camacho | Millennial · 33.4% | — | — | — | — | — |
| rosalba | Rosalba Quintero | Gen X · 17.3% | — | — | — | — | — |
| arturo | Arturo Belmont | Boomer · 5.4% | — | — | — | — | — |

**Datos demográficos (categorías de UiX, con su evidencia):**

| Perfil | Edad (generación) | Género | Región | Ocupación |
|---|---|---|---|---|
| Bryan Nájera | Centennials (Gen Z), 18-30 años (22 años) [OBSERVADO] | Hombre [OBSERVADO] | Centro (Ciudad de México) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |
| Itzel Camacho | Millennials, 31-45 años (36 años) [OBSERVADO] | Mujer [OBSERVADO] | Centro (Ciudad de México) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |
| Rosalba Quintero | Gen X, 46-60 años (52 años) [OBSERVADO] | Mujer [OBSERVADO] | Centro (Estado de México) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |
| Arturo Belmont | Boomers, 61+ años (66 años) [OBSERVADO] | Hombre [OBSERVADO] | Sur (Veracruz) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |

## Sesiones

| Sesión | Resultado | Pasos | Sin respuesta | Confianza | Fricción máx. |
|---|---|---:|---:|---|---:|
| T1-arturo-1 | exito_con_friccion | 18 | 1 | 60 → 56 | 3 |
| T1-arturo-2 | exito | 17 | 0 | 65 → 55 | 2 |
| T1-bryan-1 | exito_con_friccion | 19 | 1 | 60 → 60 | 3 |
| T1-bryan-2 | exito_con_friccion | 19 | 1 | 60 → 58 | 3 |
| T1-itzel-1 | exito_con_friccion | 17 | 0 | 60 → 50 | 3 |
| T1-itzel-2 | abandono | 9 | 0 | 60 → 25 | 5 |
| T1-rosalba-1 | exito_con_friccion | 18 | 0 | 65 → 62 | 3 |
| T1-rosalba-2 | exito_con_friccion | 17 | 0 | 65 → 62 | 3 |
| T2-arturo-1 | exito_con_friccion | 14 | 1 | 60 → 68 | 3 |
| T2-arturo-2 | exito_con_friccion | 14 | 1 | 55 → 62 | 3 |
| T2-bryan-1 | exito_con_friccion | 15 | 1 | 68 → 58 | 4 |
| T2-bryan-2 | exito_con_friccion | 15 | 1 | 68 → 58 | 4 |
| T2-itzel-1 | exito_con_friccion | 14 | 1 | 65 → 70 | 3 |
| T2-itzel-2 | exito_con_friccion | 14 | 1 | 65 → 66 | 3 |
| T2-rosalba-1 | exito_con_friccion | 14 | 1 | 68 → 70 | 3 |
| T2-rosalba-2 | exito_con_friccion | 14 | 1 | 72 → 65 | 3 |
| T3-arturo-1 | exito_con_friccion | 28 | 0 | 60 → 55 | 3 |
| T3-arturo-2 | exito_con_friccion | 35 | 0 | 60 → 55 | 3 |
| T3-bryan-1 | exito_con_friccion | 29 | 1 | 65 → 52 | 3 |
| T3-bryan-2 | exito_con_friccion | 28 | 0 | 65 → 52 | 3 |
| T3-itzel-1 | exito_con_friccion | 29 | 1 | 65 → 62 | 2 |
| T3-itzel-2 | exito | 28 | 0 | 65 → 60 | 2 |
| T3-rosalba-1 | exito_con_friccion | 29 | 1 | 68 → 65 | 3 |
| T3-rosalba-2 | fallo_max_pasos | 34 | 0 | 68 → 66 | 3 |
| T4-arturo-1 | exito | 11 | 0 | 60 → 82 | 2 |
| T4-arturo-2 | exito | 9 | 0 | 55 → 78 | 2 |
| T4-bryan-1 | exito_con_friccion | 11 | 1 | 62 → 55 | 3 |
| T4-bryan-2 | exito_con_friccion | 10 | 1 | 62 → 52 | 3 |
| T4-itzel-1 | abandono | 8 | 0 | 55 → 28 | 4 |
| T4-itzel-2 | abandono | 8 | 0 | 60 → 30 | 5 |
| T4-rosalba-1 | exito_con_friccion | 11 | 0 | 62 → 78 | 3 |
| T4-rosalba-2 | exito_con_friccion | 11 | 0 | 68 → 78 | 3 |

## Hallazgos

### H1 · El costo total del préstamo no aparece en ningún momento: ni al elegir el plazo ni en el contrato

**Severidad:** 4 (Crítico) · **Confianza:** alta

**Hallazgo.** En el simulador solo aparece el pago semanal («$0 Pesos» hasta elegir plazo) y la lista de plazos empieza en 128 semanas. 8 de 8 sesiones de T1 buscan el total y no lo encuentran; es la pantalla con más fricción alta de T1 (10 observaciones con fricción 3 o más). En el contrato de «Día de pago» el pago dice «aproximado» y tampoco hay total: 8 de 8 sesiones de T4 lo buscan e Itzel abandona en sus dos corridas (confianza 28).

**Interpretación.** La decisión de endeudarse se toma dos veces sin el dato que la sostiene. Quien hace la cuenta (Itzel: $37,800 por $22,000) pierde la confianza justo antes de aceptar; quien no la hace acepta sin saber. Es el hallazgo principal de la primera medición y sigue abierto en la PWA.

**Recomendación.** Mostrar junto al pago semanal el total a pagar y el número de pagos, que cambien con el plazo; repetirlos en el contrato con su CAT, y no presentar el pago como «aproximado» sin decir de qué depende. **Oportunidad:** Incorporar.

**Evidencia.** Pensamientos de simulador (T1) y diaPago (T4) · abandonos T4-itzel-1 y T4-itzel-2 · auditoría: «$0 Pesos» con 3 de 3 evaluadores (N1, severidad 3).

### H2 · El tercer permiso de ubicación llega desde un dominio que no es del banco y la confianza cae 20 puntos

**Severidad:** 3 (Importante) · **Confianza:** alta

**Hallazgo.** La identidad pide cinco permisos: cámara y ubicación en la selfie y, en la INE, ubicación (app), ubicación y cámara (Incode, con «identidad-digital-ocrdual.com.mx»). En el permiso de ubicación de Incode la confianza baja de 52–66 a 35–45 en 8 de 8 sesiones de T2 y la fricción media es 3.2. Bryan lo niega en sus dos corridas y pasa por «cámara negada».

**Interpretación.** La repetición se lee como insistencia y el cambio de dominio como salir del banco. Lo que sostiene la confianza en la selfie (explicar para qué) no se repite en la INE.

**Recomendación.** Pedir la ubicación una sola vez y reutilizarla; anunciar antes de la INE que la verificación la hace un proveedor del banco, con su nombre, y explicar para qué es cada permiso. Si el dominio no puede cambiar, mostrar la marca del banco en esa pantalla. **Oportunidad:** Hacer diferente.

**Evidencia.** Pensamientos de incodeUbicacion e incodeCamara · auditoría: N2 y N5 con 3 de 3 evaluadores · contraste insuficiente de «No permitir» (axe, 1.4.3).

### H3 · El buró se autoriza al continuar y su enlace abre la página de inicio del banco, no el documento

**Severidad:** 3 (Importante) · **Confianza:** alta

**Hallazgo.** «Al continuar, aceptas el Aviso de Privacidad y autorizas la Consulta de Historial Crediticio…» va en letra chica bajo el botón. 8 de 8 sesiones de T1 la notan; la mayoría la salta sin leer. Los tres enlaces abren bancoazteca.com.mx en otra pestaña. Itzel intenta leer el de buró, ve la página de inicio y abandona: «No voy a firmar algo que no pude leer». Confianza mínima de la pantalla: 25.

**Interpretación.** La autorización más sensible sigue implícita, como en el prototipo. En el MVP, además, el documento no existe: quien quiere leer antes de aceptar no puede.

**Recomendación.** Separar la autorización de buró en una casilla explícita con una frase legible de para qué se consulta, después de mostrar el total; conectar el enlace al texto real. **Oportunidad:** Hacer diferente.

**Evidencia.** Pensamientos de contacto (T1) · T1-itzel-2 (pestaña nueva con «Banco Azteca, tu banca en línea») · primera medición, hallazgo H2.

### H4 · La visita a domicilio aparece hasta el final, como sorpresa

**Severidad:** 3 (Importante) · **Confianza:** media

**Hallazgo.** Después de la oferta, «agenda una visita para confirmar tu solicitud». 4 de 8 sesiones de T4 lo dicen así: «¿Una visita? Yo quería resolverlo desde el celular». La confianza en la agenda baja a 40 en las sesiones de Itzel y Bryan, y «7 de cada 10 personas usan su préstamo el mismo día» se lee como presión.

**Interpretación.** La app se presenta como «de punta a punta desde tu celular». Si el préstamo depende de una visita, saberlo hasta el final rompe la expectativa y retrasa la decisión.

**Recomendación.** Anunciar la visita desde la bienvenida o el simulador (qué es, cuánto dura, para qué) y repetirlo antes de la oferta. **Oportunidad:** Mejorar.

**Evidencia.** Pensamientos de agendaIntro y agendaDiaHora (T4).

### H5 · Los perfiles no saben cuánto les falta: la barra aparece hasta el domicilio y arranca vacía en cada etapa

**Severidad:** 2 (Menor) · **Confianza:** alta

**Hallazgo.** La bienvenida promete «4 pasos»; la ruta mínima son 59 acciones en 30 pantallas. En T1–T3, 435 de 439 respuestas dicen no saber, o saber más o menos, en qué parte van. La barra «Tu domicilio» se nota (6 de 8 sesiones de T3), pero mide la etapa: «La barra casi vacía… otra vez a empezar» (Bryan).

**Interpretación.** Una barra por etapa que vuelve a cero confirma que falta mucho sin decir cuánto. La promesa de 4 pasos sigue sin corresponder al recorrido.

**Recomendación.** Un indicador global de pocos pasos con nombre («Paso 3 de 5 · Tu domicilio») en todo el flujo, o ajustar la promesa de la bienvenida. **Oportunidad:** Mejorar.

**Evidencia.** Métrica «sabe dónde va» · pensamientos de direccion y domicilioInicio (T3) · primera medición, hallazgo H3.

### H6 · «Confirma tus datos» pide coincidir con la INE, pero no trae lo que la INE acaba de leer

**Severidad:** 2 (Menor) · **Confianza:** alta

**Hallazgo.** 8 de 8 sesiones de T3 notan que los apellidos, la fecha y la dirección vienen vacíos después de escanear la INE. T3 es la tarea más larga (mediana de 28 pasos, 14 campos) y la de menor facilidad percibida (CES 4.5). Estado civil y ocupación se piden sin decir para qué (Arturo, dos corridas).

**Interpretación.** Escanear la INE y luego escribir lo mismo se siente como trabajo doble; la frase «debe coincidir con tu INE» lo hace evidente.

**Recomendación.** Prellenar con lo leído de la INE y pedir solo confirmar; explicar en una línea para qué se piden estado civil y ocupación. **Oportunidad:** Incorporar.

**Evidencia.** Pensamientos de datosPersonales y direccion (T3) · CES de T3 · historial: T3-arturo con datos de prueba incompletos.

### H7 · «No es mi fachada» no dice qué pasa: confirmar se vuelve un trámite

**Severidad:** 2 (Menor) · **Confianza:** media

**Hallazgo.** La foto de ejemplo parece un hotel. 8 de 8 sesiones de T3 lo comentan; 7 confirman «para avanzar» y Rosalba se niega («No voy a decir que sí solo para avanzar») y, al elegir «No es mi fachada», vuelve al mapa sin explicación. No llega a la oferta.

**Interpretación.** La foto es de ejemplo (va en estado de prototipado). Lo que es diseño: no se dice qué pasa al elegir «No», y por eso confirmar algo falso «para avanzar» parece la única salida.

**Recomendación.** Explicar qué pasa si no es tu fachada (ajustar el pin, continuar sin foto) y usar la imagen real de la dirección. **Oportunidad:** Mejorar.

**Evidencia.** Pensamientos de fachada (T3) · T3-rosalba-2 · auditoría: N3 con 3 de 3 evaluadores.

### H8 · Las referencias del domicilio no dicen qué es obligatorio

**Severidad:** 2 (Menor) · **Confianza:** media

**Hallazgo.** Es la pantalla con más observaciones de fricción alta de todo el flujo (17 con fricción 3 o más). En 6 de 8 sesiones de T3 el perfil no sabe por qué «Confirmar» sigue apagado: «Nadie me avisó que ese campo era obligatorio» (Bryan).

**Interpretación.** El botón desactivado sin explicación obliga a adivinar; con cuatro calles con «No aplica» el formulario se siente largo para un dato opcional.

**Recomendación.** Marcar qué es obligatorio y decir qué falta cuando se toca «Confirmar»; considerar si las cuatro calles son necesarias. **Oportunidad:** Mejorar.

**Evidencia.** Pensamientos de referencias (T3).

### H9 · Contraste insuficiente y carruseles sin teclado en 9 de 30 pantallas

**Severidad:** 2 (Menor) · **Confianza:** alta

**Hallazgo.** axe-core (WCAG 2.2 AA) encuentra dos reglas graves: contraste insuficiente en 7 pantallas («No permitir» y «Cancelar» en #007aff, 3.4–3.5:1; «Reenviar código en N seg.», 2:1; «Selecciona una opción» vacío, 1.5:1) y carruseles que no se desplazan con teclado (bienvenida y cierre). 4 objetivos táctiles miden menos de 24 px; el foco es visible en 128 de 129 elementos y el reflujo a 320 px funciona en todas.

**Interpretación.** El texto de las opciones que protegen al usuario (negar un permiso) es el menos legible. Es corregible con tokens de color.

**Recomendación.** Llevar los botones secundarios y textos de ayuda a 4.5:1; hacer enfocables los carruseles; revisar los 4 objetivos chicos. **Oportunidad:** Mejorar.

**Evidencia.** datos/tecnico.json (arnes tecnico) · pestaña Calidad técnica.

## Lo que funciona

- El código de verificación llega con autollenado y se valida solo: 7 de 7 sesiones que llegan lo resuelven en un paso. En el prototipo era el punto donde todos esperaban sin saber qué tocar.
- El primer toque es el esperado en 30 de 32 sesiones: «Inicia tu solicitud», «Tomar foto», el primer apellido y «Continuar» se encuentran sin dudar.
- La retoma funciona: al salir y volver a entrar a mitad de T3, la app conserva el avance en 8 de 8 sesiones («Qué bueno que no perdí lo que llené»).
- Rendimiento de laboratorio en rango bueno: LCP 2.4 s y CLS 0 con red móvil lenta, 667 KB, sin errores de JavaScript; funciona sin conexión y es instalable.
- «Verificar domicilio» tiene la confianza más alta del flujo (72): anuncia la etapa y lo que viene.
- La introducción a la selfie explica para qué es la foto y la confianza se sostiene en sus permisos (64 de media).

## Limitaciones

- 32 sesiones sintéticas (4 perfiles × 4 tareas × 2 corridas), no personas. 4 de 16 perfil-tareas cambian de resultado entre corridas: se reporta lo que se repite.
- Las tareas 2–4 empiezan a mitad del flujo, llevadas por la ruta mecánica (52 semanas, $22,000 en efectivo): el perfil no eligió esas condiciones. Itzel lo señala en T4 («no pude escoger monto ni plazo»).
- MVP sin reglas de negocio: servicios simulados y escenario feliz (OTP correcto, selfie e INE válidas, evaluación aprobada). Las ramas de error no se recorrieron.
- Cámara y ubicación simuladas: la app dice «No encontramos una cámara»; 8 de 8 sesiones de T2 lo notan y siguen porque se les avisó. Esa leyenda no existe en producción.
- Celular emulado (Pixel 7) y esperas aceleradas ×10; el rendimiento es de laboratorio.
- Los datos de prueba no traían estado civil ni ocupación hasta que T3-arturo abandonó por eso (historial); 3 sesiones de T3 corrieron sin esos datos y eligieron una opción por su cuenta.

## Para validar con personas

- Si mostrar el total a pagar y el número de pagos en el simulador y en el contrato cambia la elección de plazo y la disposición a aceptar: Efecto del total en la decisión y en la confianza (A/B Testing · prioridad alta · H1)
- Cómo reaccionan las personas a los permisos de Incode (dominio externo, tercera ubicación) y si anunciar al proveedor reduce las negativas: Tasa de negativa y comprensión del proveedor (Prueba de usabilidad · prioridad alta · H2)
- Si una casilla explícita de buró con el documento real cambia la comprensión de lo que se autoriza: Comprensión del consentimiento (Prueba de usabilidad · prioridad alta · H3)
- Si anunciar la visita a domicilio desde el inicio cambia la intención de terminar: Expectativa de «todo desde el celular» (Prueba de usabilidad · prioridad media · H4)

Para validar estos hallazgos con personas en una prueba de usabilidad, UiX recomienda 8–10 personas: los patrones de experiencia aparecen desde 8. Las corridas sintéticas no cuentan para esa muestra.

## Próximos pasos

- Mostrar el total a pagar en el simulador y en el contrato, y repetir esta medición (tercera del benchmark).
- Unificar los permisos de ubicación y anunciar al proveedor de verificación.
- Revisión manual de accesibilidad con TalkBack en permisos y formularios.
- Recorrer las ramas de error del MVP (OTP incorrecto, selfie no reconocida, INE vencida, rechazo) con los escenarios por URL.

## Trazabilidad

- Carpeta: `/Users/alexisvaldez/Documents/claude/harness-usuarios-sinteticos/estudios/2026-10-28-ou2-pwa-mvp`
- Consumo: 43 llamadas · 36.5 M tokens · 3.3 M nuevos (el resto es relectura de caché)
- Fuentes:
  - PWA Solicitud Única · Línea Amarilla — https://pwa.productdesign.mx/app/
  - Documentación del flujo (Línea Amarilla) — https://pwa.productdesign.mx/
  - Primera medición (prototipo de Figma) — estudios/2026-10-22-ou2-descubrimiento
  - Auditoría técnica — datos/tecnico.json
  - Auditoría experta — datos/auditoria.json
