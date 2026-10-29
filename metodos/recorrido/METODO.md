# Método 3 · Recorrido de un flujo interactivo

Para preguntas del tipo **«¿pueden completar el flujo?, ¿dónde se traban, dudan o abandonan?»** sobre un
prototipo de Figma o un sitio real (dev/staging). Destilado de «OU-PWA-usuario-sintetic-reporte-usabilidad»
(prompts maestros de prototipo y de dev), «Investigación-funcionalidad de entrecalles» y el skill
`auditoria-prototipos-figma`.

## Antes de tocar nada: el pre-flight

No arranca sin esta tabla, y se reporta tal cual en el protocolo:

| Recurso | Acceso | Estado | Observación |
|---|---|---|---|
| URL del material | abre sin sesión / requiere login / VPN | | |
| Dispositivo | preset de «Prototype settings» (Figma) o viewport | | |
| Versión fijada | fecha, hora, `node-id` de inicio; nadie editando | | |
| Biblioteca y panel | `arnes panel <estudio>` | | |
| Protocolo | tareas, criterio de fin, métricas | | |
| Datos de prueba | ficticios, en `estudio.yaml` | | |

- **Antes del pre-flight**: el link debe estar compartido sin restricciones («Anyone with the link · can view» en
  Figma) y abrir en una ventana de incógnito. El arnés navega como incógnito: sin tu sesión.
- **Si no carga** (certificado, DNS, VPN, IP allow-list): detenerse y reportar el error exacto.
- **Si pide credenciales**: preguntar. Nunca inventarlas ni adivinarlas.
- **Figma privado**: `state-save`/`state-load` del CLI de Playwright desde un navegador con sesión.

### Zonas tocables en Figma

Figma resalta en azul lo tocable cuando se toca algo que no lo es (*hotspot hints*). El arnés toca el fondo del
lienzo, fuera del dispositivo, compara la captura previa con la de los resaltados y saca las zonas. Dos cuidados,
aprendidos en el primer prototipo real (OU 2.0, 22/10/2026):
- **Prototipos táctiles:** el cursor de «dedo» aparece en todo el lienzo, así que el barrido de cursor (el método
  anterior) no distingue botones. Queda solo como respaldo.
- **Overlays** (hojas inferiores, modales): tocar fuera los cierra. Si el arnés detecta un velo que oscurece la
  pantalla anterior, toca dentro del overlay, en su franja superior (la manija), y comprueba que la pantalla no
  cambió (`pistas_alteraron` en el paso).
- **El perfil ve solo el teléfono.** La captura se recorta al dispositivo (como lo vería en su celular); la burbuja
  con su pensamiento queda fija a la izquierda, fuera del teléfono, para quien observa la ventana o el video. Antes
  la burbuja se ocultaba y se mostraba en cada sondeo y la ventana parpadeaba.
- **Un toque que no cambia el teléfono se repite una vez** (0.8 s después) y queda como `reintento` en el paso: en
  Figma un hotspot a veces no responde al primer toque por una transición en curso. [SUPUESTO METODOLÓGICO] Si
  tampoco responde la segunda vez, cuenta como «sin respuesta».
- El banner de cookies es HTML: se descarta con `{tipo: tocar_texto, texto: "No permitir cookies"}` en
  `preparacion`.

### Productos web y PWA (primera vez: OU 2.0 MVP, 28/10/2026)

- **Celular emulado:** `dispositivo: {emular: "Pixel 7"}` da viewport, toque, densidad y agente de usuario de Android.
  Los toques son toques (`touchscreen.tap`), no clics de escritorio.
- **Pantalla:** en una app de una sola página la URL no cambia. `pantalla: {selector: ".marco", atributo: "data-estado"}`
  dice dónde declara la app su estado; con eso se miden embudo, fin (`fin: {pantallas: [...]}`) y retoma.
- **Asentar sin parpadeo:** en web el arnés no compara capturas cada 300 ms: compara una firma de la página (pantalla,
  texto sin cifras, valores de los campos, número de elementos) y espera a que no haya `aria-busy` ni animaciones
  finitas en curso. Un spinner (animación infinita) no la detiene: es la espera, que se mide aparte.
- **Ruta mecánica** (`ruta_mecanica` en `estudio.yaml`): las acciones de quien ya conoce el camino, por rol y texto
  (`{nombre: "Continuar"}`, `{rol: radio, nombre: "No", exacto: true}`, `{etiqueta: "Calle", llenar: "…"}`,
  `{selector: "…", teclear_patron: "…([0-9]{6})"}` para un código que la app muestra). La usan `arnes tecnico` y la
  preparación de las tareas que no empiezan al inicio (`inicia_en: <pantalla>`): el arnés lleva la app hasta ahí y
  no cuenta esos pasos en la tarea. Si no llega, se detiene antes de llamar al modelo.
- **Cada sesión sin datos guardados** (`limpiar_datos: true`): borra almacenamiento local e IndexedDB, como alguien
  que nunca abrió la app.
