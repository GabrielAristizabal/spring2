from flask import Flask, request, jsonify
import pika
import json
import random

app = Flask(__name__)

# Configuración RabbitMQ
rabbit_host = "IP_PRIVADA_BROKER"      # Cambia por la IP privada de tu instancia Broker
rabbit_user = "monitoring_user"        # Usuario RabbitMQ que creaste
rabbit_password = "isis2503"           # Contraseña RabbitMQ
exchange = "monitoring_measurements"   # Exchange configurado
topic = "ML.505.Pedidos"               # Routing key / topic

def publicar_pedido(pedido):
    """Abre conexión a RabbitMQ, publica mensaje y cierra conexión"""
    try:
        credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
        )
        channel = connection.channel()

        # Declarar exchange (asegura que existe)
        channel.exchange_declare(exchange=exchange, exchange_type="topic")

        # Publicar mensaje
        channel.basic_publish(
            exchange=exchange,
            routing_key=topic,
            body=json.dumps(pedido)
        )

        connection.close()
        return True
    except Exception as e:
        print(f"[!] Error publicando pedido: {e}")
        return False

@app.route("/pedido", methods=["POST"])
def generar_pedido():
    # Si llega un JSON, lo usamos; si no, generamos aleatorio
    if request.is_json:
        pedido = request.get_json()
    else:
        pedido = {"items": [f"item{random.randint(1,100)}" for _ in range(random.randint(1, 10))]}

    if publicar_pedido(pedido):
        return jsonify({"status": "ok", "pedido": pedido}), 200
    else:
        return jsonify({"status": "error", "msg": "No se pudo enviar a RabbitMQ"}), 500

if __name__ == "__main__":
    # Escuchar en todas las interfaces en puerto 5000
    app.run(host="0.0.0.0", port=5000)
