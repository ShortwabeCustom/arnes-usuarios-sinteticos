# Lecturas legibles en toda la navegación · 31 octubre 2026

## Corrección

La salida detectada era el enlace «Abrir fuente original» del encabezado de las lecturas. Su atributo de apertura independiente evitaba deliberadamente el visor y abría archivos JSON/YAML/Markdown. Se retiró esa acción; «Abrir como página» conserva la lectura diseñada.

La resolución de rutas ahora se aplica al atributo `href` al crear los enlaces, también al cargar documentos HTML. Esto cubre clic normal, Ctrl/Cmd + clic y abrir en otra pestaña. Se corrigió además el destino del documento de primera medición y se eliminaron las salidas a archivos sin formato de los mensajes sin JavaScript. Los errores de carga ofrecen reintentar dentro de la lectura.

Los archivos de datos originales permanecen intactos. Una pestaña que ya estaba abierta directamente sobre un JSON seguirá mostrando ese archivo hasta que el usuario vuelva al reporte o a la ficha HTML; no se reemplazaron datos por páginas HTML ni se intervino el navegador.

## Vistas mejoradas

- Las 32 sesiones muestran ficha del perfil/tramo, resultado, video y recorrido por pasos. Se agregaron primera impresión, comprensión del avance y rótulo de acción; el detalle íntegro se conserva en campos y desplegables legibles.
- Síntesis: conclusión, métricas, hallazgos con observado/interpretación/recomendación y enlaces a las sesiones, positivos y límites.
- Evaluación heurística asistida por IA: conteos, buscador por pantalla/criterio/problema, severidad con escala, recomendaciones y aspectos positivos.
- Auditoría técnica: resumen, problemas de accesibilidad con pantallas afectadas, tabla de retoma, rendimiento y detalle progresivo.

## Verificación

- 90 HTML revisados (86 lecturas y cuatro entradas editoriales/anteriores), 723 recursos/enlaces locales, cero vínculos HTML a documentos JSON/YAML/Markdown.
- 48 rutas de documentos originales resueltas a páginas HTML, incluso con apertura independiente.
- Renderizado de 35 vistas estructuradas (32 sesiones y tres vistas de síntesis/auditoría) con los datos reales; sin texto `[object Object]` ni enlaces a archivos sin formato.
- Búsqueda heurística probada con resultados y sin coincidencias. Sintaxis JavaScript y tres pruebas de integración editorial correctas.
- Fuente editorial y entregable idénticos.
- Sin revisión visual nueva en navegador: se mantiene el bloqueo previo de archivos locales. Las verificaciones de lógica usan un DOM ligero, sin afirmar pruebas visuales o de navegación nativa.

Ejecutar desde el repositorio: `node estudios/2026-10-28-ou2-pwa-mvp/reporte/verificacion-lecturas/check.cjs` y `.venv/bin/python estudios/2026-10-28-ou2-pwa-mvp/reporte/verificacion-lecturas/check_links.py`.
