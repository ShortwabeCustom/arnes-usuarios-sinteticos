# Arnés de investigación UX sintética

Este repositorio automatiza la investigación UX con usuarios sintéticos que antes se hacía estudio por estudio
(GIC y PWA User Person, OU-PWA, entrecalles, recompra ×2, auditoría de prototipos). Todo en español.

**Para retomar el trabajo:** leer `docs/BITACORA.md` (estado, decisiones y pendientes). Al terminar una sesión de
trabajo, agregar una entrada ahí. Para usar el arnés por primera vez: `docs/INSTALACION.md` y luego `docs/GUIA.md`.

## Tres métodos

| Método | Pregunta | Guía |
|---|---|---|
| `persona` | ¿Quién es el usuario según los datos? → biblioteca de perfiles | `metodos/persona/METODO.md` |
| `comprension` | ¿Se entiende esta pantalla? ¿A o B? | `metodos/comprension/METODO.md` |
| `recorrido` | ¿Pueden completar el flujo? ¿Dónde se traban? | `metodos/recorrido/METODO.md` |

Leer la guía del método **antes** de diseñar o correr un estudio.

## Flujo de un estudio

```
arnes nuevo <metodo> <nombre>     → estudios/<fecha>-<nombre>/ con estudio.yaml, PROTOCOLO.md, narrativa.yaml
arnes conocimiento <metodo>       → notas del vault que hay que leer para diseñar el protocolo
  completar estudio.yaml y PROTOCOLO.md (sección «Referencias del vault»)
arnes revisar <estudio>           → preguntas sugestivas, baseline, lenguaje de la interfaz (bloquea si hay errores)
arnes estilo <estudio>            → textos contra la guía de estilo del producto (`guia_estilo: pwa`)
  ⏸ APROBACIÓN del protocolo y del consumo en tokens (arnes sesiones|recorrido --simular)
arnes sesiones --piloto           → estudio piloto: un perfil, corrida 1; revisar antes de seguir
arnes tecnico <estudio>           → web/PWA: auditoría técnica sin perfiles (WCAG con axe, rendimiento, PWA, retoma); 0 tokens
arnes medir / arnes sesiones / arnes recorrido   (recorrido visible: subtítulos + sala de observación en vivo)
arnes auditar <estudio>           → 3 evaluaciones expertas independientes, consolidadas (opcional, recomendado)
arnes analizar                    → incluye estabilidad, brechas con intervalo, homogeneidad del panel
  escribir narrativa.yaml (hallazgos, interpretación, recomendaciones, aprendizajes_metodo)
arnes reporte
arnes verificar                   → debe decir LISTO PARA ENTREGAR
arnes sintesis <estudio>          → archiva lo aprendido en 03-Sintesis/ del vault (con --simular antes)
```

`arnes` funciona sin activar `.venv` (`bin/arnes`, enlazado en `~/.local/bin`); `bin/instalar` prepara un clon nuevo y
corre solo al abrir Claude Code (`.claude/settings.json`). En `--filtro` usar `--filtro=valor` si el valor empieza con «-».

## Puntos donde se pregunta a la persona usuaria

- Antes de correr sesiones: protocolo aprobado y consumo aceptado. Las sesiones gastan cuota de la suscripción:
  se expresan en tokens (`arnes/consumo.py`), no en dólares ni pesos.
- Si el material no abre (VPN, login, prototipo privado): reportar el error exacto y preguntar. Nunca inventar
  credenciales.
- Si hay que elegir el eje de segmentación de un User Persona o suspender una variable importante.

## Vocabulario de evidencia (cerrado)

**En las fuentes y los perfiles** (método persona): `OBSERVADO` · `INFERIDO` · `APROXIMACIÓN` · `HIPÓTESIS` ·
`AUSENTE` · `SEÑAL` (1–2 casos) · `LIMITACIÓN`. «Suspendida» es el estado de una variable, no un nivel de evidencia.

**En los estudios** (métodos comprensión y recorrido): `EVIDENCIA` (medido o visto en el material) · `MODELO`
(salida de un modelo, igual para todos los perfiles) · `SIMULACIÓN` (atribuido a un perfil sintético) ·
`INFERENCIA` · `SUPUESTO` · `SUPUESTO METODOLÓGICO` (decisión del método, declarada).

Nunca presentar una simulación como hallazgo de un usuario real ni una frase sintética como cita.

## Reglas de honestidad

- Fidelidad a los datos > consistencia conductual > completitud narrativa.
- No decir que se abrió, navegó, leyó o guardó algo que no ocurrió. Lo que falló va en `limitaciones_tecnicas`.
- Las corridas de perfiles no son población: «19 de 24 corridas», nunca «79% de los clientes».
- OCEAN no es determinista: «en esta simulación, los perfiles con N alto mostraron…».
- Un toque sin respuesta en un prototipo puede ser estado de prototipado (categoría B), no defecto.
- Un heatmap de criterio experto lleva su aclaración en el propio gráfico.
- Siempre hay hallazgos positivos y una sección de límites.

## Redacción (guía editorial de GIC y PWA)

- El titular da la conclusión, no el tema. Bloques: qué pasa → qué dato lo muestra → por qué importa → qué hacer.
- Hallazgo → interpretación → recomendación, en ese orden.
- Cifras con su base. Sin «todos», «nadie», «demuestra», «provoca» salvo evidencia explícita.
- Sin símbolos crípticos (§) ni siglas sueltas: «Apertura: 68/100 · alta», no «O 68».

## Base de conocimiento: el vault de Obsidian

