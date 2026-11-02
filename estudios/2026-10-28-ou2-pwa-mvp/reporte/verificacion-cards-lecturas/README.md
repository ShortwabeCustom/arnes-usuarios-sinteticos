# Verificación · 30 de octubre de 2026

## Comprobado en Chrome, archivos locales

- Cards en 1440, 390 y 360 px: 7/8, 8/8, 7/8, 6/8; 28 segmentos activos en total; sin desbordamiento del documento.
- 22 destinos distintos de los enlaces del reporte: apertura lateral y carga de contenido.
- 49 páginas independientes cargadas a 390 px, sin desbordamiento del documento.
- Navegación tramo → sesión → volver, ocho sesiones por tramo, cierre por Escape, botón y fondo; restauración del foco y de la posición del reporte.
- Movimiento desde `translateX(-102%)`; movimiento reducido sin animación. Foco confinado explícitamente al panel con Tab y Shift+Tab.
- Apertura en nueva pestaña mediante «Abrir como página» y captura original cargada al desplegar un paso de la sesión de Itzel.
- La primera batería terminó sin errores JavaScript. La batería ampliada completó las comprobaciones anteriores y se detuvo en la simulación de error de carga: Playwright no interceptó el recurso `file://` como se esperaba. La ruta de error con acceso al original está implementada, pero esa simulación no quedó verificada.
- Las tres pruebas de conservación de la presentación editorial pasan.

## Integridad comprobada desde archivos

- Fuentes y destinos locales existentes; cifras de cada tramo verificadas contra `agregado.json`.
- Fuente editorial y HTML entregable idénticos. Generador idempotente.
- Hero idéntico al respaldo excepto por destinos de enlaces, que ahora abren páginas de lectura.

## Evidencia

Capturas de cards, detalle de tramo, sesión y protocolo en esta carpeta. Las capturas de sesión preceden el ajuste de etiqueta «registros de paso» (para distinguir registros observados de la métrica de pasos). No se realizó una auditoría completa con lector de pantalla ni dispositivos físicos.
