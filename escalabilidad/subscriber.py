import pika
import pymysql
import json

# -------------------------
# Configuración de RabbitMQ
# -------------------------
rabbit_host = "IP_PRIVADA_BROKER"        # Cambia por la IP privada del broker
rabbit_user = "monitoring_user"          # Usuario RabbitMQ
rabbit_password = "isis2503"             # Contraseña RabbitMQ
exchange = "monitoring_measurements"     # Debe coincidir con publisher
topic = "ML.505.#"                       # Escucha todos los pedidos que empiezan por ML.505

# -------------------------
# Configuración de MySQL
# -------------------------
db = pymysql.connect(
    host="ENDPOINT_RDS",   # Ej: pedidos-db.xxxxx.us-east-1.rds.amazonaws.com
    user="admin",          # Usuario MySQL
    password="TU_PASSWORD",
    database="pedidosdb"   # La base de datos que creaste
)
cursor = db.cursor()

# -------------------------
# Callback para procesar mensajes
# -------------------------
def callback(ch, method, properties, body):
    try:
        pedido = json.loads(body)
        print(f"[x] Recibido: {pedido}")

        # Si no viene con "items", lo normalizo para guardar
        if "items" in pedido:
            items = pedido["items"]
        else:
            # Si vino algo como {"prueba":"jmeter"}, lo meto en una lista
            items = [pedido]

        sql = "INSERT INTO pedidos (items) VALUES (%s)"
        cursor.execute(sql, (json.dumps(items),))
        db.commit()

        print("[x] Pedido insertado en MySQL")

    except Exception as e:
        print(f"[!] Error procesando mensaje: {e}")

# -------------------------
# Conexión a RabbitMQ
# -------------------------
credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()

channel.exchange_declare(exchange=exchange, exchange_type="topic")

# Declarar cola temporal (auto-delete)
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

# Vincular la cola al exchange con el topic
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

print("[*] Esperando mensajes de RabbitMQ...")

# Empezar a consumir
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
