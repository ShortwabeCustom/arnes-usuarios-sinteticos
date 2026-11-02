# Cards del recorrido y biblioteca de lectura

Cuatro cards con cifras originales, acentos cromáticos, acceso al detalle y ocho segmentos que representan las corridas de cada tramo. No se presentan como embudo ni conversión de clientes.

## Lecturas

- Todos los enlaces de contenido del reporte tienen destinos HTML reales en `reporte/lecturas/`. Inicio y el salto accesible al contenido conservan su navegación local.
- Al hacer clic se abre un diálogo de lectura desde la izquierda. Ctrl/Cmd + clic y «Abrir como página» permiten abrir la página independiente.
- El panel conserva posición del reporte, historial de lecturas, cierre por botón, Escape y fondo, foco contenido y restauración del foco al origen. Respeta movimiento reducido.
- Fuentes JSON/YAML presentadas como campos y grupos desplegables; registros completos disponibles sin truncamiento. Sesiones con pensamientos sintéticos y capturas originales por paso. Tramos con sus ocho sesiones y resultados comprobados contra el agregado.
- Protocolo y primera medición se presentan como documentos legibles. Detalle y tablero anterior tienen una vista de lectura sin scripts ni gráficos interactivos; los enlaces permanecen dentro de las vistas de lectura.
- Los recursos se cargan al abrir cada lectura, mediante archivos locales. No necesitan servidor ni peticiones a terceros. Los archivos del estudio permanecen intactos.

## Actualizar

Después de editar las fuentes o `reporte/fuente-editorial.html`, ejecutar desde la raíz del repositorio:

```sh
.venv/bin/python estudios/2026-10-28-ou2-pwa-mvp/reporte/assets/report-reader/build_readers.py
```

Genera 86 páginas y sus datos, actualiza los destinos de enlaces y sincroniza `fuente-editorial.html` con el entregable. La presentación editorial sigue siendo una edición revisada: modificar datos requiere revisar sus afirmaciones y conteos.

Los datos se serializan con escape de HTML y se muestran como texto. La vista de documentos HTML usa una lista permitida de elementos y atributos, sin scripts, estilos, eventos ni URLs ejecutables.

## Verificación

Ver `../../verificacion-cards-lecturas/README.md`. Respaldo anterior en `../../respaldos/antes-cards-lecturas/`.

## Evidencias multimedia

La biblioteca integra cuatro casos, las grabaciones vinculadas a las 32 sesiones y 30 mapas de acciones. La construcción usa `../evidence/build_evidence.py`; presentación y controles en `../evidence/evidence.js` y `evidence.css`. Los mapas no representan mirada. Los videos se reproducen por decisión del lector y se pausan al cambiar o cerrar la lectura. Ver `../../verificacion-evidencias/README.md` para alcance y límites de verificación.

## Navegación sin archivos sin formato

Se eliminó «Abrir fuente original». Los destinos se normalizan a HTML al crear cada enlace, también para abrirlos en otra pestaña. La síntesis y las auditorías tienen vistas especializadas en `insights.js`; las sesiones incluyen primera impresión, comprensión del avance y acción. Los datos originales se conservan intactos. Ver `../../verificacion-lecturas/README.md` y sus comprobaciones reproducibles.