El vault «vault-equipo» se busca en este orden: `ARNES_VAULT`, la carpeta de Google Drive de `conocimiento.yaml` y el
submódulo `vault/` (repositorio privado `ShortwabeCustom/vault-equipo`). En la Mac de Alexis manda Drive; su historial
de git vive fuera de Drive (`~/Documents/claude/vault-equipo.git`) y el submódulo queda vacío allí. `arnes sintesis` hace
commit y push en el vault (con guardia); `arnes vault automatizar` sube cada hora lo que Alexis escribe en Obsidian. Es un wiki vivo que mantiene la persona
usuaria: el arnés lo **lee en su ruta** y solo **escribe** en `03-Sintesis/`, más una entrada en el índice, una en
el log y una línea en «Ver también» de las notas de concepto relacionadas (convenciones de `vault-equipo/CLAUDE.md`).
No editar ninguna otra cosa del vault. Correr `arnes sintesis --simular` antes de escribir.

Lo que el vault aportó al método y el arnés aplica:
- **Creer en lo que se repite**: correr 2–3 veces; confiar en brechas grandes con intervalos separados, no en el
  orden. Una sola corrida es señal, no patrón.
- **La población sintética colapsa**: si todos los perfiles dicen lo mismo, sospechar antes de celebrar.
- **Preguntas sugestivas** (5 tipos): `arnes revisar` las bloquea.
- **Baseline y piloto** siempre.
- **Evaluación heurística con 3–5 evaluadores independientes**; severidad = frecuencia + impacto + persistencia.
- **Cognitive walkthrough**: cada fricción se ubica en una de las 4 preguntas (`walkthrough: 1–4`).
- **WCAG 2.2 · 2.5.8** (24×24 px) se mide en recorridos; **first click** (87% vs 46%) con `primer_toque`.
- **Personas por comportamiento, no por demografía; ≤ 5 activas.**
- **Tiempo en tarea solo junto a la tasa de éxito** ([[metricas-ux]]): el tiempo de una sesión sintética no mide a
  una persona; el arnés lo estima con un modelo declarado y le suma la espera real del sistema.

## Métricas de flujo (recorrido)

Pasos, clics, campos solicitados, tiempo, validaciones, cambios de canal, retoma de solicitud, visibilidad de estatus
y distancia a la compra salen de `arnes analizar`, cada una con su origen (EVIDENCIA, MODELO, INFERENCIA,
SIMULACIÓN). Detalle en `metodos/recorrido/METODO.md`. Para medir la retoma, poner `retoma` en la tarea más larga. En web/PWA:
celular emulado (`dispositivo.emular`), pantalla por `pantalla: {selector, atributo}`, `ruta_mecanica` para
`arnes tecnico` y para empezar tareas a mitad del flujo (`inicia_en`).

## Guía de voz y estilo del producto

`fuentes-producto/pwa/` guarda los manuales de UX writing de la PWA tal como los entregó el equipo (Fundamentos,
Mini Guía de Estilo, Manual de Voz y Tono) y `reglas-estilo.yaml`, con las reglas que se pueden verificar por
código (E01–E16), los criterios de tono para los evaluadores (G1–G8) y las contradicciones internas de los propios
manuales. Un estudio la activa con `guia_estilo: pwa`: `arnes estilo` revisa los textos y `arnes auditar` suma los
criterios G. La guía dice cómo quiere hablar el producto; los estudios dicen si eso se entiende. Su «María» es un
arquetipo de comunicación: no usarla como perfil sintético.

## Estándares de UiX

`fuentes-equipo/uix/` guarda las guías del equipo UiX tal como llegaron (Naming, Demográficos, Completitud de tarea,
Research en tus proyectos, Template de protocolo tipo brief) y `estandares.yaml`, que es lo que lee el arnés
(`arnes/estandares.py`):
- **Naming:** con el bloque `uix` de `estudio.yaml`, el reporte se llama `proyecto-metodologia-tema_aaaa-mm-dd-vN`;
  el tema lleva `-sintetico` al final. `arnes verificar` revisa formato y código de metodología.
- **Protocolo:** `PROTOCOLO.md` abre con el brief de UiX; cada hallazgo lleva `oportunidad` (mantener · mejorar ·
  incorporar · hacer_diferente).
- **Demográficos:** cada perfil declara edad (generación), género, región (Norte · Centro-norte · Centro · Sur) y
  ocupación, con su evidencia, o AUSENTE. Describen el panel; no lo segmentan.
- **Completitud:** el semáforo de UiX (verde ≥ 90 · amarillo 78–89 · naranja 50–77 · rojo < 50) se muestra en
  recorrido con su intervalo, como referencia. Es para personas: nunca presentarlo como tasa de éxito.
- **Muestra:** el reporte dice cuántas personas recomienda UiX para validar los hallazgos; las corridas sintéticas no
  cuentan para esa muestra.

## Crecer el arnés sin romperlo

Ver `docs/CRECER.md`. En corto: cada cambio de código con su prueba; `.githooks/pre-commit` corre guardia (correos,
llaves, CURP, tarjetas), lint y pruebas; GitHub Actions repite lo mismo en cada push; `arnes doctor` revisa el entorno;
una entrada en la bitácora por sesión.

## Lo que no se toca

- `personas/*/` son copias versionadas; las carpetas originales en `~/Documents/claude/` no se modifican.
- El texto de las sesiones en `arnes/metodos/comprension.py` y `recorrido.py` es parte del instrumento.
  Cambiarlo exige volver a correr la réplica (`docs/VALIDACION.md`).

## Entregables

`reporte/<nombre-uix>.html` (autocontenido, abre con doble clic; en recorrido es el **tablero de investigación**, ver
`docs/TABLERO.md`, y el documento completo queda en `<nombre-uix>-detalle.html`) y `.md` con el mismo nombre (naming de UiX; sin
bloque `uix`, el nombre de la carpeta). Si la persona usuaria lo pide o el reporte es para otras personas, publicarlo
además como Artifact privado y dar el link.
