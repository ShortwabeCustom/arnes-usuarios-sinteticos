# Bitácora del arnés

Para retomar el trabajo en otra conversación: qué se construyó, en qué orden, qué se decidió y por qué, y qué
quedó pendiente. Lo más reciente va arriba. Al terminar una sesión de trabajo, agregar una entrada.

---

## Estado al 28 de octubre de 2026

- **Funciona y está validado:** método `comprension` (réplica de recompra), método `recorrido` sobre un **prototipo de
  Figma real** (OU 2.0, 22/10/2026) y sobre una **PWA real** (OU 2.0 MVP, 28/10/2026: 32 sesiones, celular emulado),
  auditoría técnica sin tokens (`arnes tecnico`), auditoría experta con 3 evaluadores, guía de estilo de la PWA,
  conexión con el vault, tablero de investigación con «Calidad técnica».
- **Ver en vivo:** subtítulos y toque marcado en la ventana del celular + sala de observación local por perfil
  (`arnes/observacion.py`); varios perfiles pueden correr en paralelo (una sesión del navegador por perfil).
- **Sin probar:** el ambiente dev con VPN o login.
- **Repositorios** privados en GitHub: `ShortwabeCustom/arnes-usuarios-sinteticos` y `ShortwabeCustom/vault-equipo`
  (submódulo en `vault/`), rama `main`.
- **Pruebas:** `.venv/bin/python -m pytest tests -q` → 43 pasan (también en GitHub Actions).
- **Consumo** en tokens (`arnes estado <estudio>`). OU 2.0 prototipo ≈ 21 M; OU 2.0 MVP ≈ 37 M (≈ 3.7 M nuevos).

## Pendientes

0. Guardar tokens por modelo en cada llamada (Haiku aparece junto a Sonnet) y, después, evaluar `modelo: haiku` con su
   propia validación, como la del modo ligero.
1. ~~Segunda medición del benchmark~~ Hecha sobre la PWA MVP (28/10/2026). Siguiente: tercera medición cuando el MVP
   muestre el total a pagar y unifique los permisos de ubicación; recorrer también las ramas de error del MVP
   (escenarios por URL: `otp=incorrecto`, `selfie=noReconocida`, `ine=vencida`, `evaluacion=scoreGuardian`…).
2. Probar `recorrido` en el ambiente dev (`dev-bazsolicitudunica.com.mx`): pre-flight de acceso primero.
   Revisión manual de accesibilidad con TalkBack (axe cubre solo una parte).
3b. Tablero para estudios de comprensión (hoy solo recorrido).
3c. Pulir `arnes ensayar`: escribir los pasos mínimos en `pasos_esperados`, quitar el falso aviso de datos faltantes
    («Sí», «Viernes») y probar `--paralelo`. Prueba automática de la regla de recorte de zonas en `navegador.py`.
    Baja prioridad: el estimador del modo completo sobreestima (OU 2.0: 41 M estimados, 30.9 M reales).
3. Las sesiones de `estudios/prueba-recorrido-web` se corrieron antes de corregir la medición de la espera del sistema
   (pausas de 1.2 s); su tiempo estimado está inflado. Repetirlas si se quiere el ejemplo exacto (≈ 1 M de tokens).
4. La réplica de recompra corrió solo la corrida 1 (32 de 96 sesiones). Correr 2 y 3 para tener estabilidad entre
   corridas en el propio arnés (≈ 3 M de tokens).
5. Resolver con el equipo de UX writing las contradicciones internas de los manuales de la PWA (listadas en
   `fuentes-producto/pwa/reglas-estilo.yaml`, clave `contradicciones`).
6. Acordar con UiX un código de metodología para investigación sintética (hoy el arnés usa `pdu` o `abtesting` y
   agrega `-sintetico` al tema) y avisar las inconsistencias de sus guías (anotadas en `01-Fuentes/estandares-uix` del
   vault): el ejemplo del template no cumple el naming, la generación se define por rangos de edad que se moverán, las
   cifras de muestra de encuestas y A/B son cualitativas.
6b. Reporte editorial en comprensión: hoy solo recorrido usa el template (comprensión conserva su HTML autocontenido).
    Falta también publicarlo como Artifact: es multiarchivo y sus capturas y videos viven en `datos/`.
7. Ocupación AUSENTE en los 4 perfiles de la PWA: si alguna base la trae, agregarla a `personas/pwa/biblioteca.yaml`.
8. Si se agrega una biblioteca nueva de personas, seguir `metodos/persona/METODO.md` y correr `arnes persona probar`.

---

## Sesión del 2 de noviembre de 2026 (reporte editorial como template)

Alexis terminó a mano la edición de OU 2.0 PWA MVP (ver entradas del 29 al 31/10, más abajo) y pidió tomarla como template
para las siguientes investigaciones. Era un HTML escrito para ese estudio: cifras, citas y cuatro tramos fijos, con
constructores atados a sus rutas. Copiarlo habría heredado esas cifras, así que se convirtió en generador.

- `arnes/reporte/editorial.py` y `lecturas.py` (generalizan `build_readers.py` y `build_evidence.py`);
  `arnes/reporte/plantilla_editorial/assets/` (el diseño de Alexis, sin referencias a OU 2.0). Guía: `docs/REPORTE-EDITORIAL.md`.
- El texto va en `editorial.yaml` (`arnes nuevo` copia `metodos/recorrido/editorial.plantilla.yaml`); sin llenarlo, el reporte
  sale con textos automáticos. Ahora `<nombre>.html` es el editorial y el tablero pasa a `<nombre>-tablero.html`.
- **Decisión:** las cifras no se escriben a mano. Se calculan o se ligan a sesiones, y `arnes verificar` recuenta cifras, exige
  citas textuales, revisa casos y enlaces y avisa de números a mano y de hallazgos 3–4 fuera de los capítulos. Motivo: 435/439 y
  17–25 se corrigieron a mano en la edición; el generador da 462 de 466 y 12–26 sin intervención.
- Prueba de fondo: `estudios/2026-10-28-ou2-pwa-mvp/editorial.yaml` reproduce la edición (mismas 86 lecturas, altura 12,104 vs
  12,126 px). El estudio **sigue con su HTML revisado** (`presentacion.html_local`); el YAML es el ejemplo de referencia. También
  se generaron copias de `2026-10-22-ou2-descubrimiento` y `prueba-recorrido-web` sin `editorial.yaml`: LISTO, sin errores de
  consola ni desbordes a 1440 y 390 px. Esa prueba destapó «8/16» por una base mal tomada: sin tarea, la base son las tareas
  donde ocurre el hallazgo.
- `arnes verificar` marcaba 9 errores falsos sobre la edición de Alexis (buscaba `id="H1"` en la página principal); ahora revisa
  también las lecturas. OU 2.0 dice LISTO.
- Límite: el reporte ya no es un archivo autocontenido (necesita `assets/`, `lecturas/` y `datos/`). Solo cubre recorrido.
- Alexis pidió subir `reporte/respaldos/` y `reporte/verificacion-*` de OU 2.0. La guardia los bloqueaba por 11 falsas alarmas:
  decimales que pasan Luhn y nombres de video de Playwright (`page@<hash>.webm`). Se corrigieron ambos casos, con prueba.

