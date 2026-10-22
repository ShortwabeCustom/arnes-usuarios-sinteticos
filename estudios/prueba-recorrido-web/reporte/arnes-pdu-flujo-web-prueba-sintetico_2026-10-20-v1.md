# Al salir y volver, el flujo de prueba pierde el avance: los dos perfiles repiten sus datos

**Estudio:** Prueba del arnés · recorrido sobre flujo web local  ·  **Fecha:** 2026-10-20  ·  **Método:** recorrido
**Biblioteca:** pwa · panel base4-ocean (2 perfiles)
**Tipo de investigación:** simulación UX con usuarios sintéticos — no sustituye investigación con usuarios reales.

Estudio de humo del método de recorrido sobre un flujo web local de tres pasos. Sirve para comprobar que el arnés navega, registra toques reales, deja que cada perfil decida y mide las métricas de flujo. No evalúa un producto real.

## Resumen

- **2 de 2** sesiones completan con fricción — Bryan y Arturo llegan a «Solicitud enviada» tras repetir sus datos.
- **7** clics hasta terminar (mediana) — El camino directo son 4; la pérdida del avance agrega 3.
- **2** campos solicitados — Nombre y teléfono, escritos dos veces por la retoma.
- **4.5** esfuerzo percibido (CES 1–7, mediana) — Los dos lo explican por el avance perdido y la cuota que no ven.

- Al recargar después del paso 2, el flujo vuelve al inicio y borra lo escrito en las 2 de 2 sesiones. Los dos perfiles lo notan y repiten sus datos.
- La confianza de Arturo baja al volver a empezar («¿Otra vez desde el principio?… ya me da desconfianza») y su CES queda en 4 de 7.
- Las tres pantallas muestran «Paso N de 3»; los perfiles dicen saber dónde van en 9 de 14 pasos.
- La revisión menciona otro canal (llamada y sucursal) para dudas: no saca del flujo, pero es un punto de cambio de canal.

## Panel

| ID | Nombre | Segmento | O | C | E | A | N |
|---|---|---|---:|---:|---:|---:|---:|
| bryan | Bryan Nájera | Centennial · 43.9% | 72 | 68 | 74 | 65 | 62 |
| arturo | Arturo Belmont | Boomer · 5.4% | 42 | 79 | 38 | 68 | 67 |

**Datos demográficos (categorías de UiX, con su evidencia):**

| Perfil | Edad (generación) | Género | Región | Ocupación |
|---|---|---|---|---|
| Bryan Nájera | Centennials (Gen Z), 18-30 años (22 años) [OBSERVADO] | Hombre [OBSERVADO] | Centro (Ciudad de México) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |
| Arturo Belmont | Boomers, 61+ años (66 años) [OBSERVADO] | Hombre [OBSERVADO] | Sur (Veracruz) [HIPÓTESIS] | (Ninguna fuente del User Persona reporta ocupación) [AUSENTE] |

## Sesiones

| Sesión | Resultado | Pasos | Sin respuesta | Confianza | Fricción máx. |
|---|---|---:|---:|---|---:|
| T1-arturo | exito_con_friccion | 8 | 0 | 50 → 58 | 3 |
| T1-bryan | exito_con_friccion | 8 | 0 | 60 → 55 | 3 |

## Hallazgos

### H1 · Salir del proceso borra el avance y obliga a empezar de nuevo

**Severidad:** 3 (Importante) · **Confianza:** media

**Hallazgo.** Al recargar la página después de escribir el nombre, el flujo vuelve a la oferta inicial y los campos quedan vacíos (2 de 2 sesiones). Cada perfil escribe sus datos dos veces: 7 clics en lugar de 4.

**Interpretación.** El flujo no guarda el avance. En un trámite que se hace desde el celular, una interrupción es esperable; perder lo escrito convierte una pausa en un reinicio.

**Recomendación.** Guardar el avance por paso y, al volver, ofrecer «Continuar tu solicitud» con los datos ya escritos. **Oportunidad:** Hacer diferente.

**Evidencia.** Métrica de retoma (vuelve al inicio, 2 de 2); datos/capturas/T1-arturo/p03.png; CES 4 y 5 con la pérdida como razón.

### H2 · La revisión no muestra la cuota antes de autorizar la consulta de buró

**Severidad:** 3 (Importante) · **Confianza:** media

**Hallazgo.** Los dos perfiles llegan a la revisión sin ver el pago semanal ni el total, y lo mencionan en el cierre.

**Interpretación.** Pedir el permiso de consulta antes de mostrar el costo invierte el orden que un perfil cuidadoso espera.

**Recomendación.** Mostrar cuota semanal y total a pagar en la revisión, arriba de la autorización. **Oportunidad:** Incorporar.

**Evidencia.** datos/capturas/T1-arturo/p07.png · pensamiento del paso 7 y respuesta CES de las dos sesiones.

## Lo que funciona

- Los campos «Nombre completo» y «Teléfono celular» se entienden sin ayuda: los dos perfiles escriben el dato correcto.
- El indicador «Paso N de 3» está en todas las pantallas del proceso.

## Limitaciones

- Material de prueba local, no un producto.
- Dos perfiles y una corrida: no permite hablar de patrones.
- La espera del sistema de estas sesiones se midió con el método anterior (pausas de 1.2 s) y está inflada; el tiempo estimado también. El arnés ya mide con sondeo de 300 ms.

## Para validar con personas



Para validar estos hallazgos con personas en una prueba de usabilidad, UiX recomienda 8–10 personas: los patrones de experiencia aparecen desde 8. Las corridas sintéticas no cuentan para esa muestra.

## Próximos pasos

- Correr el método sobre el prototipo de Figma o el ambiente dev con el panel completo, con `retoma` en la tarea más larga.

## Trazabilidad

- Carpeta: `/Users/alexisvaldez/Documents/claude/harness-usuarios-sinteticos/estudios/prueba-recorrido-web`
- Llamadas registradas: 2 · costo US$ 1.79
- Fuentes:
  - Flujo web de prueba — tests/fixtures/flujo-web/index.html
  - User Persona OU-PWA — personas/pwa
