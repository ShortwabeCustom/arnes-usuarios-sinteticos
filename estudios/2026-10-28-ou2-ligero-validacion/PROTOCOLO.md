---
titulo: "Protocolo · oupwa-pdu-validacion-modo-ligero-sintetico_2026-10-28-v1"
fecha: "2026-10-28"
autor: "Alexis Valdez + Claude"
tipo: "Validación del instrumento (recorrido con usuarios sintéticos)"
estado: "Esperando aprobación del consumo"
---

# Protocolo · oupwa-pdu-validacion-modo-ligero-sintetico_2026-10-28-v1

## Brief (template de protocolo de UiX)

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | `oupwa-pdu-validacion-modo-ligero-sintetico_2026-10-28-v1` |
| **Cliente** | Arnés de usuarios sintéticos (uso interno de UX Research, Originación Única) |
| **Fecha de elaboración** | 28/10/2026 |
| **Versión** | v1 |
| **Brief** | La segunda medición de OU 2.0 consumió ≈ 37 M de tokens y varias horas. Casi todo fue relectura: en el modo completo cada paso vuelve a leer la sesión entera, así que el costo crece con el cuadrado de los pasos. El modo ligero hace una llamada nueva por paso con una bitácora corta y una sola captura. Antes de usarlo por defecto hay que comprobar que llega a los mismos resultados. |
| **Autorización** | Alexis Valdez |

- **Objetivo:** decidir si el modo ligero puede reemplazar al modo completo en los recorridos.
- **Muestra:** panel «base4» (4 perfiles) × T1 y T3 × 1 corrida = 8 sesiones. Se comparan con las 16 sesiones de T1 y T3 del modo completo (`estudios/2026-10-28-ou2-pwa-mvp`, 2 corridas).
- **Por qué T1 y T3:** T1 es la tarea corta (≈ 18 pasos) y T3 la más larga (≈ 28 pasos, con retoma a la mitad), donde la falta de memoria se notaría más.
- **Alcance:** Descriptiva. **Incentivos:** No aplica.
- **Metodología:** misma URL, panel, escenarios, instrucciones, datos de prueba y `ruta_mecanica` que el estudio base. Lo único que cambia es `memoria: bitacora` [SUPUESTO METODOLÓGICO].

## Criterios de decisión

Los de `estudio.yaml` (V1–V4). Si se sostienen V1–V3 y V4, el modo ligero pasa a ser el predeterminado de recorrido y
el modo completo queda para estudios donde la memoria visual del recorrido sea parte de la pregunta. Si cae V1 o V2,
se queda como opción para pilotos y ensayos.

## Límites

- 8 sesiones contra 16: sirve para ver diferencias grandes, no pequeñas. Una coincidencia no prueba equivalencia.
- El modo completo también varía entre sus 2 corridas: se compara contra ese rango, no contra una sola sesión.
- Los perfiles son sintéticos: lo que se valida es el instrumento, no el comportamiento de personas.