## Sesión del 29 de octubre de 2026 (validación y cierre del modo ligero)

- **Validación** aprobada por Alexis (≈ 2.3 M estimados): 8 sesiones, T1 y T3, 4 perfiles en paralelo, 13 minutos.
  Consumo real 2.54 M contra ≈ 11.5 M del modo completo (4.5× menos). Resultados y criterios en
  `estudios/2026-10-28-ou2-ligero-validacion/RESULTADOS.md`. Con los criterios fijados antes no pasó completo (V1 5 de
  8, V4 en T1 28%), pero las diferencias están entre «éxito» y «éxito con fricción» y los hallazgos fuertes se
  repitieron con la misma causa. **Alexis decidió dejarlo como predeterminado.**
- `memoria` sin declarar = `bitacora` (`recorrido._memoria`); cada sesión guarda su `memoria`. Los tres estudios de
  recorrido anteriores declaran `memoria: completa` para repetirse igual.
- `consumo.LIGERO` recalibrado con las 8 sesiones (por paso: ≈ 4 mil de texto + la captura escritos; ≈ 5.5 mil + 195 por
  paso hecho releídos); queda dentro de ±12% por tipo de token. El faltante del estimado venía de los pasos: `--simular`
  ahora usa los mínimos del ensayo × 1.15 cuando superan a `pasos_esperados`.
- Observado: el estimador del modo completo sobreestima (panel de OU 2.0: 41 M estimados, 30.9 M reales). No se
  recalibró: ya no es el predeterminado.
- Pendiente acordado para después: guardar tokens por modelo (Claude Code lista Haiku junto a Sonnet en cada paso;
  hoy no se sabe cuánto pesa) y evaluar `modelo: haiku` como otro cambio de instrumento, con su propia validación.
- Hay trabajo de otra sesión sin commit (presentación editorial del reporte de OU 2.0: `_presentacion_editorial` en
  `arnes/reporte/__init__.py`, `tests/test_presentacion_editorial.py`, archivos en `reporte/`). No se tocó.

## Sesión del 28 de octubre de 2026, noche (investigaciones más baratas y rápidas)

Pedido de Alexis: «hacer más efectivo, viable y menos costoso este tipo de investigaciones, porque está gastando
tanto y tardando demasiado». Diagnóstico: de ≈ 37 M de tokens, el 91 % fue relectura de caché; en modo completo cada
paso relee la sesión entera y el costo crece con el cuadrado de los pasos (T3, 28–35 pasos: 1.5–3 M por sesión).
Además, 3 pilotos y varias sesiones se repitieron por problemas de ruta o de datos que no necesitaban al modelo.

Lo que se construyó:
- **Modo ligero** (`memoria: bitacora`): una llamada nueva por paso con escenario, tarea, datos, una bitácora corta
  de lo hecho (`_recuerdo`, `_linea`) y una sola captura (la numerada), enviada dentro del mensaje (`motor.Llamada.imagenes`,
  stream-json): el modelo ya no hace una vuelta extra para abrir el archivo. La retoma queda anotada en la bitácora.
  Estimado (`consumo.LIGERO`): ≈ 13 mil tokens por paso, casi sin crecer; un panel como el de OU 2.0, de ≈ 41 M a ≈ 7 M.
  Es un cambio de instrumento: **no es el predeterminado** hasta validarlo (pendiente 0).
- **`arnes ensayar`** (0 tokens): recorre las tareas con acciones de perfil (zonas numeradas, desplazar, escribir,
  tocar) y avisa rutas que no llegan, objetivos que el perfil no vería y datos de prueba que faltan; da los pasos
  mínimos por tarea (`datos/ensayo.json`). Se detiene si 3 pasos seguidos no encuentran su objetivo (la primera
  versión, sin ese freno, siguió más de hora y media con la ruta desviada). En OU 2.0: sin problemas, ≈ 10 min;
  pasos mínimos T1 16 · T2 12 · T3 27 · T4 8.
- **`arnes recorrido … todos --paralelo N`**: un proceso por perfil; baja el tiempo, no los tokens.
- **Corrección del instrumento (zonas web):** un elemento recortado por un contenedor con desplazamiento (las
  opciones de «Elige tu plazo») contaba como zona aunque no se viera. Ahora cuenta solo su parte visible. En el panel
  de la segunda medición los perfiles pudieron ver números sobre opciones ocultas en esa hoja; eligieron plazo en 7
  de 8 corridas de T1, así que no parece haber cambiado resultados, pero queda declarado.
- Documentado en `metodos/recorrido/METODO.md`, `docs/GUIA.md` (consumo y por qué crece), la plantilla y CLAUDE.md.

## Sesión del 28 de octubre de 2026 (segunda medición: PWA MVP y herramienta de navegador)

**Pedido:** segunda medición sobre `https://pwa.productdesign.mx/app/` (MVP sin reglas de backend) con todas las
métricas posibles (heurísticas, accesibilidad…) y mejorar el módulo de Playwright para ver y «vivir» el recorrido.

**Herramienta (sin cambiar el instrumento de Figma; `JS_PASO` de Figma quedó idéntico):**
- `arnes/navegador.py`, web: celular emulado (`dispositivo.emular`, toques táctiles, deslizar con gesto CDP);
  pantalla por `pantalla: {selector, atributo}` (`data-estado`); asentar por firma de la página, sin capturas cada
  300 ms (adiós parpadeo); subtítulos y círculo del toque en una sombra cerrada que las capturas ocultan; acciones por
  rol y texto (`mecanico`, `ruta_mecanica`, `teclear_patron` para códigos en pantalla); `limpiar_datos`; ventana de
  observación de 3 s para avisos pasajeros (SMS simulado); pestañas nuevas (enlaces `_blank`) se miran, se cierran y se
  le cuentan al perfil; campos transparentes y enlaces de dos líneas cuentan como tocables.
- `arnes/observacion.py` + `observacion.html`: sala de observación local en vivo (pantalla, toque, pensamiento,
  intención, acción, confianza y fricción por paso, espera, tokens contra lo estimado).
- `arnes/tecnico.py` (`arnes tecnico`, 0 tokens): axe-core 4.10.3 en español (`arnes/vendor/axe`, MPL-2.0) por pantalla,
  objetivos < 24/44 px, foco con Tab, reflujo 320 px, campos, legibilidad INFLESZ (Fernández-Huerta se descartó:
  castiga frases cortas), errores, carga en frío y con caché en red lenta y CPU 4×, INP aproximado, PWA, retoma.
- Tareas a mitad del flujo (`inicia_en` + ruta mecánica); una sesión del navegador por perfil (paralelo); fin revisado
  tras el último paso; capítulos de video no fatales; `abrir` cierra una sesión vieja del mismo nombre.
- Tablero: pestaña «Calidad técnica» y 4 KPIs técnicos en el Resumen. `arnes estilo` lee los textos de la ruta
  mecánica; E02 y E08 sin falsos positivos. `arnes auditar` usa las pantallas de la ruta mecánica si existen.

