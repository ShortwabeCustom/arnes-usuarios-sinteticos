# Bitácora del arnés

Para retomar el trabajo en otra conversación: qué se construyó, en qué orden, qué se decidió y por qué, y qué
quedó pendiente. Lo más reciente va arriba. Al terminar una sesión de trabajo, agregar una entrada.

---

## Estado al 20 de octubre de 2026

- **Funciona y está validado:** método `comprension` (réplica de recompra: 240 de 240 mediciones idénticas, 86% de
  respuestas iguales al original, la misma variación que el original consigo mismo), bibliotecas `pwa` y `gic`,
  auditoría con 3 evaluadores, guía de estilo de la PWA, conexión con el vault.
- **Funciona, probado solo en material de prueba:** método `recorrido` y sus métricas de flujo, sobre
  `tests/fixtures/flujo-web` (servido con `python3 -m http.server 8737`).
- **Sin probar:** recorrido sobre un **prototipo de Figma real** (zonas activas por cursor del canvas) y sobre el
  **ambiente dev** (puede pedir VPN).
- **Repositorios** privados en GitHub: `ShortwabeCustom/arnes-usuarios-sinteticos` y `ShortwabeCustom/vault-equipo`
  (submódulo en `vault/`), rama `main`.
- **Estándares de UiX integrados** (naming, demográficos, semáforo de completitud, muestra, brief de protocolo):
  `fuentes-equipo/uix/`, `arnes/estandares.py`.
- **Pruebas:** `.venv/bin/python -m pytest tests -q` → 18 pasan (también en GitHub Actions). Los dos estudios de ejemplo dan `arnes verificar`
  → LISTO PARA ENTREGAR.
- **Consumo acumulado** de la suscripción: antes del 22/10/2026 se registraba en dólares equivalentes (≈ US$ 9); desde
  entonces, en tokens (`arnes estado <estudio>`).

## Pendientes

1. Probar `recorrido` con un prototipo de Figma real: un perfil, una tarea, revisar capturas y video, después el panel.
2. Probar `recorrido` en el ambiente dev (`dev-bazsolicitudunica.com.mx`): pre-flight de acceso primero.
3. Las sesiones de `estudios/prueba-recorrido-web` se corrieron antes de corregir la medición de la espera del sistema
   (pausas de 1.2 s); su tiempo estimado está inflado. Repetirlas si se quiere el ejemplo exacto (≈ US$ 1.80).
4. La réplica de recompra corrió solo la corrida 1 (32 de 96 sesiones). Correr 2 y 3 para tener estabilidad entre
   corridas en el propio arnés (≈ US$ 4).
5. Resolver con el equipo de UX writing las contradicciones internas de los manuales de la PWA (listadas en
   `fuentes-producto/pwa/reglas-estilo.yaml`, clave `contradicciones`).
6. Acordar con UiX un código de metodología para investigación sintética (hoy el arnés usa `pdu` o `abtesting` y
   agrega `-sintetico` al tema) y avisar las inconsistencias de sus guías (anotadas en `01-Fuentes/estandares-uix` del
   vault): el ejemplo del template no cumple el naming, la generación se define por rangos de edad que se moverán, las
   cifras de muestra de encuestas y A/B son cualitativas.
7. Ocupación AUSENTE en los 4 perfiles de la PWA: si alguna base la trae, agregarla a `personas/pwa/biblioteca.yaml`.
8. Si se agrega una biblioteca nueva de personas, seguir `metodos/persona/METODO.md` y correr `arnes persona probar`.

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
