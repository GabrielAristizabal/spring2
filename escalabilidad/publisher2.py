import os
import json
import time
import random
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError, NoRegionError

# ========= Config =========
# Puedes dejar valores por defecto aquí, pero lo ideal es usar variables de entorno.
DEFAULT_REGION = "us-east-1"
DEFAULT_TOPIC_ARN = "ARN_DE_TU_TOPIC_SNS"  # p.ej: arn:aws:sns:us-east-1:123456789012:mi-topico

REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or DEFAULT_REGION
TOPIC_ARN = os.getenv("TOPIC_ARN") or DEFAULT_TOPIC_ARN

# ========= Clientes =========
def make_clients():
    # Usa el provider chain de boto3 (rol de EC2, env vars, aws configure, etc.)
    session = boto3.Session(region_name=REGION)
    sts = session.client("sts")
    sns = session.client("sns")
    return sts, sns

# ========= Checks previos =========
def preflight(sts, sns):
    # 1) Verifica credenciales
    try:
        ident = sts.get_caller_identity()
        print(f"✅ Credenciales OK. Account: {ident['Account']} | ARN: {ident['Arn']}")
    except NoCredentialsError:
        raise RuntimeError(
            "❌ No hay credenciales AWS. Usa un IAM Role en la EC2 o configura 'aws configure' "
            "o variables de entorno (AWS_ACCESS_KEY_ID/SECRET/...)." )
    except ClientError as e:
        raise RuntimeError(f"❌ Error verificando credenciales STS: {e}")

    # 2) Verifica región
    if not REGION:
        raise RuntimeError("❌ Región no definida. Exporta AWS_DEFAULT_REGION o fija REGION en el script.")
    print(f"🌎 Región: {REGION}")

    # 3) Verifica Topic ARN
    if not TOPIC_ARN or TOPIC_ARN.startswith("ARN_DE_TU_TOPIC"):
        raise RuntimeError("❌ TOPIC_ARN no configurado. Exporta TOPIC_ARN o edita el script.")
    try:
        sns.get_topic_attributes(TopicArn=TOPIC_ARN)
        print(f"✅ Acceso al Topic OK: {TOPIC_ARN}")
    except ClientError as e:
        raise RuntimeError(f"❌ No se pudo acceder al Topic ARN.\n   Detalle: {e}")

# ========= Lógica de publicación =========
def crear_pedido():
    n_items = random.randint(1, 10)
    return {
        "pedido_id": random.randint(1000, 9999),
        "items": [f"item_{i}" for i in range(n_items)]
    }

def publicar_pedido(sns, pedido, max_retries=3, backoff=1.0):
    payload = json.dumps(pedido)
    for intento in range(1, max_retries + 1):
        try:
            resp = sns.publish(
                TopicArn=TOPIC_ARN,
                Message=payload,
                Subject="NuevoPedido"
            )
            print(f"📦 Publicado pedido_id={pedido['pedido_id']} | MessageId={resp.get('MessageId')}")
            return resp
        except (EndpointConnectionError, ClientError) as e:
            print(f"⚠️ Error publicando (intento {intento}/{max_retries}): {e}")
            if intento == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2  # exponencial
        except NoRegionError:
            raise RuntimeError("❌ No hay región configurada. Exporta AWS_DEFAULT_REGION o setea REGION.")
        except NoCredentialsError:
            raise RuntimeError("❌ Sin credenciales. Asegura rol de EC2 o configura AWS CLI/variables.")

# ========= Main =========
if __name__ == "__main__":
    sts, sns = make_clients()
    preflight(sts, sns)

    for _ in range(5):  # publica 5 pedidos de ejemplo
        pedido = crear_pedido()
        publicar_pedido(sns, pedido)
        time.sleep(1)