**Estudio `estudios/2026-10-28-ou2-pwa-mvp`:** 4 perfiles × 4 tareas × 2 corridas = 32 sesiones; auditoría técnica
(30 pantallas), auditoría experta (244 observaciones con consenso), reporte LISTO PARA ENTREGAR, síntesis en el vault.
- Hallazgo principal: el total a pagar no aparece ni en el simulador ni en el contrato (8 de 8 en T1 y en T4); Itzel
  abandona T4 dos veces en el contrato «aproximado». La confianza cae ≈ 20 puntos en el tercer permiso de ubicación
  (Incode, otro dominio). El código de verificación y la rama sin asesor ya están corregidos frente al prototipo.
- Técnica: LCP 2.4 s, CLS 0, sin conexión ✓, retoma ✓ (salvo en el código), 21 de 30 pantallas sin fallas WCAG.
- Fallas del instrumento, todas resueltas y documentadas en `datos/historial/`: SMS pasajero, «esperar», deslizar, campo
  transparente, enlace de dos líneas, datos de prueba sin estado civil, límite de la suscripción, procesos colgados.
- Consumo: ≈ 37.4 M tokens (panel 30.9 M, pilotos y repeticiones 5.6 M, auditoría 0.85 M), ≈ 3.7 M nuevos.

---

## Sesión del 22 de octubre de 2026 (tablero de investigación)

**Pedido:** rediseñar el reporte como un sistema para decidir con evidencia UX (prompt maestro «UX Research
Intelligence Dashboard»), para los próximos usos del arnés.

- `docs/TABLERO.md`: auditoría del reporte anterior, arquitectura (6 áreas), plan de visualización, estructura,
  componentes y sistema visual (secciones A–F del prompt).
- `arnes/reporte/tablero.py`, `tablero.css`, `tablero.js`: en recorrido, `arnes reporte` genera el tablero como reporte
  principal y el documento completo como `-detalle.html`. Sin librerías externas; claro y oscuro; modo ejecutivo e
  investigación; filtros de tarea, perfil, severidad y confianza; mapa del recorrido, línea de confianza con anotaciones,
  mapa de fricción, matriz severidad × confianza, hallazgo × perfil, cajón de evidencia (capturas, pensamientos
  marcados como perfil simulado, auditoría, sesión paso a paso), hipótesis y cola de validación con la muestra de UiX.
- Paleta de perfiles validada con el script de la guía de visualización (claro y oscuro; en claro, aqua y amarillo
  piden etiquetas directas y vista de tabla: las tiene).
- Integridad: lo calculado lleva «Métrica derivada»; lo que falta, «Sin dato». Prioridad = severidad × frecuencia ×
  confianza de investigación; el impacto de negocio va aparte.
- `narrativa.yaml` admite campos nuevos (`confianza`, `tablero.pasos_prometidos`, `etapas`, `impacto_usuario`,
  `validacion`, `validar_con_personas` como objetos); el reporte detallado, el `.md` y la síntesis los leen.
- Probado: sin errores de JavaScript; escritorio, móvil y oscuro revisados en capturas; `arnes verificar` → LISTO.
- Pendiente: el tablero cubre recorrido; comprensión sigue con el reporte anterior.

---

## Sesiones del 21 y 22 de octubre de 2026 (repositorios en GitHub)

- Commit inicial y push al repositorio **privado** `ShortwabeCustom/arnes-usuarios-sinteticos` (rama `main`). Es
  privado porque lleva material interno: perfiles hechos con bases de clientes, guías de UiX, manuales de la PWA y
  reportes.
- `conocimiento.yaml` ya no guarda la ruta completa del vault, que incluía el correo de la cuenta: usa
  `~/Library/CloudStorage/GoogleDrive-*/…` y `arnes/conocimiento.py` la resuelve. La variable `ARNES_VAULT` la reemplaza
  si el vault está en otro lado.
- **El vault también está en GitHub**: repositorio privado `ShortwabeCustom/vault-equipo` (141 archivos; excluye
  `.obsidian/workspace*.json`, `.claude/settings.local.json` y `.DS_Store`). Se queda en Google Drive; su historial de
  git vive fuera de Drive (`~/Documents/claude/vault-equipo.git`, con `--separate-git-dir`) porque Drive puede
  corromper una carpeta `.git`. En Drive solo se agregaron `.gitignore` y un archivo `.git` de una línea.
- En el arnés, el vault es un **submódulo en `vault/`**: quien clona con `--recursive` recibe las dos cosas. En la Mac
  de Alexis el submódulo está vacío (`deinit`) para no tener dos copias.
- `vault()` busca en este orden: `ARNES_VAULT` → Drive → `./vault`. `arnes sintesis` recuerda hacer commit y push
  si el vault es un repositorio git (el arnés no hace commits en el vault).
- Pendiente para Alexis: el `CLAUDE.md` del vault sigue en voseo y con rutas de Windows y de otra cuenta de Mac.

**Instalación automática** (pedido: que quien clone el repositorio no tenga que instalar las dependencias a mano):
- `bin/instalar`: uv, Python 3.12, dependencias, guardia de commits, vault (submódulo en la rama `main`, solo si no
  está en Drive ni en `ARNES_VAULT`), navegador de Playwright y el comando `arnes` en `~/.local/bin`. Idempotente.
- `bin/arnes`: corre `bin/instalar` si falta el entorno o si `pyproject.toml` cambió; no hay que activar `.venv`.
- `.claude/settings.json`: hook `SessionStart` que corre `bin/instalar --silencioso` al abrir Claude Code.
- `bin/playwright-cli`: el CLI de Playwright dentro del repositorio, con versión fija (0.1.22). Antes dependía de
  `~/.claude/skills/playwright/` de la Mac de Alexis.
- `vault()` baja el submódulo si no encuentra el vault, y el error ya no es una traza sino qué hacer.
- `docs/INSTALACION.md`: guía de instalación para quien clona el repositorio (requisitos de cuenta, los tres comandos,
  qué se instala, comprobación, problemas frecuentes, desinstalar). La sección 2 de la guía y el README apuntan ahí.
- Probado con un clon nuevo sin `--recursive` y con una carpeta personal vacía: en 32 s quedó todo instalado; el vault
  bajó con credenciales de GitHub (sin ellas, el aviso dice pedir acceso y `gh auth login`).

---

## Sesión del 22 de octubre de 2026 (primer recorrido sobre Figma real: OU 2.0)

**Pedido:** descubrimiento preliminar del prototipo de Originación Única 2.0, como benchmark, con heurísticas y
métricas de producto y negocio. Estudio `estudios/2026-10-22-ou2-descubrimiento`.

- La guía y el método ahora piden **compartir el link sin restricciones y probarlo en incógnito** (sugerencia de
  Alexis: es un consejo, no una pregunta).
- **Pre-flight:** el link abre sin sesión. Banner de cookies y barra lateral de flujos movían el marco: se cierra la
  barra (`show-proto-sidebar=0`) y el banner se descarta con la acción nueva `tocar_texto`.
