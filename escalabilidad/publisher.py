import boto3
import random
import json
import time

# Configuración AWS
REGION = "us-east-1"  # cámbialo si tu región es diferente
TOPIC_ARN = "link de ARN de SNS"

sns = boto3.client("sns", region_name=REGION)

def crear_pedido():
    n_items = random.randint(1, 10)
    pedido = {
        "pedido_id": random.randint(1000, 9999),
        "items": [f"item_{i}" for i in range(n_items)]
    }
    return pedido

def publicar_pedido():
    pedido = crear_pedido()
    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(pedido),
        Subject="NuevoPedido"
    )
    print("📦 Pedido publicado:", pedido)
    return response

if __name__ == "__main__":
    for _ in range(5):  # ejemplo: publica 5 pedidos
        publicar_pedido()
        time.sleep(1)
