# subscriber.py
import boto3
import pymysql
import json
import time

# Configura la cola SQS
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/PedidosQueue"
sqs = boto3.client("sqs", region_name="us-east-1")

# Configura conexión a RDS MySQL
db = pymysql.connect(
    host="tu-endpoint-rds.amazonaws.com",
    user="admin",
    password="tu_password",
    database="pedidosdb"
)

cursor = db.cursor()

def procesar_pedido(pedido):
    sql = "INSERT INTO pedidos (items) VALUES (%s)"
    cursor.execute(sql, (json.dumps(pedido["items"]),))
    db.commit()
    print("Pedido guardado:", pedido)

while True:
    # Recibir mensajes de SQS
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,   # hasta 10 pedidos a la vez
        WaitTimeSeconds=10        # long polling
    )

    if "Messages" in resp:
        for msg in resp["Messages"]:
            pedido = json.loads(msg["Body"])
            procesar_pedido(pedido)

            # Borrar mensaje de la cola después de procesarlo
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg["ReceiptHandle"]
            )
    else:
        time.sleep(1)  # esperar un poco si no hay mensajes
