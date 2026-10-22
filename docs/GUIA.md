# Guía: tu primer estudio con usuarios sintéticos

Para quien usa el arnés por primera vez. Cubre los pasos de una prueba de principio a fin y, en cada paso, la
práctica de UX research que aplica y por qué. Si quieres el detalle técnico de un método, está en
`metodos/<método>/METODO.md`; esta guía es el recorrido completo.

---

## 1. Qué es y qué no es

El arnés simula sesiones de investigación con **perfiles sintéticos construidos sobre datos reales** (por ejemplo,
los cuatro segmentos del User Persona OU-PWA, armado sobre 685,243 clientes). Cada perfil mira una pantalla o recorre
un flujo, piensa en voz alta, decide y responde. El arnés mide lo que se puede medir, junta lo que dicen los perfiles
y arma un reporte que se puede verificar.

> **Lo que produce son hipótesis, no conclusiones sobre personas.** Sirve para encontrar rápido y barato qué
> probablemente se rompe, qué se entiende mal y qué conviene probar con usuarios reales. No reemplaza esa prueba.

Úsalo para:
- comparar variantes de una pantalla antes de decidir cuál llevar a pruebas con personas;
- encontrar fricciones obvias en un prototipo o en un ambiente dev antes de reclutar;
- revisar textos contra la guía de estilo del producto;
- preparar un estudio real: qué observar, qué preguntar, dónde poner atención.

No lo uses para:
- tomar una decisión de alto impacto solo con sus resultados;
- temas sensibles (salud, duelo, deuda en crisis) sin investigación con personas;
- reportar porcentajes como si fueran de la población («el 80% de los clientes…»).

---

## 2. Antes de empezar

Necesitas:
- **Claude Code** con sesión iniciada (las sesiones sintéticas usan tu suscripción, no una API key);
- **Python 3.12** y **uv**;
- para recorridos, el CLI de Playwright (`~/.claude/skills/playwright/scripts/playwright_cli.sh`);
- el vault de Obsidian «vault-equipo» (base de conocimiento metodológico): viene con el arnés como submódulo en
  `vault/`, o en Google Drive si ya lo tienes ahí.

Instalación, una sola vez:

```bash
git clone --recursive https://github.com/ShortwabeCustom/arnes-usuarios-sinteticos.git
cd arnes-usuarios-sinteticos
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
git config core.hooksPath .githooks   # guardia y pruebas antes de cada commit
arnes doctor               # revisa todo y dice cómo arreglar lo que falte
```

Cada vez que abras una terminal nueva: `source .venv/bin/activate`.

**El vault.** Los dos repositorios son privados: pide acceso a los dos. El arnés busca el vault en este orden:
1. la variable `ARNES_VAULT`, si la defines;
2. la carpeta de Google Drive de `conocimiento.yaml` (así trabaja quien mantiene el vault);
3. el submódulo `vault/`, que trae el clon con `--recursive`. Si clonaste sin esa opción:
   `git submodule update --init vault`.

Para traer la versión más reciente del vault: `git submodule update --remote vault`.

**El vault se sube solo.** `arnes sintesis` hace commit y push en el vault al terminar. Para lo que escribes en
Obsidian, `arnes vault automatizar` instala una sincronización cada hora (trae lo de GitHub, hace commit con la lista
de notas que cambiaron y sube). `arnes vault` muestra el estado; `arnes vault sincronizar` lo hace en el momento.
Antes de cada commit pasa una guardia: si encuentra un correo, una llave, una CURP o un número de tarjeta, no sube
nada y te avisa con una notificación.

### Dos formas de trabajar

- **Conversando con Claude Code (recomendado para empezar).** Abre Claude Code en la carpeta del arnés y pide el
  estudio en lenguaje natural, o escribe `/investigacion-sintetica`. Claude sigue esta misma guía, te pregunta lo
  que falta y **te pide aprobación antes de gastar**.
- **Con los comandos `arnes`.** Esta guía los muestra en cada paso, para que sepas qué está pasando o lo hagas tú.

---

## 3. ¿Qué método necesitas?