- **El detector de zonas no servía en Figma real:** en prototipos táctiles el cursor es de «dedo» en todo el lienzo y
  daba 0 zonas. Ahora usa los **resaltados de hotspots** de Figma. Tocar fuera cerraba las hojas inferiores; ahora
  detecta el overlay por el velo y toca dentro, en la manija. Prueba nueva con imágenes sintéticas (19 pruebas).
- **Recorrido mecánico sin perfiles (US$ 0):** 24 pantallas de la bienvenida a la selfie; mapa y node-ids en
  `pantallas_info` del estudio. Solo «Efectivo» está conectado en el uso del préstamo; «Tomar selfie» es el fin.
- **Consumo en tokens, no en dinero** (pedido de Alexis: con la suscripción no hay precio por sesión). `arnes/consumo.py`
  registra los tokens de cada llamada (entrada, caché nueva, relectura de caché, salida) y los muestra en `arnes
  estado`, reportes y síntesis. `arnes recorrido … --simular` estima con un modelo medido en 9 sesiones reales
  (contexto ≈ 7,500 tokens + 1,900 por paso, 2 llamadas por paso). Las llamadas anteriores no guardaron tokens.
- **Piloto 1 fallido por el instrumento** (380 mil tokens): con la ventana visible en pantalla Retina la captura salía
  al doble que las coordenadas de la página; 0 zonas en la bienvenida y Bryan «abandonó» sin poder tocar. El mapeo
  no lo mostró porque corrió sin ventana. Arreglo: todas las capturas en `scale: 'css'`; y si una pantalla de Figma
  da 0 zonas dos veces, la sesión se detiene como `fallo_instrumento` antes de llamar al modelo. Evidencia en
  `datos/historial/piloto-1-fallo-instrumento/`.
- **Piloto 2 fallido por el instrumento** (685 mil tokens): las 4 primeras pantallas bien; en la hoja del plazo el
  navegador comparaba la captura consigo misma (`siguiente.png` se sobrescribe), no veía el overlay, tocaba fuera y
  lo cerraba. Arreglo: copia propia de la captura previa (`_previa.png`). Validado sin costo con ventana visible y el
  mismo patrón de capturas de la sesión: 23 pasos hasta «cargando». Evidencia en `datos/historial/piloto-2-…`.
- Lección: **validar el instrumento con el mismo camino de código que la sesión** (ventana visible, mismas rutas de
  captura) antes de gastar; el mapeo sin ventana no lo cubría.
- **Piloto 3 válido** (1.9 M tokens, 192 mil nuevos): el instrumento funcionó en 18 pasos. Bryan llegó fluido hasta
  el código; abandonó en «¿te está ayudando un asesor?»: «No» no habilita «Confirmar» porque el prototipo solo
  conecta la rama «Sí» (estado de prototipado, B). En el código, el avance es una zona invisible al pie (D, en duda).
  Decisión pendiente con Alexis: cómo tratar la rama del asesor en el panel.
- **Modelo de tokens recalibrado** con el piloto 3: con capturas de 1200×1026 el contexto crece ≈ 4,800 por paso (no
  1,900). Una sesión de 23 pasos ≈ 2.9 M. Recortar la captura al teléfono reduciría el crecimiento.
- **Parpadeo de la ventana** (observación de Alexis): la burbuja del pensamiento se ocultaba y se mostraba en cada
  sondeo de 0.3 s. En Figma ahora queda fija a la izquierda y **la captura del perfil se recorta al teléfono**, así
  que la burbuja no le estorba (y la captura pesa menos tokens). El destello azul de los resaltados de Figma sigue: es
  como el arnés encuentra los botones.
- **Reintento de toques en Figma:** un toque que no cambia el teléfono se repite una vez; la respuesta se juzga por
  el cambio en el teléfono, no en toda la ventana (la burbuja y los resaltados la cambian). Validado sin costo: 26
  pasos hasta el fin.
- **Opción A aprobada por Alexis:** T1 (va solo, bienvenida → pregunta del asesor, con `pregunta_cierre`: el perfil
  contesta qué respondería sin actuar) y T2 (con asesor, desde esa pantalla hasta la selfie; `url` propia de la
  tarea). Validado sin costo: T2 abre en `9830-189949` y llega a «cargando» en 6 toques. `primer_toque` medido con
  ventana visible.
- **Modelo de tokens por tamaño de captura:** crecimiento por paso = 1,518 de texto + 2 × (ancho × alto / 750).
  Reproduce el piloto (ventana completa) y estima el recorte al teléfono. Panel A: ≈ 7.9 M tokens, ≈ 1 M nuevos.
- **Panel, Bryan, invalidado por el instrumento** (2.1 M tokens, igual a lo estimado): T1 abandonó 2 de 2 por toques
  sin respuesta. El video mostró la causa: el toque movía el mouse y hacía clic en el mismo instante y Figma, a veces,
  lo tomaba como hecho fuera del botón (lo resaltaba en azul). Ahora el toque llega, espera 150 ms y toca. Validado
  sin costo: T1 y T2 dos veces, 40 toques, solo 2 sin respuesta y ambos reales (correo antes que celular).
- **Parpadeo, segunda causa:** la barra de Figma aparecía y desaparecía con el mouse. `url_figma()` agrega
  `hide-ui=1` y `show-proto-sidebar=0` a todo link de prototipo.
- **El banner de cookies nunca se cerró:** la acción `tocar_texto` se había perdido (iba en un comando que la
  revisión de seguridad bloqueó). Agregada; ahora toca el botón por su rol.
- **Los registros de sesión se limpian al guardar** (`guardia.limpiar`): un perfil leyó y escribió el correo de
  ejemplo del prototipo y la guardia bloqueó el commit. Correos, CURP y tarjetas pasan a `[correo]`, `[CURP]`,
  `[tarjeta]` en el JSON de la sesión. Las capturas no se pueden revisar así: el correo de ejemplo del prototipo
  puede verse en ellas (es ficticio).
- **Estudio terminado** (Alexis autorizó correr todas las fases sin volver a preguntar). Panel: 16 sesiones válidas
  (4 perfiles × T1 y T2 × 2 corridas). Fallas del instrumento resueltas en el camino: cálculo del teléfono con el
  lienzo vacío, clic de cookies que desplazaba la página (0 zonas), espera tras recargar entre tareas; las sesiones
  fallidas se detuvieron antes de llamar al modelo (0 tokens). Auditoría: 57 llamadas, 155 observaciones con
  consenso. Reporte `oupwa-pdu-originacion-unica-2-0-sintetico_2026-10-22-v1` → LISTO PARA ENTREGAR (1 aviso: 2 de 8
  perfil-tareas cambian entre éxito y éxito con fricción). Síntesis en `03-Sintesis/`, subida sola al repo del vault.
- **Resultado principal:** se confirma el monto viendo solo el pago semanal (8 de 8 sesiones de T1 lo señalan) y el
  consentimiento de buró va en letra chica al continuar (7 de 8). H1, H2 y H4 se sostienen; H3 y H5 se caen.
