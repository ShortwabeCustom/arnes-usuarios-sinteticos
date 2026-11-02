# Verificación de la portada

**Versión actual con flujo continuo:** capturas y resultados en [flujo/](flujo/). La grabación [jardin-en-movimiento.mp4](flujo/jardin-en-movimiento.mp4) muestra cinco caminatas simultáneas con ritmos distintos. Se revisaron cuatro tamaños, pausa por teclado, reanudación, conservación de pausa manual y movimiento reducido.

Los archivos descritos a continuación corresponden a la versión anterior del jardín, de actividad más espaciada.

Las capturas `1440-estatico.png`, `1280-estatico.png`, `390-estatico.png` y `360-estatico.png` corresponden a la versión final con reducción de movimiento. `pantalla-compartida.png`, `recorrido-breve.png` y `encuentro.png` muestran momentos del jardín a escala de escritorio.

`jardin-de-experiencias.mp4` es una grabación de Chrome mostrando la versión final en funcionamiento. El movimiento de la página se realiza con SVG y Web Animations API; el video es evidencia de revisión.

`resultados.json` contiene la verificación automatizada del navegador y el muestreo de un ciclo observado durante al menos 52 segundos. Después de esa corrida se corrigió la orientación de dos figuras y se despejó una planta del recorrido; las capturas finales y la grabación se actualizaron tras revisar esos cambios. Los archivos `escena-*s.png` documentan la observación anterior a esos ajustes menores.

Comprobado: pausa, reanudación, conservación de pausa al salir y volver, pausa fuera de pantalla, composición estática con movimiento reducido, teclado, ancla del hero, carrusel de citas y desplegables. Archivo local, sin servidor. No se probó con lector de pantalla ni dispositivos físicos. El manejador de pestaña oculta se implementó y revisó en código, sin afirmar una prueba directa del cambio de visibilidad de pestaña.

Fuentes y archivos modificados: [documentación del hero](../assets/microcosmos-hero/README.md).