| Si tu pregunta es… | Método | Lo que necesitas traer |
|---|---|---|
| ¿Se entiende esta pantalla? ¿A o B se entiende mejor? ¿El texto dice lo que creemos? | `comprension` | Imágenes de las pantallas (export de Figma o captura) |
| ¿Pueden completar el flujo? ¿Dónde se traban, dudan o abandonan? | `recorrido` | URL del prototipo de Figma o del sitio (dev/staging) |
| ¿Quién es el usuario según los datos? | `persona` | Encuesta, mazo de investigación, arquetipos |

Si dudas entre comprensión y recorrido: comprensión mira **una pantalla** a fondo (qué se lee en 5 segundos y qué
se entiende); recorrido mira **el camino** (si avanzan, cuánto les cuesta, dónde se pierden).

---

## 4. Los pasos

Son cuatro fases. Las marcadas con ⏸ son puntos de control: no se avanza sin revisar.

```
DISEÑAR          1 pregunta e hipótesis · 2 estudio y material · 3 conocimiento · 4 panel · 5 protocolo
VALIDAR          6 revisar el instrumento · 7 ⏸ aprobación · 8 ⏸ piloto
CORRER           9 sesiones y auditoría · 10 análisis
COMUNICAR        11 narrativa · 12 ⏸ reporte y verificación · 13 archivar y compartir
```

### Fase 1 · Diseñar

#### Paso 0 · Decide si vale la pena investigar

La guía «Research en tus proyectos» de UiX lo resume en una matriz de **impacto en negocio × incertidumbre**: alto y
alta, sí investigar; alto y baja, validar rápido; bajo y alta, explorar; bajo y baja, no investigar. Una mejora
cosmética o un cambio técnico sin efecto en el usuario no necesita estudio; un cambio en registro, pago o en el flujo,
sí. Anota tu decisión en `uix.decision` de `estudio.yaml` y en el brief del protocolo.

#### Paso 1 · Escribe la pregunta y las hipótesis

Una pregunta principal y de 2 a 5 hipótesis. Cada hipótesis dice **qué la confirmaría y qué la descartaría**.

```yaml
hipotesis:
  - id: H1
    texto: "En un vistazo, el monto grande hace creer que hay efectivo aunque la pantalla lo niegue."
    se_sostiene_si: "Alguna corrida de vistazo responde «sí» a «¿puedes recibir el efectivo?»"
    se_cae_si: "Ninguna"
```

**Por qué.** Definir el criterio de éxito **antes** de correr evita el sesgo de confirmación: después es tentador
buscar la métrica que favorece la variante preferida (vault: [[preguntas-sugestivas]],
[[sesgos-cognitivos-en-diseno-y-research]]).

#### Paso 2 · Crea el estudio y junta el material

```bash
arnes nuevo comprension recompra-chip --proyecto oupwa --tema recompra-resultado
arnes nuevo recorrido onboarding-dev --proyecto oupwa --tema onboarding
```

Se crea `estudios/<fecha>-<nombre>/` con `estudio.yaml`, `PROTOCOLO.md` y `narrativa.yaml`. Copia el material a
`material/` tal como llega.

- **Nombre según la guía de naming de UiX.** Con `--proyecto` y `--tema`, el bloque `uix` de `estudio.yaml` arma el
  nombre del entregable: `oupwa-pdu-onboarding-sintetico_2026-10-20-v1` (proyecto, metodología, tema, fecha de fin,
  versión). La metodología sale del método (`pdu` en recorrido, `abtesting` en comprensión) y se puede cambiar por
  otro código de la guía. El arnés agrega `-sintetico` al tema para que nadie confunda el reporte con una prueba con
  personas. Elige una sola forma del proyecto y acuérdala con CS y PD.

- **Incluye siempre el diseño actual (baseline).** En comprensión, marca esa variante con `baseline: true`; en
  recorrido, usa `baseline_url`. Un 60% de acierto parece bajo hasta ver que el diseño actual da 40%
  ([[first-click-testing]]).
- **Fija la versión.** Anota fecha, hora y, en Figma, el `node-id` de inicio. Si el prototipo cambia a mitad del
  estudio, la evidencia deja de servir.
- **Recorrido:** comprueba que la URL abre sin iniciar sesión. Si pide VPN o credenciales, resuélvelo antes. Nunca
  inventes credenciales.

#### Paso 3 · Lee lo que ya sabemos

