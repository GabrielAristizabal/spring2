import boto3
import json
import time

REGION = "us-east-1"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/PedidosQueue"

sqs = boto3.client("sqs", region_name=REGION)

def procesar_pedido(pedido):
    print("✅ Procesando pedido:", pedido)
    time.sleep(0.2)

def recibir_mensajes():
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )
        if "Messages" in response:
            for msg in response["Messages"]:
                body = json.loads(msg["Body"])
                pedido = json.loads(body["Message"])
                procesar_pedido(pedido)
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"]
                )
        else:
            time.sleep(1)

if __name__ == "__main__":
    recibir_mensajes()