- **Consumo total del estudio:** ≈ 21 M tokens (≈ 3 M nuevos): pilotos y rondas fallidas ≈ 5 M, panel ≈ 15 M,
  auditoría ≈ 0.6 M. Modelo de tokens recalibrado con el panel (error medio ≈ 3%).
- La tabla de auditoría del reporte usa los nombres de pantalla de la narrativa, no los node-ids.
- La guardia acepta textos de ayuda de un campo de correo (`ejemplo@`, `tucorreo@`, `usuario@`…): la auditoría los cita
  de la pantalla. La salida de `arnes auditar` también pasa por `limpiar`.
- Pendiente (histórico): aprobación del piloto (Bryan, T1, ≈ 21 pasos ≈ 1.2 M tokens, ≈ 80 mil nuevos) y luego el panel
  (8 sesiones ≈ 9.4 M tokens).

**Automatización y crecimiento sano** (pedido: «automatiza este proceso y haz lo que más convenga para el
crecimiento sano y útil del arnés»):
- `arnes vault` (`arnes/vault.py`): `estado`, `sincronizar` (trae, hace commit con la lista de notas que cambiaron y
  sube) y `automatizar`/`quitar` (agente de launchd `com.arnes.vault-sincronizar`, cada hora; bitácora en
  `~/Library/Logs/arnes-vault.log`; si falla, notificación de macOS). Instalado en la Mac de Alexis y probado: lee
  Google Drive sin problemas.
- `arnes sintesis` ya hace commit y push del vault (antes solo lo recordaba); `--sin-subir` lo evita.
- `arnes/guardia.py`: bloquea correos (salvo dominios de ejemplo), llaves de Anthropic, GitHub y AWS, llaves
  privadas, contraseñas escritas, CURP y números de tarjeta (con Luhn). La usan el hook, la sincronización del vault y
  la integración continua. Los dos repositorios pasan limpios.
- `.githooks/pre-commit` (guardia, lint, pruebas) y `.github/workflows/pruebas.yml` (lo mismo en GitHub).
- `arnes doctor`: revisa Python, `.venv`, Claude Code, Playwright, bibliotecas, vault, hook y remoto.
- `docs/CRECER.md`: reglas para cambiar el arnés. 18 pruebas (2 nuevas: guardia y sincronización del vault contra un
  remoto local, con integración de cambios de otro clon y bloqueo por la guardia).

---

## Sesión del 20 de octubre de 2026 (estándares de UiX)

**Pedido:** integrar al vault y al arnés las 5 guías de UiX: Naming, Demográficos, Completitud de tarea, Research en
tus proyectos y Template de protocolo tipo brief.

**En el arnés:**
- `fuentes-equipo/uix/`: las 5 guías tal como llegaron y `estandares.yaml`, la versión que lee el código.
- `arnes/estandares.py`: naming, semáforo, generación y región, demográficos por integrante, muestra recomendada,
  matriz de decisión y oportunidades.
- `arnes nuevo … --proyecto --tema`: llena el bloque `uix` de `estudio.yaml` y el brief al inicio de `PROTOCOLO.md`,
  con la muestra recomendada para validar con personas.
- El reporte se llama según el naming (`Estudio.entregable()`). Los dos estudios de ejemplo tienen bloque `uix` y sus
  reportes con el nombre anterior se borraron, porque se regeneran.
- En el reporte:
  - el panel muestra los 4 datos demográficos con su evidencia;
  - en recorrido, la completitud trae el semáforo de UiX con intervalo de Wilson y dice «sin color firme» si el
    intervalo cruza colores;
  - cada hallazgo y la priorización muestran su `oportunidad`;
  - «Para validar con personas» dice cuántas personas recomienda UiX.
- `arnes verificar` revisa el naming (formato, código de metodología), la `oportunidad` y los demográficos;
  `arnes persona validar` avisa si un perfil no declara `demograficos`.
- `personas/pwa` y `personas/gic`: bloque `demograficos` por perfil, con la evidencia de cada system prompt. Los
  prompts y las reglas no cambiaron, así que el instrumento es el mismo; la huella de la biblioteca sí cambia,
  porque incluye `biblioteca.yaml`.
- La guía, el skill y el README pasaron de voseo a tuteo, como escribe Alexis.

**Decisiones del arnés, no de las guías:**
- `-sintetico` al final del tema: sin eso, un `pdu` sugiere una prueba con personas.
- `pdu` para recorrido y `abtesting` para comprensión.
- Fecha del nombre: `uix.fecha_fin` o, si falta, la fecha del reporte.

**Lo que se aprendió:**
- Con la muestra que UiX recomienda para usabilidad (8–10), ni 10 de 10 da un color firme: el intervalo es 72–100%,
  de naranja a verde. Con 8–10 personas se encuentran problemas, pero no se certifica un verde.

**En el vault** (respaldo en `respaldos-vault/2026-10-20-antes-de-estandares-uix/`):
- Notas nuevas: `01-Fuentes/estandares-uix.md` y `03-Sintesis/estandares-uix-en-investigacion-sintetica.md`.
- Entradas en el índice y el log.
- Una línea en «Ver también» de 6 notas: metricas-ux, personas-y-arquetipos, saturacion-de-muestra,
  discount-usability-5-usuarios, designops-y-researchops y encuestas-ux.
- `arnes sintesis` actualizó la síntesis de la réplica, que apunta al reporte con el nombre nuevo.
- `conocimiento.yaml` agrega las dos notas a lo que se lee en todo estudio.

Costo: US$ 0 (no se corrieron sesiones).

---

## Sesión del 20 de octubre de 2026 (construcción completa)

### 1. Punto de partida descartado

- Se instaló **Harness² de Google Research** (`google-research/harness2`): es un framework de mejora recursiva de
  harnesses para benchmarks (JobBench, LAB, WorkBuddy), con Vertex/Gemini. **Se descartó y se borró**: no tenía
  relación con usuarios sintéticos.
- Se revisó **harness/harness-skills**: son skills para la plataforma de CI/CD Harness.io. **Se descartó** sin instalar.

### 2. Insumos analizados

Las 7 investigaciones previas en `~/Documents/claude/` (no se modificaron):
`skill-proceso-auditoria-prototipos-figma`, `GIC-User Person`, `OU-PWA-usuario-sintetic-reporte-usabilidad`,
`PWA-User Person`, `Investigacion-pantallas-de-recompra`, `Investigación-funcionalidad de entrecalles`,
`Investigacion comprension de pantallas en recompra`. De ahí salieron los tres métodos: construir persona,
comprensión de pantallas y recorrido de flujo.

### 3. Decisiones de la persona usuaria

| Decisión | Elegido | Por qué |
|---|---|---|
| Alcance de la primera versión | Los tres métodos a la vez | |
| Motor de sesiones | `claude -p` (suscripción, sin API key) | Era lo que ya usaban los estudios de recompra |
| Bibliotecas de personas | Copiadas al arnés (`personas/`), versionadas con huella | Los estudios pasados no cambian si cambia la fuente |
| Vault de Obsidian | Leído en su ruta; el arnés escribe solo síntesis | Es un wiki vivo que mantiene la persona usuaria |
| Síntesis en el vault | Sí, en `03-Sintesis/` | Pedido explícito |
| Manuales de UX writing de la PWA | Al vault (fuente + síntesis) y al arnés (reglas) | Pedido explícito |

