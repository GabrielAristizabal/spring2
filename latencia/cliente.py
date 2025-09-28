import requests

URL = "http://<DNS-ALB>/pedido"  # apunta al Load Balancer

for i in range(10):
    r = requests.get(URL)
    print(f"Respuesta {i+1}: {r.json()}")
