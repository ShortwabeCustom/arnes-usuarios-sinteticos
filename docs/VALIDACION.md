# Validación del arnés

20 de octubre de 2026. Claude Code 2.1.303, modelo `sonnet` → `claude-sonnet-5-5`.

## 1. Comprensión: réplica del estudio de recompra

Estudio: `estudios/2026-10-05-recompra-comprension-replica`. Original:
`~/Documents/claude/Investigacion comprension de pantallas en recompra`.

| Qué se comparó | Resultado |
|---|---|
| Medición de zonas (porción de saliencia, densidad, pico, alto de línea, contraste, palabras) | **240 de 240** valores idénticos |
| Orden de lectura, vistazo a 2.5/3.5/4.5 palabras/s y recorrido por perfil | **68 de 68** idénticos (con `orden_por_pliegue: false`, como el original) |
| Respuestas cerradas, corrida 1 de las 32 celdas, arnés frente a original | **145 de 168 (86%)** |
| Referencia: el original contra sí mismo, corrida 1 frente a corrida 2 | 108 de 128 (84%) |

La coincidencia del arnés con el original es del mismo orden que la variación del original consigo mismo.

### Lo que la validación enseñó

1. **La redacción de la sesión es parte del instrumento.** La primera versión del arnés hacía las preguntas como
   lista numerada y validaba con esquema JSON: coincidencia 79%, y en el vistazo del Estudio 1 los perfiles
   respondían «no sé» donde el original decía «sí». Con el texto original en el mismo motor, 4 de 4 volvieron a
   «sí»; con el texto original más el esquema JSON, también 4 de 4. La causa era la redacción, no el modelo ni el
   aislamiento. El arnés usa ahora la plantilla JSON en línea del original. Sesiones de la versión anterior:
   `datos/historial/`.
2. **Las continuaciones del original reanudaban sin el prompt del perfil.** `llamar(p2, resume=s, leer=True)`
   no volvía a pasar `--system-prompt`. El arnés lo pasa en cada turno.
3. **YAML 1.1 convierte `no` en `false`.** El arnés usa un cargador que solo acepta `true`/`false` como booleanos.
4. **El alias del modelo cambia de versión.** Cada sesión registra ahora `modelo_id`.

Diferencia residual: en el vistazo del Estudio 1 variante B el arnés etiqueta el botón como «[botón]» y el
original como «[letra muy grande]». 0 de 4 vistazos de E1-B responden «sí» a P3, contra 3 de 4 en E1-A.

## 2. Aislamiento de las sesiones

Cada sesión corre con `--system-prompt-file` (el prompt del perfil reemplaza al de Claude Code),
`--setting-sources project --strict-mcp-config --disable-slash-commands`, en una carpeta temporal fuera del
repositorio. Prueba: sin esas opciones la sesión recibía el correo de la cuenta, instrucciones de conectores MCP y
datos de entorno; con ellas quedan solo un bloque de entorno y el correo, que la suscripción no permite quitar. Las
reglas de la sesión piden ignorarlos.

## 3. Fidelidad de la biblioteca PWA

`arnes persona probar pwa` (`personas/pwa/pruebas/`):

- Preguntas fuera de cobertura respondidas con la frase exacta: **12 de 12**.
- Preguntas dentro de cobertura respondidas sin negarse: **4 de 4**.
- Pregunta que sugiere la respuesta («está muy bien hecho, ¿verdad?»): ningún perfil la acepta.

## 4. Recorrido: prueba de humo

`estudios/prueba-recorrido-web` sobre `tests/fixtures/flujo-web` (3 pasos, servido en local). Dos perfiles
completan en 6 pasos; los toques, las escrituras con datos de prueba, el embudo por pantalla, el video y el
reporte funcionan. **Falta validar contra un prototipo de Figma real** (zonas por cursor del canvas) y contra el
ambiente dev, que puede requerir VPN.

## 5. Mejoras tomadas del vault de conocimiento (20 de octubre de 2026)

**Auditoría con 3 evaluadores independientes** (`arnes auditar`, 12 llamadas, US$ 0.42) sobre las 4 pantallas de la
réplica: 43 observaciones con consenso (2 o más de 3) y 28 de un solo evaluador. El consenso cubre los 9 criterios
que el protocolo de recompra había observado a mano (W1 a W9), entre ellos la contradicción «Aprobado» / «*Sujeto a
aprobación» (3 de 3, severidad 4), la negativa escondida en el cuerpo (W1), «!María» (W9) y «Aprobado en producto»
como jerga interna (W4).

**Firmeza** (`arnes analizar`):
- Réplica, 1 corrida por perfil: 0 de 14 comparaciones entre variantes con intervalos de Wilson separados. La brecha
  más grande (E1, vistazo, P3: 75% contra 0%, 4 corridas por variante) es no concluyente.
- Estudio original, 3 corridas: estabilidad de 93% (cada perfil repite su respuesta); la brecha más grande, 92%
  contra 50% con 12 corridas por variante, tampoco tiene intervalos separados.

**Recorrido con 2 corridas** sobre el flujo de prueba: los dos perfiles repiten su resultado; primer toque correcto 4
de 4; WCAG 2.5.8 sin fallas (los enlaces chicos pasan por la excepción de espaciado; el caso que falla está cubierto
en `tests/test_arnes.py`). La alerta de ruta idéntica se dispara, como corresponde a un flujo lineal.

**Síntesis en el vault**: `03-Sintesis/estudio-2026-10-05-recompra-comprension-replica.md`, entrada en el índice y el
log, y un enlace en «Ver también» de 8 notas de concepto. Respaldo de los 10 archivos previos en
`respaldos-vault/2026-10-20-antes-de-sintesis-recompra/` (fuera de git).

## 6. Guía de estilo de la PWA

`arnes estilo` sobre las pantallas de la réplica: 2 errores («!María, tienes», sin signo de apertura, en E2-A y
E2-B) y 2 avisos («Saber mas», posible acento faltante). Ningún falso positivo en E1 después de revisar la pantalla
completa en lugar de zona por zona (antes, la frase «¡María, tienes… listos para usar!», repartida en dos zonas, se
marcaba como error). `arnes auditar` con los criterios G de la guía (12 llamadas, US$ 0.51): 59 observaciones con
consenso; G1 (certeza) con 3 de 3 en E2-A y E2-B por «*Sujeto a aprobación».

## Cómo repetir la validación

```bash
source .venv/bin/activate
arnes medir estudios/2026-10-05-recompra-comprension-replica      # compara con el medicion.json original
arnes sesiones estudios/2026-10-05-recompra-comprension-replica --filtro=-1
arnes analizar estudios/2026-10-05-recompra-comprension-replica
```
