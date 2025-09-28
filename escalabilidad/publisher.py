import pika
import time
import json
import random

# --- Configuración RabbitMQ ---
rabbit_host = "IP_PRIVADA_BROKER"       # IP privada de la instancia donde corre RabbitMQ
rabbit_user = "monitoring_user"         # usuario que creaste en RabbitMQ
rabbit_password = "isis2503"            # contraseña de ese usuario
exchange = "monitoring_measurements"    # nombre del exchange
topic = "ML.505.Pedidos"                # routing key para el exchange

# --- Conexión al broker ---
credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()
channel.exchange_declare(exchange=exchange, exchange_type="topic")

print(" [*] Enviando pedidos... CTRL+C para salir")

while True:
    # Crear pedido con 1-10 ítems
    pedido = {"items": [f"item{random.randint(1,100)}" for _ in range(random.randint(1, 10))]}
    
    # Enviar a RabbitMQ
    channel.basic_publish(
        exchange=exchange,
        routing_key=topic,
        body=json.dumps(pedido)
    )
    print(" [x] Pedido enviado:", pedido)
    time.sleep(3)  # enviar cada 3 segundos
