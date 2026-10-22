# Instalación del arnés

Para quien va a usar el arnés por primera vez en su computadora. Son tres comandos; el resto se instala solo. Cuando
termines, sigue con [GUIA.md](GUIA.md), que explica cómo hacer tu primer estudio.

Probado en macOS. En Linux debería funcionar igual, y en Windows no se ha probado (habría que usar WSL).

---

## 1. Antes de clonar (una sola vez)

Esto no se puede automatizar porque depende de tus cuentas.

| Qué | Para qué | Cómo |
|---|---|---|
| **Acceso a los dos repositorios privados** | Bajar el arnés y el vault | Pídeselo a Alexis: `ShortwabeCustom/arnes-usuarios-sinteticos` y `ShortwabeCustom/vault-equipo`. Acepta las dos invitaciones que te llegan por correo. |
| **GitHub CLI con tu sesión** | Que git pueda bajar los repositorios privados sin pedirte contraseña | `brew install gh` y luego `gh auth login` (elige GitHub.com → HTTPS → iniciar sesión en el navegador) |
| **Claude Code con tu cuenta** | Es el motor de las sesiones sintéticas; usa tu suscripción, no una API key | Instálalo desde [claude.com/claude-code](https://claude.com/claude-code) y ábrelo una vez para iniciar sesión |
| **Node.js** (solo para recorridos) | Abrir prototipos de Figma o sitios con Playwright | `brew install node` |

Si no tienes Homebrew (`brew`), instálalo desde [brew.sh](https://brew.sh).

---

## 2. Instalar (tres comandos)

```bash
git clone https://github.com/ShortwabeCustom/arnes-usuarios-sinteticos.git
cd arnes-usuarios-sinteticos
bin/instalar
```

La primera vez tarda entre 30 segundos y unos minutos, según tu conexión. Así se ve cuando sale bien:

```
→ Creando el entorno de Python 3.12 (.venv)
→ Instalando dependencias
→ Bajando el vault (submódulo vault/)
→ Preparando Playwright para los recorridos
→ Comando arnes listo en ~/.local/bin
Revisión del entorno del arnés:

  ✓ Python 3.12
  ✓ Entorno de Python del arnés (.venv)
  ✓ Claude Code (motor de las sesiones)
  ✓ CLI de Playwright (recorridos)
  ✓ Bibliotecas de personas (gic, pwa)
  ✓ Vault (vault)
  · Vault: sincronización automática
  ✓ Guardia antes de cada commit
  ✓ Repositorio conectado a GitHub

Listo para trabajar.
```

Si dice **«Listo para trabajar»**, terminaste. Las líneas con `·` son opcionales.

**Otra forma:** en lugar de `bin/instalar`, abre Claude Code en la carpeta del arnés. Al iniciar corre la misma
instalación por su cuenta. La primera vez te pregunta si confías en la carpeta: di que sí.

---

## 3. Qué instaló `bin/instalar`

No tienes que hacer nada de esto; está aquí para que sepas qué hay en tu computadora.

| Qué | Dónde | Por qué |
|---|---|---|
| **uv**, si no lo tenías | `~/.local/bin/uv` | Instala y aísla Python sin tocar el del sistema |
| **Python 3.12 y las dependencias** del arnés (PyYAML, NumPy, Pillow, OpenCV, pytest) | `.venv/`, dentro de la carpeta del arnés | Todo queda en la carpeta y no afecta a otros proyectos |
| **El vault** de Obsidian (la base de conocimiento metodológico) | `vault/`, dentro de la carpeta del arnés | El arnés lo lee para diseñar protocolos y escribe ahí lo aprendido |
| **Playwright** y su navegador | caché de npm y de Playwright | Los recorridos abren prototipos y sitios con él |
| **La guardia de commits** | `.githooks/` (configuración de git del clon) | Antes de cada commit bloquea correos, llaves, CURP y tarjetas, y corre las pruebas |
| **El comando `arnes`** | `~/.local/bin/arnes` | Funciona en cualquier terminal, sin activar nada |

Puedes correr `bin/instalar` las veces que quieras: solo hace lo que falte.

---

## 4. Comprobar que funciona

```bash
arnes doctor                  # revisa todo de nuevo
arnes bibliotecas             # debe listar «gic» y «pwa»
arnes panel pwa:base4         # los cuatro perfiles de la PWA
arnes conocimiento recorrido  # notas del vault para el método de recorrido
```

Si las cuatro responden, puedes empezar tu primer estudio: [GUIA.md](GUIA.md), sección 3.

---

## 5. Lo que pasa solo después

- **Al hacer `git pull`:** si llegaron dependencias nuevas, el siguiente `arnes` las instala antes de correr.
- **Al abrir Claude Code** en la carpeta, revisa la instalación en un segundo y repara lo que falte.
- **Al escribir una síntesis** (`arnes sintesis`), el arnés la sube al repositorio del vault.
- **Para traer lo nuevo del vault:** `arnes vault sincronizar`.

---

## 6. Si algo sale mal

| Mensaje | Qué pasa | Qué hacer |
|---|---|---|
| `No pude bajar el vault` o `No encuentro el vault` | Falta acceso a `vault-equipo` o tu sesión de GitHub | Acepta la invitación al repositorio, corre `gh auth login` y de nuevo `bin/instalar` |
| `Falta Claude Code` | `claude` no está instalado o no está en el PATH | Instálalo y ábrelo una vez para iniciar sesión |
| `Falta Node.js` | Sin Node no abren los recorridos | `brew install node` y de nuevo `bin/instalar`. Comprensión y persona funcionan sin él |
| `Agrega ~/.local/bin a tu PATH` | Tu terminal no busca comandos en esa carpeta | Agrega `export PATH="$HOME/.local/bin:$PATH"` a `~/.zshrc` y abre otra terminal. Mientras tanto usa `bin/arnes` desde la carpeta del arnés |
| `command not found: arnes` | Lo mismo que el anterior | Igual que el anterior |
| `No pude instalar uv` | Sin internet, o el instalador está bloqueado | `brew install uv` y de nuevo `bin/instalar` |
| `Guardia: esto no debería subirse a GitHub` al hacer commit | Hay un correo, una llave, una CURP o una tarjeta en lo que vas a subir | Quítalo. Si es un dato de ejemplo, usa un correo `@example.com` |

Si nada de esto lo resuelve, corre `arnes doctor` y comparte lo que diga.

---

## 7. Para quien mantiene el vault en Google Drive

Si editas el vault en Obsidian desde Google Drive, el arnés usa esa carpeta en lugar de `vault/`. Además:

```bash
arnes vault automatizar   # sube cada hora lo que escribes en Obsidian (macOS)
arnes vault               # estado: cambios sin subir, último commit
arnes vault quitar        # desactiva la sincronización automática
```

Si la sincronización falla (por ejemplo, la misma nota cambió en dos lugares), llega una notificación de macOS y el
detalle queda en `~/Library/Logs/arnes-vault.log`. Si el vault vive en otra carpeta, defínela en `ARNES_VAULT`.

---

## 8. Desinstalar

```bash
arnes vault quitar                      # solo si activaste la sincronización automática
rm ~/.local/bin/arnes
rm -rf ~/ruta/a/arnes-usuarios-sinteticos
```
