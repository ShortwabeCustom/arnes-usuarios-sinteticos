# Arnés de investigación UX sintética

Automatiza la investigación UX con usuarios sintéticos basados en evidencia: lo que antes se armaba a mano en
cada carpeta (GIC y PWA User Person, OU-PWA, entrecalles, recompra ×2, auditoría de prototipos) ahora es un
proceso con fases, datos trazables, reporte autocontenido y control final.

**Los resultados son hipótesis de UX a validar con personas.** El arnés no reemplaza la investigación con
usuarios reales; la hace más rápida de diseñar y más honesta de reportar.

**¿Primera vez?** Empieza por [docs/GUIA.md](docs/GUIA.md): los pasos de una prueba con usuarios sintéticos, de la
pregunta al reporte, con las prácticas de UX research que aplica cada uno.

## Instalación

Requiere acceso a este repositorio y a `ShortwabeCustom/vault-equipo`, Claude Code con sesión iniciada y, para
recorridos, Node.js. Lo demás se instala solo:

```bash
git clone https://github.com/ShortwabeCustom/arnes-usuarios-sinteticos.git
cd arnes-usuarios-sinteticos
bin/instalar          # Python 3.12, dependencias, vault, Playwright, guardia y el comando `arnes`
```

Al abrir Claude Code en la carpeta, `bin/instalar` corre solo.

## Qué hace

```
                 ┌──────────────────────────────────────────────────────────────┐
  datos reales → │ persona     → biblioteca de perfiles (prompts + reglas + OCEAN) │
                 └──────────────────────────────┬───────────────────────────────┘
                                                ▼
  pantallas    → comprension: medición → atención → lectura → sesiones → análisis ┐
  prototipo/web→ recorrido:   el perfil decide cada paso, el arnés toca de verdad  ┤→ narrativa → reporte → verificar
                                                                                   ┘
```

| Método | Para | Comandos |
|---|---|---|
| `persona` | Construir y probar una biblioteca de usuarios sintéticos | `arnes persona validar`, `arnes persona probar` |
| `comprension` | ¿Se entiende la pantalla? ¿A o B? | `arnes medir`, `arnes sesiones`, `arnes analizar` |
| `recorrido` | ¿Completan el flujo? ¿Dónde se traban? | `arnes recorrido`, `arnes analizar` |

Comunes: `arnes nuevo`, `arnes panel`, `arnes estado`, `arnes revisar`, `arnes auditar`, `arnes reporte`,
`arnes verificar`, `arnes conocimiento`, `arnes sintesis`, `arnes estilo`.

Guía de voz y estilo del producto: `fuentes-producto/pwa/` (manuales de UX writing de la PWA y sus reglas
verificables).

## Base de conocimiento

El arnés lee el vault de Obsidian «vault-equipo» (repositorio privado aparte, incluido como submódulo en `vault/`;
clonar con `git clone --recursive`) para diseñar cada protocolo, y al
cerrar un estudio archiva lo aprendido en `03-Sintesis/` siguiendo las convenciones del vault. Del vault salieron:
revisión de preguntas sugestivas, estabilidad entre corridas y brechas con intervalo («creer en lo que se repite»),
alerta de panel homogéneo, auditoría con evaluadores independientes, cognitive walkthrough, WCAG 2.5.8, primer toque,
baseline y piloto.

Cada sesión sintética es una llamada limpia a `claude -p` con el system prompt del perfil: usa tu suscripción
de Claude Code, sin API key. Las sesiones ya corridas no se repiten.

## Uso con Claude Code

Pide el estudio en lenguaje natural o invoca `/investigacion-sintetica`. El skill elige el método, arma el
estudio, te pide aprobación del protocolo y del costo, corre, escribe la narrativa y verifica.

## Estructura

```
arnes/                código: motor de sesiones, personas, OCEAN, medición, navegador, métodos, reporte, verificación
personas/pwa, gic/    bibliotecas copiadas de las carpetas originales, con biblioteca.yaml y pruebas de fidelidad
metodos/              guía (METODO.md) y plantillas de cada método
estudios/             un estudio por carpeta: estudio.yaml, PROTOCOLO.md, material/, datos/, narrativa.yaml, reporte/
docs/VALIDACION.md    cómo se validó el arnés contra el estudio de recompra
tests/                pruebas sin llamadas al modelo y el flujo web de prueba
```

## Validación

La réplica del estudio de comprensión de recompra reproduce la medición exacta (240 de 240 valores) y coincide
con las respuestas originales en 86%, igual que la variación del propio estudio entre corridas (84%). Detalle y
lo que se corrigió en `docs/VALIDACION.md`.

## Estudios de ejemplo

- `estudios/2026-10-05-recompra-comprension-replica` — comprensión, validación contra el original.
- `estudios/prueba-recorrido-web` — recorrido de humo sobre `tests/fixtures/flujo-web`
  (servir con `python3 -m http.server 8737` desde esa carpeta).
