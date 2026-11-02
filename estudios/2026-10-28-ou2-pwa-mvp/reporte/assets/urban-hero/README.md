# Panorama urbano del hero

Integración del MP4 proporcionado por el usuario el 30 de octubre de 2026. Reemplaza la escena SVG de Jardín de experiencias. La ciudad es una ilustración conceptual; las personas no representan participantes, tamaño de muestra ni observaciones del estudio.

## Recursos y edición

- `panorama.mp4`: copia binaria exacta del archivo `/Users/alexisvaldez/Documents/Codex/2026-10-29/3d-pixar-style-aerial-view-of-6/outputs/hero-urbano-personas-caminando.mp4`. H.264, 1920 × 1080, 24 fps, 8 segundos, 1 574 472 bytes, sin pista de audio.
- `poster.jpg`: fotograma del segundo 2, extraído con FFmpeg. Se usa al cargar, como alternativa estática y en impresión.
- `hero.css`: estilos aislados bajo `.microcosmos-hero`. Portada panorámica a todo el ancho en escritorio, con titular centrado y transición tonal marfil → ciudad → verde. El video usa un recorte de encaje en escritorio, conservando el centro de la calle; en móvil aparece debajo del texto con formato 16:9 completo. Sin zoom ni desplazamiento añadido. Saturación .68, contraste .95 y brillo 1.025 mediante filtros reversibles. Una franja verde explica tres métricas con enlaces al estudio.
- `video.js`: reproducción silenciosa y en bucle mediante el elemento video nativo; control por teclado, pausa fuera de pantalla, documento oculto e impresión. Conserva la pausa manual. Movimiento reducido inicia con póster y permite reproducción voluntaria; una promesa de reproducción rechazada conserva el póster y permite reintentar mediante el botón.

La reproducción automática se solicita desde el controlador después de consultar la preferencia de movimiento y la visibilidad. El atributo original `autoplay` se desactiva antes de adjuntar el recurso para evitar un arranque accidental con movimiento reducido. Sin JavaScript se mantiene el póster y no se presenta un botón inoperante.

El HTML editable sigue siendo `../../fuente-editorial.html`; copiar sus cambios al HTML principal. Ambos son idénticos. Se conservaron el título, identificación sintética y todo el contenido de main y nav. La introducción destaca la pregunta del costo total, sustentada en H1 de narrativa.yaml. El enlace principal dice «Descubrir qué frena la decisión» y apunta a `#hallazgos`. Las tres métricas enlazan al recorrido y a la decisión financiera. Una nota aclara que son corridas sintéticas en tramos separados, no conversión de clientes.

## Actualización: apertura con métricas

Por solicitud del usuario se dio mayor presencia a la escena y se incorporaron tres señales:

- 28/32 corridas completan su tramo: ver `datos/agregado.json → metricas.sesiones[].completa`.
- 8/8 buscan el costo total en el simulador sin encontrarlo: ver `narrativa.yaml → hallazgos → H1`.
- 2/8 abandonan en el contrato: las corridas T4-itzel-1 y T4-itzel-2, explícitamente identificadas como el mismo perfil.

Evidencia actual en `../../verificacion-hero-metricas/`. Se probaron seis tamaños, dos vueltas del video, control por teclado, enlaces de métricas, movimiento reducido e inicio voluntario, impresión, pausa fuera de pantalla y recuperación de autoplay bloqueado simulado. Se verificaron la conservación de main y la igualdad entre fuente y HTML entregable. Tras un ajuste final de espaciado y legibilidad, se recapturaron los seis tamaños completos y la grabación.

Respaldo previo a este cambio: `../../respaldos/antes-hero-metricas/` (fuente HTML y CSS). Para restaurar, copiar la fuente tanto al HTML editable como al entregable, y restaurar hero.css.

## Validación de la integración inicial

Ver `../../verificacion-video-urbano/`: capturas 1440, 1280, 1024, 768, 390 y 360 px; grabación `hero-integrado.mp4`; datos en `resultados.json`.

- Archivo local sin servidor; sin errores JavaScript ni desbordamiento horizontal. Separación entre texto y escena y relación 16:9 comprobadas en seis tamaños.
- Se reprodujeron más de dos ciclos y se detectaron dos reinicios. Fotogramas alrededor de los cierres revisados: se mantiene la disolución del recurso; no se añadió transición ni se modificó su ritmo. La disolución es perceptible, no se afirma una continuidad de posiciones perfecta.
- Pausa y reanudación por control; activación con teclado; pausa automática fuera de pantalla; pausa manual conservada al volver.
- Movimiento reducido: póster inicial y reproducción voluntaria comprobados. Impresión: video oculto, póster visible y reproducción detenida.
- Se simularon documento oculto mediante `visibilitychange` y rechazo de `play()` con `NotAllowedError`, verificando pausa y recuperación. No se afirma una prueba física de cambio de pestaña ni de todas las políticas de navegadores móviles.
- No se carga ningún script de `microcosmos-hero`, no hay figuras SVG ni animaciones WAAPI activas en el hero.
- Comparación exacta de main y nav con el respaldo; fuente y entregable idénticos. SHA-256 del MP4 coincide con el original. Sintaxis JS comprobada con `node --check`.

## Recuperación

`../../respaldos/antes-video-urbano/` contiene `reporte.html`, `fuente-editorial.html` y una copia de `microcosmos-hero/`. Para volver al jardín, restaurar ambos HTML y los recursos anteriores en `assets/microcosmos-hero/`. Los recursos antiguos también se conservaron en su ubicación original, pero ya no se cargan.
