# Evidencias y revisión UX del reporte · 31 octubre 2026

## Alcance

Revisión del código, estructura editorial, registros y medios existentes. No es una auditoría visual completa: el navegador integrado rechazó el protocolo local `file://`. No se intentó un acceso alternativo para eludir esa restricción. Quedan pendientes la inspección visual a tamaños de escritorio/móvil y la prueba de teclado y reproducción en el navegador del usuario.

El hero aprobado se conserva. No se ejecutaron sesiones de investigación nuevas, no se modificó el instrumento y no se generaron capturas o videos sintéticos adicionales.

## Problemas atendidos con criterios UX

| Problema del reporte | Criterio | Cambio aplicado |
| --- | --- | --- |
| Las conclusiones exigían buscar archivos para contrastarlas | Reconocimiento antes que recuerdo | Cuatro casos con capturas visibles y enlaces desde cada hallazgo |
| Videos y mapas existentes eran difíciles de descubrir | Jerarquía y navegación | Biblioteca propia, acceso persistente, tres vistas, búsqueda y filtro por tramo |
| Una marca verde podía confundirse con éxito | Correspondencia y prevención de interpretaciones erróneas | Leyenda, conteos, base por sesiones y tabla de acciones; verde significa respuesta visible |
| Se mezclaban evidencia e interpretación | Claridad editorial y trazabilidad | Pantalla observada, pensamiento sintético, lectura UX y evaluación asistida por IA diferenciados |
| El lector podía perder contexto o dejar un video activo | Control y libertad | Lectura lateral con historial y regreso; reproducción manual y pausa al cerrar, cambiar lectura o filtro |
| El contenido multimedia podía ser la única vía para comprender el caso | Alternativas textuales | Descripción de la captura, pensamientos por paso, registros escritos y enlace al archivo original |

Estos criterios son una revisión editorial del reporte. La evaluación heurística histórica del MVP sigue disponible como fuente independiente, identificada explícitamente como tres evaluaciones realizadas por modelos de IA. No se afirma que sean tres especialistas humanos.

## Inventario integrado

- 4 casos: contrato/costo, permiso de ubicación, fachada y buró.
- 32 grabaciones principales, exactamente las vinculadas por los 32 JSON de sesiones. Hay 16 archivos de video auxiliares en la carpeta original que no se han atribuido a pasos ni incorporado como sesiones adicionales.
- 30 mapas originales con acciones verificadas contra cada registro. Incluyen tocar y escribir, repeticiones y estados distintos sobre la primera captura disponible. No son mapas de mirada ni densidad continua.
- 86 páginas de lectura locales en total.

## Comprobaciones realizadas

- Fuentes de los cuatro casos contrastadas con sesión, pantalla, número de paso, captura y pensamiento.
- Metadatos de los 32 videos verificados con ffprobe: VP8, sin pista de audio. Un fotograma de la grabación T4-itzel-1 fue inspeccionado; muestra el MVP y el rótulo de simulación. No se revisaron los 32 videos completos ni se afirma sincronía entre pasos y segundos.
- Conteos de acciones, sesiones aportantes y respuesta visible de los 30 mapas recalculados contra los registros originales.
- 130 referencias de medios/destinos y 575 enlaces o recursos HTML comprobados; fuente editorial y entrega idénticas.
- Sintaxis JavaScript comprobada. Ejecución con un DOM ligero de los cuatro casos, sus desplegables, los 30 mapas, las 32 grabaciones, búsqueda por perfil, filtro por tramo, estado vacío y pausa. Esta comprobación no sustituye la prueba en navegador ni verifica diseño visual.
- Tres pruebas de integración editorial existentes pasan.

Resultados resumidos en `resultados.json` y `interacciones.json`. Regenerar con `assets/report-reader/build_readers.py`; el constructor de evidencias usa los medios originales y guarda sus metadatos en `assets/evidence/media-metadata.json`.
