# subscriber.py
import pika
import pymysql
import json

# --- Configuración de RabbitMQ ---
rabbit_host = "IP_PRIVADA_BROKER"   # la IP privada de tu instancia broker-instance
rabbit_user = "monitoring_user"     # creado con rabbitmqctl add_user
rabbit_password = "isis2503"        # la clave que definiste

exchange = "monitoring_measurements"
topic = "ML.505.#"  # escucha cualquier mensaje del salón ML.505 (puedes adaptarlo)

# --- Configuración de la base de datos ---
db = pymysql.connect(
    host="TU-ENDPOINT-RDS",   # Endpoint RDS
    user="admin",             # usuario maestro
    password="TU_PASSWORD",   # contraseña RDS
    database="pedidosdb"      # base de datos que creaste
)
cursor = db.cursor()

# --- Conexión a RabbitMQ ---
credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()

# Declarar el exchange (tipo topic según guía)
channel.exchange_declare(exchange=exchange, exchange_type="topic")

# Crear cola exclusiva temporal para este subscriber
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Vincular la cola al exchange con el topic deseado
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

print(" [*] Esperando mensajes de RabbitMQ...")

def callback(ch, method, properties, body):
    print(f" [x] Recibido: {body.decode()}")
    try:
        data = json.loads(body.decode().replace("'", "\""))  # convierte payload en JSON
        valor = data.get("value")
        unidad = data.get("unit")

        sql = "INSERT INTO pedidos (items) VALUES (%s)"
        cursor.execute(sql, (json.dumps({"valor": valor, "unidad": unidad}),))
        db.commit()
        print(" [x] Insertado en MySQL")
    except Exception as e:
        print(" [!] Error procesando mensaje:", e)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