```bash
arnes conocimiento comprension              # o recorrido / persona
arnes conocimiento comprension --producto pwa
```

Lista las notas del vault que aplican al método (five-second testing, cognitive walkthrough, preguntas sugestivas,
heurísticas de Nielsen, WCAG 2.2…), las del producto (manuales de UX writing de la PWA) y las de los estándares de
UiX. Léelas y cita en `PROTOCOLO.md`, en «Referencias del vault», las que sostienen alguna decisión.

**Por qué.** El estudio se diseña sobre métodos conocidos, no improvisados. Y lo que aprendas vuelve al vault al
final (paso 13).

#### Paso 4 · Elige el panel

```bash
arnes bibliotecas                 # bibliotecas y paneles disponibles
arnes panel pwa:ocean8            # fichas, personalidad y diversidad del panel
```

| Panel (PWA) | Cuándo |
|---|---|
| `base4` | Los cuatro segmentos del User Persona, sin personalidad. Es el más fiel a los datos. |
| `base4-ocean` | Los mismos cuatro con una capa de personalidad (OCEAN). |
| `ocean8` | Ocho perfiles, dos por segmento. Más variedad de reacciones; los Boomers quedan sobrerrepresentados a propósito. |

`arnes panel` muestra qué rasgos quedan sin cubrir (por ejemplo, «falta un extremo alto de Neuroticismo»). Pega esa
tabla en el protocolo y nombra los vacíos como limitación.

**Por qué.** La población sintética tiende a parecerse demasiado a sí misma: individuos creíbles, panel poco
diferenciado ([[investigacion-con-usuarios-sinteticos]]). Conocer los vacíos evita sacar conclusiones de lo que el
panel no representa.

> La «María» de los manuales de comunicación es un arquetipo para escribir, no un perfil de investigación. Los
> perfiles salen de los datos.

#### Paso 5 · Escribe el protocolo y completa `estudio.yaml`

Sigue las plantillas: `estudio.yaml` trae comentarios en cada campo y `PROTOCOLO.md` tiene la estructura.

**Empieza por el brief.** `PROTOCOLO.md` abre con el template de protocolo de UiX ya llenado en lo que el arnés sabe
(nombre, cliente, fecha, metodología y muestra). Completa el resto: brief de 2–3 líneas, autorización, descripción,
objetivo, alcance (superficial, descriptiva, profunda o predictiva), público, equipo, fuentes y tabla de tiempos.
La muestra esperada ya trae cuántas personas recomienda UiX para validar después (por ejemplo, 8–10 en una prueba de
usabilidad): las corridas sintéticas no cuentan para esa cifra.

En **comprensión**:
- Marca cada zona de texto de la pantalla (caja en píxeles, texto y rol: titular, monto, acción, nota…). Claude
  puede hacerlo mirando la imagen.
- **Primero una pregunta abierta** («Con tus palabras, ¿qué te está diciendo esta pantalla?»), después las cerradas.
  Así no siembras la respuesta.
- En cada pregunta cerrada, incluye una salida neutra (`no_se`, `en_parte`) y la respuesta correcta.
- Si la pantalla usa un nombre de ejemplo, ponlo en `nombre_de_ejemplo`.

En **recorrido**:
- Tareas con escenario e instrucción **sin usar las palabras exactas de la interfaz**. «Solicita un préstamo de
  $30,000», no «Toca Solicitar ahora».
- Un `fin` que el arnés pueda comprobar (texto visible, URL o `node-id`) y un `primer_toque` esperado.
- `retoma` en la tarea más larga, para saber si al salir y volver se conserva el avance.
- Datos de prueba **claramente ficticios**. Nunca datos reales.

En los dos: `corridas` de 2 o 3 y, si el producto tiene guía de estilo, `guia_estilo: pwa`.

### Fase 2 · Validar el instrumento

#### Paso 6 · Revisa el instrumento

```bash
arnes revisar <estudio>      # preguntas sugestivas, baseline, lenguaje de la interfaz
arnes estilo <estudio>       # textos contra la guía de estilo del producto
```

`arnes revisar` **bloquea** las preguntas sugestivas («¿no crees que…?», «…, ¿verdad?», «¿qué tanto te gustó…?») y
avisa lo demás. Corrige los errores; lee los avisos.

