# publisher_http.py
from flask import Flask, jsonify, request
import pika, json, random

app = Flask(__name__)

# --- RabbitMQ ---
rabbit_host = "IP_PRIVADA_BROKER"      # ej: 172.31.xx.yy (misma VPC)
rabbit_user = "monitoring_user"
rabbit_password = "isis2503"
exchange = "monitoring_measurements"
topic = "ML.505.Pedidos"               # el subscriber puede usar "ML.505.#"

def publish_to_rabbit(payload: dict):
    credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    params = pika.ConnectionParameters(
        host=rabbit_host,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=10
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    channel.basic_publish(exchange=exchange, routing_key=topic, body=json.dumps(payload))
    connection.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/pedido", methods=["POST"])
def generar_pedido():
    try:
        n = random.randint(1, 10)
        pedido = {"items": [f"item{random.randint(1,100)}" for _ in range(n)]}
        publish_to_rabbit(pedido)
        return jsonify({"status": "ok", "pedido": pedido}), 200
    except Exception as e:
        # Responder claro para que JMeter registre 5xx y puedas depurar
        return jsonify({"status": "error", "detail": str(e)}), 503

if __name__ == "__main__":
    # Recuerda abrir el puerto 5000 en el SG de la instancia Producer
    app.run(host="0.0.0.0", port=5000)
