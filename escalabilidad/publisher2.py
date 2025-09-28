# publisher_api.py
from flask import Flask, jsonify
import boto3
import random
import json

app = Flask(__name__)

# Configura tu cola SQS
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/PedidosQueue"

sqs = boto3.client("sqs", region_name="us-east-1")

@app.route("/crear_pedido", methods=["POST"])
def crear_pedido():
    # Generar un pedido con entre 1 y 10 items aleatorios
    num_items = random.randint(1, 10)
    pedido = {"items": [f"item{i}" for i in range(num_items)]}

    # Mandar a la cola SQS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(pedido)
    )

    return jsonify({"status": "ok", "pedido": pedido})

if __name__ == "__main__":
    # Escucha en todas las interfaces de la instancia
    app.run(host="0.0.0.0", port=5000)