**Por qué.** En la validación del arnés, cambiar solo la redacción de las preguntas movió las respuestas más que la
diferencia entre las variantes A y B. **El texto de la pregunta también es parte de lo que se mide.**

#### Paso 7 · ⏸ Aprobación del protocolo y del costo

```bash
arnes sesiones <estudio> --simular       # comprensión: cuántas sesiones va a correr
```

Antes de correr, que alguien (tú, o quien pidió el estudio) apruebe hipótesis, panel, preguntas o tareas, total de
sesiones y costo estimado. Referencias en la sección 7.

#### Paso 8 · ⏸ Estudio piloto

```bash
arnes medir <estudio>                     # comprensión: revisa el orden de lectura que imprime
arnes sesiones <estudio> --piloto         # comprensión: un perfil, corrida 1
arnes recorrido <estudio> S01 --tarea T1 --corridas 1    # recorrido: un perfil, una tarea
```

Abre lo que salió (`datos/sesiones/`; en recorrido, también `datos/capturas/` y el video en `datos/videos/`) y
pregúntate: ¿el perfil vio lo que tenía que ver?, ¿la pregunta se entendió?, ¿el toque cayó donde debía? Si algo
está mal, corrige y repite el piloto.

**Por qué.** El estudio piloto se recomienda siempre ([[marco-de-metodos-de-investigacion-ux]]). Es mucho más
barato descubrir un error con 4 sesiones que con 96.

### Fase 3 · Correr y analizar

#### Paso 9 · Corre las sesiones y la auditoría

```bash
arnes sesiones <estudio>                          # comprensión
arnes recorrido <estudio> todos                   # recorrido
arnes auditar <estudio>                           # 3 evaluaciones expertas independientes
```

Cada sesión arranca con contexto limpio: un perfil no sabe qué hicieron los demás. Si algo se corta, el mismo comando
retoma donde quedó, sin repetir lo hecho.

`arnes auditar` pone a 3 evaluadores independientes a revisar cada pantalla (UX writing en comprensión, heurísticas
de Nielsen en recorrido, más los criterios de la guía del producto). Lo que marcan 2 o más es consenso.

**Por qué.** Una evaluación heurística confiable usa entre 3 y 5 evaluadores que no ven las notas de los demás
([[evaluacion-heuristica]]).

#### Paso 10 · Analiza: primero la firmeza, después las cifras

```bash
arnes analizar <estudio>
```

Lee el bloque de **firmeza** antes que cualquier porcentaje:
- **Estabilidad entre corridas:** ¿cada perfil repite su respuesta? Lo que no se repite es señal, no patrón.
- **Brechas entre variantes:** cada comparación A/B lleva su intervalo. «No concluyente» quiere decir que los
  intervalos se tocan; **no la presentes como diferencia**, por grande que se vea.
- **Homogeneidad:** si todos los perfiles dicen lo mismo, pregúntate si la pantalla es inequívoca o si el panel no
  está diferenciando.

En recorrido, además: resultados por tarea, embudo, momentos donde cae la confianza y las métricas de flujo (pasos,
clics, campos, tiempo estimado, validaciones, cambios de canal, retoma, estatus visible, distancia a la compra).

Después lee una muestra de sesiones completas. Los números dicen dónde mirar; las sesiones dicen qué pasó.

**Por qué.** Con muestras pequeñas, dos opciones cercanas no se distinguen: cree en las brechas grandes y en lo que se
repite ([[investigacion-con-usuarios-sinteticos]]).

### Fase 4 · Comunicar

#### Paso 11 · Escribe la narrativa

`narrativa.yaml` es donde va tu interpretación. El código pone las tablas; tú pones el sentido.

- **El titular dice la conclusión, no el tema.** «La negativa no entra en un vistazo», no «Resultados del vistazo».
- **Cada hallazgo en orden: hallazgo → interpretación → recomendación**, con evidencia (sesión, captura, cifra),
  severidad de 0 a 4 y confianza (alta, media, baja).
- **Las cifras llevan su base:** «19 de 24 corridas», nunca «79% de los clientes».
- En recorrido, cada hallazgo indica `categoria` (A diseño, C cableado) y `walkthrough` (en cuál de las 4 preguntas
  del cognitive walkthrough falla). Un botón sin conexión en un prototipo **no es un defecto**: va en
  `estado_prototipado`.
