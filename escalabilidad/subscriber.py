import pika
import pymysql
import json

# --- Configuración RabbitMQ ---
rabbit_host = "IP_PRIVADA_BROKER"       # IP privada del broker
rabbit_user = "monitoring_user"
rabbit_password = "isis2503"
exchange = "monitoring_measurements"
topic = "ML.505.#"                      # escucha todo lo que venga de ML.505

# --- Configuración Base de Datos ---
db = pymysql.connect(
    host="ENDPOINT_RDS",     # Endpoint de tu base de datos MySQL en RDS
    user="admin",            # Usuario maestro
    password="TU_PASSWORD",  # Contraseña
    database="pedidosdb"     # Nombre de la base que creaste
)
cursor = db.cursor()

# --- Conexión a RabbitMQ ---
credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()
channel.exchange_declare(exchange=exchange, exchange_type="topic")

# Declarar cola temporal exclusiva
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Vincular cola al exchange
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

print(" [*] Esperando mensajes de RabbitMQ...")

def callback(ch, method, properties, body):
    pedido = json.loads(body.decode())
    print(f" [x] Recibido: {pedido}")

    # Insertar en la base MySQL
    sql = "INSERT INTO pedidos (items) VALUES (%s)"
    cursor.execute(sql, (json.dumps(pedido["items"]),))
    db.commit()
    print(" [x] Pedido insertado en MySQL")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