### 4. Lo que se construyó, en orden

1. **Núcleo:** `motor.py` (sesiones `claude -p` aisladas), `personas.py`, `ocean.py`, `estudio.py`, `yamlx.py`, CLI `arnes`.
2. **Comprensión:** `medir.py` (zonas, contraste, saliencia, modelo de lectura), `metodos/comprension.py`, reporte con visor.
3. **Recorrido:** `navegador.py` (un `run-code` de Playwright por paso), `metodos/recorrido.py` (el perfil decide cada
   paso sobre la captura con zonas numeradas; modo guion opcional), reporte con embudo y línea de tiempo.
4. **Persona:** `metodos/persona.py` (`validar` entregables 01–12, `probar` fidelidad).
5. **Verificación:** `verificar.py` (recuenta cifras, cadena hallazgo → recomendación, lenguaje prohibido).
6. **Mejoras tomadas del vault:** `robustez.py` (estabilidad entre corridas, intervalos de Wilson, panel homogéneo),
   `revisar.py` (preguntas sugestivas, baseline), `auditar.py` (3 evaluadores independientes), WCAG 2.5.8, primer
   toque, cognitive walkthrough, piloto, `conocimiento.py` (lectura del vault y síntesis).
7. **Guía de estilo de la PWA:** `fuentes-producto/pwa/` (3 manuales + `reglas-estilo.yaml`), `estilo.py`, criterios
   G1–G8 en la auditoría.
8. **Métricas de flujo:** `metricas.py` (pasos, clics, campos, tiempo estimado, validaciones, cambios de canal,
   retoma, estatus visible, distancia a la compra, CES).
9. **Documentación:** `CLAUDE.md`, `README.md`, `docs/GUIA.md`, `docs/VALIDACION.md`, `metodos/*/METODO.md`,
   skill `/investigacion-sintetica`.

### 5. Lo que se aprendió (y ya está corregido en el código)

- **La redacción de la sesión es parte del instrumento.** Con preguntas en lista, la réplica coincidía 79% con el
  original; con la plantilla JSON en línea del original, 86%. El texto de las sesiones no se cambia sin volver a
  correr la réplica.
- **El estudio original reanudaba las continuaciones sin el system prompt del perfil.** El arnés lo pasa en cada turno.
- **YAML convierte `no` en `false`.** `yamlx.py` deja `no`, `si`, `on` y `off` como texto.
- **Aislamiento de sesiones:** sin opciones, cada sesión recibía el correo de la cuenta e instrucciones de los
  conectores MCP. Con `--setting-sources project --strict-mcp-config --disable-slash-commands` y una carpeta temporal
  queda solo un bloque de entorno que la suscripción no permite quitar.
- **Con 4 corridas por celda ninguna brecha A/B es concluyente**; con las 12 del original, tampoco la mayor (92% vs 50%).
- **Los 3 evaluadores reproducen los 9 criterios de UX writing** que el protocolo de recompra había observado a mano.
- **La espera del sistema** se medía con pausas de 1.2 s y quedaba inflada; ahora se sondea cada 300 ms.
- **En sitios con `#hash`** la URL no alcanza para identificar la pantalla: la retoma se juzga por el texto visible.
- **La «María» de los manuales no coincide con los datos** (46.8% de mujeres en la base): es arquetipo de
  comunicación, no perfil de investigación.

### 6. Lo que se escribió fuera del repositorio

En el vault «vault-equipo» (respaldos previos en `respaldos-vault/`, fuera de git):
- `03-Sintesis/estudio-2026-10-05-recompra-comprension-replica.md`
- `03-Sintesis/voz-y-tono-de-la-originacion-unica.md`
- `01-Fuentes/manuales-ux-writing-pwa.md`
- Entradas en `00-Indice/index.md` y `00-Indice/log.md`; una línea en «Ver también» de 12 notas de concepto.


## 2026-10-29 — Hero editorial animado del reporte OU2 PWA

- Se sustituyó el carrusel de portada por una escena editorial de ancho completo, con ilustraciones SVG originales en azul y marfil.
- La escena presenta 24 personajes en tres planos (15 en tablet y 9 en móvil), celulares, ciclos de articulación y un protagonista que se detiene para consultar el teléfono.
- Movimiento continuo mediante Web Animations API, pausa manual, pausa fuera de pantalla y respeto de `prefers-reduced-motion`. Recursos locales en `reporte/assets/people-hero/`.
- Verificación en Chrome: 1440×900, 1366×768, 1024×768, 768×1024, 390×844 y 375×812; sin desbordamiento horizontal. Comprobación de desplazamiento, pausa y movimiento reducido. Sintaxis de ambos scripts comprobada con `node --check`.
- La entrega es una animación vectorial web, no un archivo de video renderizado.

### Refinamiento del hero — composición y movimiento

- Composición con CSS Grid: texto, escena y pie ocupan filas propias; se eliminó el espacio vacío excesivo en móvil. La escala de las figuras responde a la altura disponible mediante unidades de contenedor.
- Jerarquía tipográfica, separación de frases, llamada a la acción y pie editorial refinados. Controles con foco visible y área de interacción de 44 px.
- Personajes con inclinaciones individuales, detalles de cabello, parpadeos y balanceo del celular. El protagonista desacelera y acelera al detenerse a leer.
- Se conserva la fase de las rutas al redimensionar. Verificación en seis resoluciones, sin errores de consola ni desbordamiento; pausa y movimiento reducido correctos.

### Nueva dirección del hero: panorama humano de escala pequeña

- Se revisó la referencia de movimiento del 29 de octubre a las 10:11 y se sustituyeron los bustos por figuras originales de cuerpo completo, pequeñas y de perfil.
- El título conserva el protagonismo; el panorama usa dos planos, 18 figuras en escritorio, 12 en tablet y 6 en móvil, con articulación de rodillas, balanceo, miradas y lectura del teléfono.
- Se recuperaron los tokens de color del reporte: marfil, verde y azul apagado. El resto del documento permanece igual.
- Chrome: seis tamaños entre 375×812 y 1440×900, sin superposición entre texto y escena ni desbordamiento horizontal, sin errores de consola; pausa y movimiento reducido verificados. Ambos scripts pasan `node --check`.

### Jardín de experiencias: nueva portada editorial

