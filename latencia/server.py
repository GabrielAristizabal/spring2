from flask import Flask, jsonify, redirect, url_for
import random, time, socket, traceback
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# --- Rutas básicas ---

@app.route("/", methods=["GET"])
def root():
    # Opción A: responder algo sencillo
    return jsonify({"status": "ok", "hint": "usa /pedido o /health"}), 200
    # Opción B (alternativa): redirigir a /health
    # return redirect(url_for("health"), code=302)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# --- Manejo de errores ---

@app.errorhandler(Exception)
def handle_exception(e):
    # Si es un error HTTP conocido (404, 405, etc.), respeta su código
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "detail": e.description}), e.code
    # Para cualquier otra excepción, log y 500 JSON
    print("🔥 Excepción en la app:", repr(e))
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error"}), 500

# --- Endpoint principal ---

@app.route("/pedido", methods=["GET"])
def procesar_pedido():
    num_items = random.randint(1, 10)
    # Ubicaciones simuladas A1, B2, C3, ...
    ubicaciones = [f"{chr(65 + (i % 26))}{i+1}" for i in range(num_items)]
    # Optimización rápida (50–150 ms)
    time.sleep(random.uniform(0.05, 0.15))
    return jsonify({
        "pedido_id": random.randint(1000, 9999),
        "items": num_items,
        "ubicaciones": ubicaciones,
        "ruta_optimizada": f"Ruta({len(ubicaciones)} puntos)",
        "instancia": socket.gethostname()
    }), 200

if __name__ == "__main__":
    # Asegúrate de escuchar en 0.0.0.0:5000
    app.run(host="0.0.0.0", port=5000)