- Cada hallazgo lleva `oportunidad`, la clasificación del template de UiX: `mantener`, `mejorar`, `incorporar` o
  `hacer_diferente`. Aparece en la priorización.
- Siempre: lo que funciona, límites, qué validar con personas y `aprendizajes_metodo` (qué te enseñó el estudio sobre
  el método; va al vault).
- Sin «todos», «nadie», «demuestra», «provoca». OCEAN no predice: «en esta simulación, los perfiles con
  Neuroticismo alto mostraron…».

#### Paso 12 · ⏸ Reporte y verificación

```bash
arnes reporte <estudio>
arnes verificar <estudio>      # tiene que terminar en LISTO PARA ENTREGAR
```

`arnes verificar` recuenta cada cifra de los KPI contra los datos, revisa que cada hallazgo tenga su cadena completa,
marca el lenguaje que la guía editorial prohíbe y avisa si un KPI se apoya en algo que no se repite.

También revisa el naming de UiX y que los perfiles declaren los cuatro datos demográficos de UiX.

Abre el reporte (`reporte/<nombre-uix>.html`, funciona sin internet) y míralo completo antes de compartir. En
recorrido, la tabla de resultados trae el **semáforo de completitud de UiX** (verde ≥ 90%, amarillo 78–89%, naranja
50–77%, rojo < 50%) con su intervalo. Está pensado para personas: con pocas corridas el intervalo cruza varios colores
y el reporte lo dice, en vez de dar un color que no es firme. El panel muestra generación, género, región y ocupación
de cada perfil con su evidencia; donde el User Persona no tiene el dato, dice AUSENTE.

#### Paso 13 · Archiva y comparte

```bash
arnes sintesis <estudio> --simular     # muestra qué escribiría en el vault
arnes sintesis <estudio>               # lo escribe y lo sube a GitHub (--sin-subir para no subirlo)
```

Guarda en `03-Sintesis/` del vault lo que aprendió el estudio, con enlaces a las notas de concepto que aplicó. No
archives estudios de prueba.

Para compartir, manda el HTML del reporte o pídele a Claude que lo publique como Artifact privado. Al presentarlo,
abre con el aviso de investigación sintética y cierra con «qué validar con personas».

---

## 5. Cómo leer un resultado

Cada dato del reporte lleva una etiqueta de origen:

| Etiqueta | Quiere decir | Cuánto pesa |
|---|---|---|
| **EVIDENCIA** | Medido en el material: un toque real, un contraste, un campo del DOM | Lo más firme |
| **MODELO** | Salida de un modelo igual para todos (atención predicha, tiempo estimado) | Orienta; no es conducta |
| **INFERENCIA** | Conclusión razonable derivada de datos, o evaluación experta | Discutible |
| **SIMULACIÓN** | Lo que dijo o hizo un perfil sintético | Hipótesis |
| **SUPUESTO** | Dato que faltaba y se asumió | Declarado; revisar |

Y tres lecturas que ayudan:
- **«Sin cobertura»** no es un fallo de comprensión: el perfil está diciendo que sus datos no alcanzan para
  responder. Es un vacío de la fuente y un buen candidato a investigación con personas.
- **«No concluyente»** no es «empate»: quiere decir que con esta cantidad de corridas no se puede saber.
- **El tiempo estimado** es un modelo. Úsalo para comparar flujos entre sí, no como el tiempo que va a tardar una
  persona.

---

## 6. Reglas de oro

1. Pregunta e hipótesis antes que pantallas.
2. Baseline siempre: sin el diseño actual, ninguna cifra se puede leer.
3. Piloto siempre.
4. Pregunta abierta primero; nunca preguntas sugestivas.
5. Datos de prueba ficticios, nunca reales.
6. 2 o 3 corridas: cree en lo que se repite.
7. Las corridas no son población.
8. Hallazgo → interpretación → recomendación, en ese orden.
9. Siempre lo que funciona y siempre los límites.
10. Todo hallazgo importante termina en «validar con personas».

---

## 7. Costos y tiempos de referencia

Son uso de la suscripción de Claude Code, medidos en octubre de 2026.