- Se siguió el brief del jardín: contenido en 43 % del ancho y una composición decorativa original en el resto, sin filas, parallax, notificaciones ni desplazamientos que crucen toda la pantalla. Veinte figuras diminutas en ocho familias; seis en la recomposición móvil de 210 px.
- Ilustración SVG separable con terreno orgánico, vegetación, banco y tres patrones locales. Se revisó primero la composición estática y se ajustaron siluetas, orientación y un sendero para evitar vegetación en el recorrido.
- Cinco pequeñas historias se escalonan en un ciclo determinista de 48 segundos. La mayor parte permanece quieta. Se observaron y grabaron 52 segundos, con un máximo registrado de dos figuras moviéndose simultáneamente. Después se revisaron visualmente los ajustes de orientación y sendero y se volvió a grabar.
- Estilos aislados en `assets/microcosmos-hero/`. Recursos locales; el archivo se probó sin servidor. Se preservó el contenido de `<main>` y la navegación por comparación exacta con el respaldo.
- Se creó `reporte/fuente-editorial.html`, seleccionada mediante `presentacion.html_local` en `narrativa.yaml`, para conservar esta edición al regenerar. El detalle y Markdown mantienen su generación habitual. La presentación es una edición estática revisada; nuevos resultados requieren revisar su contenido.
- Copia recuperable de la versión previa en `reporte/respaldos/antes-jardin/`, con captura y sumas SHA-256 verificadas.
- Chrome: 1440×900, 1280×800, 390×844 y 360×800; sin desbordamiento ni cruce con el texto. Se probaron pausa, reanudación, teclado, pausa al salir de pantalla, conservación de pausa manual, reducción de movimiento, enlaces, carrusel de citas y desplegables. La pausa por pestaña oculta está implementada, sin prueba directa de ese evento.
- Validación: 34 pruebas del repositorio pasan; Ruff F/E9 y guardia pasan. La suite se ejecutó con permiso para el servidor local que requiere su prueba de observación. No se midió rendimiento en dispositivos físicos ni se realizó una auditoría completa con lector de pantalla.
- Evidencia visual y resultados en `reporte/verificacion-jardin/`; grabación breve `jardin-de-experiencias.mp4`.

### Jardín: flujo continuo de personas

- A petición del usuario se aumentó la actividad: cinco caminatas independientes en escritorio y tres en móvil, con trayectorias curvas, pasos articulados, balanceo de brazos y descansos breves en los extremos. Se mantienen los gestos de celular, conversación y saludo.
- Veinte figuras en escritorio y ocho en móvil. Se conservan título, composición, paleta y contenido del reporte; sólo cambian los recursos de `assets/microcosmos-hero/`. Respaldo previo en `reporte/respaldos/antes-flujo/`.
- Chrome local: cuatro tamaños (1440, 1280, 390 y 360), sin desbordamiento ni errores JavaScript. Muestreo durante 24 s: las cinco personas cambian de posición en cada intervalo de cuatro segundos. Pausa por teclado, reanudación, conservación de pausa manual al salir y volver y reducción de movimiento comprobadas. Sintaxis de los tres scripts correcta.
- Evidencia actual en `reporte/verificacion-jardin/flujo/`, con grabación `jardin-en-movimiento.mp4`. No se volvió a correr la suite Python porque no hubo cambios en el arnés ni en la integración de datos.

## 2026-10-30 — Video urbano en el hero del reporte OU2

- Integrado el MP4 aportado por el usuario (1920 × 1080, 8 s, sin audio, 1.6 MB) como recurso local en `assets/urban-hero/`, con copia binaria intacta. Se extrajo un póster del segundo 2.
- Composición editorial 44/56 en escritorio; texto primero en tableta y móvil, panorama horizontal 16:9 completo. Ajustes CSS reversibles de color y transición de bordes al marfil. CTA «Leer los hallazgos» a `#hallazgos`.
- Se retiró la carga de los scripts del jardín SVG. Respaldo recuperable de ambos HTML y sus recursos en `reporte/respaldos/antes-video-urbano/`. Fuente editorial y HTML entregable sincronizados; main y nav idénticos al respaldo.
- Control nativo de video con pausa, reanudación, teclado, preferencia de movimiento reducido con inicio voluntario, pausa fuera de pantalla y documento oculto, manejo de autoplay bloqueado e imagen para impresión.
- Chrome local: seis tamaños (1440, 1280, 1024, 768, 390, 360), sin desbordamiento ni errores JavaScript. Se reprodujeron dos ciclos completos, se revisaron capturas del cierre y se conservó la disolución original. Pausa manual persistente, pausa fuera de pantalla, movimiento reducido, impresión y CTA comprobados. Documento oculto y política de autoplay se probaron mediante simulaciones de los eventos/rechazos correspondientes.
- Evidencia y grabación en `reporte/verificacion-video-urbano/`. Sintaxis del nuevo JS comprobada. No se cambió el arnés Python ni se ejecutaron nuevas sesiones de investigación.

### Hero: apertura panorámica con razones para leer

- Rediseñada la portada a todo el ancho: titular centrado, video de ciudad integrado mediante transición marfil/verde y franja editorial de tres métricas enlazadas. En móvil el panorama mantiene 16:9 debajo del texto; métricas en filas legibles.
- Los conteos son 28/32 (completan su tramo), 8/8 (buscan el costo total en el simulador sin encontrarlo) y 2/8 (abandonos de T4, ambas corridas de Itzel). Se verificaron las completitudes y abandonos en agregado.json y el segundo conteo en H1 de narrativa.yaml. Bases y naturaleza sintética visibles.
- CTA «Descubrir qué frena la decisión» al hallazgo financiero; cada métrica enlaza a su sección. Fuente editorial y HTML entregable sincronizados; main y nav conservados exactamente. Respaldo en `respaldos/antes-hero-metricas/`.
- Verificación en Chrome: seis anchos, sin desbordamiento; dos reinicios del video; control por teclado, pausa persistente, reducción de movimiento e inicio voluntario, impresión y enlaces. Se conservaron las simulaciones de visibilidad/autoplay. Tras afinar el ancho del titular y la legibilidad, se actualizaron capturas completas y grabación en `verificacion-hero-metricas/`. Sintaxis JS y guardia correctas. No hubo cambios Python ni nuevas sesiones de investigación.

### Ajuste de texto y acciones del hero

- Se retiró «La vida sigue.» y se conservó «La decisión necesita claridad.» junto a la aclaración de escena conceptual.
- El enlace «Investigación sintética · 32 sesiones · 4 perfiles» es ahora un botón secundario delineado junto al principal; ambos se apilan en móvil. Fuente editorial y entregable sincronizados.
- Chrome: 1440 y 390 px, posición de botones, ausencia de desbordamiento y navegación a metodología con teclado comprobadas. Capturas `verificacion-hero-metricas/*-botones.png`.

### Cards del recorrido y lecturas desde la izquierda

