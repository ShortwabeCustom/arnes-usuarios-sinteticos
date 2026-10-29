"""Sala de observación: una página local que muestra en vivo lo que hace cada perfil sintético.

Mientras `arnes recorrido` corre, la ventana del navegador enseña el producto (con subtítulos y el toque marcado) y
esta sala enseña lo demás: quién es el perfil, qué ve, qué piensa, qué decide, cómo cambian su confianza y su fricción,
cuánto esperó y cuántos tokens lleva la sesión. Se sirve en 127.0.0.1 (no sale de la máquina) y se cierra con el proceso.

Lo que muestra es [SIMULACIÓN] salvo la ruta, los toques y las esperas, que son reales sobre el material.
"""

from __future__ import annotations

import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PAGINA = Path(__file__).with_name("observacion.html")


class Sala:
    def __init__(self, raiz: Path, titulo: str = ""):
        self.raiz = Path(raiz).resolve()
        self.estado = dict(titulo=titulo, inicio=time.strftime("%H:%M:%S"), sesion=None, pasos=[], sesiones=[], aviso="")
        self._lock = threading.Lock()
        self._srv: ThreadingHTTPServer | None = None
        self.url = ""

    # --- servidor -------------------------------------------------------------------------------------------------
    def abrir(self, puerto: int = 0, navegador: bool = True) -> str:
        sala = self

        class Manejador(BaseHTTPRequestHandler):
            def log_message(self, *a):          # sin ruido en la terminal del estudio
                pass

            def _enviar(self, cuerpo: bytes, tipo: str, codigo: int = 200):
                self.send_response(codigo)
                self.send_header("Content-Type", tipo)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(cuerpo)

            def do_GET(self):
                u = urlparse(self.path)
                if u.path in ("/", "/index.html"):
                    return self._enviar(PAGINA.read_bytes(), "text/html; charset=utf-8")
                if u.path == "/estado.json":
                    with sala._lock:
                        cuerpo = json.dumps(sala.estado, ensure_ascii=False).encode()
                    return self._enviar(cuerpo, "application/json; charset=utf-8")
                if u.path == "/archivo":
                    ruta = (sala.raiz / (parse_qs(u.query).get("ruta") or [""])[0]).resolve()
                    # solo archivos del estudio, y solo imágenes
                    if sala.raiz in ruta.parents and ruta.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and ruta.exists():
                        return self._enviar(ruta.read_bytes(), "image/png")
                return self._enviar(b"no encontrado", "text/plain; charset=utf-8", 404)

        self._srv = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
        threading.Thread(target=self._srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self._srv.server_address[1]}/"
        if navegador:
            webbrowser.open(self.url)
        return self.url

    def cerrar(self):
        if self._srv:
            self._srv.shutdown()
            self._srv = None

    # --- eventos del recorrido ------------------------------------------------------------------------------------
    def _rel(self, ruta) -> str | None:
        if not ruta:
            return None
        p = Path(ruta)
        p = p if p.is_absolute() else self.raiz / p
        try:
            return str(p.resolve().relative_to(self.raiz))
        except ValueError:
            return None

    def iniciar_sesion(self, reg: dict, tarea: dict, max_pasos: int, estimado: int | None = None):
        with self._lock:
            self.estado.update(
                sesion=dict(id=reg["id"], nombre=reg["nombre"], segmento=reg.get("segmento", ""), perfil=reg.get("perfil", ""),
                            ocean=reg.get("ocean") or {}, tarea=tarea["id"], instruccion=" ".join(str(tarea.get("instruccion", "")).split()),
                            max_pasos=max_pasos, tokens=0, tokens_estimados=estimado, inicio=time.strftime("%H:%M:%S"), resultado=None),
                pasos=[], aviso="")

    def aviso(self, texto: str):
        with self._lock:
            self.estado["aviso"] = texto

    def pantalla(self, n: int, pantalla: str, captura, zonas: int):
        """El perfil está mirando esta pantalla (antes de decidir)."""
        with self._lock:
            self.estado["pasos"].append(dict(n=n, pantalla=pantalla, captura=self._rel(captura), zonas=zonas, estado="pensando"))

    def decision(self, n: int, perfil: dict, toque: list | None, tokens: int, recorte: list | None = None):
        with self._lock:
            p = self._ultimo(n)
            p.update(estado="actuando", pensamiento=perfil.get("pensamiento"), intencion=perfil.get("intencion"),
                     interpretacion=perfil.get("interpretacion"), accion=(perfil.get("accion") or {}).get("opcion"),
                     por_que=(perfil.get("accion") or {}).get("texto"), confianza=perfil.get("confianza"),
                     friccion=perfil.get("friccion"), progreso=(perfil.get("progreso") or {}).get("opcion"),
                     escribir=perfil.get("escribir") or None, toque=toque, recorte=recorte)
            if self.estado["sesion"]:
                self.estado["sesion"]["tokens"] = tokens

    def resultado_paso(self, n: int, respuesta: str, espera_ms: int | None, pantalla_despues: str | None):
        with self._lock:
            self._ultimo(n).update(estado="hecho", respuesta=respuesta, espera_ms=espera_ms, pantalla_despues=pantalla_despues)

    def cerrar_sesion(self, reg: dict, tokens: int):
        with self._lock:
            s = self.estado["sesion"] or {}
            s.update(resultado=reg.get("resultado"), tokens=tokens, ces=(reg.get("ces") or {}).get("ces"))
            self.estado["sesiones"].append(dict(id=reg["id"], nombre=reg["nombre"], tarea=reg["tarea"], resultado=reg.get("resultado"),
                                                pasos=len(reg.get("pasos", [])), tokens=tokens))

    def _ultimo(self, n: int) -> dict:
        for p in reversed(self.estado["pasos"]):
            if p["n"] == n:
                return p
        p = dict(n=n)
        self.estado["pasos"].append(p)
        return p
