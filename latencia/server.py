from flask import Flask, jsonify
import random, time, socket

app = Flask(__name__)

@app.route("/pedido", methods=["GET"])
def procesar_pedido():
    # Simular que un pedido tiene entre 1 y 10 ítems
    num_items = random.randint(1, 10)
    # Simular ubicaciones (A1, B2, etc.)
    ubicaciones = [f"{chr(65+i)}{i+1}" for i in range(num_items)]

    # Simular optimización rápida (milisegundos)
    time.sleep(random.uniform(0.05, 0.15))

    return jsonify({
        "pedido_id": random.randint(1000, 9999),
        "items": num_items,
        "ubicaciones": ubicaciones,
        "ruta_optimizada": f"Ruta({len(ubicaciones)} puntos)",
        "instancia": socket.gethostname()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
