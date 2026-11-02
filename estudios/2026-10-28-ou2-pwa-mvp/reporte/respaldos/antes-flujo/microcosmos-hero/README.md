# Jardín de experiencias

Portada editorial decorativa del reporte OU2 PWA. Figuras originales pequeñas, terreno salvia, tramas quietas y cinco historias con descansos largos. Las figuras y sus acciones no representan participantes, métricas ni comportamiento observado del estudio.

## Fuentes y edición

- `../../fuente-editorial.html`: fuente editable del documento editorial. El entregable HTML principal es su copia.
- `composition.js`: posiciones de escritorio y móvil, familias, colores de prendas, recorridos y horarios. Veinte figuras en escritorio y seis en móvil, en ocho familias de siluetas.
- `art.js`: ilustración SVG separable: personas, vegetación, terreno, mobiliario y tres patrones. Las figuras tienen aproximadamente 28–48 px en escritorio y 24–36 px en móvil.
- `hero.css`: estilos aislados bajo `.microcosmos-hero`, proporción de escritorio 43/57 y recomposición móvil con escena de 210 px.
- `scene.js`: secuencia determinista de 48 s mediante Web Animations API. Sin parallax, eventos del cursor ni bucle JavaScript por fotograma. Los recorridos cortos vuelven caminando; no reinician en otro punto.

El `presentacion.html_local` de `../../../narrativa.yaml` hace que `arnes reporte` conserve esta presentación. Los documentos de detalle y Markdown siguen generándose desde los datos del estudio. La presentación es una edición revisada, no interpolación automática: si cambian los datos del estudio, revisar su contenido antes de regenerar. Después de editar la fuente, copiarla al HTML entregable del mismo directorio.

## Movimiento y accesibilidad

Consulta, pantalla compartida, recorrido breve, pausa sentada y encuentro se escalonan en un ciclo completo. La mayor parte de la escena permanece quieta. Una sola copa de árbol se mueve ocasionalmente.

El control visible pausa toda la escena y conserva esa elección al salir del hero y volver. La ilustración es decorativa, tiene `aria-hidden` y no recibe foco. Con reducción de movimiento se cancelan todas las animaciones y queda la composición estática. La actividad se pausa si el hero sale de pantalla o la pestaña queda oculta. Los archivos son locales y funcionan abriendo el reporte sin conexión.

## Verificación realizada

- Chrome, archivo local: 1440×900, 1280×800, 390×844 y 360×800. Capturas estáticas guardadas en `../../verificacion-jardin/`.
- Observación grabada de 52 segundos, incluyendo un ciclo completo y el reinicio. Máximo registrado: dos figuras cambiando de postura o posición a la vez. Se corrigió después la orientación de la pareja y del encuentro; se revisaron esos momentos y se grabó la versión final.
- Pausa y reanudación, teclado, pausa fuera de pantalla, conservación de pausa manual, reducción de movimiento y navegación del hero comprobadas. El carrusel de citas y los desplegables existentes también se comprobaron.
- Contenido de `<main>` y navegación comparados con el respaldo: idénticos. La selección de fuente al regenerar y la salida de `construir()` tienen pruebas automatizadas.
- Suite del repositorio: 34 pruebas pasan. Guardia del repositorio y comprobación de sintaxis de los tres scripts pasan.
- `resultados.json` conserva las medidas y resultados del navegador. `jardin-de-experiencias.mp4` es una grabación breve del navegador, no el recurso usado para animar el hero.

No se ha medido rendimiento en teléfonos físicos ni se realizó una auditoría completa con lector de pantalla. La pausa por pestaña oculta se implementó con `visibilitychange`; se verificó de forma directa la pausa por salida del hero.

## Recuperar el estado anterior

El respaldo está en `../../respaldos/antes-jardin/`: `reporte.html`, los cuatro archivos del hero anterior, una captura de escritorio y `sha256.json`. Para recuperar ese estado, restaurar el HTML principal y `assets/people-hero/` desde allí; restaurar también `fuente-editorial.html` para que una regeneración conserve esa elección.

## Integración en el repositorio

También se modificaron `arnes/reporte/__init__.py` (selección optativa de fuente editorial), `estudios/2026-10-28-ou2-pwa-mvp/narrativa.yaml` (ruta de esa fuente), el HTML entregable y `docs/BITACORA.md`. Se añadió `tests/test_presentacion_editorial.py` para comprobar selección, límites de ruta y conservación de la edición al construir el reporte. No se ejecutó una regeneración del estudio real que sobrescribiera sus entregables de detalle o Markdown; la integración se comprobó con pruebas automatizadas y con la fuente configurada del estudio.
