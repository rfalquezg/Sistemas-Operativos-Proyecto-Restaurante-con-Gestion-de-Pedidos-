from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

from simulacion import ejecutar_simulacion

CARPETA = Path(__file__).resolve().parent
ARCHIVOS = {
    "/": ("web/index.html", "text/html; charset=utf-8"),
    "/estilos.css": ("web/estilos.css", "text/css; charset=utf-8"),
    "/interfaz.js": ("web/interfaz.js", "text/javascript; charset=utf-8"),
}


class ServidorRestaurante(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ARCHIVOS:
            self.send_error(404)
            return
        archivo, tipo = ARCHIVOS[self.path]
        contenido = (CARPETA / archivo).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def do_POST(self):
        if self.path != "/api/simular":
            self.send_error(404)
            return
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            if not 0 < largo <= 10000:
                raise ValueError("La solicitud es demasiado grande o esta vacia.")
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
            resultado = ejecutar_simulacion(
                tipo=datos.get("tipo", "basico"),
                con_mutex=datos.get("con_mutex", False),
                cocineros=datos.get("cocineros", 2),
                stock=datos.get("stock", 1)
            )
            self.enviar_json(resultado, 200)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            self.enviar_json({"error": str(error)}, 400)
        except Exception:
            self.enviar_json({"error": "No se pudo ejecutar el escenario."}, 500)

    def enviar_json(self, datos, codigo):
        contenido = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenido)


if __name__ == "__main__":
    direccion = "127.0.0.1"
    puerto = 8000
    servidor = ThreadingHTTPServer((direccion, puerto), ServidorRestaurante)
    print(f"Interfaz del restaurante: http://{direccion}:{puerto}")
    print("Presiona Ctrl+C para cerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()
