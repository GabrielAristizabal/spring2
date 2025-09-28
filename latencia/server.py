from flask import Flask, jsonify
import random, time, socket, traceback
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "hint": "usa /pedido o /health"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "detail": e.description}), e.code
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error"}), 500

@app.route("/pedido", methods=["GET"])
def procesar_pedido():
    num_items = random.randint(1, 10)
    ubicaciones = [f"{chr(65 + (i % 26))}{i+1}" for i in range(num_items)]
    # Simulación rápida de optimización (50–150 ms)
    time.sleep(random.uniform(0.05, 0.15))
    return jsonify({
        "pedido_id": random.randint(1000, 9999),
        "items": num_items,
        "ubicaciones": ubicaciones,
        "ruta_optimizada": f"Ruta({len(ubicaciones)} puntos)",
        "instancia": socket.gethostname()
    }), 200

if __name__ == "__main__":
    # Importante: escucha en todas las interfaces
    app.run(host="0.0.0.0", port=5000)