- Se rediseñaron las cuatro cards siguiendo la referencia: superficie oscura, acentos ámbar/verde/azul/terracota, esquinas redondeadas, cifra protagonista, acceso al detalle y ocho segmentos de completitud. Se mantienen textos, bases y conteos (7/8, 8/8, 7/8, 6/8).
- Todos los enlaces de contenido del reporte abren páginas diseñadas dentro de un diálogo que entra desde la izquierda. Inicio y salto accesible conservan su función. Cierre por Escape/botón/fondo, foco confinado y restaurado, regreso entre lecturas, scroll conservado y movimiento reducido.
- 49 páginas locales independientes: cinco secciones, cuatro tramos, 32 sesiones y ocho fuentes/documentos. Archivos originales accesibles explícitamente. Datos estructurados desplegables y documentos HTML con semántica conservada, sin scripts del original; gráficos interactivos disponibles en el original.
- Generación reproducible con `assets/report-reader/build_readers.py`, carga local por demanda, sin servidor. Fuente editorial y entregable sincronizados; hero conservado salvo los destinos de enlaces. Respaldo en `respaldos/antes-cards-lecturas/`.
- Chrome: cards a 1440/390/360, 22 destinos del reporte, 49 páginas a 390 px, navegación anidada, movimiento lateral, teclado, cierre, restauración de posición, página independiente y captura de sesión comprobados. La simulación de error de carga por interceptación `file://` no fue concluyente; se conserva como limitación en la evidencia. Tres pruebas de integración editorial pasan; no se ejecutaron nuevas sesiones de investigación.
- Evidencia y detalles en `verificacion-cards-lecturas/`. El navegador integrado bloqueó la recarga del archivo local por su política de URLs; la pestaña del usuario requiere recarga manual.

### Claridad y corrección de la métrica de confianza

- Se sustituyó el rango negativo aislado por una comparación antes/después: 60.3/100 → 40.5/100, promedios de las mismas ocho corridas sintéticas redondeados a un decimal. La escala de 0 a 100 y el significado de la cifra aparecen junto a la métrica; se explica una caída media aproximada de 20 puntos, no porcentajes.
- La revisión de los registros `inePermisoUbicacion` → `incodeUbicacion` detectó un error previo: las diferencias por corrida son 18, 12, 26, 25, 17, 16, 22 y 22; el rango correcto es 12–26, no 17–25. Promedios exactos: 60.25 antes, 40.5 después; diferencia media 19.75. Se corrigieron la card, H3, la síntesis fuente, el detalle completo y la afirmación correspondiente en el tablero anterior enlazado. Registros de sesiones y respaldos históricos intactos.
- Nueva lectura lateral `lecturas/confianza-calculo.html` con escala, momentos comparados, tabla de las ocho corridas, enlaces a cada sesión, fórmula y ejemplo. Fuentes de lectura regeneradas (50 páginas); HTML editorial y entregable idénticos.
- Verificación de pares y cálculos directamente contra las ocho sesiones, de los destinos locales y de sincronización. Sin nuevas sesiones ni cambios en el instrumento. No se repitió la revisión visual en navegador en este ajuste.

### Orientación: unidad, pregunta y base visibles

- Se reemplazó la fracción aislada por «462 de 466 respuestas con dudas sobre el avance». La card muestra la pregunta del instrumento («¿Sabes en qué parte del proceso vas y cuánto te falta?»), las tres opciones y sus conteos: 400 «más o menos», 62 «no» y 4 «sí».
- Base explícita: respuestas repetidas a lo largo de 24 sesiones sintéticas en registro, identidad y datos. Los campos vacíos de la INE se presentan como otro hallazgo con su propia base de ocho corridas.
- Se corrigió el conteo editorial previo 435/439 tras contrastar las sesiones originales con agregado.json: T1 = 127/127 respuestas con dudas; T2 = 103/106; T3 = 232/233. Se actualizaron la síntesis, H5 y sus representaciones enlazadas; registros de sesión y respaldos intactos.
- Nueva lectura `lecturas/orientacion-calculo.html` con reglas de inclusión, tablas por tramo y por sesión, 24 enlaces y advertencia de que las sesiones largas aportan más respuestas. Recursos regenerados (51 páginas).
- Verificación exacta contra registros y agregado, destinos y sincronización de fuente/entregable. Resultado en `verificacion-metricas/orientacion.json`. Sin nuevas sesiones ni revisión visual adicional de navegador.

## 2026-10-31 · Biblioteca de evidencias y lectura UX del reporte OU 2.0

- Se conservó el hero aprobado y se añadió una sección con cuatro capturas del MVP: contrato/costo, permiso de ubicación, fachada y consentimiento de buró. Accesos contextuales desde los hallazgos y navegación principal hacia la biblioteca.
- Biblioteca con cuatro casos, 32 grabaciones vinculadas por las sesiones y 30 mapas originales de toques/escritura. Búsqueda por tema/perfil, filtro por tramo, vistas por tipo, estados vacíos y carga por demanda. Las 16 grabaciones auxiliares no vinculadas por los JSON no se contabilizan como sesiones adicionales.
- Cada caso diferencia evidencia visual, pensamiento del perfil sintético, interpretación UX, límites y fuente. Evaluación heurística histórica identificada como asistida por IA; no como tres evaluadores humanos. Los mapas explican origen, unidad, superposición y leyenda; respuesta visible no equivale a éxito, consentimiento ni atención.
- Videos con controles nativos, sin reproducción automática y con alternativa escrita/archivo original. Pausa al cerrar el panel, cambiar lectura, cerrar desplegable o cambiar filtro. Integración con las lecturas laterales y sus páginas independientes: 86 páginas generadas.
- Se verificaron contra las fuentes los cuatro casos y conteos de los 30 mapas, metadatos de 32 videos, 130 referencias locales y 575 recursos/enlaces HTML; fuente editorial y entregable idénticos. Sintaxis y lógica de renderizado/filtros comprobadas con DOM ligero; tres pruebas editoriales pasan. No se realizó una nueva revisión visual en navegador: el protocolo local fue bloqueado por la política del navegador integrado. Límite registrado en `reporte/verificacion-evidencias/README.md`.
- No se ejecutaron nuevas sesiones, no se cambiaron datos del estudio ni el instrumento. Constructor reproducible en `assets/evidence/build_evidence.py`, invocado desde el constructor de lecturas.

### 2026-10-31 · Eliminar salidas a archivos sin formato

- A partir de la captura de T2-arturo-1.json se identificó y retiró «Abrir fuente original», que evitaba el visor. Los enlaces se normalizan a lecturas HTML al crearse, también para Ctrl/Cmd + clic y apertura en otra pestaña. Mensajes sin JavaScript regresan al reporte; errores de carga ofrecen reintentar. Archivos originales intactos.
- Se amplió la ficha de las 32 sesiones con perfil/tramo, primera impresión, orientación y acción por paso. Nuevas vistas de síntesis (hallazgos/interpretación/recomendación), evaluación heurística asistida por IA (búsqueda y criterios) y auditoría técnica (accesibilidad, retoma y rendimiento). Registros íntegros conservados en campos/desplegables.
- Corregido el destino fuente de primera medición. 86 lecturas regeneradas. Revisión de 90 HTML y 723 recursos/enlaces locales: cero enlaces a JSON/YAML/Markdown. 48 rutas originales comprobadas hacia HTML; 35 vistas renderizadas con DOM ligero, buscador heurístico y estados vacíos correctos. Tres pruebas editoriales pasan. Sin nueva revisión visual en navegador por la restricción ya documentada.
- Verificación reproducible y límites en `reporte/verificacion-lecturas/`. La pestaña ya abierta en JSON necesita volver a la lectura HTML; no se modificó el contenido de los datos para redirigirla.
