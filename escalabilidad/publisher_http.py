from flask import Flask, jsonify
import pika, json, random, socket
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker

app = Flask(__name__)

# --- RabbitMQ ---
rabbit_host = "IP_PRIVADA_BROKER"      # ej: 172.31.xx.yy
rabbit_user = "monitoring_user"
rabbit_password = "isis2503"
exchange = "monitoring_measurements"
topic = "ML.505.Pedidos"

def publish_to_rabbit(payload: dict):
    credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    params = pika.ConnectionParameters(
        host=rabbit_host,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=10,
        connection_attempts=3,
        retry_delay=1.0
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # durable=True para que el exchange sobreviva reinicios (opcional)
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    channel.basic_publish(exchange=exchange, routing_key=topic, body=json.dumps(payload))
    connection.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/diag", methods=["GET"])
def diag():
    """Prueba conexión a 5672 y publicación de prueba; NO usa JMeter."""
    try:
        # prueba de socket cruda (red/SG)
        s = socket.create_connection((rabbit_host, 5672), timeout=3)
        s.close()
    except Exception as e:
        return jsonify({"status":"error", "where":"tcp_connect", "detail": str(e)}), 503

    try:
        publish_to_rabbit({"ping":"ok"})
        return jsonify({"status":"ok", "rabbit":"publish_ok"}), 200
    except AMQPConnectionError as e:
        return jsonify({"status":"error", "where":"amqp_connect", "detail": str(e)}), 503
    except ChannelClosedByBroker as e:
        return jsonify({"status":"error", "where":"channel_closed", "detail": str(e)}), 503
    except Exception as e:
        return jsonify({"status":"error", "where":"publish", "detail": str(e)}), 503

@app.route("/pedido", methods=["POST"])
def generar_pedido():
    try:
        n = random.randint(1, 10)
        pedido = {"items": [f"item{random.randint(1,100)}" for _ in range(n)]}
        publish_to_rabbit(pedido)
        return jsonify({"status": "ok", "pedido": pedido}), 200
    except AMQPConnectionError as e:
        app.logger.exception("AMQP connection error")
        return jsonify({"status":"error","where":"amqp_connect","detail": str(e)}), 503
    except ChannelClosedByBroker as e:
        app.logger.exception("Channel closed by broker")
        return jsonify({"status":"error","where":"channel_closed","detail": str(e)}), 503
    except Exception as e:
        app.logger.exception("Generic publish error")
        return jsonify({"status":"error","where":"publish","detail": str(e)}), 503

if __name__ == "__main__":
    # Abre puerto 5000 en el SG del Producer
    app.run(host="0.0.0.0", port=5000)