- **Lo que ve el perfil en web:** además de la captura, la lista de elementos con su rol y estado (seleccionado,
  desactivado, lo que dice un campo, el rango de un deslizador). «Escribir» reemplaza el contenido del campo; en un
  deslizador, escribir un valor toca el punto de la barra que le corresponde. [SUPUESTO METODOLÓGICO]

### Ver la sesión en vivo

- **Ventana del navegador:** el producto en el celular emulado, con **subtítulos** arriba (quién es, qué piensa, qué
  hace, confianza y fricción) y un **círculo** donde cae cada toque. Viven en una sombra cerrada: el perfil no los ve
  (las capturas los ocultan) y no alteran el texto, las zonas ni la accesibilidad medida.
- **Sala de observación** (`arnes/observacion.py`): con `visible: true` el arnés abre una página local
  (`http://127.0.0.1:…`) que se actualiza cada segundo: la pantalla que ve el perfil con su toque, su pensamiento,
  intención y acción, la respuesta de la app, la espera, confianza y fricción por paso, los tokens de la sesión
  contra lo estimado y las sesiones ya terminadas. No sale de la máquina.
- **Video por capítulos:** `datos/videos/<sesión>.webm`, un capítulo por paso.

## Auditoría técnica (`arnes tecnico`, 0 tokens)

Recorre la ruta mecánica en el celular emulado y mide, por pantalla: WCAG 2.0/2.1/2.2 A y AA con axe-core (en español;
`arnes/vendor/axe`), objetivos < 24 y < 44 px, foco visible con Tab, reflujo a 320 px, campos (etiqueta,
autocompletado, teclado), tamaño mínimo de texto, legibilidad INFLESZ y errores de consola y red. Una vez por
estudio: carga en frío y con caché en red móvil lenta y CPU 4× (TTFB, FCP, LCP, CLS, TBT, peso), respuesta a toques
(INP aproximado), PWA (manifiesto, íconos, service worker, sin conexión) y retoma en `tecnico.retoma_en`. Resultado en
`datos/tecnico.json`; el tablero lo muestra en «Calidad técnica» y `arnes estilo` revisa también esos textos.
axe encuentra una parte de los problemas: lo demás exige revisión manual.

## Cómo corre una sesión (modo autónomo)

```
por cada paso:
  arnés    → captura la pantalla y mapea lo que responde (Figma: resaltados de hotspots · web: DOM)
  arnés    → dibuja números sobre cada zona activa
  perfil   → mira la captura limpia, dice qué ve, qué cree, qué quiere hacer y elige un número
  arnés    → ejecuta el toque, espera a que la pantalla se asiente, le dice al perfil qué pasó
  fin      → llegó a la pantalla de fin · el perfil abandona o cree que terminó · atascado · máximo de pasos
```

- Cada paso **reanuda la sesión del mismo perfil**: recuerda su propio recorrido, nunca el de otros.
- **La ruta y los toques son reales**; pensamiento, decisiones, confianza y fricción son **[SIMULACIÓN]**.
- El perfil ve las zonas numeradas; un usuario real no las ve. Es una ayuda del instrumento
  **[SUPUESTO METODOLÓGICO]**, por eso declara su intención antes de elegir y puede responder «lo que quiero
  tocar no está marcado» (marca 0).
- `--guion` reproduce pasos escritos a mano (como entrecalles): sirve para un video demostrativo o para
  repetir una ruta exacta.

## Clasificar antes de puntuar (skill de auditoría)

| | Categoría | Qué es | ¿Severidad? |
|---|---|---|---|
| **A** | Hallazgo de diseño | Contenido, arquitectura del flujo, orden, ausencias | Sí |
| **C** | Defecto de cableado | Hay conexión, pero el destino contradice lo elegido | Sí, con nota de verificación |
| **B** | Estado de prototipado | Elemento sin conexión; fin del prototipo | **No.** Va en `estado_prototipado` |
| **D** | En duda | Pudo causarlo el método | **No**, hasta resolverlo |

Un toque sin respuesta en Figma **no declara un marco terminal ni un defecto**: puede ser estado de
prototipado. Antes de escribir «el prototipo termina en X», agotar: reesperar, desplazar la coordenada,
scroll, flecha derecha, mirar el video.

Cada hallazgo A o C lleva heurística de Nielsen, criterio WCAG 2.2 (por número: «1.4.3 Contraste mínimo»),
o ambos. Severidad Nielsen 0–4.

## Lo aprendido en las corridas anteriores

1. **No detenerse en la primera pantalla bloqueada.** En OU-PWA la primera corrida declaró «no se pudo
   evaluar» en la Tarea 1; la segunda, por otra vía, llegó al final.
2. **Seguir hasta el final real del proceso**, no hasta donde «se sintió terminado».
3. **Vigilar integraciones de terceros**: cambios de dominio, permisos del navegador (cámara, ubicación),
   pasos que exigen algo fuera de la pantalla. En OU-PWA el escaneo de identidad saltaba sin aviso a un
   dominio externo: hallazgo de confianza.
