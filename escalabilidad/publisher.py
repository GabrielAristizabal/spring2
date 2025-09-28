from flask import Flask, jsonify
import pika, json, random

app = Flask(__name__)

rabbit_host = "IP_PRIVADA_BROKER"
rabbit_user = "monitoring_user"
rabbit_password = "isis2503"
exchange = "monitoring_measurements"
topic = "ML.505.Pedidos"

credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()
channel.exchange_declare(exchange=exchange, exchange_type="topic")

@app.route("/pedido", methods=["POST"])
def generar_pedido():
    pedido = {"items": [f"item{random.randint(1,100)}" for _ in range(random.randint(1, 10))]}
    channel.basic_publish(exchange=exchange, routing_key=topic, body=json.dumps(pedido))
    return jsonify({"status": "ok", "pedido": pedido})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
