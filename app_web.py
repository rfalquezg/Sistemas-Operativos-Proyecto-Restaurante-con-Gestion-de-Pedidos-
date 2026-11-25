
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

from simulacion import ejecutar_simulacion


# Carpeta principal del proyecto.
BASE = Path(__file__).resolve().parent

# Archivos que utiliza la interfaz web.
RECURSOS = {
    "/": ("web/index.html", "text/html; charset=utf-8"),
    "/estilos.css": ("web/estilos.css", "text/css; charset=utf-8"),
    "/interfaz.js": ("web/interfaz.js", "text/javascript; charset=utf-8"),
}


# Servidor de la aplicacion Gestion de Pedidos.
class ServidorRestaurante(BaseHTTPRequestHandler):

    # Enviar los archivos HTML, CSS y JavaScript al navegador.
    def do_GET(self):

        # Evitar el error 404 cuando el navegador pide el favicon.
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # Verificar que el archivo solicitado este permitido.
        if self.path not in RECURSOS:
            self.send_error(404, "Pagina no encontrada")
            return

        nombre, tipo = RECURSOS[self.path]
        ruta = BASE / nombre

        # Comprobar que el archivo exista dentro del proyecto.
        if not ruta.is_file():
            self.send_error(
                404,
                f"No existe {nombre}. Revisa la carpeta web."
            )
            return

        # Leer el archivo solicitado.
        contenido = ruta.read_bytes()

        # Enviar el contenido al navegador.
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        self.wfile.write(contenido)

    # Recibir los parametros de la simulacion.
    def do_POST(self):

        # Solo permitir solicitudes para ejecutar simulaciones.
        if self.path != "/api/simular":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            # Leer el tamaño de los datos enviados.
            longitud = int(
                self.headers.get("Content-Length", "0")
            )

            # Comprobar que la solicitud sea valida.
            if not 0 < longitud <= 4096:
                raise ValueError(
                    "Solicitud vacia o demasiado grande."
                )

            # Convertir la informacion recibida a JSON.
            datos = json.loads(
                self.rfile.read(longitud).decode("utf-8")
            )

            if not isinstance(datos, dict):
                raise ValueError(
                    "Los parametros deben ser un objeto JSON."
                )

            # Ejecutar los hilos con los datos seleccionados.
            resultado = ejecutar_simulacion(
                tipo=datos.get("tipo", "basico"),
                con_mutex=datos.get("con_mutex", False),
                cocineros=datos.get("cocineros", 2),
                stock=datos.get("stock", 1)
            )

            # Devolver los resultados a la interfaz web.
            self.enviar_json(resultado, 200)

        except (
                ValueError,
                TypeError,
                UnicodeDecodeError
        ) as error:

            self.enviar_json({
                "error": str(error)
            }, 400)

        except Exception as error:

            print(f"Error al ejecutar la simulacion: {error}")

            self.enviar_json({
                "error": "Ocurrio un error al ejecutar los hilos."
            }, 500)

    # Enviar los resultados en formato JSON.
    def enviar_json(self, datos, codigo):

        contenido = json.dumps(
            datos,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(codigo)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(contenido))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(contenido)


# Iniciar el servidor de Gestion de Pedidos.
if __name__ == "__main__":

    direccion = "127.0.0.1"
    puerto = 8000

    servidor = ThreadingHTTPServer(
        (direccion, puerto),
        ServidorRestaurante
    )

    print("=" * 55)
    print("GESTION DE PEDIDOS")
    print("=" * 55)
    print(f"Interfaz disponible en http://{direccion}:{puerto}")
    print("Presiona Ctrl+C para cerrar el servidor.")
    print("=" * 55)

    try:
        servidor.serve_forever()

    except KeyboardInterrupt:
        print("\nCerrando el servidor...")

    finally:
        servidor.server_close()
        print("Servidor cerrado correctamente.")