4. **Datos de prueba, nunca reales.**
5. **No cambiar el tamaño de ventana en Figma**: el encuadre es parte del prototipo; cambiarlo produce
   hallazgos falsos de «queda cortado».
6. **Descartar el banner de cookies antes de medir** (`preparacion` en `estudio.yaml`): desplaza el marco del
   dispositivo y hace que todos los toques caigan fuera.

## Análisis y reporte

- `arnes analizar`: resultados por tarea, embudo por pantalla, momentos candidatos (caída de confianza ≥ 15 o
  fricción ≥ 3), toques reales sobre cada pantalla, `pasos.csv` y `resumen-sesiones.csv`.
- El investigador revisa capturas y pensamientos y escribe en `narrativa.yaml`: hallazgos (con `sesiones`
  afectadas → frecuencia), momentos de verdad (🟢 verde · 🟡 amarillo · 🔴 rojo), positivos, estado de
  prototipado.
- `Prioridad = Frecuencia (1–5) × Severidad (1–4) × Impacto de negocio (1–5)`. Crítico ≥ 48 · Alto ≥ 24 ·
  Medio ≥ 10 · Bajo.
- Patrones: nunca llamar patrón a lo que mostró un solo perfil. «En esta simulación, los perfiles con N alto
  mostraron…», nunca «los N alto hacen…».
- El embudo coloreado por severidad lleva **en el propio gráfico** el aviso de que no es comportamiento medido.

## Firmeza, accesibilidad y primer toque (del vault)

- `corridas: 2` por perfil y tarea: reportar solo lo que se repite.
- `primer_toque` por tarea (first-click testing): acertar el primer clic se asocia con 87% de tareas completadas
  contra 46% si falla.
- WCAG 2.2 · 2.5.8 se mide sobre las zonas activas (24×24 px CSS o espaciado). En Figma es aproximado (rejilla de
  12 px); las excepciones (enlace dentro de un texto, control esencial) se revisan a mano.
- `arnes auditar`: 3 evaluaciones heurísticas independientes (Nielsen) sobre la primera captura de cada pantalla.
- En `narrativa.yaml`, `walkthrough: 1–4` ubica cada fricción en una de las 4 preguntas del cognitive walkthrough.

## Métricas de flujo

`arnes analizar` calcula, por sesión y por tarea, lo que producto pide siempre. Cada cifra dice de dónde sale:

| Métrica | Cómo se obtiene | Origen |
|---|---|---|
| Pasos, pantallas, clics | ruta real: decisiones, pantallas distintas, toques (con y sin respuesta) | EVIDENCIA |
| Campos solicitados | campos visibles del DOM en web; `pantallas_info` en Figma | EVIDENCIA |
| Tiempo | lectura + decisión (KLM, 1.35 s) + toque + tecleo, más la espera real del sistema (sondeo de 300 ms); solo sesiones que completan | MODELO + EVIDENCIA |
| Validaciones | mensajes de validación que aparecen tras una acción (`aria-invalid`, `role=alert`, clases de error); pantallas de verificación por texto (código, INE, selfie, firma) | EVIDENCIA + INFERENCIA |
| Cambios de canal | cambio de dominio, pestañas nuevas, permisos del navegador (cámara, ubicación, notificaciones); menciones a sucursal, llamada, WhatsApp, app | EVIDENCIA + INFERENCIA |
| Retoma de solicitud | `retoma` en la tarea: sale tras el paso N y vuelve a entrar; conserva el avance, ofrece retomar, vuelve al inicio u otra pantalla | EVIDENCIA |
| Visibilidad de estatus | pantallas con «Paso N de M» o barra de progreso; el perfil dice si sabe dónde va | EVIDENCIA + SIMULACIÓN |
| Distancia a la compra | pasos, clics, campos y tiempo que faltan desde cada pantalla hasta el fin | EVIDENCIA + MODELO |
| Esfuerzo percibido (CES 1–7) | pregunta al perfil al cerrar la tarea; siempre junto a la tasa de éxito | SIMULACIÓN |
| Completitud y semáforo de UiX | sesiones que llegan al fin (éxito con o sin fricción) con intervalo de Wilson; color de la guía de completitud de UiX (verde ≥ 90 · amarillo 78–89 · naranja 50–77 · rojo < 50). Si el intervalo cruza colores, el reporte dice «sin color firme» | EVIDENCIA + INFERENCIA |

El semáforo de UiX viene de estudios con personas (promedio de referencia 78%, MeasuringU). En un recorrido sintético
sirve para ver dónde mirar, no como tasa de éxito: «2 de 2 sesiones» no es «100% de los usuarios». Para validar con
personas, la guía «Research en tus proyectos» de UiX recomienda 8–10 participantes en una prueba de usabilidad; el
reporte lo dice en «Para validar con personas».

En sitios que navegan por `#hash`, la URL puede no cambiar cuando cambia la pantalla: la retoma se juzga por el
texto visible. En `narrativa.yaml`, un KPI con `verificar: "metrica|T1|clics"` hace que `arnes verificar` recuente la
mediana.