| Qué | Costo aproximado | Tiempo |
|---|---|---|
| Comprensión, una sesión de vistazo | US$ 0.02–0.04 | segundos |
| Comprensión, lectura completa con continuación | US$ 0.07–0.15 | ~30 s |
| Comprensión, estudio de 96 sesiones | US$ 5–8 | 15–25 min (6 en paralelo) |
| Recorrido, una sesión de 6–8 pasos | US$ 0.25–0.95 | 3–6 min |
| Auditoría, 4 pantallas × 3 evaluadores | US$ 0.40–0.50 | 2–3 min |
| Prueba de fidelidad de una biblioteca | US$ 0.30 | 2 min |

---

## 8. Tropiezos conocidos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `--filtro -1` da error | El valor empieza con «-» | `--filtro=-1` |
| El perfil dice «dice María y yo me llamo Bryan» | Falta el nombre de ejemplo | `nombre_de_ejemplo: María` |
| En Figma ningún toque responde | El banner de cookies desplazó el marco | Agregar el cierre del banner en `preparacion` |
| «El prototipo termina aquí» en una pantalla con más flujo | Un toque sin efecto no significa fin | Revisar captura y video; puede ser estado de prototipado |
| Todos los perfiles siguen la misma ruta | Flujo lineal, o panel que no diferencia | Revisar si el material permite desviarse |
| Una cifra del KPI no recuenta | La narrativa quedó vieja | Volver a `arnes analizar` y corregir la narrativa |
| El reporte «es más viejo que la narrativa» | Se editó la narrativa después del reporte | `arnes reporte` de nuevo |
| `arnes vault`: «conflicto en alguna nota» | La misma nota cambió en dos lugares | Abrir la nota, resolver y `git pull --rebase` en el vault |
| No encuentra el vault | Ni Drive ni el submódulo están disponibles | `git submodule update --init vault`, o sincronizar Drive |

---

## 9. Hoja de comandos

```bash
source .venv/bin/activate

# diseñar
arnes nuevo <comprension|recorrido|persona> <nombre> [--proyecto oupwa] [--tema …]
arnes conocimiento <metodo> [--producto pwa]
arnes bibliotecas
arnes panel <biblioteca:panel | estudio>

# validar
arnes revisar <estudio>
arnes estilo <estudio>
arnes sesiones <estudio> --simular
arnes medir <estudio>                              # comprensión
arnes sesiones <estudio> --piloto                  # comprensión
arnes recorrido <estudio> <integrante> --tarea T1  # recorrido, piloto

# correr y analizar
arnes sesiones <estudio>                           # comprensión
arnes recorrido <estudio> todos [--corridas N]     # recorrido
arnes auditar <estudio>
arnes analizar <estudio>
arnes estado <estudio>                             # qué fases se hicieron y cuánto costó

# comunicar
arnes reporte <estudio>
arnes verificar <estudio>
arnes sintesis <estudio> [--simular]

# bibliotecas de personas
arnes persona validar <biblioteca>
arnes persona probar <biblioteca>

# entorno y vault
arnes doctor                                       # qué falta en el entorno
arnes vault                                        # estado del vault como repositorio
arnes vault sincronizar [-m "mensaje"]             # commit y push del vault ahora
arnes vault automatizar [--cada 60] | quitar       # sincronización automática
```

## 10. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Reglas que sigue el agente | `CLAUDE.md` |
| Guía de cada método | `metodos/<método>/METODO.md` |
| Plantillas | `metodos/<método>/estudio.plantilla.yaml`, `PROTOCOLO.plantilla.md`, `metodos/narrativa.plantilla.yaml` |
| Perfiles sintéticos | `personas/pwa`, `personas/gic` |
| Manuales de UX writing del producto | `fuentes-producto/pwa` |
| Estándares de UiX (naming, demográficos, completitud, protocolo, muestra) | `fuentes-equipo/uix` (`estandares.yaml` es la versión que lee el arnés) |
| Estudios de ejemplo | `estudios/2026-10-05-recompra-comprension-replica` (comprensión), `estudios/prueba-recorrido-web` (recorrido) |
| Cómo se validó el arnés | `docs/VALIDACION.md` |
| Base de conocimiento | vault de Obsidian «vault-equipo»: repositorio `ShortwabeCustom/vault-equipo`, submódulo en `vault/` |
